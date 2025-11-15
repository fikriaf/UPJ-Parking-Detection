#!/usr/bin/env python3
"""
Simple test - Upload image without calibration
"""

import requests
from pathlib import Path

BASE_URL = "http://localhost:8000"
API_KEY = "parkit-admin-secret-key-change-this"
HEADERS = {"X-API-Key": API_KEY}

IMAGE_PATH = Path(r"D:\script\PYTHON\UPJ-Parking-Detection\Dataset Parkiran UPJ.v3i.yolov12\test\images\35_jpg.rf.77b7bac4c0bd7f7cf5fb1ded133385fb.jpg")

print("Testing simple upload WITHOUT calibration...")
print(f"Image: {IMAGE_PATH.name}")

if not IMAGE_PATH.exists():
    print(f"❌ Image not found: {IMAGE_PATH}")
    exit(1)

try:
    with open(IMAGE_PATH, 'rb') as f:
        files = {'file': ('test.jpg', f, 'image/jpeg')}
        response = requests.post(
            f"{BASE_URL}/api/frames/upload?session_id=simple-test-123",
            files=files,
            headers=HEADERS,
            timeout=30
        )
    
    print(f"\nStatus: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"✅ Success!")
        print(f"   Detections: {result['detection_count']}")
        print(f"   Frame ID: {result['frame_id']}")
    else:
        print(f"❌ Failed")
        print(f"   Error: {response.text}")

except Exception as e:
    print(f"❌ Exception: {e}")
