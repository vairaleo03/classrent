from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from enum import Enum

class BookingStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    CANCELLED = "cancelled"
    COMPLETED = "completed"

class Booking(BaseModel):
    user_id: str
    space_id: str
    start_datetime: datetime
    end_datetime: datetime
    purpose: str
    status: BookingStatus = BookingStatus.PENDING
    materials_requested: List[str] = []
    notes: Optional[str]
    created_at: datetime = datetime.utcnow()
    updated_at: datetime = datetime.utcnow()

class BookingCreate(BaseModel):
    space_id: str
    start_datetime: datetime
    end_datetime: datetime
    purpose: str
    materials_requested: List[str] = []
    notes: Optional[str]

class BookingUpdate(BaseModel):
    start_datetime: Optional[datetime]
    end_datetime: Optional[datetime]
    purpose: Optional[str]
    materials_requested: Optional[List[str]]
    notes: Optional[str]

class BookingResponse(BaseModel):
    id: str
    user_id: str
    space_id: str
    space_name: str
    start_datetime: datetime
    end_datetime: datetime
    purpose: str
    status: BookingStatus
    materials_requested: List[str]
    notes: Optional[str]
    created_at: datetime