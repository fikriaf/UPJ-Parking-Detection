from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
import os

from app.api import frames, results, users, admin, calibration
from app.core.config import settings
from app.db.mongodb import connect_to_mongo, close_mongo_connection

app = FastAPI(
    title="ParkIt API",
    description="Parking Detection System using YOLOv12m",
    version="1.0.0"
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
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
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

# Include routers
app.include_router(frames.router, prefix="/api/frames", tags=["Frames"])
app.include_router(results.router, prefix="/api/results", tags=["Results"])
app.include_router(users.router, prefix="/api/users", tags=["Users"])
app.include_router(admin.router, prefix="/api/admin", tags=["Admin"])
app.include_router(calibration.router, prefix="/api/admin/calibration", tags=["Calibration"])
