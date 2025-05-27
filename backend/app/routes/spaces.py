from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from bson import ObjectId
from datetime import datetime, timedelta
from ..database import get_database
from ..models.space import SpaceResponse
from .auth import get_current_user

router = APIRouter()

@router.get("/", response_model=List[SpaceResponse])
async def get_all_spaces(
    space_type: Optional[str] = Query(None, description="Filtra per tipo di spazio"),
    capacity_min: Optional[int] = Query(None, description="Capacità minima"),
    materials: Optional[str] = Query(None, description="Materiali richiesti (separati da virgola)"),
    current_user: dict = Depends(get_current_user)
):
    """Recupera tutti gli spazi disponibili con filtri opzionali"""
    db = await get_database()
    
    # Costruisci query di filtro
    filter_query = {"is_active": True}
    
    if space_type:
        filter_query["type"] = space_type
    
    if capacity_min:
        filter_query["capacity"] = {"$gte": capacity_min}
    
    if materials:
        material_list = [m.strip() for m in materials.split(",")]
        filter_query["materials.name"] = {"$in": material_list}
    
    spaces = []
    async for space in db.spaces.find(filter_query):
        space_response = SpaceResponse(
            id=str(space["_id"]),
            **{k: v for k, v in space.items() if k != "_id"}
        )
        spaces.append(space_response)
    
    return spaces

@router.get("/{space_id}", response_model=SpaceResponse)
async def get_space_details(
    space_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Recupera dettagli di uno spazio specifico"""
    db = await get_database()
    
    try:
        space = await db.spaces.find_one({"_id": ObjectId(space_id)})
        if not space:
            raise HTTPException(status_code=404, detail="Spazio non trovato")
        
        return SpaceResponse(
            id=str(space["_id"]),
            **{k: v for k, v in space.items() if k != "_id"}
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail="ID spazio non valido")

@router.get("/{space_id}/availability")
async def check_space_availability(
    space_id: str,
    date: str = Query(..., description="Data in formato YYYY-MM-DD"),
    current_user: dict = Depends(get_current_user)
):
    """Verifica disponibilità di uno spazio per una data specifica"""
    db = await get_database()
    
    try:
        # Converte la data
        check_date = datetime.strptime(date, "%Y-%m-%d").date()
        start_datetime = datetime.combine(check_date, datetime.min.time())
        end_datetime = datetime.combine(check_date, datetime.max.time())
        
        # Trova tutte le prenotazioni per quel giorno
        bookings = []
        async for booking in db.bookings.find({
            "space_id": space_id,
            "status": {"$in": ["pending", "confirmed"]},
            "start_datetime": {"$gte": start_datetime, "$lt": end_datetime}
        }).sort("start_datetime", 1):
            bookings.append({
                "start_time": booking["start_datetime"].strftime("%H:%M"),
                "end_time": booking["end_datetime"].strftime("%H:%M"),
                "purpose": booking["purpose"]
            })
        
        # Recupera orari disponibili dello spazio
        space = await db.spaces.find_one({"_id": ObjectId(space_id)})
        if not space:
            raise HTTPException(status_code=404, detail="Spazio non trovato")
        
        available_hours = space.get("available_hours", {"start_time": "08:00", "end_time": "20:00"})
        
        return {
            "date": date,
            "available_hours": available_hours,
            "bookings": bookings,
            "space_name": space["name"]
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato data non valido. Usa YYYY-MM-DD")

@router.get("/types/list")
async def get_space_types(current_user: dict = Depends(get_current_user)):
    """Recupera tutti i tipi di spazi disponibili"""
    db = await get_database()
    
    pipeline = [
        {"$match": {"is_active": True}},
        {"$group": {"_id": "$type", "count": {"$sum": 1}}},
        {"$sort": {"_id": 1}}
    ]
    
    types = []
    async for doc in db.spaces.aggregate(pipeline):
        types.append({
            "type": doc["_id"],
            "count": doc["count"]
        })
    
    return types

@router.get("/{space_id}/materials")
async def get_space_materials(
    space_id: str,
    current_user: dict = Depends(get_current_user)
):
    """Recupera tutti i materiali disponibili in uno spazio"""
    db = await get_database()
    
    try:
        space = await db.spaces.find_one({"_id": ObjectId(space_id)})
        if not space:
            raise HTTPException(status_code=404, detail="Spazio non trovato")
        
        return {
            "space_name": space["name"],
            "materials": space.get("materials", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=400, detail="ID spazio non valido")