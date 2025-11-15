import cv2
import numpy as np
from typing import List
from app.models.calibration import ParkingRow
from app.models.empty_space import EmptySpace, DetectionWithRow

class VisualizationService:
    """Service for drawing parking visualizations on images"""
    
    @staticmethod
    def draw_parking_rows(image: np.ndarray, rows: List[ParkingRow], global_start_x: int = 0, global_end_x: int = None) -> np.ndarray:
        """Draw horizontal lines for parking rows and vertical boundary lines"""
        img_copy = image.copy()
        img_height, img_width = img_copy.shape[:2]
        
        if global_end_x is None:
            global_end_x = img_width
        
        for row in rows:
            # Draw blue horizontal line
            cv2.line(
                img_copy,
                (0, row.y_coordinate),
                (img_width, row.y_coordinate),
                (255, 0, 0),  # Blue
                2
            )
            
            # Add row label
            cv2.putText(
                img_copy,
                row.label,
                (10, row.y_coordinate - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.6,
                (255, 0, 0),
                2
            )
            
            # Draw yellow vertical boundary lines for this row
            start_x = row.start_x if row.start_x is not None else global_start_x
            end_x = row.end_x if row.end_x is not None else global_end_x
            
            # Left boundary (start_x)
            cv2.line(
                img_copy,
                (start_x, max(0, row.y_coordinate - 60)),
                (start_x, min(img_height, row.y_coordinate + 60)),
                (0, 255, 255),  # Yellow
                2
            )
            
            # Right boundary (end_x)
            cv2.line(
                img_copy,
                (end_x, max(0, row.y_coordinate - 60)),
                (end_x, min(img_height, row.y_coordinate + 60)),
                (0, 255, 255),  # Yellow
                2
            )
            
            # Add small labels for boundaries
            cv2.putText(
                img_copy,
                f"X:{start_x}",
                (start_x + 5, row.y_coordinate - 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (0, 255, 255),
                1
            )
            cv2.putText(
                img_copy,
                f"X:{end_x}",
                (end_x - 60, row.y_coordinate - 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.4,
                (0, 255, 255),
                1
            )
        
        return img_copy
    
    @staticmethod
    def draw_empty_spaces(image: np.ndarray, empty_spaces: List[EmptySpace]) -> np.ndarray:
        """Draw green rectangles for empty parking spaces"""
        img_copy = image.copy()
        
        for space in empty_spaces:
            if space.can_fit_motorcycle:
                # Draw green rectangle
                cv2.rectangle(
                    img_copy,
                    (space.x1, space.y1),
                    (space.x2, space.y2),
                    (0, 255, 0),  # Green
                    2
                )
                
                # Add semi-transparent green fill
                overlay = img_copy.copy()
                cv2.rectangle(
                    overlay,
                    (space.x1, space.y1),
                    (space.x2, space.y2),
                    (0, 255, 0),
                    -1
                )
                cv2.addWeighted(overlay, 0.2, img_copy, 0.8, 0, img_copy)
        
        return img_copy
    
    @staticmethod
    def draw_detections_with_rows(
        image: np.ndarray,
        detections: List[DetectionWithRow]
    ) -> np.ndarray:
        """Draw bounding boxes with row labels"""
        img_copy = image.copy()
        
        for det in detections:
            bbox = det.bbox
            x1, y1 = int(bbox["x1"]), int(bbox["y1"])
            x2, y2 = int(bbox["x2"]), int(bbox["y2"])
            
            # Draw red bounding box
            cv2.rectangle(img_copy, (x1, y1), (x2, y2), (0, 0, 255), 2)
            
            # Add label with confidence and row
            label = f"{det.class_name} {det.confidence:.2f}"
            if det.assigned_row is not None:
                label += f" R{det.assigned_row}"
            
            # Draw label background
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(img_copy, (x1, y1 - 20), (x1 + w, y1), (0, 0, 255), -1)
            
            # Draw label text
            cv2.putText(
                img_copy,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (255, 255, 255),
                1
            )
        
        return img_copy
    
    @staticmethod
    def add_space_labels(image: np.ndarray, empty_spaces: List[EmptySpace]) -> np.ndarray:
        """Add 'EMPTY' text labels on spaces"""
        img_copy = image.copy()
        
        for space in empty_spaces:
            if space.can_fit_motorcycle:
                # Calculate center of space
                center_x = (space.x1 + space.x2) // 2
                center_y = (space.y1 + space.y2) // 2
                
                # Add "EMPTY" text with capacity
                capacity = space.motorcycle_capacity if hasattr(space, 'motorcycle_capacity') else 1
                text = f"EMPTY x{capacity}" if capacity > 1 else "EMPTY"
                (w, h), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)
                
                # Draw text background
                cv2.rectangle(
                    img_copy,
                    (center_x - w // 2 - 5, center_y - h // 2 - 5),
                    (center_x + w // 2 + 5, center_y + h // 2 + 5),
                    (0, 0, 0),
                    -1
                )
                
                # Draw text
                cv2.putText(
                    img_copy,
                    text,
                    (center_x - w // 2, center_y + h // 2),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )
                
                # Add width info
                width_text = f"{int(space.width)}px"
                cv2.putText(
                    img_copy,
                    width_text,
                    (center_x - 30, center_y + h // 2 + 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.4,
                    (255, 255, 255),
                    1
                )
        
        return img_copy
    
    @staticmethod
    def draw_complete_visualization(
        image: np.ndarray,
        rows: List[ParkingRow],
        detections: List[DetectionWithRow],
        empty_spaces: List[EmptySpace],
        global_start_x: int = 0,
        global_end_x: int = None
    ) -> np.ndarray:
        """
        Draw complete parking visualization with all elements
        
        Elements drawn:
        - Blue horizontal lines: Parking rows
        - Yellow vertical lines: Row X boundaries (perspective correction)
        - Green rectangles: Empty parking spaces
        - Red boxes: Detected motorcycles
        - White text: Labels and measurements
        """
        img = image.copy()
        
        # Draw in order: rows (with boundaries) -> empty spaces -> detections -> labels
        img = VisualizationService.draw_parking_rows(img, rows, global_start_x, global_end_x)
        img = VisualizationService.draw_empty_spaces(img, empty_spaces)
        img = VisualizationService.draw_detections_with_rows(img, detections)
        img = VisualizationService.add_space_labels(img, empty_spaces)
        
        return img

# Singleton instance
visualization_service = VisualizationService()
