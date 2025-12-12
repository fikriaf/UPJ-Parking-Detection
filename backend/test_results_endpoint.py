#!/usr/bin/env python3
"""
Test GET /api/results/{session_id} endpoint
Output: JSON dengan posisi kosong per baris
"""

import requests
import json
import sys

# Configuration
BASE_URL = "https://overtame-dewitt-throbbingly.ngrok-free.dev"
API_KEY = "parkit-admin-best-UHUYYYYY"
HEADERS = {
    "X-API-Key": API_KEY,
    "ngrok-skip-browser-warning": "true"
}

def get_session_results(session_id):
    """Get results from endpoint and extract empty spaces per row"""
    
    print(f"\n{'='*60}")
    print(f"GET /api/results/{session_id}")
    print(f"{'='*60}")
    
    try:
        response = requests.get(
            f"{BASE_URL}/api/results/{session_id}",
            headers=HEADERS,
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            return None
        
        data = response.json()
        
        # Extract info
        result = {
            "session_id": data.get("session_id"),
            "camera_id": data.get("camera_id"),
            "status": data.get("status"),
            "total_frames": data.get("total_frames", 0),
            "max_detection_count": data.get("max_detection_count", 0),
        }
        
        # Extract from best_frame
        best_frame = data.get("best_frame", {})
        if best_frame:
            result["total_motorcycles"] = best_frame.get("total_motorcycles", best_frame.get("detection_count", 0))
            result["total_empty_spaces"] = best_frame.get("total_empty_spaces", 0)
            result["parking_occupancy_rate"] = best_frame.get("parking_occupancy_rate", 0)
            
            # Empty spaces per row
            result["empty_spaces_per_row"] = best_frame.get("empty_spaces_per_row", {})
            
            # Detail posisi kosong per baris
            empty_spaces = best_frame.get("empty_spaces", [])
            spaces_by_row = {}
            
            for space in empty_spaces:
                row_idx = space.get("row_index", 0)
                row_key = f"row_{row_idx}"
                
                if row_key not in spaces_by_row:
                    spaces_by_row[row_key] = []
                
                spaces_by_row[row_key].append({
                    "space_id": space.get("space_id"),
                    "x1": space.get("x1"),
                    "x2": space.get("x2"),
                    "y1": space.get("y1"),
                    "y2": space.get("y2"),
                    "width": space.get("width"),
                    "can_fit_motorcycle": space.get("can_fit_motorcycle", False)
                })
            
            result["posisi_kosong_per_baris"] = spaces_by_row
        
        return result
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def get_latest_session_id():
    """Get latest session ID from /api/admin/sessions"""
    try:
        response = requests.get(
            f"{BASE_URL}/api/admin/sessions?limit=1&skip=0",
            headers=HEADERS,
            timeout=10
        )
        
        print(f"   Status: {response.status_code}")
        
        if response.status_code == 200:
            data = response.json()
            sessions = data.get("sessions", [])
            if sessions:
                return sessions[0].get("session_id")
        else:
            print(f"   Response: {response.text[:200]}")
        return None
    except Exception as e:
        print(f"   Error: {e}")
        return None

def main():
    # Get session_id from argument or use latest
    if len(sys.argv) > 1:
        session_id = sys.argv[1]
    else:
        print("Mencari session terbaru...")
        session_id = get_latest_session_id()
        
        if not session_id:
            print("❌ Tidak ada session. Jalankan dengan: python test_results_endpoint.py <session_id>")
            return 1
        
        print(f"Menggunakan session terbaru: {session_id}")
    
    # Get results
    result = get_session_results(session_id)
    
    if result:
        print("\n" + "="*60)
        print("📊 OUTPUT JSON - POSISI KOSONG PER BARIS")
        print("="*60)
        print(json.dumps(result, indent=2, ensure_ascii=False))
        
        # Save to file
        output_file = f"result_{session_id[:8]}.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        print(f"\n✅ Saved to: {output_file}")
        
        # Summary
        print("\n" + "="*60)
        print("📋 SUMMARY")
        print("="*60)
        print(f"Session: {result['session_id']}")
        print(f"Camera: {result['camera_id']}")
        print(f"Total Motor: {result.get('total_motorcycles', 0)}")
        print(f"Total Ruang Kosong: {result.get('total_empty_spaces', 0)}")
        print(f"Occupancy: {result.get('parking_occupancy_rate', 0)}%")
        
        print("\n📍 Ruang Kosong per Baris:")
        for row, count in result.get('empty_spaces_per_row', {}).items():
            print(f"   Row {row}: {count} ruang kosong")
        
        return 0
    
    return 1

if __name__ == "__main__":
    sys.exit(main())
