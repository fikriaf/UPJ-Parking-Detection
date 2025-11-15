# Manual Verification Checklist

Use this checklist to manually verify the parking calibration system after running automated tests.

## Pre-Test Setup

- [ ] Server is running on `http://localhost:8000`
- [ ] MongoDB is connected and accessible
- [ ] YOLO model exists at `models/best.pt`
- [ ] `.env` file is configured with correct values
- [ ] All dependencies are installed (`pip install -r requirements.txt`)

## Automated Tests

- [ ] Run `python test_calibration.py` - All tests pass
- [ ] Run `python test_e2e_parking.py` - All tests pass
- [ ] Check console output - No errors or warnings
- [ ] Review test summary - 100% pass rate

## Test Data Verification

### Generated Test Images
Check `test_data/images/` directory:

- [ ] `sparse_parking.jpg` exists (7 motorcycles, large gaps)
- [ ] `dense_parking.jpg` exists (12 motorcycles, small gaps)
- [ ] `empty_rows.jpg` exists (4 motorcycles, empty middle row)
- [ ] `single_motorcycle.jpg` exists (1 motorcycle)
- [ ] All images are valid JPG files
- [ ] Images show gray background with white lines and red rectangles

### Visualization Images
Check `uploads/best_frames/` directory:

- [ ] Visualization images are created for test sessions
- [ ] Images show detected motorcycles (red boxes)
- [ ] Images show parking row lines (blue lines)
- [ ] Images show empty spaces (green rectangles)
- [ ] Images have "EMPTY" labels on available spaces
- [ ] Image dimensions are correct (1920x1080)

## API Endpoint Verification

### Calibration Endpoints (Admin)

#### Create Calibration
```bash
curl -X POST "http://localhost:8000/api/admin/calibration" \
  -H "X-API-Key: parkit-admin-secret-key-change-this" \
  -H "Content-Type: application/json" \
  -d '{
    "camera_id": "manual-test-camera",
    "rows": [
      {"row_index": 0, "y_coordinate": 100, "label": "Row 1"},
      {"row_index": 1, "y_coordinate": 300, "label": "Row 2"}
    ],
    "min_space_width": 150,
    "space_coefficient": 0.8
  }'
```

- [ ] Returns 200 status code
- [ ] Response includes `camera_id` field
- [ ] Response includes `rows` array
- [ ] Response includes `created_at` timestamp

#### Get Calibration
```bash
curl "http://localhost:8000/api/admin/calibration/manual-test-camera" \
  -H "X-API-Key: parkit-admin-secret-key-change-this"
```

- [ ] Returns 200 status code
- [ ] Response matches created calibration
- [ ] All fields are present and correct

#### Update Calibration
```bash
curl -X PUT "http://localhost:8000/api/admin/calibration/manual-test-camera" \
  -H "X-API-Key: parkit-admin-secret-key-change-this" \
  -H "Content-Type: application/json" \
  -d '{"min_space_width": 120}'
```

- [ ] Returns 200 status code
- [ ] Response shows updated `min_space_width`
- [ ] Other fields remain unchanged

#### List Calibrations
```bash
curl "http://localhost:8000/api/admin/calibration" \
  -H "X-API-Key: parkit-admin-secret-key-change-this"
```

- [ ] Returns 200 status code
- [ ] Response is an array
- [ ] Array includes test calibrations

#### Delete Calibration
```bash
curl -X DELETE "http://localhost:8000/api/admin/calibration/manual-test-camera" \
  -H "X-API-Key: parkit-admin-secret-key-change-this"
```

- [ ] Returns 200 status code
- [ ] Response confirms deletion
- [ ] Subsequent GET returns 404

### Frame Upload Endpoint

#### Upload with Calibration
```bash
# First create calibration, then upload frame
curl -X POST "http://localhost:8000/api/frames/upload?session_id=manual-test&camera_id=test-e2e-camera" \
  -H "X-API-Key: parkit-admin-secret-key-change-this" \
  -F "file=@test_data/images/sparse_parking.jpg"
```

- [ ] Returns 200 status code
- [ ] Response includes `detection_count`
- [ ] Response includes `parking_analysis` object
- [ ] `parking_analysis` has `total_empty_spaces`
- [ ] `parking_analysis` has `parking_occupancy_rate`

#### Upload without Calibration
```bash
curl -X POST "http://localhost:8000/api/frames/upload?session_id=manual-test-2" \
  -H "X-API-Key: parkit-admin-secret-key-change-this" \
  -F "file=@test_data/images/sparse_parking.jpg"
```

- [ ] Returns 200 status code
- [ ] Response includes `detection_count`
- [ ] Response does NOT include `parking_analysis`
- [ ] System handles gracefully (no errors)

### Results Endpoints

#### Get Session Results
```bash
curl "http://localhost:8000/api/results/manual-test"
```

