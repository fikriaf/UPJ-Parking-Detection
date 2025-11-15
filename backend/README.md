# ParkIt Backend API

Backend FastAPI untuk sistem deteksi parkiran menggunakan YOLOv12m.

## Features

- ✅ **Admin upload frames** dari CCTV/camera
- ✅ Otomatis compare frames dan simpan yang paling banyak deteksi
- ✅ **Public view** - User lihat hasil tanpa auth
- ✅ **Live detection** - Real-time monitoring
- ✅ **Camera calibration** - Configure parking rows and detect empty spaces
- ✅ **Empty space detection** - Automatically find available parking spots
- ✅ Admin dashboard dengan API key
- ✅ MongoDB database
- ✅ YOLOv12m detection (mAP50: 95.3%)

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Setup Model

Copy file `best.pt` hasil training ke folder `models/`:

```bash
mkdir models
cp path/to/best.pt models/
```

### 3. Environment Variables

Copy `.env.example` ke `.env` dan sesuaikan:

```bash
cp .env.example .env
```

### 4. Run Server

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Server akan jalan di `http://localhost:8000`

## API Endpoints

### 🎯 Calibration (Admin Only)

Camera calibration allows the system to detect empty parking spaces by defining parking rows and perspective parameters.

#### Create/Update Calibration
```http
POST /api/admin/calibration/
Content-Type: application/json
X-API-Key: parkit-admin-secret-key-change-this

{
  "camera_id": "parking-area-1",
  "rows": [
    {
      "row_index": 0,
      "y_coordinate": 500,
      "label": "Row 1 (Bottom)"
    },
    {
      "row_index": 1,
      "y_coordinate": 300,
      "label": "Row 2 (Middle)"
    },
    {
      "row_index": 2,
      "y_coordinate": 100,
      "label": "Row 3 (Top)"
    }
  ],
  "min_space_width": 150.0,
  "space_coefficient": 0.8,
  "row_start_x": 0,
  "row_end_x": 1920
}
```

Response:
```json
{
  "message": "Calibration saved successfully",
  "camera_id": "parking-area-1"
}
```

**Parameters:**
- `camera_id`: Unique identifier for the camera
- `rows`: Array of parking rows with Y coordinates (top to bottom)
- `min_space_width`: Minimum width (pixels) for empty space at bottom row
- `space_coefficient`: Reduction factor per row for perspective (0.1-1.0)
- `row_start_x`: Left boundary of parking area (default: 0)
- `row_end_x`: Right boundary of parking area (default: 1920)

**Validation Rules:**
- Row count: 1-10
- Y coordinates must be in ascending order
- min_space_width: 10-500 pixels
- space_coefficient: 0.1-1.0

#### Get Calibration
```http
GET /api/admin/calibration/{camera_id}
X-API-Key: parkit-admin-secret-key-change-this
```

Response:
```json
{
  "camera_id": "parking-area-1",
  "rows": [...],
  "min_space_width": 150.0,
  "space_coefficient": 0.8,
  "row_start_x": 0,
  "row_end_x": 1920,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

#### List All Calibrations
```http
GET /api/admin/calibration/
X-API-Key: parkit-admin-secret-key-change-this
```

Response:
```json
{
  "calibrations": [
    {
      "camera_id": "parking-area-1",
      "rows": [...],
      "min_space_width": 150.0,
      "space_coefficient": 0.8
    }
  ],
  "total": 1
}
```

#### Delete Calibration
```http
DELETE /api/admin/calibration/{camera_id}
X-API-Key: parkit-admin-secret-key-change-this
```

Response:
```json
{
  "message": "Calibration deleted successfully"
}
```

### 📸 Frames (Admin Only)

#### Upload Frame
```http
POST /api/frames/upload?session_id={session_id}&camera_id={camera_id}
Content-Type: multipart/form-data
X-API-Key: parkit-admin-secret-key-change-this

