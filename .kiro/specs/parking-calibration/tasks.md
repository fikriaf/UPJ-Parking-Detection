# Implementation Plan - Parking Calibration System

## Task List

- [x] 1. Create data models for calibration and empty spaces


  - Create `CameraCalibration` model with rows, min_space_width, and coefficient
  - Create `ParkingRow` model with row_index, y_coordinate, and label
  - Create `EmptySpace` model with coordinates and validation fields
  - Create `DetectionWithRow` model extending existing BoundingBox
  - _Requirements: 1.1, 1.2, 1.3, 1.4_





- [x] 2. Implement CalibrationService





  - [x] 2.1 Create `app/services/calibration_service.py`


    - Implement `save_calibration()` method with MongoDB operations
    - Implement `get_calibration()` method to fetch by camera_id

    - Implement `delete_calibration()` method

    - Implement `list_calibrations()` method
    - _Requirements: 1.5, 4.1, 4.2, 4.3, 4.4_
  

  - [x] 2.2 Add validation logic


    - Validate row count (1-10)
    - Validate Y coordinates are in ascending order
    - Validate min_space_width (10-500 pixels)


    - Validate space_coefficient (0.1-1.0)
    - _Requirements: 1.1, 1.2, 1.3, 1.4_


- [x] 3. Implement EmptySpaceDetector




  - [x] 3.1 Create `app/services/empty_space_detector.py`

    - Implement `assign_to_row()` to assign detections to nearest row
    - Implement `calculate_expected_space()` using coefficient formula

    - Implement `detect_empty_spaces()` to find gaps between motorcycles
    - Implement `calculate_row_boundaries()` for Y coordinates
    - _Requirements: 2.1, 2.2, 2.3, 2.4_



  
  - [x] 3.2 Add edge space detection

    - Detect empty space before first motorcycle in row
    - Detect empty space after last motorcycle in row
    - Validate space width against expected size

    - _Requirements: 2.2, 2.3, 2.4_


  

  - [x] 3.3 Calculate occupancy metrics

    - Count total motorcycles
    - Count total empty spaces
    - Calculate empty spaces per row
    - Calculate parking occupancy rate percentage


    - _Requirements: 2.5, 3.5_


- [x] 4. Implement VisualizationService enhancements




  - [x] 4.1 Create `app/services/visualization_service.py` (or update existing)

    - Implement `draw_parking_rows()` to draw horizontal row lines
    - Implement `draw_empty_spaces()` to draw green rectangles for empty spaces
    - Implement `draw_detections_with_rows()` to show row assignments


    - Implement `add_space_labels()` to add "EMPTY" text on spaces
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 5. Create admin calibration endpoints




  - [x] 5.1 Create `app/api/calibration.py`

    - Implement POST `/api/admin/calibration` endpoint


    - Implement GET `/api/admin/calibration/{camera_id}` endpoint
    - Implement PUT `/api/admin/calibration/{camera_id}` endpoint
    - Implement DELETE `/api/admin/calibration/{camera_id}` endpoint
    - Implement GET `/api/admin/calibration` endpoint (list all)
    - Add API key authentication to all endpoints

    - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_
  
  - [x] 5.2 Add request/response models

    - Create Pydantic models for calibration requests
    - Add validation for all input fields
    - Create response models with proper serialization
    - _Requirements: 1.1, 1.2, 1.3, 1.4_





- [x] 6. Integrate calibration into frame upload

  - [x] 6.1 Update `app/api/frames.py`





    - Add `camera_id` parameter to upload endpoint


    - Lookup calibration data by camera_id after YOLO detection

    - Call EmptySpaceDetector if calibration exists

    - Store enhanced results with empty spaces data
    - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_
  
  - [x] 6.2 Update detection session model





    - Add `camera_id` field to DetectionSession
    - Add `empty_spaces` field to store EmptySpace list

    - Add occupancy metrics fields
    - Update MongoDB schema
    - _Requirements: 2.5, 3.5_

- [x] 7. Update results endpoints


  - [x] 7.1 Update `app/api/results.py`





    - Modify GET `/api/results/{session_id}` to include empty spaces
    - Modify GET `/api/results/live` to include empty spaces
    - Ensure empty_spaces array is returned in response
    - Include occupancy metrics in response
    - _Requirements: 2.5, 3.5_
  


  - [x] 7.2 Update image generation




    - Call VisualizationService to draw row lines
    - Call VisualizationService to draw empty spaces
    - Save enhanced image with all visualizations
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

- [x] 8. Update main.py and documentation








  - [x] 8.1 Register calibration router




    - Import calibration router in main.py
    - Add router with `/api/admin/calibration` prefix
    - Update API documentation
    - _Requirements: 4.1, 4.2, 4.3, 4.4_
  
  - [x] 8.2 Update README.md




    - Document calibration endpoints
    - Add example calibration JSON
    - Document empty spaces response format
    - Add usage examples for admin and users
    - _Requirements: All_

- [x] 9. Error handling and edge cases




  - [x] 9.1 Handle missing calibration gracefully


    - Skip empty space detection if no calibration
    - Return basic detection results
    - Log warning message
    - _Requirements: 2.1_
  
  - [x] 9.2 Handle edge cases


    - Handle single motorcycle in row (no gaps)
    - Handle no motorcycles in row (entire row empty)
    - Handle invalid row assignments
    - Handle calculation errors
    - _Requirements: 2.1, 2.2, 2.3_

- [x] 10. Integration and validation

  - [x] 10.1 End-to-end testing





    - Create test calibration data
    - Upload test frames with motorcycles
    - Verify empty spaces are detected correctly
    - Verify coordinates are accurate
    - Verify visualization is correct
    - _Requirements: All_
  
  - [x] 10.2 Update .env.example


    - Add default calibration settings if needed
    - Document new configuration options
    - _Requirements: 1.5_

## Notes

- Start with data models and services before API endpoints
- Test each service independently before integration
- Calibration is optional - system should work without it
- Empty space detection only runs if calibration exists
- Visualization should clearly show empty spaces in green
- All admin endpoints require X-API-Key header
- Public endpoints (results) do not require authentication
