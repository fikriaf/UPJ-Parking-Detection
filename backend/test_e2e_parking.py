#!/usr/bin/env python3
"""
Comprehensive End-to-End Test for Parking Calibration System
Tests the complete flow from calibration to detection to visualization
"""

import requests
import json
import uuid
import cv2
import numpy as np
from pathlib import Path
import time
import sys

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "parkit-admin-secret-key-change-this"
HEADERS = {"X-API-Key": API_KEY}
TEST_DIR = Path("test_data")
TEST_IMAGES_DIR = TEST_DIR / "images"

# Test results tracking
test_results = {
    "passed": 0,
    "failed": 0,
    "tests": []
}

def log_test(name, passed, message=""):
    """Log test result"""
    status = "✅ PASS" if passed else "❌ FAIL"
    print(f"{status}: {name}")
    if message:
        print(f"  {message}")
    
    test_results["tests"].append({
        "name": name,
        "passed": passed,
        "message": message
    })
    
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1

def create_synthetic_parking_image(width=1920, height=1080, motorcycles=None):
    """
    Create a synthetic parking lot image with motorcycles
    motorcycles: List of (x, y, row_index) tuples
    """
    # Create blank image (parking lot background)
    img = np.ones((height, width, 3), dtype=np.uint8) * 128  # Gray background
    
    # Draw parking lot lines
    for y in [100, 300, 500]:
        cv2.line(img, (0, y), (width, y), (255, 255, 255), 2)
    
    # Draw motorcycles (simple rectangles)
    if motorcycles:
        for x, y, row_idx in motorcycles:
            # Motorcycle dimensions (approximate)
            w, h = 80, 120
            x1, y1 = x - w//2, y - h//2
            x2, y2 = x + w//2, y + h//2
            
            # Draw motorcycle as colored rectangle
            cv2.rectangle(img, (x1, y1), (x2, y2), (0, 0, 255), -1)
            cv2.rectangle(img, (x1, y1), (x2, y2), (255, 255, 255), 2)
    
    return img

def setup_test_environment():
    """Create test directories and synthetic images"""
    print("\n=== Setting Up Test Environment ===")
    
    # Create directories
    TEST_DIR.mkdir(exist_ok=True)
    TEST_IMAGES_DIR.mkdir(exist_ok=True)
    
    # Create test images with different scenarios
    test_scenarios = {
        "sparse_parking.jpg": [
            (200, 100, 0),
            (600, 100, 0),
            (1200, 100, 0),
            (300, 300, 1),
            (900, 300, 1),
            (400, 500, 2),
            (1000, 500, 2),
        ],
        "dense_parking.jpg": [
            (150, 100, 0), (280, 100, 0), (410, 100, 0), (540, 100, 0),
            (200, 300, 1), (330, 300, 1), (460, 300, 1), (590, 300, 1),
            (250, 500, 2), (380, 500, 2), (510, 500, 2), (640, 500, 2),
        ],
        "empty_rows.jpg": [
            (300, 100, 0),
            (600, 100, 0),
            # Row 1 is empty
            (400, 500, 2),
            (800, 500, 2),
        ],
        "single_motorcycle.jpg": [
            (960, 300, 1),  # Single motorcycle in middle row
        ],
    }
    
    for filename, motorcycles in test_scenarios.items():
        img = create_synthetic_parking_image(motorcycles=motorcycles)
        cv2.imwrite(str(TEST_IMAGES_DIR / filename), img)
    
    print(f"✅ Created {len(test_scenarios)} test images in {TEST_IMAGES_DIR}")
    return True

