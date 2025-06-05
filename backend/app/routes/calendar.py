from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from ..database import get_database
from .auth import get_current_user

router = APIRouter()

@router.get("/bookings", response_model=List[Dict])
async def get_calendar_bookings(
    start_date: str = Query(..., description="Data inizio in formato YYYY-MM-DD"),
    end_date: str = Query(..., description="Data fine in formato YYYY-MM-DD"),
    space_id: Optional[str] = Query(None, description="Filtra per spazio specifico"),
    current_user: dict = Depends(get_current_user)
):
    """
    Recupera tutte le prenotazioni per il calendario condiviso
    Visibile a tutti gli utenti dell'applicazione
    """
    try:
        db = await get_database()
        
        # Converte le date
        start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        end_dt = datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1)
        
        # Costruisci query
        filter_query = {
            "start_datetime": {"$gte": start_dt, "$lt": end_dt},
            "status": {"$in": ["confirmed", "pending"]}  # Non mostra quelle cancellate
        }
        
        if space_id:
            filter_query["space_id"] = space_id
        
        # Recupera prenotazioni con dettagli utente e spazio
        bookings = []
        async for booking in db.bookings.find(filter_query).sort("start_datetime", 1):
            # Recupera dettagli utente
            user = await db.users.find_one({"_id": ObjectId(booking["user_id"])})
            # Recupera dettagli spazio
            space = await db.spaces.find_one({"_id": ObjectId(booking["space_id"])})
            
            booking_data = {
                "id": str(booking["_id"]),
                "space_id": booking["space_id"],
                "space_name": space["name"] if space else "Spazio eliminato",
                "space_location": space["location"] if space else "",
                "user_id": booking["user_id"],
                "user_name": user["full_name"] if user else "Utente eliminato",
                "user_role": user.get("role", "student") if user else "student",
                "start_datetime": booking["start_datetime"].isoformat(),
                "end_datetime": booking["end_datetime"].isoformat(),
                "purpose": booking["purpose"],
                "status": booking["status"],
                "materials_requested": booking.get("materials_requested", []),
                "notes": booking.get("notes", ""),
                "created_at": booking["created_at"].isoformat(),
                # Privacy: nascondi alcuni dettagli se non è la propria prenotazione
                "is_own_booking": str(booking["user_id"]) == str(current_user["_id"])
            }
            
            # Nascondi dettagli privati se non è la propria prenotazione
            if not booking_data["is_own_booking"]:
                # Mostra solo informazioni pubbliche
                booking_data["notes"] = ""  # Nascondi note private
                booking_data["purpose"] = booking_data["purpose"][:50] + "..." if len(booking_data["purpose"]) > 50 else booking_data["purpose"]
            
            bookings.append(booking_data)
        
        return bookings
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Formato data non valido. Usa YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel recupero prenotazioni: {str(e)}")

@router.get("/availability/{space_id}")
async def get_space_availability(
    space_id: str,
    date: str = Query(..., description="Data in formato YYYY-MM-DD"),
    current_user: dict = Depends(get_current_user)
):
    """
    Verifica disponibilità dettagliata di uno spazio per una data specifica
    Mostra slot orari liberi e occupati
    """
    try:
        db = await get_database()
        
        # Verifica che lo spazio esista
        space = await db.spaces.find_one({"_id": ObjectId(space_id)})
        if not space:
            raise HTTPException(status_code=404, detail="Spazio non trovato")
        
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
            # Recupera nome utente per la prenotazione
            user = await db.users.find_one({"_id": ObjectId(booking["user_id"])})
            
            bookings.append({
                "id": str(booking["_id"]),
                "start_time": booking["start_datetime"].strftime("%H:%M"),
                "end_time": booking["end_datetime"].strftime("%H:%M"),
                "user_name": user["full_name"] if user else "Utente eliminato",
                "purpose": booking["purpose"],
                "is_own": str(booking["user_id"]) == str(current_user["_id"]),
                "status": booking["status"]
            })
        
        # Genera slot orari disponibili
        available_hours = space.get("available_hours", {"start_time": "08:00", "end_time": "20:00"})
        start_hour = int(available_hours["start_time"].split(":")[0])
        end_hour = int(available_hours["end_time"].split(":")[0])
        
        time_slots = []
        for hour in range(start_hour, end_hour):
            slot_start = f"{hour:02d}:00"
            slot_end = f"{hour + 1:02d}:00"
            
            # Verifica se lo slot è occupato
            is_occupied = any(
                booking["start_time"] <= slot_start < booking["end_time"] or
                booking["start_time"] < slot_end <= booking["end_time"]
                for booking in bookings
            )
            
            # Trova la prenotazione che occupa questo slot
            occupying_booking = None
            if is_occupied:
                for booking in bookings:
                    if (booking["start_time"] <= slot_start < booking["end_time"] or
                        booking["start_time"] < slot_end <= booking["end_time"]):
                        occupying_booking = booking
                        break
            
            time_slots.append({
                "start_time": slot_start,
                "end_time": slot_end,
                "available": not is_occupied,
                "booking": occupying_booking
            })
        
        return {
            "space_id": space_id,
            "space_name": space["name"],
            "space_location": space["location"],
            "date": date,
            "available_hours": available_hours,
            "time_slots": time_slots,
            "bookings": bookings,
            "booking_constraints": space.get("booking_constraints", {})
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato data non valido. Usa YYYY-MM-DD")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nella verifica disponibilità: {str(e)}")

