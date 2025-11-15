# Parking Calibration System - Testing Guide

This guide explains how to run the end-to-end tests for the parking calibration system.

## Prerequisites

1. **Server Running**: Make sure the backend server is running
   ```bash
   cd backend
   uvicorn main:app --reload
   ```

2. **MongoDB Connected**: Ensure MongoDB connection is configured in `.env`

3. **YOLO Model**: The YOLO model should be available at `models/best.pt`

4. **Python Dependencies**: Install required packages
   ```bash
   pip install requests opencv-python numpy
   ```

## Test Files

### 1. `test_calibration.py` - Basic API Tests
Tests the calibration API endpoints without requiring actual images.

**What it tests:**
- Calibration CRUD operations (Create, Read, Update, Delete)
- List all calibrations
- Validation of calibration data
- Frame upload flow (without actual images)
- Results endpoints

**Run it:**
```bash
cd backend
python test_calibration.py
```

**Expected output:**
- ✅ Calibration created successfully
- ✅ Calibration retrieved successfully
- ✅ Calibration updated successfully
- ✅ Invalid calibrations correctly rejected
- ✅ List calibrations working

### 2. `test_e2e_parking.py` - Comprehensive End-to-End Tests
Full end-to-end testing with synthetic test images.

**What it tests:**
1. Server health check
2. Create calibration data
3. Retrieve calibration data
4. Upload frames with motorcycles
5. Verify empty spaces are detected
6. Verify coordinates are accurate
7. Verify visualization images are created
8. Multiple parking scenarios (sparse, dense, empty rows, single motorcycle)
9. Edge cases (missing camera_id, invalid API key, etc.)

**Run it:**
```bash
cd backend
python test_e2e_parking.py
```

**Expected output:**
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

## Test Data

The `test_e2e_parking.py` script automatically creates synthetic test images in `test_data/images/`:

1. **sparse_parking.jpg** - Few motorcycles with large gaps
2. **dense_parking.jpg** - Many motorcycles with small gaps
3. **empty_rows.jpg** - Some rows completely empty
4. **single_motorcycle.jpg** - Only one motorcycle in the lot

These images are simple colored rectangles representing motorcycles on a gray background with white parking row lines.

## Manual Testing with Real Images

To test with real parking lot images:

1. Create a `test_images/` directory in the backend folder
2. Add your parking lot images (JPG format)
3. Modify the test script or use the API directly:

```python
import requests

# Upload real image
with open('test_images/real_parking.jpg', 'rb') as f:
    files = {'file': f}
    response = requests.post(
        'http://localhost:8000/api/frames/upload?session_id=test-123&camera_id=test-e2e-camera',
        files=files,
        headers={'X-API-Key': 'parkit-admin-secret-key-change-this'}
    )
    print(response.json())
```

## Verification Checklist

After running tests, verify:

- [ ] All calibration CRUD operations work
- [ ] Empty spaces are detected between motorcycles
- [ ] Coordinates are within valid ranges (0-1920 for X, 0-1080 for Y)
- [ ] Width calculations are accurate (x2 - x1 = width)
- [ ] Visualization images are created in `uploads/best_frames/`
- [ ] Parking occupancy rate is calculated correctly
- [ ] Empty spaces per row are counted correctly
- [ ] Edge cases are handled gracefully (no crashes)

## Troubleshooting

### Server Connection Error
```
❌ Cannot connect to server
```
**Solution**: Start the server with `uvicorn main:app --reload`

### API Key Error
```
❌ Invalid or missing API key
```
**Solution**: Check that `ADMIN_API_KEY` in `.env` matches the test script

### YOLO Model Not Found
```
❌ Model file not found
```
**Solution**: Ensure `models/best.pt` exists or update `MODEL_PATH` in `.env`

### MongoDB Connection Error
```
❌ Cannot connect to MongoDB
```
**Solution**: Check `MONGODB_URL` in `.env` and ensure MongoDB is accessible

### No Empty Spaces Detected
This is normal if:
- Parking is completely full (no gaps)
- Gaps are smaller than `min_space_width`
- No calibration data exists for the camera

## Test Coverage

The tests cover all requirements from the specification:

- **Requirement 1**: Admin calibration configuration ✅
- **Requirement 2**: Distance calculation between motorcycles ✅
- **Requirement 3**: Parking space validation ✅
- **Requirement 4**: Calibration API endpoints ✅
- **Requirement 5**: Visualization of results ✅

## Continuous Integration

To run tests in CI/CD:

```bash
# Start server in background
uvicorn main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

# Wait for server to start
sleep 5

# Run tests
python test_e2e_parking.py
TEST_RESULT=$?

# Stop server
kill $SERVER_PID

# Exit with test result
exit $TEST_RESULT
```

## Next Steps

After all tests pass:

1. Review generated visualization images in `uploads/best_frames/`
2. Test with real parking lot images
3. Adjust calibration parameters based on actual camera perspective
4. Deploy to production environment
5. Monitor empty space detection accuracy

## Support

If tests fail or you encounter issues:

1. Check the server logs for errors
2. Verify all dependencies are installed
3. Ensure MongoDB is running and accessible
4. Review the test output for specific error messages
5. Check the `test_data/` directory for generated test images
