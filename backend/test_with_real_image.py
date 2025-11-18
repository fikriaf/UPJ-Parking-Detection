#!/usr/bin/env python3
"""
Test Parking Calibration System dengan Real Image dari Dataset UPJ
"""

import requests
import json
import uuid
from pathlib import Path
import sys

# Configuration
BASE_URL = "http://localhost:8000"
API_KEY = "parkit-admin-best-UHUYYYYY"
HEADERS = {"X-API-Key": API_KEY}

# Real image path
REAL_IMAGE_PATH = Path(r"D:\script\PYTHON\UPJ-Parking-Detection\backend\3.jpg")

def test_server_health():
    """Test 1: Server health check"""
    print("\n=== Test 1: Server Health Check ===")
    
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running")
            return True
        else:
            print(f"❌ Server returned status: {response.status_code}")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server")
        print("Make sure server is running: uvicorn main:app --reload")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_create_calibration():
    """Test 2: Create calibration for UPJ parking"""
    print("\n=== Test 2: Create Calibration for UPJ Parking ===")
    
    # Calibration data untuk parking UPJ dengan perspective correction
    # 
    # ⚠️ ROW NUMBERING: DIMULAI DARI BAWAH (Row 0 = paling bawah/dekat kamera)
    # Y coordinates: Y besar = bawah (dekat), Y kecil = atas (jauh)
    # X boundaries: setiap row punya start_x dan end_x sendiri (mengerucut ke atas)
    # min_space_width: lebar space di ROW 0 (paling bawah, paling dekat kamera)
    # space_coefficient: faktor pengurangan untuk row lebih atas (0.7-0.9)
    #
    # Formula: expected_space = min_space_width * (coefficient ^ row_index)
    # - Row 0 (bottom): 150 * (0.85^0) = 150px (terbesar)
    # - Row 1 (middle): 150 * (0.85^1) = 127px
    # - Row 2 (top): 150 * (0.85^2) = 108px (terkecil)
    calibration_data = {
        "camera_id": "upj-parking-camera-1",
        "rows": [
            {
                "row_index": 0, 
                "y_coordinate": 6400,  # Y terbesar = paling bawah (dekat kamera)
                "label": "Row 0 (Bottom/Near)",
                "start_x": 400,  # Lebih lebar (dekat kamera)
                "end_x": 6100
            },
            {
                "row_index": 1, 
                "y_coordinate": 5650,  # Y sedang = tengah
                "label": "Row 1 (Middle)",
                "start_x": 600,  # Sedang
                "end_x": 5900
            },
            {
                "row_index": 2, 
                "y_coordinate": 5250,  # Y terkecil = paling atas (jauh dari kamera)
                "label": "Row 2 (Top/Far)",
                "start_x": 650,  # Lebih sempit (perspektif mengerucut)
                "end_x": 5700
            }
        ],
        "min_space_width": 100.0,  # Lebar space di ROW 0 (paling bawah)
        "space_coefficient": 0.85,  # Row ke atas akan lebih kecil
        "row_start_x": 40,  # Global fallback (jika per-row tidak diset)
        "row_end_x": 6100
    }
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/admin/calibration",
            json=calibration_data,
            headers=HEADERS
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Calibration created for camera: {result['camera_id']}")
            print(f"   Rows configured: {len(result['rows'])}")
            print(f"   Min space width: {result['min_space_width']} pixels")
            print(f"   Space coefficient: {result['space_coefficient']}")
            return True, result
        else:
            print(f"❌ Failed to create calibration")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def test_upload_real_image(camera_id):
    """Test 3: Upload real UPJ parking image"""
    print("\n=== Test 3: Upload Real UPJ Parking Image ===")
    
    # Check if image exists
    if not REAL_IMAGE_PATH.exists():
        print(f"❌ Image not found: {REAL_IMAGE_PATH}")
        print("Please check the path and try again")
        return False, None
    
    print(f"Image path: {REAL_IMAGE_PATH}")
    print(f"Image size: {REAL_IMAGE_PATH.stat().st_size / 1024:.1f} KB")
    
    session_id = str(uuid.uuid4())
    
    try:
        with open(REAL_IMAGE_PATH, 'rb') as f:
            files = {'file': ('upj_parking.jpg', f, 'image/jpeg')}
            response = requests.post(
                f"{BASE_URL}/api/frames/upload?session_id={session_id}&camera_id={camera_id}",
                files=files,
                headers=HEADERS
            )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Image uploaded successfully")
            print(f"   Session ID: {session_id}")
            print(f"   Frame ID: {result['frame_id']}")
            print(f"   Motorcycles detected: {result['detection_count']}")
            
            if 'parking_analysis' in result:
                analysis = result['parking_analysis']
                print(f"\n📊 Parking Analysis:")
                print(f"   Total motorcycles: {analysis['total_motorcycles']}")
                print(f"   Empty spaces: {analysis['total_empty_spaces']}")
                print(f"   Occupancy rate: {analysis['parking_occupancy_rate']}%")
                
                if 'empty_spaces_per_row' in analysis:
                    print(f"\n   Empty spaces per row:")
                    for row_idx, count in analysis['empty_spaces_per_row'].items():
                        print(f"     Row {row_idx}: {count} empty spaces")
            else:
                print("   ⚠️  No parking analysis (calibration may not be applied)")
            
            return True, session_id
        else:
            print(f"❌ Failed to upload image")
            print(f"   Status: {response.status_code}")
            print(f"   Error: {response.text}")
            return False, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def test_get_session_results(session_id):
    """Test 4: Get detailed session results"""
    print("\n=== Test 4: Get Session Results ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/results/{session_id}")
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Session results retrieved")
            print(f"   Session ID: {result['session_id']}")
            print(f"   Camera ID: {result.get('camera_id', 'N/A')}")
            print(f"   Status: {result.get('status', 'N/A')}")
            print(f"   Total frames: {len(result.get('frames', []))}")
            print(f"   Max detections: {result.get('max_detection_count', 0)}")
            
            # Check empty spaces
            if 'empty_spaces' in result:
                empty_spaces = result['empty_spaces']
                print(f"\n📍 Empty Spaces Details:")
                print(f"   Total empty spaces: {len(empty_spaces)}")
                
                if empty_spaces:
                    print(f"\n   First 3 empty spaces:")
                    for i, space in enumerate(empty_spaces[:3], 1):
                        print(f"     {i}. {space['space_id']}")
                        print(f"        Row: {space['row_index']}")
                        print(f"        Position: X({space['x1']}-{space['x2']}), Y({space['y1']}-{space['y2']})")
                        print(f"        Width: {space['width']:.1f} pixels")
                        print(f"        Can fit motorcycle: {space['can_fit_motorcycle']}")
            
            # Check visualization
            if 'best_frame' in result and result['best_frame']:
                best_frame = result['best_frame']
                if 'image_path' in best_frame:
                    img_path = Path(best_frame['image_path'])
                    if img_path.exists():
                        print(f"\n🖼️  Visualization Image:")
                        print(f"   Path: {img_path}")
                        print(f"   Size: {img_path.stat().st_size / 1024:.1f} KB")
                        print(f"   ✅ Image file exists")
                    else:
                        print(f"   ❌ Image file not found: {img_path}")
            
            return True
        else:
            print(f"❌ Failed to get results")
            print(f"   Status: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_verify_coordinates(session_id):
    """Test 5: Verify coordinate accuracy"""
    print("\n=== Test 5: Verify Coordinate Accuracy ===")
    
    try:
        response = requests.get(f"{BASE_URL}/api/results/{session_id}")
        
        if response.status_code == 200:
            result = response.json()
            
            if 'empty_spaces' not in result or not result['empty_spaces']:
                print("⚠️  No empty spaces to verify")
                return True
            
            empty_spaces = result['empty_spaces']
            all_valid = True
            invalid_count = 0
            
            for space in empty_spaces:
                # Check X coordinates
                if not (0 <= space['x1'] < space['x2'] <= 1920):
                    print(f"❌ Invalid X coordinates in {space['space_id']}: {space['x1']}-{space['x2']}")
                    all_valid = False
                    invalid_count += 1
                
                # Check Y coordinates
                if not (0 <= space['y1'] < space['y2'] <= 1080):
                    print(f"❌ Invalid Y coordinates in {space['space_id']}: {space['y1']}-{space['y2']}")
                    all_valid = False
                    invalid_count += 1
                
                # Check width calculation
                calculated_width = space['x2'] - space['x1']
                if abs(calculated_width - space['width']) > 1:
                    print(f"❌ Width mismatch in {space['space_id']}: calculated={calculated_width}, stored={space['width']}")
                    all_valid = False
                    invalid_count += 1
            
            if all_valid:
                print(f"✅ All {len(empty_spaces)} empty spaces have valid coordinates")
                return True
            else:
                print(f"❌ Found {invalid_count} coordinate issues")
                return False
        else:
            print(f"❌ Failed to get results: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def cleanup(camera_id):
    """Cleanup test data"""
    print("\n=== Cleanup ===")
    
    try:
        response = requests.delete(
            f"{BASE_URL}/api/admin/calibration/{camera_id}",
            headers=HEADERS
        )
        
        if response.status_code == 200:
            print(f"✅ Deleted calibration for {camera_id}")
        else:
            print(f"⚠️  Could not delete calibration: {response.status_code}")
    except Exception as e:
        print(f"⚠️  Cleanup error: {e}")

def main():
    """Run all tests with real UPJ parking image"""
    print("="*60)
    print("🚗 Parking Calibration System - Real Image Test")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Image: {REAL_IMAGE_PATH.name}")
    
    # Test 1: Server health
    if not test_server_health():
        print("\n❌ Server is not running. Please start it first:")
        print("   cd backend && uvicorn main:app --reload")
        return 1
    
    # Test 2: Create calibration
    success, calibration = test_create_calibration()
    if not success:
        print("\n❌ Cannot proceed without calibration")
        return 1
    
    camera_id = calibration['camera_id']
    
    # Test 3: Upload real image
    success, session_id = test_upload_real_image(camera_id)
    if not success:
        cleanup(camera_id)
        return 1
    
    # Test 4: Get results
    test_get_session_results(session_id)
    
    # Test 5: Verify coordinates
    test_verify_coordinates(session_id)
    
    # Cleanup
    # cleanup(camera_id)
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)
    print("\nNext steps:")
    print("1. Check visualization image in uploads/best_frames/")
    print("2. Adjust calibration parameters if needed")
    print("3. Test with more images from the dataset")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
