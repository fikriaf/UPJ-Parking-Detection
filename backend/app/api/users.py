from fastapi import APIRouter, HTTPException
from app.models.user import User, UserCreate
from app.db.mongodb import get_database
from passlib.context import CryptContext

router = APIRouter()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def get_password_hash(password):
    return pwd_context.hash(password)

@router.post("/register")
async def register(user: UserCreate):
    """Register new user (optional - for tracking)"""
    db = get_database()
    
    # Check if user exists
    existing = await db.users.find_one({"$or": [{"username": user.username}, {"email": user.email}]})
    if existing:
        raise HTTPException(status_code=400, detail="Username or email already registered")
    
    # Create user
    hashed_password = get_password_hash(user.password)
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    
    result = await db.users.insert_one(new_user.dict(by_alias=True, exclude={"id"}))
    
    return {
        "message": "User registered successfully",
        "user_id": str(result.inserted_id),
        "username": user.username
    }

@router.get("/{username}",
    summary="Get User Info",
    description="**🔓 Public Endpoint** - Ambil info user berdasarkan username.")
async def get_user(username: str):
    """Get user info by username"""
    db = get_database()
    user = await db.users.find_one({"username": username})
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    return {
        "user_id": str(user.get("_id")),
        "username": user["username"],
        "email": user["email"],
        "is_active": user.get("is_active", True),
        "is_admin": user.get("is_admin", False),
        "created_at": user.get("created_at")
    }
