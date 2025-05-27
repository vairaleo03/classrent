from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class Material(BaseModel):
    name: str
    description: Optional[str] = None
    quantity: int = 1
    category: Optional[str] = "generale"  # "elettronica", "arredamento", "didattica", ecc.
    is_available: bool = True
    maintenance_notes: Optional[str] = None

class MaterialCreate(BaseModel):
    name: str
    description: Optional[str] = None
    quantity: int = 1
    category: Optional[str] = "generale"
    maintenance_notes: Optional[str] = None

class MaterialUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    quantity: Optional[int] = None
    category: Optional[str] = None
    is_available: Optional[bool] = None
    maintenance_notes: Optional[str] = None

class MaterialResponse(BaseModel):
    id: str
    name: str
    description: Optional[str]
    quantity: int
    category: str
    is_available: bool
    maintenance_notes: Optional[str]
    spaces_count: int = 0  # Numero di spazi che hanno questo materiale

class MaterialUsage(BaseModel):
    material_id: str
    space_id: str
    space_name: str
    booking_id: str
    user_id: str
    usage_date: datetime
    quantity_used: int = 1
    notes: Optional[str] = None

class MaterialInventory(BaseModel):
    material_id: str
    total_quantity: int
    available_quantity: int
    reserved_quantity: int
    maintenance_quantity: int = 0
    last_updated: datetime = datetime.utcnow()

# Modello per statistiche materiali
class MaterialStats(BaseModel):
    material_id: str
    material_name: str
    total_bookings: int
    most_used_space: Optional[str]
    average_usage_per_month: float
    last_usage_date: Optional[datetime]