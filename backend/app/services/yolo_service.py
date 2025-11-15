from ultralytics import YOLO
import cv2
import numpy as np
from typing import List, Tuple
from app.core.config import settings
from app.models.detection import BoundingBox
import os

class YOLOService:
    def __init__(self):
        self.model = None
        self.load_model()
    
    def load_model(self):
        """Load YOLO model"""
        if not os.path.exists(settings.MODEL_PATH):
            raise FileNotFoundError(f"Model not found at {settings.MODEL_PATH}")
        
        self.model = YOLO(settings.MODEL_PATH)
        print(f"✅ Model loaded from {settings.MODEL_PATH}")
    
    def detect(self, image: np.ndarray) -> Tuple[List[BoundingBox], int]:
        """
        Detect objects in image
        Returns: (list of bounding boxes, detection count)
        """
        results = self.model.predict(
            image,
            conf=settings.CONFIDENCE_THRESHOLD,
            iou=settings.IOU_THRESHOLD,
            max_det=settings.MAX_DETECTIONS,
            verbose=False
        )
        
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                conf = float(box.conf[0].cpu().numpy())
                cls = int(box.cls[0].cpu().numpy())
                class_name = result.names[cls]
                
                detections.append(BoundingBox(
                    x1=float(x1),
                    y1=float(y1),
                    x2=float(x2),
                    y2=float(y2),
                    confidence=conf,
                    class_name=class_name
                ))
        
        return detections, len(detections)
    
    def draw_detections(self, image: np.ndarray, detections: List[BoundingBox]) -> np.ndarray:
        """Draw bounding boxes on image"""
        img_copy = image.copy()
        
        for det in detections:
            x1, y1, x2, y2 = int(det.x1), int(det.y1), int(det.x2), int(det.y2)
            
            # Draw box
            cv2.rectangle(img_copy, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label
            label = f"{det.class_name} {det.confidence:.2f}"
            (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
            cv2.rectangle(img_copy, (x1, y1 - 20), (x1 + w, y1), (0, 255, 0), -1)
            cv2.putText(img_copy, label, (x1, y1 - 5), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 1)
        
        return img_copy

# Singleton instance
yolo_service = YOLOService()
