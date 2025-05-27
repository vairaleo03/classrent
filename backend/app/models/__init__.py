"""
Models package for ClassRent

Contiene tutti i modelli Pydantic per l'applicazione.
"""

from .user import User, UserCreate, UserLogin, UserResponse
from .space import Space, SpaceResponse, Material, TimeSlot
from .booking import Booking, BookingCreate, BookingUpdate, BookingResponse, BookingStatus
from .material import (
    Material as MaterialModel, 
    MaterialCreate, 
    MaterialUpdate, 
    MaterialResponse,
    MaterialUsage,
    MaterialInventory,
    MaterialStats
)

__all__ = [
    # User models
    "User",
    "UserCreate", 
    "UserLogin",
    "UserResponse",
    
    # Space models
    "Space",
    "SpaceResponse",
    "Material",
    "TimeSlot",
    
    # Booking models
    "Booking",
    "BookingCreate",
    "BookingUpdate", 
    "BookingResponse",
    "BookingStatus",
    
    # Material models
    "MaterialModel",
    "MaterialCreate",
    "MaterialUpdate",
    "MaterialResponse",
    "MaterialUsage",
    "MaterialInventory",
    "MaterialStats"
]