file: <image_file>
```

**Parameters:**
- `session_id`: Unique session identifier
- `camera_id`: Camera identifier (optional, required for empty space detection)

Response:
```json
{
  "frame_id": "uuid",
  "session_id": "session123",
  "detection_count": 15,
  "detections": [...],
  "is_best": true
}
```

#### Complete Session
```http
POST /api/frames/complete/{session_id}
X-API-Key: parkit-admin-secret-key-change-this
```

### 📊 Results (Public - No Auth)

#### Get Result
```http
GET /api/results/{session_id}
```

Response (without calibration):
```json
{
  "session_id": "session123",
  "status": "completed",
  "max_detection_count": 15,
  "best_frame": {...},
  "total_frames": 10
}
```

Response (with calibration and empty space detection):
```json
{
  "session_id": "session123",
  "camera_id": "parking-area-1",
  "status": "completed",
  "max_detection_count": 15,
  "best_frame": {
    "frame_id": "uuid",
    "timestamp": "2024-01-01T00:00:00Z",
    "detections": [
      {
        "bbox": {"x1": 100, "y1": 150, "x2": 200, "y2": 250},
        "confidence": 0.95,
        "assigned_row": 0,
        "row_y_coordinate": 100
      }
    ],
    "detection_count": 15,
    "empty_spaces": [
      {
        "space_id": "row0_space0",
        "row_index": 0,
        "x1": 200,
        "x2": 350,
        "y1": 50,
        "y2": 150,
        "width": 150.0,
        "can_fit_motorcycle": true
      }
    ],
    "total_motorcycles": 15,
    "total_empty_spaces": 5,
    "empty_spaces_per_row": {
      "0": 2,
      "1": 2,
      "2": 1
    },
    "parking_occupancy_rate": 75.0
  },
  "total_frames": 10
}
```

**Empty Space Fields:**
- `space_id`: Unique identifier for the empty space
- `row_index`: Which parking row the space belongs to
- `x1, x2, y1, y2`: Coordinates of the empty space rectangle
- `width`: Width of the empty space in pixels
- `can_fit_motorcycle`: Whether the space is large enough for a motorcycle
- `total_motorcycles`: Total number of motorcycles detected
- `total_empty_spaces`: Total number of empty spaces found
- `empty_spaces_per_row`: Count of empty spaces per row
- `parking_occupancy_rate`: Percentage of occupied spaces (motorcycles / (motorcycles + empty_spaces) * 100)

#### Get Result Image
```http
GET /api/results/{session_id}/image
```

Returns: Image file with bounding boxes

#### Get Latest Results
```http
GET /api/results/latest?limit=10&skip=0
```

#### Get Live Detection
```http
GET /api/results/live
```

Returns current active detection session.

### 👤 Users (Optional)

#### Register
```http
POST /api/users/register
Content-Type: application/json

{
  "username": "user123",
  "email": "user@example.com",
  "password": "password123"
}
```

Response:
```json
{
  "message": "User registered successfully",
  "user_id": "507f1f77bcf86cd799439011",
  "username": "user123"
}
```

#### Get User
```http
GET /api/users/{user_id}
```

### 🔐 Admin

All admin endpoints require API key in header.

#### Get Stats
```http
GET /api/admin/stats
X-API-Key: parkit-admin-secret-key-change-this
```

Response:
```json
{
  "total_users": 100,
  "total_sessions": 500,
  "active_sessions": 50,
  "completed_sessions": 450,
  "total_detections": 7500
}
```

#### Get All Users
```http
GET /api/admin/users?limit=50&skip=0
X-API-Key: parkit-admin-secret-key-change-this
```

#### Get All Sessions
```http
GET /api/admin/sessions?limit=50&skip=0&status=completed
X-API-Key: parkit-admin-secret-key-change-this
```

#### Toggle User Active
```http
PUT /api/admin/users/{username}/toggle-active
X-API-Key: parkit-admin-secret-key-change-this
```

#### Delete Session (Admin)
```http
DELETE /api/admin/sessions/{session_id}
X-API-Key: parkit-admin-secret-key-change-this
```

## Usage Flow

### Admin Flow (Upload Frames):

1. **Create session** → Generate unique `session_id` (UUID)
2. **Upload frames** → POST to `/api/frames/upload` multiple times (with API key)
3. **Complete session** → POST to `/api/frames/complete/{session_id}` (with API key)

### User Flow (View Results):

1. **View live** → GET `/api/results/live` (no auth)
2. **View specific** → GET `/api/results/{session_id}` (no auth)
3. **View image** → GET `/api/results/{session_id}/image` (no auth)
4. **View history** → GET `/api/results/latest` (no auth)

### Admin Example (Calibration Setup):

```python
import requests

