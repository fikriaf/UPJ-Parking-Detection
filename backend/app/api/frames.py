from fastapi import APIRouter, File, UploadFile, HTTPException, Query, Header
from typing import Optional
import cv2
import numpy as np
from datetime import datetime
import uuid
import os
import logging

from app.services.yolo_service import yolo_service
from app.services.calibration_service import calibration_service
from app.services.empty_space_detector import EmptySpaceDetector
from app.services.visualization_service import visualization_service
from app.models.detection import FrameDetection, DetectionSession
from app.db.mongodb import get_database
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)

async def verify_admin_key(x_api_key: Optional[str] = Header(None)):
    """Verify admin API key"""
    from app.core.config import settings
    if not x_api_key or x_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return True

@router.post("/upload")
async def upload_frame(
    session_id: str = Query(...),
    file: UploadFile = File(...),
    x_api_key: str = Header(...),
    camera_id: Optional[str] = Query(None)
):
    """
    Upload a frame for detection (Admin only)
    Frames are compared and the one with most detections is saved
    If camera_id provided, will detect empty parking spaces
    """
    try:
        await verify_admin_key(x_api_key)
        
        # Read image
        contents = await file.read()
        nparr = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if image is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        logger.info(f"Image loaded: {image.shape}")
        
        # Detect objects
        detections, count = yolo_service.detect(image)
        logger.info(f"Detections: {count}")
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in upload_frame: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")
    
    # Process with calibration if camera_id provided
    parking_analysis = None
    if camera_id:
        calibration = await calibration_service.get_calibration(camera_id)
        if calibration:
            try:
                detector = EmptySpaceDetector(calibration)
                parking_analysis = detector.process_detections(detections, session_id)
            except Exception as e:
                # Log error but continue with basic detection
                logger.warning(f"Error processing empty spaces for camera {camera_id}: {e}")
                parking_analysis = None
        else:
            # No calibration found - skip empty space detection
            logger.info(f"No calibration found for camera {camera_id}, skipping empty space detection")
    
    # Create frame detection
    frame_id = str(uuid.uuid4())
    frame_detection = FrameDetection(
        frame_id=frame_id,
        timestamp=datetime.utcnow(),
        detections=detections,
        detection_count=count
    )
    
    # Get or create session
    db = get_database()
    session = await db.detection_sessions.find_one({"session_id": session_id})
    
    if not session:
        # Create new session
        best_frame_data = frame_detection.dict() if count > 0 else None
        
        # Save initial best frame image with visualization
        if best_frame_data and count > 0:
            os.makedirs("uploads/best_frames", exist_ok=True)
            img_path = f"uploads/best_frames/{session_id}.jpg"
            
            # Draw visualization
            if parking_analysis and camera_id:
                # Draw complete parking visualization with rows, empty spaces, and detections
                calibration = await calibration_service.get_calibration(camera_id)
                if calibration:
                    img_with_viz = visualization_service.draw_complete_visualization(
                        image,
                        calibration.rows,
                        parking_analysis.detections,
                        parking_analysis.empty_spaces,
                        calibration.row_start_x,
                        calibration.row_end_x
                    )
                    cv2.imwrite(img_path, img_with_viz)
                else:
                    # Fallback to basic detection visualization
                    img_with_boxes = yolo_service.draw_detections(image, detections)
                    cv2.imwrite(img_path, img_with_boxes)
            else:
                # No calibration - use basic detection visualization
                img_with_boxes = yolo_service.draw_detections(image, detections)
                cv2.imwrite(img_path, img_with_boxes)
            
            best_frame_data["image_path"] = img_path
        
        session_data = {
            "session_id": session_id,
            "camera_id": camera_id,
            "user_id": None,
            "frames": [frame_detection.dict()],
            "max_detection_count": count,
            "best_frame": best_frame_data,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow(),
            "status": "active"
        }
        
        # Add parking analysis if available
        if parking_analysis:
            session_data["parking_analysis"] = parking_analysis.dict()
            session_data["empty_spaces"] = [space.dict() for space in parking_analysis.empty_spaces]
            session_data["total_motorcycles"] = parking_analysis.total_motorcycles
            session_data["total_empty_spaces"] = parking_analysis.total_empty_spaces
            # Convert integer keys to strings for MongoDB
            session_data["empty_spaces_per_row"] = {str(k): v for k, v in parking_analysis.empty_spaces_per_row.items()}
            session_data["parking_occupancy_rate"] = parking_analysis.parking_occupancy_rate
        
        await db.detection_sessions.insert_one(session_data)
    else:
        # Update existing session
        frames = session.get("frames", [])
        frames.append(frame_detection.dict())
        
        # Keep only last N frames
        if len(frames) > settings.MAX_FRAMES_PER_SESSION:
            frames = frames[-settings.MAX_FRAMES_PER_SESSION:]
        
        # Update best frame if current has more detections
        max_count = session.get("max_detection_count", 0)
        best_frame = session.get("best_frame")
        
        if count > max_count:
            max_count = count
            best_frame = frame_detection.dict()
            
            # Save best frame image with visualization
            os.makedirs("uploads/best_frames", exist_ok=True)
            img_path = f"uploads/best_frames/{session_id}.jpg"
            
            # Draw visualization
            if parking_analysis and camera_id:
                # Draw complete parking visualization with rows, empty spaces, and detections
                calibration = await calibration_service.get_calibration(camera_id)
                if calibration:
                    img_with_viz = visualization_service.draw_complete_visualization(
                        image,
                        calibration.rows,
                        parking_analysis.detections,
                        parking_analysis.empty_spaces,
                        calibration.row_start_x,
                        calibration.row_end_x
                    )
                    cv2.imwrite(img_path, img_with_viz)
                else:
                    # Fallback to basic detection visualization
                    img_with_boxes = yolo_service.draw_detections(image, detections)
                    cv2.imwrite(img_path, img_with_boxes)
            else:
                # No calibration - use basic detection visualization
                img_with_boxes = yolo_service.draw_detections(image, detections)
                cv2.imwrite(img_path, img_with_boxes)
            
            best_frame["image_path"] = img_path
        
        update_data = {
            "frames": frames,
            "max_detection_count": max_count,
            "best_frame": best_frame,
            "updated_at": datetime.utcnow()
        }
        
        # Update parking analysis if available
        if parking_analysis:
            update_data["parking_analysis"] = parking_analysis.dict()
            update_data["camera_id"] = camera_id
            update_data["empty_spaces"] = [space.dict() for space in parking_analysis.empty_spaces]
            update_data["total_motorcycles"] = parking_analysis.total_motorcycles
            update_data["total_empty_spaces"] = parking_analysis.total_empty_spaces
            # Convert integer keys to strings for MongoDB
            update_data["empty_spaces_per_row"] = {str(k): v for k, v in parking_analysis.empty_spaces_per_row.items()}
            update_data["parking_occupancy_rate"] = parking_analysis.parking_occupancy_rate
        
        await db.detection_sessions.update_one(
            {"session_id": session_id},
            {"$set": update_data}
        )
    
    response = {
        "frame_id": frame_id,
        "session_id": session_id,
        "detection_count": count,
        "detections": [det.dict() for det in detections],
        "is_best": count > session.get("max_detection_count", 0) if session else True
    }
    
    # Add parking analysis if available
    if parking_analysis:
        response["parking_analysis"] = {
            "total_motorcycles": parking_analysis.total_motorcycles,
            "total_empty_spaces": parking_analysis.total_empty_spaces,
            # Convert integer keys to strings for JSON compatibility
            "empty_spaces_per_row": {str(k): v for k, v in parking_analysis.empty_spaces_per_row.items()},
            "parking_occupancy_rate": parking_analysis.parking_occupancy_rate
        }
    
    return response

@router.post("/complete/{session_id}")
async def complete_session(session_id: str, x_api_key: str = Header(...)):
    """Mark session as completed (Admin only)"""
    await verify_admin_key(x_api_key)
    db = get_database()
    result = await db.detection_sessions.update_one(
        {"session_id": session_id},
        {"$set": {"status": "completed", "updated_at": datetime.utcnow()}}
    )
    
    if result.modified_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session completed", "session_id": session_id}
