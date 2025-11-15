# Design Document - Parking Calibration System

## Overview

Sistem kalibrasi kamera parkiran yang menghitung jarak horizontal antar motor berdasarkan perspektif kamera. Sistem menggunakan koordinat baris parkiran dan koefisien pengurangan untuk menghitung jarak yang akurat di setiap baris.

## Architecture

### High-Level Flow

```
Admin → POST Calibration → MongoDB
                              ↓
CCTV → Upload Frame → YOLO Detection → Assign to Rows → Calculate Distance → Enhanced Result
                                                              ↓
                                                         User View
```

### Components

1. **Calibration Service**: Manage kalibrasi data
2. **Distance Calculator**: Hitung jarak antar bounding boxes
3. **Row Assigner**: Assign detection ke baris terdekat
4. **Spacing Validator**: Validasi jarak parkir
5. **Visualization Service**: Gambar garis dan jarak di image

## Data Models

### Calibration Model

```python
class ParkingRow(BaseModel):
    row_index: int
    y_coordinate: int
    label: str

class CameraCalibration(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    camera_id: str
    rows: List[ParkingRow]
    min_space_width: float  # Minimum width for empty space at bottom row
    space_coefficient: float  # Reduction factor per row (for perspective)
    row_start_x: int = 0  # Left boundary of parking area
    row_end_x: int = 1920  # Right boundary of parking area (image width)
    created_at: datetime
    updated_at: datetime
```

### Enhanced Detection Model

```python
class DetectionWithRow(BaseModel):
    bbox: BoundingBox
    assigned_row: Optional[int] = None
    row_y_coordinate: Optional[int] = None

class EmptySpace(BaseModel):
    space_id: str
    row_index: int
    x1: int
    x2: int
    y1: int
    y2: int
    width: float
    can_fit_motorcycle: bool

class SessionWithSpaces(BaseModel):
    session_id: str
    camera_id: str
    detections: List[DetectionWithRow]
    empty_spaces: List[EmptySpace]
    total_motorcycles: int
    total_empty_spaces: int
    empty_spaces_per_row: dict  # {row_index: count}
    parking_occupancy_rate: float  # percentage
```

## Components and Interfaces

### 1. Calibration Service

**File**: `app/services/calibration_service.py`

```python
class CalibrationService:
    def save_calibration(camera_id: str, data: CameraCalibration) -> bool
    def get_calibration(camera_id: str) -> Optional[CameraCalibration]
    def delete_calibration(camera_id: str) -> bool
    def list_calibrations() -> List[CameraCalibration]
    def validate_calibration(data: dict) -> bool
```

**Validation Rules:**
- Row count: 1-10
- Y coordinates: ascending order
- Base distance: 10-500 pixels
- Coefficient: 0.1-1.0

### 2. Distance Calculator

**File**: `app/services/distance_calculator.py`

```python
class DistanceCalculator:
    def __init__(calibration: CameraCalibration)
    
    def assign_to_row(bbox: BoundingBox) -> int
        # Find nearest row based on bbox center Y
        
    def calculate_row_distance(row_index: int) -> float
        # Formula: base_distance * (coefficient ^ row_index)
        
    def calculate_horizontal_distance(bbox1: BoundingBox, bbox2: BoundingBox) -> float
        # Distance between two bboxes (right edge to left edge)
        
    def process_detections(detections: List[BoundingBox]) -> List[DetectionWithDistance]
        # Main processing function
```

**Algorithm:**

1. **Assign to Row**:
   ```python
   bbox_center_y = (bbox.y1 + bbox.y2) / 2
   nearest_row = min(rows, key=lambda r: abs(r.y_coordinate - bbox_center_y))
   ```

2. **Calculate Row Distance**:
   ```python
   distance = base_distance * (coefficient ** row_index)
   ```

3. **Calculate Horizontal Distance**:
   ```python
   # Sort detections by X coordinate within same row
   # For each detection, find left and right neighbors
   left_distance = current.x1 - left_neighbor.x2
   right_distance = right_neighbor.x1 - current.x2
   ```

### 3. Empty Space Detector

**File**: `app/services/empty_space_detector.py`

```python
class EmptySpace(BaseModel):
    space_id: str
    row_index: int
    x1: int  # Left boundary
    x2: int  # Right boundary
    y1: int  # Top boundary (from row line)
    y2: int  # Bottom boundary (from row line)
    width: float  # Space width in pixels
    can_fit_motorcycle: bool  # True if width >= min_threshold

class EmptySpaceDetector:
    def __init__(calibration: CameraCalibration)
    
    def detect_empty_spaces(detections: List[BoundingBox], row_index: int) -> List[EmptySpace]:
        # Find gaps between motorcycles in a row
        # Gap = space between right edge of left motor and left edge of right motor
        
    def calculate_row_boundaries(row_index: int) -> tuple[int, int]:
        # Calculate Y boundaries for parking space visualization
        
    def validate_space_size(width: float, row_index: int) -> bool:
        # Check if space can fit a motorcycle
        # min_space = min_threshold * (coefficient ^ row_index)
```

**Algorithm:**

1. **Detect Empty Spaces**:
   ```python
   # Sort detections by X coordinate within same row
   sorted_detections = sorted(detections, key=lambda d: d.x1)
   
   empty_spaces = []
   for i in range(len(sorted_detections) - 1):
       left_motor = sorted_detections[i]
       right_motor = sorted_detections[i + 1]
       
       gap_x1 = left_motor.x2
       gap_x2 = right_motor.x1
       gap_width = gap_x2 - gap_x1
       
       # Calculate expected space size for this row
       expected_space = min_threshold * (coefficient ** row_index)
       
       if gap_width >= expected_space:
           empty_spaces.append(EmptySpace(
               space_id=f"row{row_index}_space{i}",
               row_index=row_index,
               x1=gap_x1,
               x2=gap_x2,
               y1=row_y - 50,  # Approximate parking space height
               y2=row_y + 50,
               width=gap_width,
               can_fit_motorcycle=True
           ))
   ```