def test_server_health():
    """Test 1: Server health check"""
    print("\n=== Test 1: Server Health Check ===")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            log_test("Server Health", True, "Server is running")
            return True
        else:
            log_test("Server Health", False, f"Status code: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        log_test("Server Health", False, "Cannot connect to server")
        print("❌ Make sure server is running: cd backend && uvicorn main:app --reload")
        return False
    except Exception as e:
        log_test("Server Health", False, str(e))
        return False

def test_create_calibration():
    """Test 2: Create calibration data"""
    print("\n=== Test 2: Create Calibration ===")
    
    calibration_data = {
        "camera_id": "test-e2e-camera",
        "rows": [
            {"row_index": 0, "y_coordinate": 100, "label": "Row 1 (Top)"},
            {"row_index": 1, "y_coordinate": 300, "label": "Row 2 (Middle)"},
            {"row_index": 2, "y_coordinate": 500, "label": "Row 3 (Bottom)"}
        ],
        "min_space_width": 150.0,
        "space_coefficient": 0.8,
        "row_start_x": 0,
        "row_end_x": 1920
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/admin/calibration",
            json=calibration_data,
            headers=HEADERS
        )
        
        if response.status_code == 200:
            result = response.json()
            # Verify calibration data
            if result["camera_id"] == "test-e2e-camera" and len(result["rows"]) == 3:
                log_test("Create Calibration", True, f"Created calibration for {result['camera_id']}")
                return True, result
            else:
                log_test("Create Calibration", False, "Invalid calibration data returned")
                return False, None
        else:
            log_test("Create Calibration", False, f"Status: {response.status_code}, {response.text}")
            return False, None
    except Exception as e:
        log_test("Create Calibration", False, str(e))
        return False, None

def test_get_calibration(camera_id):
    """Test 3: Retrieve calibration"""
    print("\n=== Test 3: Get Calibration ===")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/admin/calibration/{camera_id}",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            result = response.json()
            # Verify all fields
            required_fields = ["camera_id", "rows", "min_space_width", "space_coefficient"]
            missing_fields = [f for f in required_fields if f not in result]
            
            if not missing_fields:
                log_test("Get Calibration", True, f"Retrieved calibration with all fields")
                return True, result
            else:
                log_test("Get Calibration", False, f"Missing fields: {missing_fields}")
                return False, None
        else:
            log_test("Get Calibration", False, f"Status: {response.status_code}")
            return False, None
    except Exception as e:
        log_test("Get Calibration", False, str(e))
        return False, None

def test_upload_frame_with_detection(image_path, camera_id, session_id):
    """Test 4: Upload frame and detect motorcycles with empty spaces"""
    print(f"\n=== Test 4: Upload Frame ({image_path.name}) ===")
    
    try:
        with open(image_path, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            response = requests.post(
                f"{BASE_URL}/api/frames/upload?session_id={session_id}&camera_id={camera_id}",
                files=files,
                headers=HEADERS
            )
        
        if response.status_code == 200:
            result = response.json()
            
            # Verify detection fields
            has_detections = "detection_count" in result
            has_parking_analysis = "parking_analysis" in result
            
            if has_detections:
                detection_count = result["detection_count"]
                message = f"Detected {detection_count} motorcycles"
                
                if has_parking_analysis:
                    analysis = result["parking_analysis"]
                    message += f", {analysis['total_empty_spaces']} empty spaces"
                    message += f", {analysis['parking_occupancy_rate']}% occupancy"
                
                log_test(f"Upload Frame - {image_path.name}", True, message)
                return True, result
            else:
                log_test(f"Upload Frame - {image_path.name}", False, "Missing detection data")
                return False, None
        else:
            log_test(f"Upload Frame - {image_path.name}", False, f"Status: {response.status_code}")
            return False, None
    except Exception as e:
        log_test(f"Upload Frame - {image_path.name}", False, str(e))
        return False, None

def test_verify_empty_spaces(session_id):
    """Test 5: Verify empty spaces are detected correctly"""
    print("\n=== Test 5: Verify Empty Spaces ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/results/{session_id}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Check if empty spaces data exists
            has_empty_spaces = "empty_spaces" in result
            has_metrics = "total_motorcycles" in result and "total_empty_spaces" in result
            
            if has_empty_spaces and has_metrics:
                empty_spaces = result["empty_spaces"]
                total_motorcycles = result["total_motorcycles"]
                total_empty_spaces = result["total_empty_spaces"]
                
                # Verify empty space structure
                if empty_spaces and len(empty_spaces) > 0:
                    first_space = empty_spaces[0]
                    required_fields = ["space_id", "row_index", "x1", "x2", "y1", "y2", "width", "can_fit_motorcycle"]
                    missing_fields = [f for f in required_fields if f not in first_space]
                    
                    if not missing_fields:
                        message = f"Found {total_empty_spaces} empty spaces, {total_motorcycles} motorcycles"
                        log_test("Verify Empty Spaces", True, message)
                        return True, result
                    else:
                        log_test("Verify Empty Spaces", False, f"Missing fields in empty space: {missing_fields}")
                        return False, None
                else:
                    # No empty spaces found - this is valid if parking is full
                    log_test("Verify Empty Spaces", True, "No empty spaces (parking may be full)")
                    return True, result
            else:
                log_test("Verify Empty Spaces", False, "Missing empty spaces or metrics data")
                return False, None
        else:
            log_test("Verify Empty Spaces", False, f"Status: {response.status_code}")
            return False, None
    except Exception as e:
        log_test("Verify Empty Spaces", False, str(e))
        return False, None

def test_verify_coordinates(session_id):
    """Test 6: Verify coordinates are accurate"""
    print("\n=== Test 6: Verify Coordinates ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/results/{session_id}")
        
        if response.status_code == 200:
            result = response.json()
            
            if "empty_spaces" in result:
                empty_spaces = result["empty_spaces"]
                
                # Verify coordinate validity
                all_valid = True
                invalid_spaces = []
                
                for space in empty_spaces:
                    # Check coordinate constraints
                    if not (0 <= space["x1"] < space["x2"] <= 1920):
                        all_valid = False
                        invalid_spaces.append(f"{space['space_id']}: invalid X coordinates")
                    
                    if not (0 <= space["y1"] < space["y2"] <= 1080):
                        all_valid = False
                        invalid_spaces.append(f"{space['space_id']}: invalid Y coordinates")
                    
                    # Check width calculation
                    calculated_width = space["x2"] - space["x1"]
                    if abs(calculated_width - space["width"]) > 1:  # Allow 1px tolerance
                        all_valid = False
                        invalid_spaces.append(f"{space['space_id']}: width mismatch")
                
                if all_valid:
                    log_test("Verify Coordinates", True, f"All {len(empty_spaces)} spaces have valid coordinates")
                    return True
                else:
                    log_test("Verify Coordinates", False, f"Invalid coordinates: {invalid_spaces}")
                    return False
            else:
                log_test("Verify Coordinates", True, "No empty spaces to verify")
                return True
        else:
            log_test("Verify Coordinates", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        log_test("Verify Coordinates", False, str(e))
        return False

def test_verify_visualization(session_id):
    """Test 7: Verify visualization is correct"""
    print("\n=== Test 7: Verify Visualization ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/results/{session_id}")
        
        if response.status_code == 200:
            result = response.json()
            
            # Check if best frame has image path
            if "best_frame" in result and result["best_frame"]:
                best_frame = result["best_frame"]
                
                if "image_path" in best_frame:
                    image_path = best_frame["image_path"]
                    
                    # Check if image file exists
                    if Path(image_path).exists():
                        # Load and verify image
                        img = cv2.imread(image_path)
                        
                        if img is not None:
                            height, width = img.shape[:2]
                            log_test("Verify Visualization", True, f"Image exists: {width}x{height}")
                            return True
                        else:
                            log_test("Verify Visualization", False, "Cannot read image file")
                            return False
                    else:
                        log_test("Verify Visualization", False, f"Image file not found: {image_path}")
                        return False
                else:
                    log_test("Verify Visualization", False, "No image_path in best_frame")
                    return False
            else:
                log_test("Verify Visualization", False, "No best_frame data")
                return False
        else:
            log_test("Verify Visualization", False, f"Status: {response.status_code}")
            return False
    except Exception as e:
        log_test("Verify Visualization", False, str(e))
        return False

def test_multiple_scenarios():
    """Test 8: Test multiple parking scenarios"""
    print("\n=== Test 8: Multiple Parking Scenarios ===")
    
    camera_id = "test-e2e-camera"
    scenarios_passed = 0
    scenarios_total = 0
    
    test_images = list(TEST_IMAGES_DIR.glob("*.jpg"))
    
    for img_path in test_images:
        scenarios_total += 1
        session_id = str(uuid.uuid4())
        
        success, result = test_upload_frame_with_detection(img_path, camera_id, session_id)
        
        if success:
            scenarios_passed += 1
    
    if scenarios_passed == scenarios_total:
        log_test("Multiple Scenarios", True, f"All {scenarios_total} scenarios passed")
        return True
    else:
        log_test("Multiple Scenarios", False, f"{scenarios_passed}/{scenarios_total} scenarios passed")
        return False

def test_edge_cases():
    """Test 9: Edge cases"""
    print("\n=== Test 9: Edge Cases ===")
    
    edge_cases_passed = 0
    edge_cases_total = 3
    
    # Test 9.1: Upload without camera_id (should work but no empty spaces)
    print("\n  9.1: Upload without camera_id")
    session_id = str(uuid.uuid4())
    test_img = list(TEST_IMAGES_DIR.glob("*.jpg"))[0]
    
    try:
        with open(test_img, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            response = requests.post(
                f"{BASE_URL}/api/frames/upload?session_id={session_id}",
                files=files,
                headers=HEADERS
            )
        
        if response.status_code == 200:
            result = response.json()
            # Should have detections but no parking_analysis
            if "detection_count" in result and "parking_analysis" not in result:
                print("    ✅ Works without camera_id (no parking analysis)")
                edge_cases_passed += 1
            else:
                print("    ❌ Unexpected response structure")
        else:
            print(f"    ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"    ❌ Error: {e}")
    
    # Test 9.2: Upload with non-existent camera_id (should work but no empty spaces)
    print("\n  9.2: Upload with non-existent camera_id")
    session_id = str(uuid.uuid4())
    
    try:
        with open(test_img, 'rb') as f:
            files = {'file': ('test.jpg', f, 'image/jpeg')}
            response = requests.post(
                f"{BASE_URL}/api/frames/upload?session_id={session_id}&camera_id=non-existent",
                files=files,
                headers=HEADERS
            )
        
        if response.status_code == 200:
            result = response.json()
            # Should have detections but no parking_analysis
            if "detection_count" in result:
                print("    ✅ Handles non-existent camera_id gracefully")
                edge_cases_passed += 1
            else:
                print("    ❌ Unexpected response structure")
        else:
            print(f"    ❌ Failed: {response.status_code}")
    except Exception as e:
        print(f"    ❌ Error: {e}")
    
    # Test 9.3: Invalid API key
    print("\n  9.3: Invalid API key")
    try:
        response = requests.get(
            f"{BASE_URL}/api/admin/calibration/test-e2e-camera",
            headers={"X-API-Key": "invalid-key"}
        )
        
        if response.status_code == 403:
            print("    ✅ Correctly rejects invalid API key")
            edge_cases_passed += 1
        else:
            print(f"    ❌ Expected 403, got {response.status_code}")
    except Exception as e:
        print(f"    ❌ Error: {e}")
    
    if edge_cases_passed == edge_cases_total:
        log_test("Edge Cases", True, f"All {edge_cases_total} edge cases handled")
        return True
    else:
        log_test("Edge Cases", False, f"{edge_cases_passed}/{edge_cases_total} edge cases passed")
        return False

def cleanup_test_data():
    """Cleanup test data"""
    print("\n=== Cleanup ===")
    
    try:
        # Delete test calibration
        response = requests.delete(
            f"{BASE_URL}/api/admin/calibration/test-e2e-camera",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            print("✅ Deleted test calibration")
        else:
            print(f"⚠️  Could not delete calibration: {response.status_code}")
        
        # Note: We keep test images for manual inspection
        print(f"ℹ️  Test images kept in {TEST_IMAGES_DIR} for inspection")
        
    except Exception as e:
        print(f"⚠️  Cleanup error: {e}")

def print_summary():
    """Print test summary"""
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    
    total = test_results["passed"] + test_results["failed"]
    pass_rate = (test_results["passed"] / total * 100) if total > 0 else 0
    
    print(f"Total Tests: {total}")
    print(f"Passed: {test_results['passed']} ✅")
    print(f"Failed: {test_results['failed']} ❌")
    print(f"Pass Rate: {pass_rate:.1f}%")
    
    if test_results["failed"] > 0:
        print("\nFailed Tests:")
        for test in test_results["tests"]:
            if not test["passed"]:
                print(f"  ❌ {test['name']}: {test['message']}")
    
    print("="*60)
    
    return test_results["failed"] == 0

def main():
    """Run all end-to-end tests"""
    print("🚀 Parking Calibration System - End-to-End Tests")
    print(f"Base URL: {BASE_URL}")
    print(f"API Key: {API_KEY[:10]}...")
    
    # Setup
    if not setup_test_environment():
        print("❌ Failed to setup test environment")
        return 1
    
    # Test 1: Server health
    if not test_server_health():
        print("\n❌ Server is not running. Please start it first:")
        print("   cd backend && uvicorn main:app --reload")
        return 1
    
    # Test 2-3: Calibration CRUD
    success, calibration = test_create_calibration()
    if not success:
        print("❌ Cannot proceed without calibration")
        return 1
    
    camera_id = calibration["camera_id"]
    test_get_calibration(camera_id)
    
    # Test 4-7: Frame upload and verification
    session_id = str(uuid.uuid4())
    test_img = list(TEST_IMAGES_DIR.glob("*.jpg"))[0]
    
    success, result = test_upload_frame_with_detection(test_img, camera_id, session_id)
    if success:
        test_verify_empty_spaces(session_id)
        test_verify_coordinates(session_id)
        test_verify_visualization(session_id)
    
    # Test 8: Multiple scenarios
    test_multiple_scenarios()
    
    # Test 9: Edge cases
    test_edge_cases()
    
    # Cleanup
    cleanup_test_data()
    
    # Summary
    all_passed = print_summary()
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main())