- [ ] Returns 200 status code
- [ ] Response includes `session_id`
- [ ] Response includes `best_frame`
- [ ] If calibration used, includes `empty_spaces` array
- [ ] If calibration used, includes occupancy metrics

#### Get Live Detection
```bash
curl "http://localhost:8000/api/results/live"
```

- [ ] Returns 200 status code
- [ ] Response includes most recent session
- [ ] Response structure matches session results

## Data Validation

### Empty Space Data Structure
For each empty space, verify:

- [ ] `space_id` is unique and descriptive (e.g., "row0_space0")
- [ ] `row_index` is valid (0-2 for 3-row setup)
- [ ] `x1` < `x2` (left boundary < right boundary)
- [ ] `y1` < `y2` (top boundary < bottom boundary)
- [ ] `width` = `x2 - x1` (accurate calculation)
- [ ] `can_fit_motorcycle` is boolean
- [ ] Coordinates are within image bounds (0-1920 for X, 0-1080 for Y)

### Detection with Row Data Structure
For each detection, verify:

- [ ] `bbox` has x1, y1, x2, y2 coordinates
- [ ] `confidence` is between 0 and 1
- [ ] `class_name` is "motor"
- [ ] `assigned_row` is valid row index
- [ ] `row_y_coordinate` matches row definition

### Parking Analysis Data Structure
Verify:

- [ ] `session_id` matches request
- [ ] `camera_id` matches calibration
- [ ] `total_motorcycles` = count of detections
- [ ] `total_empty_spaces` = count of empty spaces
- [ ] `empty_spaces_per_row` is a dictionary with row indices as keys
- [ ] `parking_occupancy_rate` is between 0 and 100
- [ ] Occupancy calculation: `(motorcycles / (motorcycles + empty_spaces)) * 100`

## Edge Cases

### Invalid Calibration Data

- [ ] Row Y coordinates not in ascending order → Rejected (400/422)
- [ ] `min_space_width` < 10 → Rejected (400/422)
- [ ] `min_space_width` > 500 → Rejected (400/422)
- [ ] `space_coefficient` < 0.1 → Rejected (400/422)
- [ ] `space_coefficient` > 1.0 → Rejected (400/422)
- [ ] More than 10 rows → Rejected (400/422)
- [ ] `row_end_x` <= `row_start_x` → Rejected (400/422)

### Authentication

- [ ] Request without API key → 403 Forbidden
- [ ] Request with invalid API key → 403 Forbidden
- [ ] Request with correct API key → Success

### Missing Data

- [ ] Upload frame with non-existent camera_id → Works (no parking analysis)
- [ ] Get calibration for non-existent camera → 404 Not Found
- [ ] Delete non-existent calibration → 404 Not Found

### Special Scenarios

- [ ] Empty parking lot (no motorcycles) → Entire row marked as empty
- [ ] Full parking lot (no gaps) → No empty spaces detected
- [ ] Single motorcycle in row → Edge spaces detected
- [ ] Overlapping motorcycles → Handled gracefully (no negative widths)

## Visualization Verification

Open visualization images in `uploads/best_frames/` and verify:

### Visual Elements
- [ ] Parking row lines are drawn (blue horizontal lines)
- [ ] Motorcycle bounding boxes are drawn (red rectangles)
- [ ] Empty spaces are drawn (green rectangles)
- [ ] "EMPTY" labels are visible on spaces
- [ ] All elements are clearly visible and not overlapping

### Accuracy
- [ ] Row lines match calibration Y coordinates
- [ ] Empty spaces are between motorcycles
- [ ] Empty spaces don't overlap with motorcycles
- [ ] Edge spaces (start/end of row) are detected
- [ ] Space dimensions look reasonable

## Performance

- [ ] Frame upload completes in < 2 seconds
- [ ] Empty space detection adds < 100ms overhead
- [ ] Visualization generation completes quickly
- [ ] No memory leaks after multiple uploads
- [ ] Server remains responsive under load

## Documentation

- [ ] README.md includes testing section
- [ ] TEST_GUIDE.md is comprehensive and clear
- [ ] TESTING_SUMMARY.md covers all implementation details
- [ ] QUICK_TEST_REFERENCE.md provides quick commands
- [ ] All code has appropriate comments
- [ ] API endpoints are documented with examples

## Cleanup

After verification:

- [ ] Delete test calibrations
- [ ] Remove test sessions from database (optional)
- [ ] Keep test images for future reference
- [ ] Keep visualization images for inspection

## Sign-Off

- [ ] All automated tests pass
- [ ] All manual verifications complete
- [ ] All edge cases handled correctly
- [ ] Documentation is complete and accurate
- [ ] System is ready for production use

---

**Verified by:** ___________________  
**Date:** ___________________  
**Notes:** ___________________
