from fastapi import APIRouter, HTTPException, Header, Query
from typing import Optional, List
from datetime import datetime
import uuid
import random
import string

from app.db.mongodb import get_database
from app.models.motorcycle import MotorcycleRegister, MotorcycleResponse, MotorcycleUpdate
from app.core.config import settings

router = APIRouter()

def generate_code():
    """Generate unique 8-character code for motorcycle"""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# Public endpoints (no auth required)

@router.post("/register", response_model=MotorcycleResponse, 
    summary="Daftarkan Motor Baru",
    description="""
**🔓 Public Endpoint - Tidak perlu autentikasi**

Daftarkan motor baru dan dapatkan kode unik 8 karakter.

### Contoh Request:
```json
{
  "owner_name": "John Doe",
  "phone": "08123456789",
  "brand": "Honda",
  "model": "Vario 150",
  "color": "Hitam"
}
```

### Contoh Response:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "code": "A1B2C3D4",
  "owner_name": "John Doe",
  "phone": "08123456789",
  "brand": "Honda",
  "model": "Vario 150",
  "color": "Hitam",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```
""")
async def register_motorcycle(data: MotorcycleRegister):
    """Register a new motorcycle (Public)"""
    db = get_database()
    
    # Generate unique code
    code = generate_code()
    while await db.motorcycles.find_one({"code": code}):
        code = generate_code()
    
    # Create motorcycle record
    motorcycle_id = str(uuid.uuid4())
    now = datetime.utcnow()
    
    motorcycle_data = {
        "id": motorcycle_id,
        "code": code,
        "owner_name": data.owner_name,
        "phone": data.phone,
        "email": data.email,
        "brand": data.brand,
        "model": data.model,
        "color": data.color,
        "is_active": True,
        "created_at": now,
        "updated_at": now
    }
    
    await db.motorcycles.insert_one(motorcycle_data)
    
    return MotorcycleResponse(**motorcycle_data)

@router.get("/check/{code}",
    summary="Cek Status Motor",
    description="""
**🔓 Public Endpoint - Tidak perlu autentikasi**

Cek apakah motor dengan kode tertentu sudah terdaftar.

### Contoh Response (Terdaftar):
```json
{
  "registered": true,
  "code": "A1B2C3D4",
  "owner_name": "John Doe",
  "brand": "Honda",
  "model": "Vario 150",
  "color": "Hitam",
  "is_active": true
}
```

### Contoh Response (Tidak Terdaftar):
```json
{
  "registered": false,
  "code": "XXXXXXXX",
  "message": "Motor tidak terdaftar"
}
```
""")
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
    """
    Get motorcycle details by code (Public)
    """
    db = get_database()
    motorcycle = await db.motorcycles.find_one({"code": code.upper()})
    
    if not motorcycle:
        raise HTTPException(status_code=404, detail="Motorcycle not found")
    
    return MotorcycleResponse(**motorcycle)

@router.put("/my/{code}", response_model=MotorcycleResponse)
async def update_my_motorcycle(code: str, data: MotorcycleUpdate):
    """
    Update motorcycle details (Public - owner can update their own)
    """
    db = get_database()
    motorcycle = await db.motorcycles.find_one({"code": code.upper()})
    
    if not motorcycle:
        raise HTTPException(status_code=404, detail="Motorcycle not found")
    
    # Build update data
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
    
    await db.motorcycles.update_one(
        {"code": code.upper()},
        {"$set": update_data}
    )
    
    updated = await db.motorcycles.find_one({"code": code.upper()})
    return MotorcycleResponse(**updated)


# Admin endpoints (auth required)

async def verify_admin_key(x_api_key: Optional[str] = Header(None)):
    """Verify admin API key"""
    if not x_api_key or x_api_key != settings.ADMIN_API_KEY:
        raise HTTPException(status_code=403, detail="Invalid or missing API key")
    return True

@router.get("/", response_model=List[MotorcycleResponse])
async def list_motorcycles(
    x_api_key: str = Header(...),
    limit: int = Query(50, ge=1, le=100),
    skip: int = Query(0, ge=0),
    search: Optional[str] = Query(None, description="Search by code or owner name")
):
    """
    List all registered motorcycles (Admin only)
    """
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

@router.get("/stats")
async def get_motorcycle_stats(x_api_key: str = Header(...)):
    """
    Get motorcycle registration statistics (Admin only)
    """
    await verify_admin_key(x_api_key)
    db = get_database()
    
    total = await db.motorcycles.count_documents({})
    active = await db.motorcycles.count_documents({"is_active": True})
    inactive = await db.motorcycles.count_documents({"is_active": False})
    
    # Count by brand
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

@router.put("/admin/{code}/toggle-active")
async def toggle_motorcycle_active(code: str, x_api_key: str = Header(...)):
    """
    Toggle motorcycle active status (Admin only)
    """
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

@router.delete("/admin/{code}")
async def delete_motorcycle(code: str, x_api_key: str = Header(...)):
    """
    Delete a motorcycle registration (Admin only)
    """
    await verify_admin_key(x_api_key)
    db = get_database()
    
    result = await db.motorcycles.delete_one({"code": code.upper()})
    
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Motorcycle not found")
    
    return {
        "message": "Motorcycle deleted",
        "code": code.upper()
    }
