from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class EmptySpace(BaseModel):
    space_id: str = Field(..., description="Unique identifier for the space")
    row_index: int = Field(..., ge=0, description="Row index where space is located")
    x1: int = Field(..., description="Left boundary X coordinate")
    x2: int = Field(..., description="Right boundary X coordinate")
    y1: int = Field(..., description="Top boundary Y coordinate")
    y2: int = Field(..., description="Bottom boundary Y coordinate")
    width: float = Field(..., description="Width of the space in pixels")
    can_fit_motorcycle: bool = Field(..., description="Whether space can fit a motorcycle")
    motorcycle_capacity: int = Field(default=1, ge=0, description="Number of motorcycles that can fit in this space")
    
    class Config:
        schema_extra = {
            "example": {
                "space_id": "row0_space0",
                "row_index": 0,
                "x1": 200,
                "x2": 350,
                "y1": 50,
                "y2": 150,
                "width": 150.0,
                "can_fit_motorcycle": True,
                "motorcycle_capacity": 1
            }
        }

class DetectionWithRow(BaseModel):
    bbox: Dict[str, float] = Field(..., description="Bounding box coordinates")
    confidence: float = Field(..., description="Detection confidence")
    class_name: str = Field(default="motor", description="Detected class")
    assigned_row: Optional[int] = Field(None, description="Assigned parking row index")
    row_y_coordinate: Optional[int] = Field(None, description="Y coordinate of assigned row")
    
    class Config:
        schema_extra = {
            "example": {
                "bbox": {"x1": 100, "y1": 150, "x2": 200, "y2": 250},
                "confidence": 0.95,
                "class_name": "motor",
                "assigned_row": 0,
                "row_y_coordinate": 100
            }
        }

class ParkingAnalysis(BaseModel):
    session_id: str
    camera_id: Optional[str] = None
    detections: List[DetectionWithRow]
    empty_spaces: List[EmptySpace]
    total_motorcycles: int
    total_empty_spaces: int
    empty_spaces_per_row: Dict[int, int] = Field(default_factory=dict)
    parking_occupancy_rate: float = Field(..., description="Percentage of occupied spaces")
    
    def dict(self, **kwargs):
        """Override dict() to convert integer keys to strings for MongoDB compatibility"""
        d = super().dict(**kwargs)
        # Convert integer keys to strings
        if 'empty_spaces_per_row' in d and d['empty_spaces_per_row']:
            d['empty_spaces_per_row'] = {str(k): v for k, v in d['empty_spaces_per_row'].items()}
        return d
    
    class Config:
        schema_extra = {
            "example": {
                "session_id": "abc-123",
                "camera_id": "parking-area-1",
                "detections": [],
                "empty_spaces": [],
                "total_motorcycles": 15,
                "total_empty_spaces": 5,
                "empty_spaces_per_row": {"0": 2, "1": 2, "2": 1},
                "parking_occupancy_rate": 75.0
            }
        }
