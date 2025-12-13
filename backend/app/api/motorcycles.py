from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional, List
from datetime import datetime
import uuid
import random
import string

from app.db.mongodb import get_database
from app.models.motorcycle import MotorcycleRegister, MotorcycleResponse, MotorcycleUpdate
from app.core.config import settings

# Public router - no auth required
router = APIRouter()

# Admin router - requires API key
admin_router = APIRouter()


def generate_code():
    """Generate unique 8-character code for motorcycle"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))


async def verify_admin_key(x_api_key: Optional[str] = Header(None)):
    """Verify admin API key"""
    if not x_api_key or x_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return True


# ============================================
# PUBLIC ENDPOINTS (no auth required)
# ============================================

@router.post("/register", response_model=MotorcycleResponse,
    summary="Daftarkan Motor Baru",
    description="""
**🔓 Public Endpoint - Tidak perlu autentikasi**

Daftarkan motor baru dan dapatkan kode unik 8 karakter.

Jika `user_id` diberikan, data `owner_name` dan `email` akan otomatis diambil dari profil user.
""")
async def register_motorcycle(data: MotorcycleRegister):
    """Register a new motorcycle (Public)"""
    db = get_database()

    # Auto-fill from user if user_id provided
    owner_name = data.owner_name
    email = data.email
    phone = data.phone
    user_id = data.user_id

    if user_id:
        # Try to find user by username or _id
        from bson import ObjectId
        user = None
        
        # Try by username first
        user = await db.users.find_one({"username": user_id})
        
        # If not found, try by ObjectId
        if not user and ObjectId.is_valid(user_id):
            user = await db.users.find_one({"_id": ObjectId(user_id)})
        
        if user:
            # Auto-fill from user profile if not provided
            if not owner_name:
                owner_name = user.get("username")
            if not email:
                email = user.get("email")
            # Store the actual user_id (as string)
            user_id = str(user.get("_id")) if user.get("_id") else user.get("username")
        else:
            raise HTTPException(status_code=404, detail="User not found")
    
    # Validate owner_name is provided
    if not owner_name:
        raise HTTPException(status_code=400, detail="owner_name is required if user_id is not provided")

    code = generate_code()
    while await db.motorcycles.find_one({"code": code}):
        code = generate_code()

    motorcycle_id = str(uuid.uuid4())
    now = datetime.utcnow()

    motorcycle_data = {
        "id": motorcycle_id,
        "code": code,
        "user_id": user_id,
        "owner_name": owner_name,
        "phone": phone,
        "email": email,
        "brand": data.brand,
        "model": data.model,
        "color": data.color,
        "length_cm": data.length_cm,
        "width_cm": data.width_cm,
        "is_active": True,
        "created_at": now,
        "updated_at": now
    }

    await db.motorcycles.insert_one(motorcycle_data)
    return MotorcycleResponse(**motorcycle_data)


@router.get("/check/{code}",
    summary="Cek Status Motor",
    description="**🔓 Public Endpoint** - Cek apakah motor terdaftar.")
async def check_motorcycle(code: str):
    """Check if motorcycle is registered"""
    db = get_database()
    motorcycle = await db.motorcycles.find_one({"code": code.upper()})

    if not motorcycle:
        return {
            "registered": False,
            "code": code.upper(),
            "message": "Motor tidak terdaftar"
        }

    return {
        "registered": True,
        "code": motorcycle["code"],
        "owner_name": motorcycle["owner_name"],
        "brand": motorcycle.get("brand"),
        "model": motorcycle.get("model"),
        "color": motorcycle.get("color"),
        "is_active": motorcycle.get("is_active", True)
    }


@router.get("/my/{code}", response_model=MotorcycleResponse)
async def get_my_motorcycle(code: str):
    """Get motorcycle details by code (Public)"""
    db = get_database()
    motorcycle = await db.motorcycles.find_one({"code": code.upper()})

    if not motorcycle:
        raise HTTPException(status_code=404, detail="Motorcycle not found")

    return MotorcycleResponse(**motorcycle)


@router.get("/user/{user_id}", response_model=List[MotorcycleResponse],
    summary="Get Motor by User",
    description="**🔓 Public Endpoint** - Ambil semua motor yang terdaftar oleh user tertentu.")
async def get_motorcycles_by_user(user_id: str):
    """Get all motorcycles registered by a specific user"""
    db = get_database()
    
    # Search by user_id field
    motorcycles = await db.motorcycles.find({"user_id": user_id}).sort("created_at", -1).to_list(100)
    
    if not motorcycles:
        return []
    
    return [MotorcycleResponse(**m) for m in motorcycles]


@router.delete("/my/{code}",
    summary="Hapus Motor Sendiri",
    description="**🔓 Public Endpoint** - Hapus motor berdasarkan kode unik.")
async def delete_my_motorcycle(code: str):
    """Delete own motorcycle by code (Public)"""
    db = get_database()
    
    result = await db.motorcycles.delete_one({"code": code.upper()})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Motorcycle not found")
    
    return {
        "message": "Motor berhasil dihapus",
        "code": code.upper()
    }


@router.put("/my/{code}", response_model=MotorcycleResponse)
async def update_my_motorcycle(code: str, data: MotorcycleUpdate):
    """Update motorcycle details (Public - owner can update their own)"""
    db = get_database()
    motorcycle = await db.motorcycles.find_one({"code": code.upper()})

    if not motorcycle:
        raise HTTPException(status_code=404, detail="Motorcycle not found")

    update_data = {"updated_at": datetime.utcnow()}

    if data.owner_name is not None:
        update_data["owner_name"] = data.owner_name
    if data.phone is not None:
        update_data["phone"] = data.phone
    if data.email is not None:
        update_data["email"] = data.email
    if data.brand is not None:
        update_data["brand"] = data.brand
    if data.model is not None:
        update_data["model"] = data.model
    if data.color is not None:
        update_data["color"] = data.color
    if data.length_cm is not None:
        update_data["length_cm"] = data.length_cm
    if data.width_cm is not None:
        update_data["width_cm"] = data.width_cm

    await db.motorcycles.update_one(
        {"code": code.upper()},
        {"$set": update_data}
    )

    updated = await db.motorcycles.find_one({"code": code.upper()})
    return MotorcycleResponse(**updated)


# ============================================
# ADMIN ENDPOINTS (requires X-API-Key)
# ============================================

@admin_router.get("/", response_model=List[MotorcycleResponse])
async def list_motorcycles(
    x_api_key: str = Header(...),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    search: Optional[str] = Query(None, description="Search by code or owner name")
):
    """List all registered motorcycles (Admin only)"""
    await verify_admin_key(x_api_key)
    db = get_database()

    query = {}
    if search:
        query["$or"] = [
            {"code": {"$regex": search, "$options": "i"}},
            {"owner_name": {"$regex": search, "$options": "i"}}
        ]

    cursor = db.motorcycles.find(query).sort("created_at", -1).skip(skip).limit(limit)
    motorcycles = await cursor.to_list(length=limit)

    return [MotorcycleResponse(**m) for m in motorcycles]


@admin_router.get("/stats")
async def get_motorcycle_stats(x_api_key: str = Header(...)):
    """Get motorcycle registration statistics (Admin only)"""
    await verify_admin_key(x_api_key)
    db = get_database()

    total = await db.motorcycles.count_documents({})
    active = await db.motorcycles.count_documents({"is_active": True})
    inactive = await db.motorcycles.count_documents({"is_active": False})

    pipeline = [
        {"$match": {"brand": {"$ne": None}}},
        {"$group": {"_id": "$brand", "count": {"$sum": 1}}},
        {"$sort": {"count": -1}},
        {"$limit": 10}
    ]
    brands = await db.motorcycles.aggregate(pipeline).to_list(10)

    return {
        "total_registered": total,
        "active": active,
        "inactive": inactive,
        "top_brands": [{"brand": b["_id"], "count": b["count"]} for b in brands]
    }


@admin_router.put("/{code}/toggle-active")
async def toggle_motorcycle_active(code: str, x_api_key: str = Header(...)):
    """Toggle motorcycle active status (Admin only)"""
    await verify_admin_key(x_api_key)
    db = get_database()

    motorcycle = await db.motorcycles.find_one({"code": code.upper()})
    if not motorcycle:
        raise HTTPException(status_code=404, detail="Motorcycle not found")

    new_status = not motorcycle.get("is_active", True)

    await db.motorcycles.update_one(
        {"code": code.upper()},
        {"$set": {"is_active": new_status, "updated_at": datetime.utcnow()}}
    )

    return {
        "code": code.upper(),
        "is_active": new_status,
        "message": f"Motorcycle {'activated' if new_status else 'deactivated'}"
    }


@admin_router.delete("/{code}")
async def delete_motorcycle(code: str, x_api_key: str = Header(...)):
    """Delete a motorcycle registration (Admin only)"""
    await verify_admin_key(x_api_key)
    db = get_database()

    result = await db.motorcycles.delete_one({"code": code.upper()})

    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Motorcycle not found")

    return {
        "message": "Motorcycle deleted",
        "code": code.upper()
    }
