# Admin API Documentation

This document describes the admin API endpoints that require authentication via API key. These endpoints are designed for administrators to manage the ParkIt system.

## Base URL

```
http://localhost:8000
```

## Authentication

All admin endpoints require an API key to be included in the request headers.

**Header:**
```
X-API-Key: your-api-key-here
```

**Default API Key:** `parkit-admin-secret-key-change-this`

⚠️ **Important:** Change the default API key in production!

---

## Endpoints

## Camera Calibration

### 1. Create/Update Calibration

Create or update camera calibration settings for empty space detection.

**Endpoint:** `POST /api/admin/calibration/`

**Authentication:** Required (API Key)

**Request Body:**

```json
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

**Validation Rules:**
- `camera_id`: Required, unique identifier
- `rows`: Required, 1-10 rows
- `y_coordinate`: Must be in descending order (bottom to top). Row 0 = bottom (largest Y), Row 1, 2... = going up (smaller Y)
- `min_space_width`: 10-500 pixels
- `space_coefficient`: 0.1-1.0
- `row_start_x`, `row_end_x`: Optional, default 0 and 1920

**Response:**

```json
{
  "message": "Calibration saved successfully",
  "camera_id": "parking-area-1"
}
```

**Error Responses:**

- `400 Bad Request`: Validation error
- `401 Unauthorized`: Invalid or missing API key

---

### 2. Get Calibration

Retrieve calibration settings for a specific camera.

**Endpoint:** `GET /api/admin/calibration/{camera_id}`

**Authentication:** Required (API Key)

**Response:**

```json
{
  "camera_id": "parking-area-1",
  "rows": [
    {
      "row_index": 0,
      "y_coordinate": 100,
      "label": "Row 1 (Top)"
    }
  ],
  "min_space_width": 150.0,
  "space_coefficient": 0.8,
  "row_start_x": 0,
  "row_end_x": 1920,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T10:00:00Z"
}
```

**Error Responses:**

- `404 Not Found`: Calibration not found

---

### 3. List All Calibrations

Retrieve all camera calibrations.

**Endpoint:** `GET /api/admin/calibration/`

**Authentication:** Required (API Key)

**Response:**

```json
{
  "calibrations": [
    {
      "camera_id": "parking-area-1",
      "rows": [...],
      "min_space_width": 150.0,
      "space_coefficient": 0.8,
      "row_start_x": 0,
      "row_end_x": 1920
    }
  ],
  "total": 1
}
```

---

### 4. Delete Calibration

Delete calibration settings for a specific camera.

**Endpoint:** `DELETE /api/admin/calibration/{camera_id}`

**Authentication:** Required (API Key)

**Response:**

```json
{
  "message": "Calibration deleted successfully"
}
```

**Error Responses:**

- `404 Not Found`: Calibration not found

---

## Frame Upload

### 5. Upload Frame

Upload a frame image for detection processing.

**Endpoint:** `POST /api/frames/upload`

**Authentication:** Required (API Key)

**Query Parameters:**
- `session_id` (required): Unique session identifier
- `camera_id` (optional): Camera identifier for calibration

**Request:**
- Content-Type: `multipart/form-data`
- Body: Form data with `file` field containing the image

**Example:**

```bash
curl -X POST "http://localhost:8000/api/frames/upload?session_id=abc-123&camera_id=parking-area-1" \
  -H "X-API-Key: your-api-key" \
  -F "file=@image.jpg"