2. **Edge Spaces** (start and end of row):
   ```python
   # Check space before first motor
   if first_motor.x1 > row_start_x + expected_space:
       # Add empty space at start
   
   # Check space after last motor
   if last_motor.x2 < row_end_x - expected_space:
       # Add empty space at end
   ```

### 4. Visualization Service

**File**: `app/services/visualization_service.py`

```python
class VisualizationService:
    def draw_parking_rows(image: np.ndarray, rows: List[ParkingRow]) -> np.ndarray
        # Draw horizontal lines for each row
        
    def draw_empty_spaces(image: np.ndarray, empty_spaces: List[EmptySpace]) -> np.ndarray
        # Draw rectangles for empty parking spaces
        
    def draw_detections_with_rows(image: np.ndarray, detections: List[DetectionWithRow]) -> np.ndarray
        # Draw bounding boxes with row labels
        
    def add_space_labels(image: np.ndarray, empty_spaces: List[EmptySpace]) -> np.ndarray
        # Add "EMPTY" text labels on spaces
```

**Color Coding:**
- Green: Empty parking spaces (can fit motorcycle)
- Blue: Row lines
- Red: Motorcycle bounding boxes
- White: Space labels and dimensions

## API Endpoints

### Admin Calibration Endpoints

```python
# POST /api/admin/calibration
async def create_calibration(
    data: CameraCalibration,
    x_api_key: str = Header(...)
) -> dict

# GET /api/admin/calibration/{camera_id}
async def get_calibration(
    camera_id: str,
    x_api_key: str = Header(...)
) -> CameraCalibration

# PUT /api/admin/calibration/{camera_id}
async def update_calibration(
    camera_id: str,
    data: CameraCalibration,
    x_api_key: str = Header(...)
) -> dict

# DELETE /api/admin/calibration/{camera_id}
async def delete_calibration(
    camera_id: str,
    x_api_key: str = Header(...)
) -> dict

# GET /api/admin/calibration
async def list_calibrations(
    x_api_key: str = Header(...)
) -> List[CameraCalibration]
```

### Modified Frame Upload

```python
# POST /api/frames/upload
async def upload_frame(
    session_id: str,
    camera_id: str,  # NEW: Required for calibration lookup
    file: UploadFile,
    x_api_key: str = Header(...)
) -> dict
```

**Processing Flow:**
1. YOLO detection (existing)
2. Lookup calibration by camera_id
3. If calibration exists:
   - Assign detections to rows
   - Calculate distances
   - Validate spacing
4. Save enhanced detection result

## Database Schema

### Calibrations Collection

```json
{
  "_id": ObjectId,
  "camera_id": "parking-area-1",
  "rows": [
    {
      "row_index": 0,
      "y_coordinate": 100,
      "label": "Row 1"
    }
  ],
  "base_distance": 150.0,
  "distance_coefficient": 0.8,
  "min_distance_threshold": 50.0,
  "max_distance_threshold": 200.0,
  "created_at": ISODate,
  "updated_at": ISODate
}
```

### Enhanced Detection Sessions

```json
{
  "_id": ObjectId,
  "session_id": "abc-123",
  "camera_id": "parking-area-1",
  "frames": [...],
  "best_frame": {
    "detections": [
      {
        "bbox": {"x1": 100, "y1": 150, "x2": 200, "y2": 250},
        "assigned_row": 0,
        "row_y_coordinate": 100
      },
      {
        "bbox": {"x1": 350, "y1": 160, "x2": 450, "y2": 260},
        "assigned_row": 0,
        "row_y_coordinate": 100
      }
    ],
    "empty_spaces": [
      {
        "space_id": "row0_space0",
        "row_index": 0,
        "x1": 200,
        "x2": 350,
        "y1": 50,
        "y2": 150,
        "width": 150,
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
  }
}
```

## Error Handling

1. **No Calibration**: Skip distance calculation, return basic detection
2. **Invalid Calibration**: Log error, skip distance calculation
3. **Row Assignment Failure**: Assign to nearest row or skip
4. **Distance Calculation Error**: Set distance to null, continue processing

## Testing Strategy

### Unit Tests

1. **CalibrationService**:
   - Test validation rules
   - Test CRUD operations
   
2. **DistanceCalculator**:
   - Test row assignment with various Y coordinates
   - Test distance formula with different coefficients
   - Test horizontal distance calculation
   
3. **SpacingValidator**:
   - Test threshold validation
   - Test efficiency calculation

### Integration Tests

1. Upload frame with calibration data
2. Verify distance calculation in result
3. Verify visualization includes row lines and distance lines

### Manual Testing

1. Configure calibration for test parking area
2. Upload multiple frames
3. Verify distances are calculated correctly
4. Verify visualization is accurate

## Performance Considerations

- Calibration data cached in memory (reload on update)
- Distance calculation: O(n log n) for sorting + O(n) for neighbor finding
- Minimal impact on existing detection pipeline (~5-10ms overhead)

## Future Enhancements

1. **Auto-calibration**: Detect parking rows automatically from image
2. **Perspective correction**: Apply homography transformation
3. **Occupancy detection**: Detect empty vs occupied spaces
4. **Historical analysis**: Track parking patterns over time
