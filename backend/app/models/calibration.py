from pydantic import BaseModel, Field, validator
from typing import List, Optional
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

class ParkingRow(BaseModel):
    row_index: int = Field(..., ge=0, description="Row index (0 = top)")
    y_coordinate: int = Field(..., ge=0, description="Y coordinate of row line")
    label: str = Field(..., description="Row label (e.g., 'Row 1')")
    start_x: Optional[int] = Field(None, ge=0, description="Left boundary X for this row (optional, uses global if not set)")
    end_x: Optional[int] = Field(None, ge=0, description="Right boundary X for this row (optional, uses global if not set)")

class CameraCalibration(BaseModel):
    id: Optional[PyObjectId] = Field(alias="_id", default=None)
    camera_id: str = Field(..., description="Unique camera identifier")
    rows: List[ParkingRow] = Field(..., min_items=1, max_items=10)
    min_space_width: float = Field(..., ge=10, le=500, description="Minimum width for empty space at bottom row (pixels)")
    space_coefficient: float = Field(..., ge=0.1, le=1.0, description="Reduction factor per row for perspective")
    row_start_x: int = Field(default=0, ge=0, description="Left boundary of parking area")
    row_end_x: int = Field(default=1920, ge=0, description="Right boundary of parking area")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('rows')
    def validate_rows_order(cls, v):
        """
        Validate that rows are properly ordered
        Row numbering: Row 0 = bottom (largest Y), Row 1, 2... = going up (smaller Y)
        So Y coordinates should be in DESCENDING order (bottom to top)
        """
        if len(v) > 1:
            for i in range(len(v) - 1):
                if v[i].y_coordinate <= v[i + 1].y_coordinate:
                    raise ValueError(
                        "Row Y coordinates must be in descending order (bottom to top). "
                        "Row 0 should have the largest Y (bottom), Row 1, 2... smaller Y (going up)"
                    )
        return v
    
    @validator('row_end_x')
    def validate_row_boundaries(cls, v, values):
        """Validate that row_end_x > row_start_x"""
        if 'row_start_x' in values and v <= values['row_start_x']:
            raise ValueError("row_end_x must be greater than row_start_x")
        return v
    
    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}

class CalibrationCreate(BaseModel):
    camera_id: str
    rows: List[ParkingRow]
    min_space_width: float = Field(..., ge=10, le=500)
    space_coefficient: float = Field(..., ge=0.1, le=1.0)
    row_start_x: int = Field(default=0, ge=0)
    row_end_x: int = Field(default=1920, ge=0)

class CalibrationUpdate(BaseModel):
    rows: Optional[List[ParkingRow]] = None
    min_space_width: Optional[float] = Field(None, ge=10, le=500)
    space_coefficient: Optional[float] = Field(None, ge=0.1, le=1.0)
    row_start_x: Optional[int] = Field(None, ge=0)
    row_end_x: Optional[int] = Field(None, ge=0)