```

**Response:**

```json
{
  "frame_id": "frame-uuid",
  "session_id": "abc-123",
  "detection_count": 15,
  "detections": [...],
  "is_best": true,
  "empty_spaces": [...],
  "total_motorcycles": 15,
  "total_empty_spaces": 5
}
```

**Validation:**
- File type: JPG, JPEG, PNG only
- Max file size: 10MB
- Session ID: Required, UUID format recommended

**Error Responses:**

- `400 Bad Request`: Invalid file or parameters
- `413 Payload Too Large`: File exceeds size limit

---

### 6. Complete Session

Mark a detection session as completed and finalize processing.

**Endpoint:** `POST /api/frames/complete/{session_id}`

**Authentication:** Required (API Key)

**Response:**

```json
{
  "message": "Session completed successfully",
  "session_id": "abc-123",
  "best_frame_id": "frame-uuid",
  "max_detection_count": 15
}
```

**Error Responses:**

- `404 Not Found`: Session not found

---

## System Statistics

### 7. Get System Stats

Retrieve overall system statistics.

**Endpoint:** `GET /api/admin/stats`

**Authentication:** Required (API Key)

**Response:**

```json
{
  "total_users": 100,
  "total_sessions": 500,
  "active_sessions": 50,
  "completed_sessions": 450,
  "total_detections": 7500
}
```

---

## Session Management

### 8. Get All Sessions

Retrieve all detection sessions with pagination and filtering.

**Endpoint:** `GET /api/admin/sessions`

**Authentication:** Required (API Key)

**Query Parameters:**
- `limit` (optional, default: 50): Number of results per page
- `skip` (optional, default: 0): Number of results to skip
- `status` (optional): Filter by status ("active" or "completed")

**Example:**

```
GET /api/admin/sessions?limit=20&skip=0&status=completed
```

**Response:**

```json
{
  "sessions": [
    {
      "session_id": "abc-123",
      "camera_id": "parking-area-1",
      "status": "completed",
      "max_detection_count": 15,
      "total_frames": 10,
      "created_at": "2024-01-15T10:00:00Z",
      "updated_at": "2024-01-15T10:05:00Z"
    }
  ],
  "total": 1,
  "limit": 20,
  "skip": 0
}
```

---

### 9. Delete Session

Delete a specific detection session and all associated data.

**Endpoint:** `DELETE /api/admin/sessions/{session_id}`

**Authentication:** Required (API Key)

**Response:**

```json
{
  "message": "Session deleted successfully",
  "session_id": "abc-123"
}
```

**Error Responses:**

- `404 Not Found`: Session not found

---

## User Management

### 10. Get All Users

Retrieve all system users with pagination.

**Endpoint:** `GET /api/admin/users`

**Authentication:** Required (API Key)

**Query Parameters:**
- `limit` (optional, default: 50): Number of results per page
- `skip` (optional, default: 0): Number of results to skip

**Response:**

```json
{
  "users": [
    {
      "username": "user123",
      "email": "user@example.com",
      "is_active": true,
      "is_admin": false,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ],
  "total": 1,
  "limit": 50,
  "skip": 0
}
```

---

### 11. Toggle User Active Status

Activate or deactivate a user account.

**Endpoint:** `PUT /api/admin/users/{username}/toggle-active`

**Authentication:** Required (API Key)

**Response:**

```json
{
  "message": "User status updated successfully",
  "username": "user123",
  "is_active": false
}
```

**Error Responses:**

- `404 Not Found`: User not found

---

## Error Handling

### HTTP Status Codes

- `200 OK`: Request successful
- `400 Bad Request`: Invalid request parameters or validation error
- `401 Unauthorized`: Missing or invalid API key
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `413 Payload Too Large`: File size exceeds limit
- `500 Internal Server Error`: Server error

### Error Response Format

```json
{
  "detail": "Error message description"
}
```

### Validation Error Format

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "Field validation error message",
      "type": "value_error"
    }
  ]
}
```

---

## Usage Examples

### JavaScript/Fetch

```javascript
const API_KEY = 'parkit-admin-secret-key-change-this';
const BASE_URL = 'http://localhost:8000';

// Helper function for authenticated requests
async function apiRequest(endpoint, options = {}) {
  const response = await fetch(`${BASE_URL}${endpoint}`, {
    ...options,
    headers: {
      'X-API-Key': API_KEY,
      ...options.headers
    }
  });
  
  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'Request failed');
  }
  
  return response.json();
}

// Create calibration
const calibrationData = {
  camera_id: 'parking-area-1',
  rows: [
    { row_index: 0, y_coordinate: 500, label: 'Row 1 (Bottom)' },
    { row_index: 1, y_coordinate: 300, label: 'Row 2 (Middle)' },
    { row_index: 2, y_coordinate: 100, label: 'Row 3 (Top)' }
  ],
  min_space_width: 150,
  space_coefficient: 0.8
};

apiRequest('/api/admin/calibration/', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify(calibrationData)
})
.then(data => console.log('Calibration created:', data))
.catch(error => console.error('Error:', error));

// Upload frame
const formData = new FormData();
formData.append('file', fileInput.files[0]);

fetch(`${BASE_URL}/api/frames/upload?session_id=abc-123&camera_id=parking-area-1`, {
  method: 'POST',
  headers: { 'X-API-Key': API_KEY },
  body: formData
})
.then(response => response.json())
.then(data => console.log('Frame uploaded:', data))
.catch(error => console.error('Error:', error));

// Get system stats
apiRequest('/api/admin/stats')
  .then(stats => console.log('System stats:', stats))
  .catch(error => console.error('Error:', error));

// Get sessions
apiRequest('/api/admin/sessions?limit=20&status=completed')
  .then(data => console.log('Sessions:', data.sessions))
  .catch(error => console.error('Error:', error));

// Delete session
apiRequest('/api/admin/sessions/abc-123', { method: 'DELETE' })
  .then(data => console.log('Session deleted:', data))
  .catch(error => console.error('Error:', error));
```

### Python/Requests

```python
import requests

API_KEY = 'parkit-admin-secret-key-change-this'
BASE_URL = 'http://localhost:8000'
headers = {'X-API-Key': API_KEY}

# Create calibration
calibration_data = {
    'camera_id': 'parking-area-1',
    'rows': [
        {'row_index': 0, 'y_coordinate': 500, 'label': 'Row 1 (Bottom)'},
        {'row_index': 1, 'y_coordinate': 300, 'label': 'Row 2 (Middle)'},
        {'row_index': 2, 'y_coordinate': 100, 'label': 'Row 3 (Top)'}
    ],
    'min_space_width': 150.0,
    'space_coefficient': 0.8
}

response = requests.post(
    f'{BASE_URL}/api/admin/calibration/',
    json=calibration_data,
    headers=headers
)
print(response.json())

# Upload frame
session_id = 'abc-123'
camera_id = 'parking-area-1'

with open('image.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        f'{BASE_URL}/api/frames/upload?session_id={session_id}&camera_id={camera_id}',
        files=files,
        headers=headers
    )
    print(response.json())

# Complete session
response = requests.post(
    f'{BASE_URL}/api/frames/complete/{session_id}',
    headers=headers
)
print(response.json())

# Get system stats
response = requests.get(f'{BASE_URL}/api/admin/stats', headers=headers)
stats = response.json()
print(f"Total sessions: {stats['total_sessions']}")
print(f"Active sessions: {stats['active_sessions']}")

# Get sessions
response = requests.get(
    f'{BASE_URL}/api/admin/sessions?limit=20&status=completed',
    headers=headers
)
sessions = response.json()
for session in sessions['sessions']:
    print(f"Session: {session['session_id']}, Detections: {session['max_detection_count']}")

# Delete session
response = requests.delete(
    f'{BASE_URL}/api/admin/sessions/{session_id}',
    headers=headers
)
print(response.json())

# Get users
response = requests.get(f'{BASE_URL}/api/admin/users', headers=headers)
users = response.json()
for user in users['users']:
    print(f"User: {user['username']}, Active: {user['is_active']}")

# Toggle user active
response = requests.put(
    f'{BASE_URL}/api/admin/users/user123/toggle-active',
    headers=headers
)
print(response.json())
```

### cURL

```bash
API_KEY="parkit-admin-secret-key-change-this"

# Create calibration
curl -X POST "http://localhost:8000/api/admin/calibration/" \
  -H "X-API-Key: $API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": "parking-area-1",
    "rows": [
      {"row_index": 0, "y_coordinate": 500, "label": "Row 1 (Bottom)"},
      {"row_index": 1, "y_coordinate": 300, "label": "Row 2 (Middle)"},
      {"row_index": 2, "y_coordinate": 100, "label": "Row 3 (Top)"}
    ],
    "min_space_width": 150,
    "space_coefficient": 0.8
  }'

# Get calibration
curl "http://localhost:8000/api/admin/calibration/parking-area-1" \
  -H "X-API-Key: $API_KEY"

# Upload frame
curl -X POST "http://localhost:8000/api/frames/upload?session_id=abc-123&camera_id=parking-area-1" \
  -H "X-API-Key: $API_KEY" \
  -F "file=@image.jpg"

# Complete session
curl -X POST "http://localhost:8000/api/frames/complete/abc-123" \
  -H "X-API-Key: $API_KEY"

# Get system stats
curl "http://localhost:8000/api/admin/stats" \
  -H "X-API-Key: $API_KEY"

# Get sessions
curl "http://localhost:8000/api/admin/sessions?limit=20&status=completed" \
  -H "X-API-Key: $API_KEY"

# Delete session
curl -X DELETE "http://localhost:8000/api/admin/sessions/abc-123" \
  -H "X-API-Key: $API_KEY"

# Get users
curl "http://localhost:8000/api/admin/users" \
  -H "X-API-Key: $API_KEY"

# Toggle user active
curl -X PUT "http://localhost:8000/api/admin/users/user123/toggle-active" \
  -H "X-API-Key: $API_KEY"
```

---

## Best Practices

### Security

1. **Change Default API Key**: Always change the default API key in production
2. **Use HTTPS**: Always use HTTPS in production to encrypt API key transmission
3. **Rotate Keys**: Regularly rotate API keys
4. **Limit Access**: Only share API keys with authorized administrators

### Performance

1. **Batch Uploads**: Upload multiple frames in sequence for better performance
2. **Pagination**: Use pagination for large datasets
3. **Caching**: Result images are cached; use appropriate cache headers

### Error Handling

1. **Retry Logic**: Implement retry logic for network errors
2. **Validation**: Validate data client-side before sending to API
3. **Logging**: Log all API errors for debugging

### Workflow

1. **Setup Calibration**: Configure camera calibration before uploading frames
2. **Upload Frames**: Upload multiple frames for a session
3. **Complete Session**: Always complete the session after uploading
4. **Monitor**: Use stats endpoint to monitor system health

---

## Rate Limiting

Currently, there is no rate limiting implemented. However, it's recommended to:
- Limit concurrent uploads to 5 per session
- Wait for upload completion before starting new uploads
- Implement client-side throttling for bulk operations

---

## Notes

- All timestamps are in ISO 8601 format (UTC)
- Session IDs should be UUIDs for uniqueness
- Camera IDs must match calibration settings for empty space detection
- Frames are automatically processed upon upload
- Best frame is selected based on highest detection count
- Completed sessions cannot be modified
