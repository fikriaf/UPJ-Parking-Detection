#!/usr/bin/env python3
"""
Debug script untuk melihat detail deteksi dan empty space
"""

import requests
import json
from pathlib import Path

BASE_URL = "http://localhost:8000"
API_KEY = "parkit-admin-secret-key-change-this"
HEADERS = {"X-API-Key": API_KEY}

def debug_detection(session_id=None):
    """Get detailed detection info"""
    print("="*60)
    print("DEBUG: Empty Space Detection")
    print("="*60)
    
    # Get session
    if session_id:
        response = requests.get(f"{BASE_URL}/api/results/{session_id}")
    else:
        response = requests.get(f"{BASE_URL}/api/results/live")
    
    if response.status_code != 200:
        print(f"❌ Session not found (status: {response.status_code})")
        print("\nTry: python debug_detection.py <session_id>")
        return
    
    result = response.json()
    
    if not result.get('session_id'):
        print("❌ No session data")
        return
    
    print(f"\n📊 Session: {result['session_id']}")
    print(f"Camera: {result.get('camera_id', 'N/A')}")
    print(f"Total motorcycles detected: {result.get('max_detection_count', 0)}")
    
    # Show parking analysis
    if 'parking_analysis' in result:
        analysis = result['parking_analysis']
        print(f"\n📈 Parking Analysis:")
        print(f"  Total motorcycles: {analysis.get('total_motorcycles', 0)}")
        print(f"  Total empty spaces: {analysis.get('total_empty_spaces', 0)}")
        print(f"  Occupancy rate: {analysis.get('parking_occupancy_rate', 0)}%")
        
        # Empty spaces per row
        if 'empty_spaces_per_row' in analysis:
            print(f"\n  Empty spaces per row:")
            for row_idx, count in sorted(analysis['empty_spaces_per_row'].items()):
                print(f"    Row {row_idx}: {count} empty spaces")
    
    # Show detections with row assignment
    if 'parking_analysis' in result and 'detections' in result['parking_analysis']:
        detections = result['parking_analysis']['detections']
        print(f"\n🏍️  Motorcycle Detections ({len(detections)} total):")
        
        # Group by row
        by_row = {}
        for det in detections:
            row = det.get('assigned_row', 'N/A')
            if row not in by_row:
                by_row[row] = []
            by_row[row].append(det)
        
        for row_idx in sorted(by_row.keys()):
            dets = by_row[row_idx]
            print(f"\n  Row {row_idx}: {len(dets)} motorcycles")
            for i, det in enumerate(dets, 1):
                bbox = det['bbox']
                print(f"    {i}. X: {bbox['x1']:.0f}-{bbox['x2']:.0f} (width: {bbox['x2']-bbox['x1']:.0f}px), "
                      f"Y: {bbox['y1']:.0f}-{bbox['y2']:.0f}, Conf: {det['confidence']:.2f}")
    
    # Show empty spaces detail
    if 'empty_spaces' in result:
        empty_spaces = result['empty_spaces']
        print(f"\n🟢 Empty Spaces ({len(empty_spaces)} total):")
        
        # Group by row
        by_row = {}
        for space in empty_spaces:
            row = space['row_index']
            if row not in by_row:
                by_row[row] = []
            by_row[row].append(space)
        
        for row_idx in sorted(by_row.keys()):
            spaces = by_row[row_idx]
            print(f"\n  Row {row_idx}: {len(spaces)} empty spaces")
            for space in spaces:
                capacity = space.get('motorcycle_capacity', 1)
                print(f"    {space['space_id']}: X: {space['x1']}-{space['x2']} "
                      f"(width: {space['width']:.0f}px), Capacity: {capacity} motor(s)")
    
    # Get calibration to show expected space per row
    camera_id = result.get('camera_id')
    if camera_id:
        print(f"\n⚙️  Calibration for {camera_id}:")
        cal_response = requests.get(
            f"{BASE_URL}/api/admin/calibration/{camera_id}",
            headers=HEADERS
        )
        
        if cal_response.status_code == 200:
            cal = cal_response.json()
            print(f"  Min space width (Row 0): {cal['min_space_width']}px")
            print(f"  Space coefficient: {cal['space_coefficient']}")
            
            # Calculate expected space per row
            print(f"\n  Expected space width per row:")
            for row in cal['rows']:
                row_idx = row['row_index']
                expected = cal['min_space_width'] * (cal['space_coefficient'] ** row_idx)
                start_x = row.get('start_x', cal.get('row_start_x', 0))
                end_x = row.get('end_x', cal.get('row_end_x', 1920))
                print(f"    Row {row_idx} ({row['label']}): {expected:.1f}px")
                print(f"      Y: {row['y_coordinate']}, X: {start_x}-{end_x} (width: {end_x-start_x}px)")
    
    print("\n" + "="*60)
    print("💡 TIPS:")
    print("  - Jika row tidak ada motorcycles: Cek Y coordinate row")
    print("  - Jika row tidak ada empty spaces: Cek expected space vs actual gap")
    print("  - Jika space di edge tidak terdeteksi: Cek start_x dan end_x")
    print("="*60)

if __name__ == "__main__":
    import sys
    session_id = sys.argv[1] if len(sys.argv) > 1 else None
    debug_detection(session_id)