# Admin API key
headers = {"X-API-Key": "parkit-admin-secret-key-change-this"}

# Create calibration for parking area
calibration_data = {
    "camera_id": "parking-area-1",
    "rows": [
        {
            "row_index": 0, 
            "y_coordinate": 100, 
            "label": "Row 1 (Top/Far)",
            "start_x": 400,
            "end_x": 1520
        },
        {
            "row_index": 1, 
            "y_coordinate": 300, 
            "label": "Row 2 (Middle)",
            "start_x": 200,
            "end_x": 1720
        },
        {
            "row_index": 2, 
            "y_coordinate": 500, 
            "label": "Row 3 (Bottom/Near)",
            "start_x": 0,
            "end_x": 1920
        }
    ],
    "min_space_width": 150.0,
    "space_coefficient": 0.8,
    "row_start_x": 0,
    "row_end_x": 1920
}

response = requests.post(
    "http://localhost:8000/api/admin/calibration/",
    json=calibration_data,
    headers=headers
)
print(response.json())

# Get calibration
response = requests.get(
    "http://localhost:8000/api/admin/calibration/parking-area-1",
    headers=headers
)
print(response.json())

# List all calibrations
response = requests.get(
    "http://localhost:8000/api/admin/calibration/",
    headers=headers
)
print(response.json())
```

### Admin Example (Upload with Calibration):

```python
import requests
import uuid

# Admin API key
headers = {"X-API-Key": "parkit-admin-secret-key-change-this"}

# Generate session ID
session_id = str(uuid.uuid4())
camera_id = "parking-area-1"  # Must match calibration camera_id

