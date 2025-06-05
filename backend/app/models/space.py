from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class Material(BaseModel):
    name: str
    description: Optional[str]
    quantity: int = 1

class TimeSlot(BaseModel):
    start_time: str  # "09:00"
    end_time: str    # "18:00"

class Space(BaseModel):
    name: str
    type: str  # "aula", "laboratorio", "sala_riunioni", "box_medico"
    capacity: int
    materials: List[Material] = []
    location: str
    description: Optional[str]
    available_hours: TimeSlot
    booking_constraints: dict = {}  # es. {"max_duration": 120, "advance_booking_days": 7}
    is_active: bool = True

class SpaceResponse(BaseModel):
    id: str
    name: str
    type: str
    capacity: int
    materials: List[Material]
    location: str
    description: Optional[str]
    available_hours: TimeSlot
    booking_constraints: dict