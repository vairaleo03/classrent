from fastapi import APIRouter, Depends, HTTPException
from typing import List
from bson import ObjectId
from ..models.booking import BookingCreate, BookingUpdate, BookingResponse
from ..services.booking_service import booking_service
from .auth import get_current_user

router = APIRouter()

@router.post("/", response_model=dict)
async def create_booking(
    booking: BookingCreate,
    current_user: dict = Depends(get_current_user)
):
    """Crea una nuova prenotazione"""
    result = await booking_service.create_booking(
        booking.dict(),
        str(current_user["_id"])
    )
    return result

@router.get("/", response_model=List[BookingResponse])
async def get_my_bookings(current_user: dict = Depends(get_current_user)):
    """Recupera le prenotazioni dell'utente corrente"""
    bookings = await booking_service.get_user_bookings(str(current_user["_id"]))
    return bookings

@router.put("/{booking_id}", response_model=dict)
async def update_booking(
    booking_id: str,
    booking_update: BookingUpdate,
    current_user: dict = Depends(get_current_user)
):
    """Aggiorna una prenotazione"""
    result = await booking_service.update_booking(
        booking_id,
        str(current_user["_id"]),
        booking_update.dict(exclude_unset=True)
    )
    return result

@router.delete("/{booking_id}", response_model=dict)
async def cancel_booking(
    booking_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Cancella una prenotazione"""
    result = await booking_service.cancel_booking(
        booking_id,
        str(current_user["_id"])
    )
    return result

@router.get("/history", response_model=List[BookingResponse])
async def get_booking_history(current_user: dict = Depends(get_current_user)):
    """Recupera lo storico completo delle prenotazioni"""
    bookings = await booking_service.get_user_bookings(str(current_user["_id"]))
    return bookings