from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from ..database import get_database
from ..models.booking import Booking, BookingStatus, BookingResponse
from .enhanced_email_service import enhanced_email_service  # AGGIORNATO
from .calendar_service import calendar_service

class BookingService:
    def __init__(self):
        pass
    
    async def create_booking(self, booking_data: Dict, user_id: str) -> Dict:
        """Crea una nuova prenotazione con email personalizzata per l'utente"""
        db = await get_database()
        
        try:
            # Validazione dati di input
            validation_result = await self._validate_booking_data(booking_data)
            if not validation_result["valid"]:
                return {"error": validation_result["error"]}
            
            # Converte stringhe datetime se necessario
            if isinstance(booking_data.get("start_datetime"), str):
                booking_data["start_datetime"] = datetime.fromisoformat(
                    booking_data["start_datetime"].replace('Z', '+00:00')
                )
            if isinstance(booking_data.get("end_datetime"), str):
                booking_data["end_datetime"] = datetime.fromisoformat(
                    booking_data["end_datetime"].replace('Z', '+00:00')
                )
            
            # Verifica che lo spazio esista
            space = await db.spaces.find_one({"_id": ObjectId(booking_data["space_id"])})
            if not space:
                return {"error": "Spazio non trovato"}
            
            # Verifica disponibilità
            if not await self.check_availability(
                booking_data["space_id"], 
                booking_data["start_datetime"], 
                booking_data["end_datetime"]
            ):
                return {"error": "Lo spazio non è disponibile nell'orario richiesto"}
            
            # Verifica vincoli dello spazio
            constraint_check = await self.check_constraints(booking_data, space)
            if not constraint_check["valid"]:
                return {"error": constraint_check["error"]}
            
            # Prepara i dati della prenotazione
            booking = {
                "user_id": user_id,
                "space_id": booking_data["space_id"],
                "start_datetime": booking_data["start_datetime"],
                "end_datetime": booking_data["end_datetime"],
                "purpose": booking_data.get("purpose", "Prenotazione generica"),
                "status": BookingStatus.CONFIRMED,  # Auto-conferma
                "materials_requested": booking_data.get("materials_requested", []),
                "notes": booking_data.get("notes", ""),
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Inserisci nel database
            result = await db.bookings.insert_one(booking)
            booking_id = str(result.inserted_id)
            
            # Recupera informazioni utente
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            if not user:
                return {"error": "Utente non trovato"}
            
            # IMPORTANTE: Invia email PERSONALIZZATA all'utente che ha prenotato
            try:
                email_sent = await enhanced_email_service.send_booking_confirmation(
                    user_email=user["email"],  # Email dell'utente che prenota
                    booking=booking,
                    space=space
                )
                print(f"📧 Email conferma inviata a {user['email']}: {email_sent}")
            except Exception as e:
                print(f"⚠️ Errore invio email (non critico): {e}")
            
            # Operazioni calendario (opzionali)
            try:
                booking_calendar_data = {
                    'booking_id': booking_id,
                    'space_name': space['name'],
                    'location': space['location'],
                    'start_datetime': booking['start_datetime'],
                    'end_datetime': booking['end_datetime'],
                    'purpose': booking['purpose'],
                    'materials_requested': booking['materials_requested'],
                    'notes': booking['notes']
                }
                
                # Aggiungi al calendario se configurato
                calendar_added = await calendar_service.add_booking_to_calendar(
                    booking_calendar_data, 
                    user["email"]
                )
                
                # Programma reminder automatico
                await self._schedule_automatic_reminder(booking_id, user["email"], booking['start_datetime'])
                
            except Exception as e:
                print(f"⚠️ Errore operazioni calendar (non critico): {e}")
            
            return {
                "booking_id": booking_id, 
                "status": "created",
                "message": f"Prenotazione creata con successo! Email di conferma inviata a {user['email']}"
            }
            
        except Exception as e:
            print(f"❌ Errore nella creazione prenotazione: {e}")
            return {"error": f"Errore interno: {str(e)}"}
    
    async def _schedule_automatic_reminder(self, booking_id: str, user_email: str, start_datetime: datetime):
        """Programma reminder automatico 24h prima"""
        try:
            reminder_time = start_datetime - timedelta(hours=24)
            
            # Solo se il reminder è nel futuro
            if reminder_time > datetime.utcnow():
                from apscheduler.schedulers.asyncio import AsyncIOScheduler
                from apscheduler.jobstores.memory import MemoryJobStore
                
                jobstores = {
                    'default': MemoryJobStore(),
                }
                
                scheduler = AsyncIOScheduler(jobstores=jobstores)
                
                # Aggiungi job per reminder
                scheduler.add_job(
                    func=enhanced_email_service.send_booking_reminder,
                    trigger='date',
                    run_date=reminder_time,
                    args=[user_email, booking_id],
                    id=f"reminder_{booking_id}",
                    replace_existing=True
                )
                
                if not scheduler.running:
                    scheduler.start()
                
                print(f"⏰ Reminder programmato per {reminder_time.strftime('%d/%m/%Y %H:%M')} - {user_email}")
            else:
                print(f"⚠️ Reminder non programmato: booking troppo vicino ({start_datetime})")
                
        except Exception as e:
            print(f"⚠️ Errore programmazione reminder (non critico): {e}")
    
    async def cancel_booking(self, booking_id: str, user_id: str, reason: str = "") -> Dict:
        """Cancella prenotazione con notifica email personalizzata"""
        db = await get_database()
        
        try:
            # Recupera prenotazione prima di cancellarla
            booking = await db.bookings.find_one({
                "_id": ObjectId(booking_id),
                "user_id": user_id
            })
            
            if not booking:
                return {"error": "Prenotazione non trovata"}
            
            # Recupera dettagli spazio e utente
            space = await db.spaces.find_one({"_id": ObjectId(booking["space_id"])})
            user = await db.users.find_one({"_id": ObjectId(user_id)})
            
            # Aggiorna stato nel database
            result = await db.bookings.update_one(
                {
                    "_id": ObjectId(booking_id),
                    "user_id": user_id
                },
                {
                    "$set": {
                        "status": BookingStatus.CANCELLED,
                        "updated_at": datetime.utcnow(),
                        "cancellation_reason": reason
                    }
                }
            )
            
            if result.modified_count == 0:
                return {"error": "Impossibile cancellare la prenotazione"}
            
            # Invia email di notifica cancellazione all'utente
            if user and space:
                try:
                    await enhanced_email_service.send_booking_cancellation(
                        user_email=user["email"],
                        booking=booking,
                        space=space,
                        reason=reason
                    )
                    print(f"📧 Email cancellazione inviata a {user['email']}")
                except Exception as e:
                    print(f"⚠️ Errore invio email cancellazione: {e}")
            
            # Rimuovi dal calendario se configurato
            try:
                await calendar_service.remove_booking_from_calendar(booking_id)
            except Exception as e:
                print(f"⚠️ Errore rimozione calendario: {e}")
            
            return {
                "status": "cancelled", 
                "message": f"Prenotazione cancellata. Notifica inviata a {user['email'] if user else 'utente'}"
            }
            
        except Exception as e:
            print(f"❌ Errore cancellazione prenotazione: {e}")
            return {"error": f"Errore interno: {str(e)}"}
    
    async def update_booking(self, booking_id: str, user_id: str, update_data: Dict) -> Dict:
        """Aggiorna prenotazione con notifica email se necessario"""
        db = await get_database()
        
        try:
            # Verifica proprietario
            booking = await db.bookings.find_one({
                "_id": ObjectId(booking_id),
                "user_id": user_id
            })
            
            if not booking:
                return {"error": "Prenotazione non trovata"}
            
            # Verifica se può essere modificata
            if booking["start_datetime"] <= datetime.utcnow():
                return {"error": "Non è possibile modificare prenotazioni già iniziate"}
            
            # Se vengono modificati orari importanti, verifica disponibilità
            if "start_datetime" in update_data or "end_datetime" in update_data:
                new_start = update_data.get("start_datetime", booking["start_datetime"])
                new_end = update_data.get("end_datetime", booking["end_datetime"])
                
                # Converte stringhe se necessario
                if isinstance(new_start, str):
                    new_start = datetime.fromisoformat(new_start.replace('Z', '+00:00'))
                if isinstance(new_end, str):
                    new_end = datetime.fromisoformat(new_end.replace('Z', '+00:00'))
                
                # Verifica disponibilità escludendo la prenotazione corrente
                overlapping = await db.bookings.find_one({
                    "_id": {"$ne": ObjectId(booking_id)},
                    "space_id": booking["space_id"],
                    "status": {"$in": [BookingStatus.PENDING, BookingStatus.CONFIRMED]},
                    "$and": [
                        {"start_datetime": {"$lt": new_end}},
                        {"end_datetime": {"$gt": new_start}}
                    ]
                })
                
                if overlapping:
                    return {"error": "Lo spazio non è disponibile nei nuovi orari"}
            
            # Aggiorna prenotazione
            update_data["updated_at"] = datetime.utcnow()
            
            await db.bookings.update_one(
                {"_id": ObjectId(booking_id)},
                {"$set": update_data}
            )
            
            # Se ci sono stati cambiamenti significativi, invia email di notifica
            significant_changes = any(key in update_data for key in ['start_datetime', 'end_datetime', 'space_id'])
            
            if significant_changes:
                try:
                    user = await db.users.find_one({"_id": ObjectId(user_id)})
                    space = await db.spaces.find_one({"_id": ObjectId(booking["space_id"])})
                    
                    if user and space:
                        # Invia email di notifica modifiche
                        updated_booking = {**booking, **update_data}
                        await enhanced_email_service.send_booking_confirmation(
                            user_email=user["email"],
                            booking=updated_booking,
                            space=space
                        )
                        print(f"📧 Email aggiornamento inviata a {user['email']}")
                        
                except Exception as e:
                    print(f"⚠️ Errore invio email aggiornamento: {e}")
            
            return {"status": "updated", "message": "Prenotazione aggiornata con successo"}
            
        except Exception as e:
            print(f"❌ Errore aggiornamento prenotazione: {e}")
            return {"error": f"Errore interno: {str(e)}"}
    
    # ... [resto dei metodi rimangono uguali] ...
    
    async def _validate_booking_data(self, booking_data: Dict) -> Dict:
        """Valida i dati della prenotazione"""
        
        # Campi obbligatori
        required_fields = ["space_id", "start_datetime", "end_datetime"]
        for field in required_fields:
            if field not in booking_data or not booking_data[field]:
                return {"valid": False, "error": f"Campo {field} obbligatorio"}
        
        # Validazione ObjectId
        try:
            ObjectId(booking_data["space_id"])
        except:
            return {"valid": False, "error": "ID spazio non valido"}
        
        # Validazione orari
        try:
            start_dt = booking_data["start_datetime"]
            end_dt = booking_data["end_datetime"]
            
            if isinstance(start_dt, str):
                start_dt = datetime.fromisoformat(start_dt.replace('Z', '+00:00'))
            if isinstance(end_dt, str):
                end_dt = datetime.fromisoformat(end_dt.replace('Z', '+00:00'))
            
            if end_dt <= start_dt:
                return {"valid": False, "error": "L'ora di fine deve essere dopo l'ora di inizio"}
            
            if start_dt < datetime.utcnow():
                return {"valid": False, "error": "Non puoi prenotare nel passato"}
            
            # Durata massima 8 ore
            duration = (end_dt - start_dt).total_seconds() / 3600
            if duration > 8:
                return {"valid": False, "error": "La durata massima è 8 ore"}
            
            # Durata minima 30 minuti
            if duration < 0.5:
                return {"valid": False, "error": "La durata minima è 30 minuti"}
                
        except Exception as e:
            return {"valid": False, "error": f"Formato data/ora non valido: {str(e)}"}
        
        return {"valid": True}
    
    async def check_availability(self, space_id: str, start_time: datetime, end_time: datetime) -> bool:
        """Verifica se lo spazio è disponibile"""
        db = await get_database()
        
        try:
            overlapping = await db.bookings.find_one({
                "space_id": space_id,
                "status": {"$in": [BookingStatus.PENDING, BookingStatus.CONFIRMED]},
                "$and": [
                    {"start_datetime": {"$lt": end_time}},
                    {"end_datetime": {"$gt": start_time}}
                ]
            })
            
            return overlapping is None
            
        except Exception as e:
            print(f"❌ Errore verifica disponibilità: {e}")
            return False
    
    async def check_constraints(self, booking_data: Dict, space: Dict) -> Dict:
        """Verifica i vincoli di prenotazione dello spazio"""
        
        try:
            constraints = space.get("booking_constraints", {})
            start_dt = booking_data["start_datetime"]
            end_dt = booking_data["end_datetime"]
            
            if isinstance(start_dt, str):
                start_dt = datetime.fromisoformat(start_dt.replace('Z', '+00:00'))
            if isinstance(end_dt, str):
                end_dt = datetime.fromisoformat(end_dt.replace('Z', '+00:00'))
            
            # Durata massima
            if "max_duration" in constraints:
                duration_minutes = (end_dt - start_dt).total_seconds() / 60
                if duration_minutes > constraints["max_duration"]:
                    return {
                        "valid": False, 
                        "error": f"Durata massima consentita: {constraints['max_duration']} minuti"
                    }
            
            # Anticipo minimo prenotazione
            if "advance_booking_days" in constraints:
                min_advance = datetime.utcnow() + timedelta(days=constraints["advance_booking_days"])
                if start_dt < min_advance:
                    return {
                        "valid": False, 
                        "error": f"Prenotazione consentita con almeno {constraints['advance_booking_days']} giorni di anticipo"
                    }
            
            # Orari disponibili
            available_hours = space.get("available_hours", {})
            if available_hours:
                start_hour = start_dt.strftime("%H:%M")
                end_hour = end_dt.strftime("%H:%M")
                
                space_start = available_hours.get("start_time", "00:00")
                space_end = available_hours.get("end_time", "23:59")
                
                if start_hour < space_start or end_hour > space_end:
                    return {
                        "valid": False, 
                        "error": f"Spazio disponibile solo dalle {space_start} alle {space_end}"
                    }
            
            return {"valid": True}
            
        except Exception as e:
            print(f"❌ Errore verifica vincoli: {e}")
            return {"valid": False, "error": "Errore nella verifica dei vincoli"}
    
    async def get_user_bookings(self, user_id: str) -> List[BookingResponse]:
        """Recupera le prenotazioni dell'utente"""
        db = await get_database()
        
        bookings = []
        try:
            async for booking in db.bookings.find({"user_id": user_id}).sort("start_datetime", -1):
                space = await db.spaces.find_one({"_id": ObjectId(booking["space_id"])})
                
                booking_response = BookingResponse(
                    id=str(booking["_id"]),
                    user_id=booking["user_id"],
                    space_id=booking["space_id"],
                    space_name=space["name"] if space else "Spazio eliminato",
                    start_datetime=booking["start_datetime"],
                    end_datetime=booking["end_datetime"],
                    purpose=booking["purpose"],
                    status=booking["status"],
                    materials_requested=booking.get("materials_requested", []),
                    notes=booking.get("notes", ""),
                    created_at=booking["created_at"]
                )
                bookings.append(booking_response)
                
        except Exception as e:
            print(f"❌ Errore recupero prenotazioni: {e}")
        
        return bookings

booking_service = BookingService()