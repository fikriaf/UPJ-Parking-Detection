from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse
from typing import List
import os

from app.db.mongodb import get_database
from app.models.detection import DetectionSession

router = APIRouter()

@router.get("/{session_id}")
async def get_result(session_id: str):
    """Get detection result for a session (Public - for users to view)"""
    db = get_database()
    session = await db.detection_sessions.find_one({"session_id": session_id})
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    response = {
        "session_id": session["session_id"],
        "camera_id": session.get("camera_id"),
        "status": session.get("status", "active"),
        "max_detection_count": session.get("max_detection_count", 0),
        "best_frame": session.get("best_frame"),
        "total_frames": len(session.get("frames", [])),
        "created_at": session.get("created_at"),
        "updated_at": session.get("updated_at")
    }
    
    # Add parking analysis if available
    if "parking_analysis" in session:
        response["parking_analysis"] = session["parking_analysis"]
    
    # Add empty spaces and occupancy metrics if available
    if "empty_spaces" in session:
        response["empty_spaces"] = session["empty_spaces"]
    
    if "total_motorcycles" in session:
        response["total_motorcycles"] = session["total_motorcycles"]
    
    if "total_empty_spaces" in session:
        response["total_empty_spaces"] = session["total_empty_spaces"]
    
    if "empty_spaces_per_row" in session:
        response["empty_spaces_per_row"] = session["empty_spaces_per_row"]
    
    if "parking_occupancy_rate" in session:
        response["parking_occupancy_rate"] = session["parking_occupancy_rate"]
    
    return response

@router.get("/{session_id}/image")
async def get_result_image(session_id: str):
    """Get best frame image with detections (Public - for users to view)"""
    db = get_database()
    session = await db.detection_sessions.find_one({"session_id": session_id})
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    best_frame = session.get("best_frame")
    if not best_frame or not best_frame.get("image_path"):
        raise HTTPException(status_code=404, detail="No image available")
    
    img_path = best_frame["image_path"]
    if not os.path.exists(img_path):
        raise HTTPException(status_code=404, detail="Image file not found")
    
    return FileResponse(img_path)

@router.get("/latest")
async def get_latest_results(limit: int = 10, skip: int = 0):
    """Get latest detection results (Public - for users to view)"""
    db = get_database()
    cursor = db.detection_sessions.find({"status": "completed"}).sort("created_at", -1).skip(skip).limit(limit)
    sessions = await cursor.to_list(length=limit)
    
    return {
        "total": len(sessions),
        "sessions": [
            {
                "session_id": s["session_id"],
                "camera_id": s.get("camera_id"),
                "max_detection_count": s.get("max_detection_count", 0),
                "status": s.get("status", "active"),
                "created_at": s.get("created_at"),
                "updated_at": s.get("updated_at"),
                "has_parking_analysis": bool(s.get("parking_analysis"))
            }
            for s in sessions
        ]
    }

@router.get("/live")
async def get_live_result():
    """Get current live detection (latest active session)"""
    db = get_database()
    session = await db.detection_sessions.find_one(
        {"status": "active"},
        sort=[("updated_at", -1)]
    )
    
    if not session:
        return {
            "message": "No active session",
            "session_id": None,
            "max_detection_count": 0
        }
    
    response = {
        "session_id": session["session_id"],
        "camera_id": session.get("camera_id"),
        "max_detection_count": session.get("max_detection_count", 0),
        "best_frame": session.get("best_frame"),
        "updated_at": session.get("updated_at")
    }
    
    # Add parking analysis if available
    if "parking_analysis" in session:
        response["parking_analysis"] = session["parking_analysis"]
    
    # Add empty spaces and occupancy metrics if available
    if "empty_spaces" in session:
        response["empty_spaces"] = session["empty_spaces"]
    
    if "total_motorcycles" in session:
        response["total_motorcycles"] = session["total_motorcycles"]
    
    if "total_empty_spaces" in session:
        response["total_empty_spaces"] = session["total_empty_spaces"]
    
    if "empty_spaces_per_row" in session:
        response["empty_spaces_per_row"] = session["empty_spaces_per_row"]
    
    if "parking_occupancy_rate" in session:
        response["parking_occupancy_rate"] = session["parking_occupancy_rate"]
    
    return response
