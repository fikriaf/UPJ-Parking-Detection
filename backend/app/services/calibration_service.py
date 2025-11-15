from typing import List, Optional
from datetime import datetime
from app.models.calibration import CameraCalibration, CalibrationCreate, CalibrationUpdate
from app.db.mongodb import get_database

class CalibrationService:
    """Service for managing camera calibration data"""
    
    @staticmethod
    async def save_calibration(data: CalibrationCreate) -> CameraCalibration:
        """
        Create or update calibration data for a camera
        """
        db = get_database()
        
        # Check if calibration already exists
        existing = await db.calibrations.find_one({"camera_id": data.camera_id})
        
        if existing:
            # Update existing
            calibration = CameraCalibration(
                **data.dict(),
                _id=existing["_id"],
                created_at=existing["created_at"],
                updated_at=datetime.utcnow()
            )
            await db.calibrations.replace_one(
                {"camera_id": data.camera_id},
                calibration.dict(by_alias=True, exclude={"id"})
            )
        else:
            # Create new
            calibration = CameraCalibration(**data.dict())
            result = await db.calibrations.insert_one(
                calibration.dict(by_alias=True, exclude={"id"})
            )
            calibration.id = result.inserted_id
        
        return calibration
    
    @staticmethod
    async def get_calibration(camera_id: str) -> Optional[CameraCalibration]:
        """
        Get calibration data for a specific camera
        """
        db = get_database()
        calibration = await db.calibrations.find_one({"camera_id": camera_id})
        
        if calibration:
            return CameraCalibration(**calibration)
        return None
    
    @staticmethod
    async def update_calibration(camera_id: str, data: CalibrationUpdate) -> Optional[CameraCalibration]:
        """
        Update specific fields of calibration data
        """
        db = get_database()
        
        # Get existing calibration
        existing = await db.calibrations.find_one({"camera_id": camera_id})
        if not existing:
            return None
        
        # Update only provided fields
        update_data = data.dict(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        await db.calibrations.update_one(
            {"camera_id": camera_id},
            {"$set": update_data}
        )
        
        # Return updated calibration
        updated = await db.calibrations.find_one({"camera_id": camera_id})
        return CameraCalibration(**updated)
    
    @staticmethod
    async def delete_calibration(camera_id: str) -> bool:
        """
        Delete calibration data for a camera
        """
        db = get_database()
        result = await db.calibrations.delete_one({"camera_id": camera_id})
        return result.deleted_count > 0
    
    @staticmethod
    async def list_calibrations(skip: int = 0, limit: int = 50) -> List[CameraCalibration]:
        """
        List all calibration data
        """
        db = get_database()
        cursor = db.calibrations.find().skip(skip).limit(limit)
        calibrations = await cursor.to_list(length=limit)
        
        return [CameraCalibration(**cal) for cal in calibrations]
    
    @staticmethod
    def validate_calibration(data: dict) -> tuple[bool, Optional[str]]:
        """
        Validate calibration data
        Returns: (is_valid, error_message)
        """
        try:
            # Pydantic will handle validation
            CalibrationCreate(**data)
            return True, None
        except Exception as e:
            return False, str(e)

# Singleton instance
calibration_service = CalibrationService()
