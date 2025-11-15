from fastapi import APIRouter, HTTPException, Header
from typing import Optional
from datetime import datetime

from app.db.mongodb import get_database
from app.core.config import settings

router = APIRouter()

async def verify_admin_key(x_api_key: Optional[str] = Header(None)):
    """Verify admin API key"""
    if not x_api_key or x_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return True

@router.get("/stats")
async def get_stats(x_api_key: str = Header(...)):
    """Get system statistics"""
    await verify_admin_key(x_api_key)
    db = get_database()
    
    total_users = await db.users.count_documents({})
    total_sessions = await db.detection_sessions.count_documents({})
    active_sessions = await db.detection_sessions.count_documents({"status": "active"})
    completed_sessions = await db.detection_sessions.count_documents({"status": "completed"})
    
    # Total detections
    pipeline = [
        {"$group": {"_id": None, "total": {"$sum": "$max_detection_count"}}}
    ]
    result = await db.detection_sessions.aggregate(pipeline).to_list(1)
    total_detections = result[0]["total"] if result else 0
    
    return {
        "total_users": total_users,
        "total_sessions": total_sessions,
        "active_sessions": active_sessions,
        "completed_sessions": completed_sessions,
        "total_detections": total_detections,
        "timestamp": datetime.utcnow()
    }

@router.get("/users")
async def get_all_users(
    x_api_key: str = Header(...),
    limit: int = 50,
    skip: int = 0
):
    """Get all users"""
    await verify_admin_key(x_api_key)
    db = get_database()
    cursor = db.users.find({}).skip(skip).limit(limit)
    users = await cursor.to_list(length=limit)
    
    return {
        "total": len(users),
        "users": [
            {
                "username": u["username"],
                "email": u["email"],
                "is_active": u.get("is_active", True),
                "is_admin": u.get("is_admin", False),
                "created_at": u.get("created_at")
            }
            for u in users
        ]
    }

@router.get("/sessions")
async def get_all_sessions(
    x_api_key: str = Header(...),
    limit: int = 50,
    skip: int = 0,
    status: str = None
):
    """Get all detection sessions"""
    await verify_admin_key(x_api_key)
    db = get_database()
    
    query = {}
    if status:
        query["status"] = status
    
    cursor = db.detection_sessions.find(query).sort("created_at", -1).skip(skip).limit(limit)
    sessions = await cursor.to_list(length=limit)
    
    return {
        "total": len(sessions),
        "sessions": [
            {
                "session_id": s["session_id"],
                "user_id": s.get("user_id"),
                "max_detection_count": s.get("max_detection_count", 0),
                "status": s.get("status", "active"),
                "total_frames": len(s.get("frames", [])),
                "created_at": s.get("created_at"),
                "updated_at": s.get("updated_at")
            }
            for s in sessions
        ]
    }

@router.put("/users/{username}/toggle-active")
async def toggle_user_active(
    username: str,
    x_api_key: str = Header(...)
):
    """Toggle user active status"""
    await verify_admin_key(x_api_key)
    db = get_database()
    user = await db.users.find_one({"username": username})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_status = not user.get("is_active", True)
    await db.users.update_one(
        {"username": username},
        {"$set": {"is_active": new_status}}
    )
    
    return {
        "message": f"User {'activated' if new_status else 'deactivated'}",
        "username": username,
        "is_active": new_status
    }

@router.delete("/sessions/{session_id}")
async def delete_session_admin(
    session_id: str,
    x_api_key: str = Header(...)
):
    """Delete any session (admin)"""
    await verify_admin_key(x_api_key)
    db = get_database()
    
    # Get session to delete image
    session = await db.detection_sessions.find_one({"session_id": session_id})
    if session:
        best_frame = session.get("best_frame")
        if best_frame and best_frame.get("image_path"):
            try:
                import os
                os.remove(best_frame["image_path"])
            except:
                pass
    
    result = await db.detection_sessions.delete_one({"session_id": session_id})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session deleted", "session_id": session_id}
