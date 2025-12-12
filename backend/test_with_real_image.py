#!/usr/bin/env python3
"""
Test Parking Calibration System dengan Real Image dari Dataset UPJ
Mengambil result dan verify langsung dari endpoint API
"""

import requests
import json
import uuid
from pathlib import Path
import sys
import time

# Configuration
BASE_URL = "https://overtame-dewitt-throbbingly.ngrok-free.dev"
API_KEY = "parkit-admin-best-UHUYYYYY"
HEADERS = {
    "X-API-Key": API_KEY,
    "ngrok-skip-browser-warning": "true"
}

# Real image path
REAL_IMAGE_PATH = Path(r"D:\script\PYTHON\UPJ-Parking-Detection\backend\3.jpg")

def test_server_health():
    """Test 1: Server health check"""
    print("\n=== Test 1: Server Health Check ===")
    
    try:
        response = requests.get(f"{BASE_URL}/health", headers=HEADERS, timeout=10)
        if response.status_code == 200:
            print("✅ Server is running")
            print(f"   Response: {response.json()}")
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
                "label": "Row 0",
                "start_x": 400,  # Lebih lebar (dekat kamera)
                "end_x": 6100
            },
            {
                "row_index": 1, 
                "y_coordinate": 5650,  # Y sedang = tengah
                "label": "Row 1",
                "start_x": 600,  # Sedang
                "end_x": 5900
            },
            {
                "row_index": 2, 
                "y_coordinate": 5250,  # Y terkecil = paling atas (jauh dari kamera)
                "label": "Row 2",
                "start_x": 800,  # Lebih sempit (perspektif mengerucut)
                "end_x": 5700
            },
            {
                "row_index": 3, 
                "y_coordinate": 4744,  # Y terbesar = paling bawah (dekat kamera)
                "label": "Row 3",
                "start_x": 1030,  # Lebih lebar (dekat kamera)
                "end_x": 5376
            },
            {
                "row_index": 4, 
                "y_coordinate": 4444,  # Y sedang = tengah
                "label": "Row 4",
                "start_x": 1146,  # Sedang
                "end_x": 5346
            },
            {
                "row_index": 5, 
                "y_coordinate": 4100,  # Y terkecil = paling atas (jauh dari kamera)
                "label": "Row 5",
                "start_x": 1262,  # Lebih sempit (perspektif mengerucut)
                "end_x": 5083
            },
            {
                "row_index": 6, 
                "y_coordinate": 3870,  # Y sedang = tengah
                "label": "Row 6",
                "start_x": 1372,  # Sedang
                "end_x": 4967
            },
            {
                "row_index": 7, 
                "y_coordinate": 3600,  # Y terkecil = paling atas (jauh dari kamera)
                "label": "Row 7",
                "start_x": 1513,  # Lebih sempit (perspektif mengerucut)
                "end_x": 4722
            },
            {
                "row_index": 8, 
                "y_coordinate": 3371,  # Y terbesar = paling bawah (dekat kamera)
                "label": "Row 8",
                "start_x": 1574,  # Lebih lebar (dekat kamera)
                "end_x": 4679
            },
            {
                "row_index": 9, 
                "y_coordinate": 3158,  # Y sedang = tengah
                "label": "Row 9",
                "start_x": 1299,  # Sedang
                "end_x": 4557
            }
        ],
        "min_space_width": 106.0,  # Lebar space di ROW 0 (paling bawah)
        "space_coefficient": 0.95,  # Row ke atas akan lebih kecil
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
    """Test 4: Get detailed session results from endpoint"""
    print("\n=== Test 4: Get Session Results ===")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/results/{session_id}",
            headers=HEADERS,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            print(f"✅ Session results retrieved")
            print(f"   Session ID: {result['session_id']}")
            print(f"   Camera ID: {result.get('camera_id', 'N/A')}")
            print(f"   Status: {result.get('status', 'N/A')}")
            print(f"   Total frames: {result.get('total_frames', 0)}")
            print(f"   Max detections: {result.get('max_detection_count', 0)}")
            
            # Check best_frame
            if 'best_frame' in result and result['best_frame']:
                frame = result['best_frame']
                print(f"\n📊 Best Frame Analysis:")
                print(f"   Total Motorcycles: {frame.get('total_motorcycles', frame.get('detection_count', 0))}")
                print(f"   Empty Spaces: {frame.get('total_empty_spaces', 'N/A')}")
                print(f"   Occupancy Rate: {frame.get('parking_occupancy_rate', 'N/A')}%")
                
                # Empty spaces per row
                if 'empty_spaces_per_row' in frame:
                    print(f"\n   Empty Spaces per Row:")
                    for row, count in frame['empty_spaces_per_row'].items():
                        print(f"     Row {row}: {count} spaces")
                
                # Detections
                detections = frame.get('detections', [])
                print(f"\n   Detections: {len(detections)} motorcycles")
                if detections:
                    print(f"   First 3 detections:")
                    for i, det in enumerate(detections[:3], 1):
                        bbox = det.get('bbox', {})
                        conf = det.get('confidence', 0)
                        row = det.get('assigned_row', 'N/A')
                        print(f"     {i}. Conf: {conf:.2%}, Row: {row}")
            
            return True, result
        else:
            print(f"❌ Failed to get results")
            print(f"   Status: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def test_get_result_image(session_id):
    """Test 5: Get result image from endpoint"""
    print(f"\n=== Test 5: Get Result Image ===")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/results/{session_id}/image",
            headers=HEADERS,
            timeout=30
        )
        
        if response.status_code == 200:
            content_type = response.headers.get('content-type', '')
            content_length = len(response.content)
            
            print("✅ Result image retrieved from endpoint")
            print(f"   Content-Type: {content_type}")
            print(f"   Size: {content_length / 1024:.1f} KB")
            
            # Save image locally for verification
            output_path = Path(f"test_result_{session_id[:8]}.jpg")
            with open(output_path, 'wb') as f:
                f.write(response.content)
            print(f"   Saved to: {output_path}")
            
            return True
        elif response.status_code == 404:
            print("⚠️ No image available for this session")
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_verify_coordinates(session_id):
    """Test 6: Verify coordinate accuracy from endpoint data"""
    print("\n=== Test 6: Verify Coordinate Accuracy ===")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/results/{session_id}",
            headers=HEADERS,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            
            if 'best_frame' not in result or not result['best_frame']:
                print("⚠️ No best_frame to verify")
                return True
            
            frame = result['best_frame']
            empty_spaces = frame.get('empty_spaces', [])
            
            if not empty_spaces:
                print("⚠️ No empty spaces to verify")
                return True
            
            all_valid = True
            invalid_count = 0
            
            for space in empty_spaces:
                # Check X coordinates
                x1, x2 = space.get('x1', 0), space.get('x2', 0)
                y1, y2 = space.get('y1', 0), space.get('y2', 0)
                
                if x1 >= x2:
                    print(f"❌ Invalid X coordinates in {space.get('space_id')}: {x1}-{x2}")
                    all_valid = False
                    invalid_count += 1
                
                if y1 >= y2:
                    print(f"❌ Invalid Y coordinates in {space.get('space_id')}: {y1}-{y2}")
                    all_valid = False
                    invalid_count += 1
                
                # Check width calculation
                calculated_width = x2 - x1
                stored_width = space.get('width', 0)
                if abs(calculated_width - stored_width) > 1:
                    print(f"❌ Width mismatch in {space.get('space_id')}: calc={calculated_width}, stored={stored_width}")
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


