from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime

class User(BaseModel):
    email: EmailStr
    full_name: str
    hashed_password: str
    created_at: datetime = datetime.utcnow()
    role: str = "student"  # student, professor, admin
    # Rimosso is_active - tutti gli utenti sono sempre attivi

class UserCreate(BaseModel):
    email: EmailStr
    full_name: str
    password: str
    role: str = "student"

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: str
    is_active: bool = True  # Sempre True nella response per compatibilità frontend
    role: str