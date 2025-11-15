# Requirements Document - Parking Calibration System

## Introduction

Sistem kalibrasi kamera parkiran untuk menghitung jarak antar motor berdasarkan perspektif kamera. Sistem ini memungkinkan admin untuk mendefinisikan baris parkiran dan parameter jarak, kemudian backend akan otomatis menghitung jarak kanan-kiri antar bounding box dengan memperhitungkan perspektif (baris atas lebih kecil dari baris bawah).

## Glossary

- **Parking Row**: Baris parkiran horizontal di area parkir
- **Calibration Data**: Data konfigurasi kamera yang berisi koordinat baris dan parameter jarak
- **Bounding Box**: Kotak deteksi motor dari YOLO
- **Distance Coefficient**: Koefisien pengurangan jarak untuk baris yang lebih tinggi
- **Base Distance**: Jarak horizontal antar bounding box di baris terbawah
- **Row Line**: Garis horizontal yang mendefinisikan posisi Y dari baris parkiran

## Requirements

### Requirement 1: Admin Kalibrasi Kamera

**User Story:** As an admin, I want to configure camera calibration for parking area, so that the system can accurately calculate distances between motorcycles based on perspective.

#### Acceptance Criteria

1. WHEN admin sends calibration data, THE System SHALL validate that row count is between 1 and 10
2. WHEN admin sends calibration data, THE System SHALL validate that each row has valid Y coordinate
3. WHEN admin sends calibration data, THE System SHALL validate that base distance is greater than 0
4. WHEN admin sends calibration data, THE System SHALL validate that distance coefficient is between 0 and 1
5. WHEN calibration data is valid, THE System SHALL store it in MongoDB with camera_id as identifier

### Requirement 2: Perhitungan Jarak Antar Motor

**User Story:** As a system, I want to calculate horizontal distance between detected motorcycles, so that I can determine if parking spaces are properly utilized.

#### Acceptance Criteria

1. WHEN detection is processed, THE System SHALL assign each bounding box to nearest parking row based on Y coordinate
2. WHEN bounding box is assigned to row, THE System SHALL calculate distance to left neighbor if exists
3. WHEN bounding box is assigned to row, THE System SHALL calculate distance to right neighbor if exists
4. WHEN calculating distance for row N, THE System SHALL apply formula: `distance = base_distance * (coefficient ^ row_index)`
5. WHEN distance is calculated, THE System SHALL include it in detection result

### Requirement 3: Validasi Jarak Parkir

**User Story:** As a system, I want to validate if motorcycles are parked with proper spacing, so that I can alert if parking is too dense.

#### Acceptance Criteria

1. WHEN distance between two motorcycles is less than minimum threshold, THE System SHALL mark it as "too close"
2. WHEN distance between two motorcycles is within acceptable range, THE System SHALL mark it as "normal"
3. WHEN distance between two motorcycles is greater than maximum threshold, THE System SHALL mark it as "wasted space"
4. WHEN validation is complete, THE System SHALL include spacing status in detection result
5. WHEN session is completed, THE System SHALL calculate overall parking efficiency percentage

### Requirement 4: Endpoint Kalibrasi

**User Story:** As an admin, I want API endpoints to manage camera calibration, so that I can configure and update parking area settings.

#### Acceptance Criteria

1. WHEN admin calls POST /api/admin/calibration, THE System SHALL create or update calibration data
2. WHEN admin calls GET /api/admin/calibration/{camera_id}, THE System SHALL return current calibration settings
3. WHEN admin calls DELETE /api/admin/calibration/{camera_id}, THE System SHALL remove calibration data
4. WHEN admin calls GET /api/admin/calibration, THE System SHALL return list of all calibrations
5. WHEN calibration endpoint is called without valid API key, THE System SHALL return 403 Forbidden

### Requirement 5: Visualisasi Hasil

**User Story:** As a user, I want to see parking row lines and distance information on detection image, so that I can understand the parking layout.

#### Acceptance Criteria

1. WHEN best frame image is generated, THE System SHALL draw parking row lines on image
2. WHEN motorcycles are detected, THE System SHALL draw distance lines between neighbors
3. WHEN distance is too close, THE System SHALL draw line in red color
4. WHEN distance is normal, THE System SHALL draw line in green color
5. WHEN distance is wasted space, THE System SHALL draw line in yellow color

## Data Model

### Calibration Data Structure

```json
{
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
    },
    {
      "row_index": 2,
      "y_coordinate": 500,
      "label": "Row 3 (Bottom)"
    }
  ],
  "base_distance": 150,
  "distance_coefficient": 0.8,
  "min_distance_threshold": 50,
  "max_distance_threshold": 200,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

### Enhanced Detection Result

```json
{
  "session_id": "abc-123",
  "detections": [
    {
      "bbox": {"x1": 100, "y1": 150, "x2": 200, "y2": 250},
      "confidence": 0.95,
      "assigned_row": 0,
      "left_distance": null,
      "right_distance": 120,
      "spacing_status": "normal"
    },
    {
      "bbox": {"x1": 320, "y1": 160, "x2": 420, "y2": 260},
      "confidence": 0.92,
      "assigned_row": 0,
      "left_distance": 120,
      "right_distance": 130,
      "spacing_status": "normal"
    }
  ],
  "parking_efficiency": 85.5,
  "total_spaces_used": 15,
  "proper_spacing_count": 12,
  "too_close_count": 2,
  "wasted_space_count": 1
}
```

## Constraints

- Maximum 10 parking rows per camera
- Row Y coordinates must be in ascending order (top to bottom)
- Distance coefficient must be between 0.1 and 1.0
- Base distance must be between 10 and 500 pixels
- Calibration data is required before distance calculation can be performed
- If no calibration data exists, system will skip distance calculation

## Notes

- Perspektif kamera membuat objek di baris atas terlihat lebih kecil dan lebih rapat
- Formula jarak: `distance_at_row_N = base_distance * (coefficient ^ row_index)`
- Contoh: base=150px, coef=0.8, maka row0=150px, row1=120px, row2=96px
- Bounding box di-assign ke row terdekat berdasarkan center Y coordinate