def test_get_live_results():
    """Test 7: Get live detection results from endpoint"""
    print("\n=== Test 7: Get Live Results ===")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/results/live",
            headers=HEADERS,
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Live results retrieved")
            print(f"   Session ID: {result.get('session_id', 'N/A')}")
            print(f"   Camera ID: {result.get('camera_id', 'N/A')}")
            print(f"   Status: {result.get('status', 'N/A')}")
            print(f"   Max Detections: {result.get('max_detection_count', 0)}")
            
            if 'best_frame' in result and result['best_frame']:
                frame = result['best_frame']
                print(f"\n📊 Live Analysis:")
                print(f"   Motorcycles: {frame.get('total_motorcycles', frame.get('detection_count', 0))}")
                print(f"   Empty Spaces: {frame.get('total_empty_spaces', 'N/A')}")
                print(f"   Occupancy: {frame.get('parking_occupancy_rate', 'N/A')}%")
            
            return True, result.get('session_id')
        elif response.status_code == 404:
            print("⚠️ No active session found")
            return True, None
        else:
            print(f"❌ Failed: {response.status_code}")
            return False, None
    except Exception as e:
        print(f"❌ Error: {e}")
        return False, None

def test_get_latest_results():
    """Test 8: Get latest results history from endpoint"""
    print("\n=== Test 8: Get Latest Results History ===")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/results/latest?limit=5",
            headers=HEADERS,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data.get('results', [])
            print(f"✅ Retrieved {len(results)} sessions from endpoint")
            
            for i, r in enumerate(results[:5], 1):
                print(f"\n   {i}. Session: {r.get('session_id', 'N/A')[:8]}...")
                print(f"      Camera: {r.get('camera_id', 'N/A')}")
                print(f"      Status: {r.get('status', 'N/A')}")
                print(f"      Detections: {r.get('max_detection_count', 0)}")
            
            return True
        else:
            print(f"❌ Failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_admin_stats():
    """Test 9: Get admin statistics from endpoint"""
    print("\n=== Test 9: Get Admin Statistics ===")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/admin/stats",
            headers=HEADERS,
            timeout=10
        )
        
        if response.status_code == 200:
            stats = response.json()
            print("✅ Admin stats retrieved from endpoint")
            print(f"   Total Users: {stats.get('total_users', 0)}")
            print(f"   Total Sessions: {stats.get('total_sessions', 0)}")
            print(f"   Active Sessions: {stats.get('active_sessions', 0)}")
            print(f"   Completed Sessions: {stats.get('completed_sessions', 0)}")
            print(f"   Total Detections: {stats.get('total_detections', 0)}")
            return True
        elif response.status_code == 403:
            print("❌ Forbidden - Check API key")
            return False
        else:
            print(f"❌ Failed: {response.status_code}")
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
    print("   (Verify langsung dari endpoint API)")
    print("="*60)
    print(f"Base URL: {BASE_URL}")
    print(f"Image: {REAL_IMAGE_PATH.name}")
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Test 1: Server health
    if not test_server_health():
        print("\n❌ Server is not running. Please start it first.")
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
    
    # Test 4: Get results from endpoint
    test_get_session_results(session_id)
    
    # Test 5: Get result image from endpoint
    test_get_result_image(session_id)
    
    # Test 6: Verify coordinates from endpoint data
    test_verify_coordinates(session_id)
    
    # Test 7: Get live results
    test_get_live_results()
    
    # Test 8: Get latest results
    test_get_latest_results()
    
    # Test 9: Admin stats
    test_admin_stats()
    
    # Cleanup (optional - comment out to keep calibration)
    # cleanup(camera_id)
    
    print("\n" + "="*60)
    print("✅ All tests completed!")
    print("="*60)
    print("\nSemua result diambil dan diverify langsung dari endpoint API.")
    print(f"Result image disimpan di: test_result_{session_id[:8]}.jpg")
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
