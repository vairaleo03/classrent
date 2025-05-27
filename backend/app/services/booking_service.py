from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from ..database import get_database
from ..models.booking import Booking, BookingStatus, BookingResponse
from .email_service import email_service
from .calendar_service import calendar_service

class BookingService:
    def __init__(self):
        pass
    
    async def create_booking(self, booking_data: Dict, user_id: str) -> Dict:
        """Crea una nuova prenotazione"""
        db = await get_database()
        
        # Verifica disponibilità
        if not await self.check_availability(
            booking_data["space_id"], 
            booking_data["start_datetime"], 
            booking_data["end_datetime"]
        ):
            return {"error": "Lo spazio non è disponibile nell'orario richiesto"}
        
        # Verifica vincoli dello spazio
        space = await db.spaces.find_one({"_id": ObjectId(booking_data["space_id"])})
        if not await self.check_constraints(booking_data, space):
            return {"error": "La prenotazione non rispetta i vincoli dello spazio"}
        
        # Crea prenotazione
        booking = Booking(
            user_id=user_id,
            **booking_data
        )
        
        result = await db.bookings.insert_one(booking.dict())
        booking_id = str(result.inserted_id)
        
        # Recupera informazioni utente
        user = await db.users.find_one({"_id": ObjectId(user_id)})
        
        # Prepara dati per calendario e email
        booking_calendar_data = {
            'booking_id': booking_id,
            'space_name': space['name'],
            'location': space['location'],
            'start_datetime': booking.start_datetime,
            'end_datetime': booking.end_datetime,
            'purpose': booking.purpose,
            'materials_requested': booking.materials_requested,
            'notes': booking.notes
        }
        
        # Aggiungi al calendario (se configurato)
        calendar_added = await calendar_service.add_booking_to_calendar(
            booking_calendar_data, 
            user["email"]
        )
        
        # Invia email di conferma
        await email_service.send_booking_confirmation(user["email"], booking, space)
        
        # Programma reminder
        await self.schedule_reminder(booking_id, user["email"], booking.start_datetime)
        
        return {
            "booking_id": booking_id, 
            "status": "created",
            "calendar_added": calendar_added
        }
    
    async def check_availability(self, space_id: str, start_time: datetime, end_time: datetime) -> bool:
        """Verifica se lo spazio è disponibile"""
        db = await get_database()
        
        overlapping = await db.bookings.find_one({
            "space_id": space_id,
            "status": {"$in": ["pending", "confirmed"]},
            "$or": [
                {
                    "start_datetime": {"$lt": end_time},
                    "end_datetime": {"$gt": start_time}
                }
            ]
        })
        
        return overlapping is None
    
    async def check_constraints(self, booking_data: Dict, space: Dict) -> bool:
        """Verifica i vincoli di prenotazione dello spazio"""
        constraints = space.get("booking_constraints", {})
        
        # Durata massima
        if "max_duration" in constraints:
            duration = (booking_data["end_datetime"] - booking_data["start_datetime"]).total_seconds() / 60
            if duration > constraints["max_duration"]:
                return False
        
        # Anticipo minimo prenotazione
        if "advance_booking_days" in constraints:
            min_advance = datetime.now() + timedelta(days=constraints["advance_booking_days"])
            if booking_data["start_datetime"] < min_advance:
                return False
        
        # Orari disponibili
        available_hours = space.get("available_hours", {})
        if available_hours:
            start_hour = booking_data["start_datetime"].strftime("%H:%M")
            end_hour = booking_data["end_datetime"].strftime("%H:%M")
            
            if (start_hour < available_hours.get("start_time", "00:00") or 
                end_hour > available_hours.get("end_time", "23:59")):
                return False
        
        return True
    
    async def get_user_bookings(self, user_id: str) -> List[BookingResponse]:
        """Recupera le prenotazioni dell'utente"""
        db = await get_database()
        
        bookings = []
        async for booking in db.bookings.find({"user_id": user_id}).sort("start_datetime", -1):
            space = await db.spaces.find_one({"_id": ObjectId(booking["space_id"])})
            
            booking_response = BookingResponse(
                id=str(booking["_id"]),
                space_name=space["name"] if space else "Spazio eliminato",
                **booking
            )
            bookings.append(booking_response)
        
        return bookings
    
    async def update_booking(self, booking_id: str, user_id: str, update_data: Dict) -> Dict:
        """Aggiorna una prenotazione"""
        db = await get_database()
        
        # Verifica proprietario
        booking = await db.bookings.find_one({
            "_id": ObjectId(booking_id),
            "user_id": user_id
        })
        
        if not booking:
            return {"error": "Prenotazione non trovata"}
        
        # Verifica se può essere modificata
        if booking["start_datetime"] <= datetime.now():
            return {"error": "Non è possibile modificare prenotazioni già iniziate"}
        
        # Se vengono modificati orari, verifica disponibilità
        if "start_datetime" in update_data or "end_datetime" in update_data:
            new_start = update_data.get("start_datetime", booking["start_datetime"])
            new_end = update_data.get("end_datetime", booking["end_datetime"])
            
            # Verifica disponibilità escludendo la prenotazione corrente
            overlapping = await db.bookings.find_one({
                "_id": {"$ne": ObjectId(booking_id)},
                "space_id": booking["space_id"],
                "status": {"$in": ["pending", "confirmed"]},
                "$or": [
                    {
                        "start_datetime": {"$lt": new_end},
                        "end_datetime": {"$gt": new_start}
                    }
                ]
            })
            
            if overlapping:
                return {"error": "Lo spazio non è disponibile nei nuovi orari"}
        
        # Aggiorna prenotazione
        update_data["updated_at"] = datetime.now()
        await db.bookings.update_one(
            {"_id": ObjectId(booking_id)},
            {"$set": update_data}
        )
        
        # Aggiorna calendario se configurato
        if "start_datetime" in update_data or "end_datetime" in update_data:
            space = await db.spaces.find_one({"_id": ObjectId(booking["space_id"])})
            updated_booking = {**booking, **update_data}
            
            booking_calendar_data = {
                'booking_id': booking_id,
                'space_name': space['name'],
                'location': space['location'],
                'start_datetime': updated_booking['start_datetime'],
                'end_datetime': updated_booking['end_datetime'],
                'purpose': updated_booking['purpose'],
                'materials_requested': updated_booking.get('materials_requested', []),
                'notes': updated_booking.get('notes', '')
            }
            
            await calendar_service.update_booking_in_calendar(booking_id, booking_calendar_data)
        
        return {"status": "updated"}
    
    async def cancel_booking(self, booking_id: str, user_id: str) -> Dict:
        """Cancella una prenotazione"""
        db = await get_database()
        
        # Recupera prenotazione prima di cancellarla
        booking = await db.bookings.find_one({
            "_id": ObjectId(booking_id),
            "user_id": user_id
        })
        
        if not booking:
            return {"error": "Prenotazione non trovata"}
        
        result = await db.bookings.update_one(
            {
                "_id": ObjectId(booking_id),
                "user_id": user_id,
                "start_datetime": {"$gt": datetime.now()}
            },
            {
                "$set": {
                    "status": BookingStatus.CANCELLED,
                    "updated_at": datetime.now()
                }
            }
        )
        
        if result.modified_count == 0:
            return {"error": "Prenotazione non trovata o non cancellabile"}
        
        # Rimuovi dal calendario se configurato
        await calendar_service.remove_booking_from_calendar(booking_id)
        
        return {"status": "cancelled"}
    
    async def schedule_reminder(self, booking_id: str, email: str, start_time: datetime):
        """Programma reminder per la prenotazione"""
        from apscheduler.schedulers.asyncio import AsyncIOScheduler
        
        reminder_time = start_time - timedelta(hours=24)
        if reminder_time > datetime.now():
            scheduler = AsyncIOScheduler()
            scheduler.add_job(
                email_service.send_reminder,
                'date',
                run_date=reminder_time,
                args=[email, booking_id]
            )
            scheduler.start()
    
    async def get_booking_statistics(self, user_id: str) -> Dict:
        """Recupera statistiche delle prenotazioni dell'utente"""
        db = await get_database()
        
        pipeline = [
            {"$match": {"user_id": user_id}},
            {
                "$group": {
                    "_id": None,
                    "total_bookings": {"$sum": 1},
                    "confirmed_bookings": {
                        "$sum": {"$cond": [{"$eq": ["$status", "confirmed"]}, 1, 0]}
                    },
                    "cancelled_bookings": {
                        "$sum": {"$cond": [{"$eq": ["$status", "cancelled"]}, 1, 0]}
                    },
                    "total_hours": {
                        "$sum": {
                            "$divide": [
                                {"$subtract": ["$end_datetime", "$start_datetime"]},
                                3600000  # Convert to hours
                            ]
                        }
                    }
                }
            }
        ]
        
        result = await db.bookings.aggregate(pipeline).to_list(length=1)
        
        if result:
            stats = result[0]
            del stats["_id"]
            return stats
        else:
            return {
                "total_bookings": 0,
                "confirmed_bookings": 0,
                "cancelled_bookings": 0,
                "total_hours": 0
            }

booking_service = BookingService()