@router.get("/stats")
async def get_calendar_stats(
    current_user: dict = Depends(get_current_user)
):
    """
    Statistiche del calendario per dashboard
    """
    try:
        db = await get_database()
        
        now = datetime.now()
        today_start = datetime.combine(now.date(), datetime.min.time())
        today_end = datetime.combine(now.date(), datetime.max.time())
        week_start = today_start - timedelta(days=now.weekday())
        week_end = week_start + timedelta(days=7)
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        next_month = (month_start + timedelta(days=32)).replace(day=1)
        
        # Prenotazioni oggi
        today_bookings = await db.bookings.count_documents({
            "start_datetime": {"$gte": today_start, "$lt": today_end},
            "status": {"$in": ["confirmed", "pending"]}
        })
        
        # Prenotazioni questa settimana
        week_bookings = await db.bookings.count_documents({
            "start_datetime": {"$gte": week_start, "$lt": week_end},
            "status": {"$in": ["confirmed", "pending"]}
        })
        
        # Prenotazioni questo mese
        month_bookings = await db.bookings.count_documents({
            "start_datetime": {"$gte": month_start, "$lt": next_month},
            "status": {"$in": ["confirmed", "pending"]}
        })
        
        # Spazi più utilizzati questo mese
        popular_spaces_pipeline = [
            {
                "$match": {
                    "start_datetime": {"$gte": month_start, "$lt": next_month},
                    "status": {"$in": ["confirmed", "pending"]}
                }
            },
            {
                "$group": {
                    "_id": "$space_id",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 5}
        ]
        
        popular_spaces = []
        async for space_stat in db.bookings.aggregate(popular_spaces_pipeline):
            space = await db.spaces.find_one({"_id": ObjectId(space_stat["_id"])})
            if space:
                popular_spaces.append({
                    "space_id": str(space["_id"]),
                    "space_name": space["name"],
                    "booking_count": space_stat["count"]
                })
        
        # Prossime prenotazioni per l'utente corrente
        user_next_bookings = []
        async for booking in db.bookings.find({
            "user_id": str(current_user["_id"]),
            "start_datetime": {"$gte": now},
            "status": {"$in": ["confirmed", "pending"]}
        }).sort("start_datetime", 1).limit(3):
            space = await db.spaces.find_one({"_id": ObjectId(booking["space_id"])})
            user_next_bookings.append({
                "id": str(booking["_id"]),
                "space_name": space["name"] if space else "Spazio eliminato",
                "start_datetime": booking["start_datetime"].isoformat(),
                "purpose": booking["purpose"]
            })
        
        return {
            "today_bookings": today_bookings,
            "week_bookings": week_bookings,
            "month_bookings": month_bookings,
            "popular_spaces": popular_spaces,
            "user_next_bookings": user_next_bookings,
            "last_updated": now.isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nel recupero statistiche: {str(e)}")

@router.post("/bulk-availability")
async def check_bulk_availability(
    request_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """
    Verifica disponibilità di più spazi per più date
    Utile per trovare alternative rapidamente
    """
    try:
        space_ids = request_data.get("space_ids", [])
        dates = request_data.get("dates", [])
        start_time = request_data.get("start_time", "09:00")
        end_time = request_data.get("end_time", "11:00")
        
        if not space_ids or not dates:
            raise HTTPException(status_code=400, detail="space_ids e dates sono obbligatori")
        
        db = await get_database()
        results = []
        
        for space_id in space_ids:
            space = await db.spaces.find_one({"_id": ObjectId(space_id)})
            if not space:
                continue
                
            space_result = {
                "space_id": space_id,
                "space_name": space["name"],
                "space_location": space["location"],
                "availability": []
            }
            
            for date_str in dates:
                try:
                    check_date = datetime.strptime(date_str, "%Y-%m-%d")
                    start_datetime = datetime.combine(check_date.date(), datetime.strptime(start_time, "%H:%M").time())
                    end_datetime = datetime.combine(check_date.date(), datetime.strptime(end_time, "%H:%M").time())
                    
                    # Verifica conflitti
                    conflict = await db.bookings.find_one({
                        "space_id": space_id,
                        "status": {"$in": ["confirmed", "pending"]},
                        "$or": [
                            {
                                "start_datetime": {"$lt": end_datetime},
                                "end_datetime": {"$gt": start_datetime}
                            }
                        ]
                    })
                    
                    space_result["availability"].append({
                        "date": date_str,
                        "available": conflict is None,
                        "conflict_reason": "Spazio già occupato" if conflict else None
                    })
                    
                except ValueError:
                    space_result["availability"].append({
                        "date": date_str,
                        "available": False,
                        "conflict_reason": "Formato data non valido"
                    })
            
            results.append(space_result)
        
        return {"results": results}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Errore nella verifica bulk: {str(e)}")