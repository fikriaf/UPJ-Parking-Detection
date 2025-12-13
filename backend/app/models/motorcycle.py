from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class MotorcycleRegister(BaseModel):
    """Model for registering a motorcycle"""
    user_id: Optional[str] = Field(None, description="ID user yang terdaftar (optional)")
    owner_name: Optional[str] = Field(None, min_length=1, max_length=100, description="Nama pemilik (auto-fill dari user jika user_id ada)")
    phone: Optional[str] = Field(None, max_length=20, description="Nomor telepon")
    email: Optional[str] = Field(None, max_length=100, description="Email (auto-fill dari user jika user_id ada)")
    brand: Optional[str] = Field(None, max_length=50, description="Merk motor")
    model: Optional[str] = Field(None, max_length=50, description="Model motor")
    color: Optional[str] = Field(None, max_length=30, description="Warna motor")

class MotorcycleResponse(BaseModel):
    """Response model for motorcycle"""
    id: str
    code: str  # Kode unik untuk identifikasi (bukan plat)
    user_id: Optional[str] = None  # Link ke user jika ada
    owner_name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    color: Optional[str] = None
    is_active: bool = True
    created_at: datetime
    updated_at: datetime

class MotorcycleUpdate(BaseModel):
    """Model for updating motorcycle"""
    owner_name: Optional[str] = Field(None, min_length=1, max_length=100)
    phone: Optional[str] = Field(None, max_length=20)
    email: Optional[str] = Field(None, max_length=100)
    brand: Optional[str] = Field(None, max_length=50)
    model: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=30)
    is_active: Optional[bool] = None