# Upload frames from CCTV/camera
for frame_path in frame_paths:
    with open(frame_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(
            f"http://localhost:8000/api/frames/upload?session_id={session_id}&camera_id={camera_id}",
            files=files,
            headers=headers
        )
        print(response.json())

# Complete session
requests.post(
    f"http://localhost:8000/api/frames/complete/{session_id}",
    headers=headers
)
```

### User Example (View Results with Empty Spaces):

```python
import requests

# Get live detection (no auth needed)
response = requests.get("http://localhost:8000/api/results/live")
result = response.json()
print(f"Total motorcycles: {result['best_frame']['total_motorcycles']}")
print(f"Total empty spaces: {result['best_frame']['total_empty_spaces']}")
print(f"Occupancy rate: {result['best_frame']['parking_occupancy_rate']}%")

# Get specific result
session_id = "abc-123"
response = requests.get(f"http://localhost:8000/api/results/{session_id}")
result = response.json()

# Check empty spaces per row
if 'empty_spaces_per_row' in result['best_frame']:
    for row_idx, count in result['best_frame']['empty_spaces_per_row'].items():
        print(f"Row {row_idx}: {count} empty spaces")

# List all empty spaces
if 'empty_spaces' in result['best_frame']:
    for space in result['best_frame']['empty_spaces']:
        print(f"Space {space['space_id']}: width={space['width']}px, can_fit={space['can_fit_motorcycle']}")

# Download image (includes visualization of empty spaces)
response = requests.get(f"http://localhost:8000/api/results/{session_id}/image")
with open('result.jpg', 'wb') as f:
    f.write(response.content)

# Get latest results
response = requests.get("http://localhost:8000/api/results/latest?limit=10")
print(response.json())
```

### Admin Example:

```python
import requests

headers = {"X-API-Key": "parkit-admin-secret-key-change-this"}

# Get stats
response = requests.get("http://localhost:8000/api/admin/stats", headers=headers)
print(response.json())

# Get all sessions
response = requests.get("http://localhost:8000/api/admin/sessions", headers=headers)
print(response.json())
```

## Model Info

- **Model**: YOLOv12m
- **mAP50**: 95.3%
- **mAP50-95**: 50.4%
- **Precision**: 92.9%
- **Recall**: 85.3%
- **Inference Speed**: ~77ms per frame (13 FPS)
- **Class**: motor (1 class)

## Database Schema

### Users Collection
```json
{
  "_id": ObjectId,
  "username": "string",
  "email": "string",
  "hashed_password": "string",
  "is_active": true,
  "is_admin": false,
  "created_at": "datetime"
}
```

### Calibrations Collection
```json
{
  "_id": ObjectId,
  "camera_id": "parking-area-1",
  "rows": [
    {
      "row_index": 0,
      "y_coordinate": 100,
      "label": "Row 1 (Top)"
    },
    {
      "row_index": 1,
      "y_coordinate": 300,
      "label": "Row 2"
    }
  ],
  "min_space_width": 150.0,
  "space_coefficient": 0.8,
  "row_start_x": 0,
  "row_end_x": 1920,
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Detection Sessions Collection
```json
{
  "_id": ObjectId,
  "session_id": "string",
  "camera_id": "parking-area-1",
  "user_id": "string",
  "frames": [
    {
      "frame_id": "string",
      "timestamp": "datetime",
      "detections": [
        {
          "bbox": {"x1": 100, "y1": 150, "x2": 200, "y2": 250},
          "confidence": 0.95,
          "assigned_row": 0,
          "row_y_coordinate": 100
        }
      ],
      "detection_count": 15,
      "empty_spaces": [
        {
          "space_id": "row0_space0",
          "row_index": 0,
          "x1": 200,
          "x2": 350,
          "y1": 50,
          "y2": 150,
          "width": 150.0,
          "can_fit_motorcycle": true
        }
      ],
      "total_motorcycles": 15,
      "total_empty_spaces": 5,
      "empty_spaces_per_row": {"0": 2, "1": 2, "2": 1},
      "parking_occupancy_rate": 75.0
    }
  ],
  "best_frame": {...},
  "max_detection_count": 15,
  "status": "completed",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Testing

### Quick Start

Run all tests with the test runner script:

**Windows:**
```bash
cd backend
run_tests.bat
```

**Linux/Mac:**
```bash
cd backend
chmod +x run_tests.sh
./run_tests.sh
```

### Test Suites

#### 1. Basic API Tests (`test_calibration.py`)

Tests calibration API endpoints without requiring actual images:

```bash
cd backend
python test_calibration.py
```

Test ini akan:
- ✅ Test CRUD operations untuk calibration
- ✅ Test validation logic
- ✅ Test list calibrations
- ✅ Test results endpoints dengan parking analysis
- ✅ Cleanup test data

#### 2. Comprehensive E2E Tests (`test_e2e_parking.py`)

Full end-to-end testing with synthetic test images:

```bash
cd backend
python test_e2e_parking.py
```

Test ini akan:
- ✅ Create synthetic parking lot images with motorcycles
- ✅ Test complete flow: calibration → detection → empty spaces → visualization
- ✅ Verify empty spaces are detected correctly
- ✅ Verify coordinates are accurate
- ✅ Verify visualization images are created
- ✅ Test multiple scenarios (sparse, dense, empty rows, single motorcycle)
- ✅ Test edge cases (missing camera_id, invalid API key, etc.)
- ✅ Generate detailed test report

**Test Output:**
```
🚀 Parking Calibration System - End-to-End Tests
✅ PASS: Server Health
✅ PASS: Create Calibration
✅ PASS: Get Calibration
✅ PASS: Upload Frame - sparse_parking.jpg
✅ PASS: Verify Empty Spaces
✅ PASS: Verify Coordinates
✅ PASS: Verify Visualization
✅ PASS: Multiple Scenarios
✅ PASS: Edge Cases

============================================================
TEST SUMMARY
============================================================
Total Tests: 9
Passed: 9 ✅
Failed: 0 ❌
Pass Rate: 100.0%
============================================================
```

### Test Data

The E2E test automatically creates synthetic test images in `test_data/images/`:
- `sparse_parking.jpg` - Few motorcycles with large gaps
- `dense_parking.jpg` - Many motorcycles with small gaps
- `empty_rows.jpg` - Some rows completely empty
- `single_motorcycle.jpg` - Only one motorcycle

### Detailed Testing Guide

For comprehensive testing documentation, see [TEST_GUIDE.md](TEST_GUIDE.md)

### Manual Testing dengan cURL

#### Test Calibration CRUD
```bash
# Create calibration
curl -X POST "http://localhost:8000/api/admin/calibration/" \
  -H "X-API-Key: parkit-admin-secret-key-change-this" \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": "parking-area-1",
    "rows": [
      {"row_index": 0, "y_coordinate": 100, "label": "Row 1"},
      {"row_index": 1, "y_coordinate": 300, "label": "Row 2"}
    ],
    "min_space_width": 150,
    "space_coefficient": 0.8
  }'

# Get calibration
curl "http://localhost:8000/api/admin/calibration/parking-area-1" \
  -H "X-API-Key: parkit-admin-secret-key-change-this"

# List all calibrations
curl "http://localhost:8000/api/admin/calibration/" \
  -H "X-API-Key: parkit-admin-secret-key-change-this"
```

#### Test Frame Upload dengan Calibration
```bash
# Upload frame dengan camera_id
curl -X POST "http://localhost:8000/api/frames/upload?session_id=test-123&camera_id=parking-area-1" \
  -H "X-API-Key: parkit-admin-secret-key-change-this" \
  -F "file=@test_image.jpg"
```

## Calibration Guide

### How Calibration Works

The calibration system uses perspective-aware calculations to detect empty parking spaces:

1. **Define Parking Rows**: Specify Y coordinates for each horizontal parking row
2. **Set Perspective Parameters**: 
   - `min_space_width`: Minimum width for empty space at the bottom row (in pixels)
   - `space_coefficient`: Reduction factor for rows higher up (0.1-1.0)
3. **Automatic Detection**: System calculates expected space width per row using formula:
   ```
   expected_width_at_row = min_space_width * (space_coefficient ^ row_index)
   ```
   **Row numbering starts from bottom**: Row 0 = bottom (closest to camera, largest spaces), Row 1, 2, 3... going up (farther, smaller spaces).

### Example Calculation

For a 3-row parking area:
- `min_space_width = 150` pixels (bottom row)
- `space_coefficient = 0.8`

Expected widths (with perspective correction, **row numbering from bottom**):
- Row 0 (bottom/near): 150 * (0.8^0) = 150 pixels (largest, closest to camera)
- Row 1 (middle): 150 * (0.8^1) = 120 pixels  
- Row 2 (top/far): 150 * (0.8^2) = 96 pixels (smallest, farther from camera)

### Setting Up Calibration

1. **Capture a reference frame** from your camera
2. **Identify parking row Y coordinates** (use image editor to find pixel positions)
3. **Measure minimum space width** at the bottom row
4. **Estimate coefficient** based on perspective (0.8 is a good starting point)
5. **Create calibration** via API
6. **Test with real frames** and adjust parameters as needed

### Visualization

When calibration is active, the result image includes:
- **Blue lines**: Parking row positions
- **Green rectangles**: Empty parking spaces
- **Red boxes**: Detected motorcycles
- **Labels**: "EMPTY" text on available spaces

## Notes

- Frames disimpan max 10 per session (configurable)
- Best frame otomatis dipilih berdasarkan jumlah deteksi terbanyak
- Image best frame disimpan di `uploads/best_frames/`
- Admin endpoints protected dengan API key di header `X-API-Key`
- Calibration optional - system works without it
- Empty space detection only runs if calibration exists for camera_id
- Row Y coordinates must be in ascending order (top to bottom)
- System automatically assigns detections to nearest row
- Empty spaces are detected between motorcycles and at row edges

## License

MIT
