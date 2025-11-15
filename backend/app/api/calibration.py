from fastapi import APIRouter, HTTPException, Header
from typing import List, Optional

from app.models.calibration import CameraCalibration, CalibrationCreate, CalibrationUpdate
from app.services.calibration_service import calibration_service
from app.core.config import settings

router = APIRouter()

async def verify_admin_key(x_api_key: Optional[str] = Header(None)):
    """Verify admin API key"""
    if not x_api_key or x_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return True

@router.post("", response_model=CameraCalibration)
async def create_calibration(
    data: CalibrationCreate,
    x_api_key: str = Header(...)
):
    """
    Create or update camera calibration (Admin only)
    """
    await verify_admin_key(x_api_key)
    
    try:
        calibration = await calibration_service.save_calibration(data)
        return calibration
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{camera_id}", response_model=CameraCalibration)
async def get_calibration(
    camera_id: str,
    x_api_key: str = Header(...)
):
    """
    Get calibration for a specific camera (Admin only)
    """
    await verify_admin_key(x_api_key)
    
    calibration = await calibration_service.get_calibration(camera_id)
    if not calibration:
        raise HTTPException(status_code=404, detail="Calibration not found")
    
    return calibration

@router.put("/{camera_id}", response_model=CameraCalibration)
async def update_calibration(
    camera_id: str,
    data: CalibrationUpdate,
    x_api_key: str = Header(...)
):
    """
    Update specific fields of calibration (Admin only)
    """
    await verify_admin_key(x_api_key)
    
    calibration = await calibration_service.update_calibration(camera_id, data)
    if not calibration:
        raise HTTPException(status_code=404, detail="Calibration not found")
    
    return calibration

@router.delete("/{camera_id}")
async def delete_calibration(
    camera_id: str,
    x_api_key: str = Header(...)
):
    """
    Delete calibration for a camera (Admin only)
    """
    await verify_admin_key(x_api_key)
    
    success = await calibration_service.delete_calibration(camera_id)
    if not success:
        raise HTTPException(status_code=404, detail="Calibration not found")
    
    return {"message": "Calibration deleted", "camera_id": camera_id}

@router.get("", response_model=List[CameraCalibration])
async def list_calibrations(
    x_api_key: str = Header(...),
    skip: int = 0,
    limit: int = 50
):
    """
    List all calibrations (Admin only)
    """
    await verify_admin_key(x_api_key)
    
    calibrations = await calibration_service.list_calibrations(skip, limit)
    return calibrations
