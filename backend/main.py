from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_redoc_html
from fastapi.openapi.utils import get_openapi
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os

from app.api import frames, results, users, admin, calibration, motorcycles
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection

# API Description with examples
API_DESCRIPTION = """
# ParkIt API - Smart Parking Detection System

Sistem deteksi parkir motor menggunakan YOLOv8 dengan kalkulasi ruang kosong otomatis.

## 🔓 Public Endpoints (Tanpa Autentikasi)

Endpoint yang bisa diakses oleh semua user tanpa API key:

| Endpoint | Deskripsi |
|----------|-----------|
| `GET /api/results/live` | Lihat hasil deteksi terbaru |
| `GET /api/results/latest` | Lihat history deteksi |
| `GET /api/results/{session_id}` | Detail hasil deteksi |
| `GET /api/results/{session_id}/image` | Gambar hasil deteksi |
| `POST /api/motorcycles/register` | Daftarkan motor |
| `GET /api/motorcycles/check/{code}` | Cek status motor |
| `GET /api/motorcycles/my/{code}` | Detail motor saya |
| `PUT /api/motorcycles/my/{code}` | Update data motor |

## 🔐 Admin Endpoints (Perlu API Key)

Endpoint yang memerlukan header `X-API-Key`:

| Endpoint | Deskripsi |
|----------|-----------|
| `POST /api/frames/upload` | Upload frame untuk deteksi |
| `POST /api/frames/complete/{session_id}` | Selesaikan session |
| `GET /api/admin/stats` | Statistik sistem |
| `GET /api/admin/sessions` | List semua session |
| `DELETE /api/admin/sessions/{session_id}` | Hapus session |
| `GET /api/admin/calibration` | List kalibrasi |
| `POST /api/admin/calibration` | Buat kalibrasi baru |
| `GET /api/motorcycles/` | List semua motor (admin) |
| `GET /api/motorcycles/stats` | Statistik motor |

## 🔑 Autentikasi

Untuk endpoint admin, tambahkan header:
```
X-API-Key: your-api-key-here
```

## 📝 Contoh Request & Response

### Register Motor
```json
// POST /api/motorcycles/register
// Request:
{
  "owner_name": "John Doe",
  "phone": "08123456789",
  "brand": "Honda",
  "model": "Vario 150",
  "color": "Hitam"
}

// Response:
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "code": "A1B2C3D4",
  "owner_name": "John Doe",
  "brand": "Honda",
  "model": "Vario 150",
  "color": "Hitam",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z"
}
```

### Get Live Results
```json
// GET /api/results/live
// Response:
{
  "session_id": "abc-123-def",
  "camera_id": "cam-1",
  "status": "completed",
  "max_detection_count": 45,
  "total_motorcycles": 45,
  "total_empty_spaces": 12,
  "parking_occupancy_rate": 78.9,
  "empty_spaces_per_row": {
    "0": 3,
    "1": 4,
    "2": 5
  }
}
```

### Upload Frame (Admin)
```json
// POST /api/frames/upload?session_id=xxx&camera_id=cam-1
// Headers: X-API-Key: your-key
// Body: multipart/form-data with 'file' field

// Response:
{
  "frame_id": "frame-uuid",
  "session_id": "session-uuid",
  "detection_count": 45,
  "parking_analysis": {
    "total_motorcycles": 45,
    "total_empty_spaces": 12,
    "parking_occupancy_rate": 78.9
  }
}
```

### Create Calibration (Admin)
```json
// POST /api/admin/calibration
// Headers: X-API-Key: your-key
// Request:
{
  "camera_id": "cam-1",
  "rows": [
    {"row_index": 0, "y_coordinate": 6400, "start_x": 400, "end_x": 6100, "label": "Row 0"},
    {"row_index": 1, "y_coordinate": 5650, "start_x": 600, "end_x": 5900, "label": "Row 1"}
  ],
  "min_space_width": 40.0,
  "space_coefficient": 0.85,
  "row_start_x": 40,
  "row_end_x": 6100
}
```
"""

# OpenAPI Tags with descriptions
TAGS_METADATA = [
    {
        "name": "🔓 Public - Results",
        "description": "Endpoint publik untuk melihat hasil deteksi parkir. **Tidak perlu autentikasi.**"
    },
    {
        "name": "🔓 Public - Motorcycles",
        "description": "Endpoint publik untuk registrasi dan cek motor. **Tidak perlu autentikasi.**"
    },
    {
        "name": "🔐 Admin - Frames",
        "description": "Upload dan proses frame deteksi. **Perlu header X-API-Key.**"
    },
    {
        "name": "🔐 Admin - Management",
        "description": "Manajemen session dan statistik. **Perlu header X-API-Key.**"
    },
    {
        "name": "🔐 Admin - Calibration",
        "description": "Konfigurasi kalibrasi kamera. **Perlu header X-API-Key.**"
    },
    {
        "name": "🔐 Admin - Motorcycles",
        "description": "Manajemen data motor (admin). **Perlu header X-API-Key.**"
    },
]

app = FastAPI(
    title="ParkIt API",
    description=API_DESCRIPTION,
    version="1.0.0",
    openapi_tags=TAGS_METADATA,
    docs_url="/docs",  # Swagger UI
    redoc_url=None,  # Disable default redoc, we'll create custom
)

# CORS
# Development: allow all origins
# Production: specify ngrok URLs
allowed_origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:8080",
    "*",  # Allow all for development
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH"],
    allow_headers=["*", "X-API-Key", "Content-Type", "Authorization"],
    expose_headers=["*"],
)

# Events
@app.on_event("startup")
async def startup_event():
    await connect_to_mongo()
    print("✅ Connected to MongoDB")

@app.on_event("shutdown")
async def shutdown_event():
    await close_mongo_connection()
    print("❌ Disconnected from MongoDB")

# Health check
@app.get("/")
async def root():
    return {
        "message": "ParkIt API",
        "status": "running",
        "timestamp": datetime.utcnow()
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Custom ReDoc endpoint
@app.get("/api-docs", include_in_schema=False)
async def api_docs():
    return get_redoc_html(
        openapi_url="/openapi.json",
        title="ParkIt API Documentation",
        redoc_favicon_url="https://fastapi.tiangolo.com/img/favicon.png"
    )

# Include routers with categorized tags
app.include_router(results.router, prefix="/api/results", tags=["🔓 Public - Results"])
app.include_router(frames.router, prefix="/api/frames", tags=["🔐 Admin - Frames"])
app.include_router(users.router, prefix="/api/users", tags=["🔐 Admin - Management"])
app.include_router(admin.router, prefix="/api/admin", tags=["🔐 Admin - Management"])
app.include_router(calibration.router, prefix="/api/admin/calibration", tags=["🔐 Admin - Calibration"])
app.include_router(motorcycles.router, prefix="/api/motorcycles", tags=["🔓 Public - Motorcycles"])
