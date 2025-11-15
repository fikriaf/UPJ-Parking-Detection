#!/usr/bin/env python3
"""
Helper script untuk menentukan Y coordinates parking rows dari image
Klik pada image untuk menandai posisi rows
"""

import cv2
import numpy as np
from pathlib import Path

# Image path
IMAGE_PATH = Path(r"D:\script\PYTHON\UPJ-Parking-Detection\Dataset Parkiran UPJ.v3i.yolov12\test\images\35_jpg.rf.77b7bac4c0bd7f7cf5fb1ded133385fb.jpg")

# Global variables
rows = []
img_display = None
img_original = None

def mouse_callback(event, x, y, flags, param):
    """Handle mouse clicks to mark row positions"""
    global rows, img_display, img_original
    
    if event == cv2.EVENT_LBUTTONDOWN:
        # Add new row
        row_index = len(rows)
        rows.append({
            "row_index": row_index,
            "y_coordinate": y,
            "label": f"Row {row_index + 1}",
            "x": x  # Store X for reference
        })
        
        print(f"✅ Row {row_index} added: Y={y}, X={x}")
        
        # Redraw
        img_display = img_original.copy()
        draw_rows(img_display)
        cv2.imshow("Calibration Helper", img_display)
    
    elif event == cv2.EVENT_RBUTTONDOWN:
        # Remove last row
        if rows:
            removed = rows.pop()
            print(f"❌ Removed Row {removed['row_index']}: Y={removed['y_coordinate']}")
            
            # Redraw
            img_display = img_original.copy()
            draw_rows(img_display)
            cv2.imshow("Calibration Helper", img_display)

def draw_rows(img):
    """Draw marked rows on image"""
    for row in rows:
        y = row['y_coordinate']
        
        # Draw horizontal line
        cv2.line(img, (0, y), (img.shape[1], y), (255, 0, 0), 2)
        
        # Draw label
        cv2.putText(
            img,
            f"{row['label']} (Y:{y})",
            (10, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.6,
            (255, 0, 0),
            2
        )
        
        # Draw row index at click position
        cv2.circle(img, (row['x'], y), 5, (0, 255, 0), -1)

def print_calibration_json():
    """Print calibration JSON for copy-paste"""
    print("\n" + "="*60)
    print("CALIBRATION DATA (Copy this to your test script)")
    print("="*60)
    print('"rows": [')
    
    for i, row in enumerate(rows):
        comma = "," if i < len(rows) - 1 else ""
        print(f'    {{')
        print(f'        "row_index": {row["row_index"]},')
        print(f'        "y_coordinate": {row["y_coordinate"]},')
        print(f'        "label": "{row["label"]}"')
        print(f'    }}{comma}')
    
    print(']')
    print("="*60)
    
    # Calculate suggested X boundaries based on perspective
    if len(rows) >= 2:
        print("\nSUGGESTED X BOUNDARIES (adjust as needed):")
        print("="*60)
        
        # Assume perspective: top rows narrower, bottom rows wider
        # Example: top row 400-1100 (700px), bottom row 120-1480 (1360px)
        total_rows = len(rows)
        
        for i, row in enumerate(rows):
            # Linear interpolation for X boundaries
            # Top row (i=0): narrower
            # Bottom row (i=total_rows-1): wider
            ratio = i / (total_rows - 1) if total_rows > 1 else 0
            
            start_x = int(400 - (280 * ratio))  # 400 -> 120
            end_x = int(1100 + (380 * ratio))   # 1100 -> 1480
            
            print(f'Row {i}: "start_x": {start_x}, "end_x": {end_x}  (width: {end_x - start_x}px)')
        
        print("="*60)

def main():
    """Main function"""
    global img_display, img_original
    
    print("="*60)
    print("PARKING CALIBRATION HELPER")
    print("="*60)
    print(f"Image: {IMAGE_PATH.name}")
    print()
    print("INSTRUCTIONS:")
    print("1. LEFT CLICK on image to mark parking row positions")
    print("2. RIGHT CLICK to remove last marked row")
    print("3. Press 'S' to save and print calibration data")
    print("4. Press 'Q' to quit")
    print("="*60)
    
    # Check if image exists
    if not IMAGE_PATH.exists():
        print(f"❌ Image not found: {IMAGE_PATH}")
        return
    
    # Load image
    img_original = cv2.imread(str(IMAGE_PATH))
    if img_original is None:
        print(f"❌ Cannot read image: {IMAGE_PATH}")
        return
    
    # Resize if too large
    height, width = img_original.shape[:2]
    max_height = 900
    if height > max_height:
        scale = max_height / height
        new_width = int(width * scale)
        img_original = cv2.resize(img_original, (new_width, max_height))
        print(f"ℹ️  Image resized to {new_width}x{max_height} for display")
    
    img_display = img_original.copy()
    
    # Create window and set mouse callback
    cv2.namedWindow("Calibration Helper")
    cv2.setMouseCallback("Calibration Helper", mouse_callback)
    
    # Show image
    cv2.imshow("Calibration Helper", img_display)
    
    print("\n✅ Window opened. Start clicking on parking rows!")
    
    # Main loop
    while True:
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q') or key == ord('Q'):
            print("\n👋 Quitting...")
            break
        
        elif key == ord('s') or key == ord('S'):
            if rows:
                print_calibration_json()
            else:
                print("\n⚠️  No rows marked yet!")
    
    cv2.destroyAllWindows()
    
    if rows:
        print(f"\n✅ Marked {len(rows)} rows")
        print("Copy the calibration data above to your test script!")
    else:
        print("\n⚠️  No rows were marked")

if __name__ == "__main__":
    main()
