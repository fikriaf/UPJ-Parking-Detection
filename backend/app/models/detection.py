from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type, handler):
        from pydantic_core import core_schema
        return core_schema.union_schema([
            core_schema.is_instance_schema(ObjectId),
            core_schema.chain_schema([
                core_schema.str_schema(),
                core_schema.no_info_plain_validator_function(cls.validate),
            ])
        ])

    @classmethod
    def validate(cls, v):
        if isinstance(v, ObjectId):
            return v
        if isinstance(v, str) and ObjectId.is_valid(v):
            return ObjectId(v)
        raise ValueError("Invalid ObjectId")

    @classmethod
    def __get_pydantic_json_schema__(cls, schema, handler):
        return {"type": "string"}

class BoundingBox(BaseModel):
    x1: float
    y1: float
    x2: float
    y2: float
    confidence: float
    class_name: str = "motor"

class FrameDetection(BaseModel):
    frame_id: str
    timestamp: datetime
    detections: List[BoundingBox]
    detection_count: int
    image_path: Optional[str] = None

class DetectionSession(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    session_id: str
    camera_id: Optional[str] = Field(None, description="Camera identifier for calibration lookup")
    user_id: Optional[str] = None
    frames: List[FrameDetection] = []
    best_frame: Optional[FrameDetection] = None
    max_detection_count: int = 0
    empty_spaces: List[Dict] = Field(default_factory=list, description="List of detected empty parking spaces")
    total_motorcycles: int = Field(default=0, description="Total number of motorcycles detected")
    total_empty_spaces: int = Field(default=0, description="Total number of empty spaces detected")
    empty_spaces_per_row: Dict[str, int] = Field(default_factory=dict, description="Empty spaces count per row")
    parking_occupancy_rate: Optional[float] = Field(None, description="Parking occupancy rate percentage")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    status: str = "active"  # active, completed
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
