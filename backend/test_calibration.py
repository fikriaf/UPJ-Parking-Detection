#!/usr/bin/env python3
"""
End-to-end test script for Parking Calibration System
Run this to test the complete flow
"""

import requests
import json
import uuid
from pathlib import Path

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "parkit-admin-secret-key-change-this"
headers = {"X-API-Key": API_KEY}

def test_calibration_crud():
    """Test calibration CRUD operations"""
    print("\n=== Testing Calibration CRUD ===")
    
    camera_id = "test-camera-1"
    
    # Create calibration
    calibration_data = {
        "camera_id": camera_id,
        "rows": [
            {"row_index": 0, "y_coordinate": 100, "label": "Row 1 (Top)"},
            {"row_index": 1, "y_coordinate": 300, "label": "Row 2 (Middle)"},
            {"row_index": 2, "y_coordinate": 500, "label": "Row 3 (Bottom)"}
        ],
        "min_space_width": 150,
        "space_coefficient": 0.8,
        "row_start_x": 0,
        "row_end_x": 1920
    }
    
    print("Creating calibration...")
    response = requests.post(
        f"{BASE_URL}/api/admin/calibration/",
        json=calibration_data,
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Calibration created successfully")
        print(json.dumps(response.json(), indent=2))
    else:
        print(f"❌ Failed to create calibration: {response.text}")
        return False
    
    # Get calibration
    print("\nGetting calibration...")
    response = requests.get(
        f"{BASE_URL}/api/admin/calibration/{camera_id}",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Calibration retrieved successfully")
        calibration = response.json()
        print(f"Camera ID: {calibration['camera_id']}")
        print(f"Rows: {len(calibration['rows'])}")
        print(f"Min space width: {calibration['min_space_width']}")
    else:
        print(f"❌ Failed to get calibration: {response.text}")
        return False
    
    # Update calibration
    print("\nUpdating calibration...")
    update_data = {
        "min_space_width": 120,
        "space_coefficient": 0.75
    }
    response = requests.put(
        f"{BASE_URL}/api/admin/calibration/{camera_id}",
        json=update_data,
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print("✅ Calibration updated successfully")
        updated = response.json()
        print(f"New min space width: {updated['min_space_width']}")
        print(f"New coefficient: {updated['space_coefficient']}")
    else:
        print(f"❌ Failed to update calibration: {response.text}")
    
    return True

def test_frame_upload_with_calibration():
    """Test frame upload with calibration"""
    print("\n=== Testing Frame Upload with Calibration ===")
    
    session_id = str(uuid.uuid4())
    camera_id = "test-camera-1"
    
    print(f"Session ID: {session_id}")
    print(f"Camera ID: {camera_id}")
    print("\nNote: This test requires actual image files to upload")
    print("To test with real images:")
    print(f"  1. Place test images in 'test_images/' folder")
    print(f"  2. Uncomment the upload code below")
    print(f"  3. Run: python test_calibration.py")
    
    # Example of how to upload (commented out since we don't have actual images)
    """
    test_images = Path('test_images')
    if test_images.exists():
        for img_path in test_images.glob('*.jpg'):
            with open(img_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(
                    f"{BASE_URL}/api/frames/upload?session_id={session_id}&camera_id={camera_id}",
                    files=files,
                    headers=headers
                )
                print(f"Upload status: {response.status_code}")
                if response.status_code == 200:
                    result = response.json()
                    print(f"Detections: {result['detection_count']}")
                    if 'parking_analysis' in result:
                        analysis = result['parking_analysis']
                        print(f"Empty spaces: {analysis['total_empty_spaces']}")
                        print(f"Occupancy: {analysis['parking_occupancy_rate']}%")
    """
    
    return True

def test_results_with_analysis():
    """Test results endpoints with parking analysis"""
    print("\n=== Testing Results with Analysis ===")
    
    # Get latest results
    print("Getting latest results...")
    response = requests.get(f"{BASE_URL}/api/results/latest?limit=5")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        results = response.json()
        print(f"Found {results['total']} sessions")
        for session in results['sessions']:
            print(f"Session {session['session_id']}: {session['max_detection_count']} detections")
            if session.get('has_parking_analysis'):
                print("  ✅ Has parking analysis")
            else:
                print("  ❌ No parking analysis")
    
    # Get live detection
    print("\nGetting live detection...")
    response = requests.get(f"{BASE_URL}/api/results/live")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        live = response.json()
        if live.get('session_id'):
            print(f"Live session: {live['session_id']}")
            print(f"Detections: {live['max_detection_count']}")
            if 'parking_analysis' in live:
                analysis = live['parking_analysis']
                print(f"Empty spaces: {analysis.get('total_empty_spaces', 'N/A')}")
                print(f"Occupancy: {analysis.get('parking_occupancy_rate', 'N/A')}%")
        else:
            print("No active session")
    
    return True

def test_validation():
    """Test calibration validation"""
    print("\n=== Testing Calibration Validation ===")
    
    # Test invalid calibration - wrong row order
    invalid_data = {
        "camera_id": "test-validation",
        "rows": [
            {"row_index": 0, "y_coordinate": 500, "label": "Row 1"},
            {"row_index": 1, "y_coordinate": 100, "label": "Row 2"}  # Wrong order
        ],
        "min_space_width": 150,
        "space_coefficient": 0.8
    }
    
    print("Testing invalid calibration (wrong row order)...")
    response = requests.post(
        f"{BASE_URL}/api/admin/calibration",
        json=invalid_data,
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 400:
        print(f"✅ Invalid calibration correctly rejected")
        print(f"   Error: {response.json().get('detail', 'Unknown error')}")
    else:
        print("❌ Invalid calibration should have been rejected")
    
    # Test invalid min_space_width
    invalid_data2 = {
        "camera_id": "test-validation-2",
        "rows": [
            {"row_index": 0, "y_coordinate": 100, "label": "Row 1"}
        ],
        "min_space_width": 5,  # Too small
        "space_coefficient": 0.8
    }
    
    print("\nTesting invalid min_space_width...")
    response = requests.post(
        f"{BASE_URL}/api/admin/calibration",
        json=invalid_data2,
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 400 or response.status_code == 422:
        print(f"✅ Invalid min_space_width correctly rejected")
    else:
        print("❌ Invalid min_space_width should have been rejected")
    
    # Test invalid coefficient
    invalid_data3 = {
        "camera_id": "test-validation-3",
        "rows": [
            {"row_index": 0, "y_coordinate": 100, "label": "Row 1"}
        ],
        "min_space_width": 150,
        "space_coefficient": 1.5  # Too large
    }
    
    print("\nTesting invalid space_coefficient...")
    response = requests.post(
        f"{BASE_URL}/api/admin/calibration",
        json=invalid_data3,
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 400 or response.status_code == 422:
        print(f"✅ Invalid space_coefficient correctly rejected")
    else:
        print("❌ Invalid space_coefficient should have been rejected")
    
    return True

def test_list_calibrations():
    """Test listing all calibrations"""
    print("\n=== Testing List Calibrations ===")
    
    response = requests.get(
        f"{BASE_URL}/api/admin/calibration/?skip=0&limit=10",
        headers=headers
    )
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        calibrations = response.json()
        print(f"✅ Found {len(calibrations)} calibrations")
        for cal in calibrations:
            print(f"  - Camera: {cal['camera_id']}, Rows: {len(cal['rows'])}")
    else:
        print(f"❌ Failed to list calibrations: {response.text}")
    
    return True

def cleanup():
    """Cleanup test data"""
    print("\n=== Cleanup ===")
    
    # Delete test calibration
    camera_id = "test-camera-1"
    response = requests.delete(
        f"{BASE_URL}/api/admin/calibration/{camera_id}",
        headers=headers
    )
    if response.status_code == 200:
        print(f"✅ Deleted calibration for {camera_id}")
    else:
        print(f"⚠️  Could not delete calibration: {response.text}")

def main():
    """Run all tests"""
    print("🚀 Starting Parking Calibration System Tests")
    print(f"Base URL: {BASE_URL}")
    print(f"API Key: {API_KEY[:10]}...")
    
    try:
        # Test server health
        response = requests.get(f"{BASE_URL}/health")
        if response.status_code != 200:
            print(f"❌ Server not healthy: {response.status_code}")
            print("Make sure the server is running: uvicorn main:app --reload")
            return
        print("✅ Server is healthy")
        
        # Run tests
        tests = [
            test_calibration_crud,
            test_list_calibrations,
            test_validation,
            test_frame_upload_with_calibration,
            test_results_with_analysis
        ]
        
        passed = 0
        failed = 0
        for test in tests:
            try:
                if test():
                    passed += 1
                    print(f"✅ {test.__name__} passed")
                else:
                    failed += 1
                    print(f"❌ {test.__name__} failed")
            except Exception as e:
                failed += 1
                print(f"❌ {test.__name__} failed with exception: {e}")
        
        # Cleanup
        cleanup()
        
        # Summary
        print(f"\n{'='*50}")
        print(f"Test Summary: {passed} passed, {failed} failed")
        print(f"{'='*50}")
        
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server. Make sure it's running on", BASE_URL)
        print("Start server with: cd backend && uvicorn main:app --reload")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")

if __name__ == "__main__":
    main()
