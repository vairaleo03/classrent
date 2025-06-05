from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from bson import ObjectId
from ..database import get_database

class DatabaseCalendarService:
    """
    Sistema calendario che usa SOLO il database MongoDB
    Non richiede API esterne - tutto memorizzato in ClassRent
    """
    
    def __init__(self):
        self.is_configured = True  # Sempre configurato perché usa solo DB
        print("✅ Sistema Calendario Database configurato")
    
    async def add_booking_to_calendar(self, booking_data: Dict[str, Any], user_email: str = None) -> bool:
        """
        Aggiunge prenotazione al calendario database
        Crea record calendario collegato alla prenotazione
        """
        try:
            db = await get_database()
            
            # Crea evento calendario nel database
            calendar_event = {
                "booking_id": booking_data.get('booking_id'),
                "space_id": booking_data.get('space_id'),
                "space_name": booking_data.get('space_name'),
                "location": booking_data.get('location'),
                "start_datetime": booking_data.get('start_datetime'),
                "end_datetime": booking_data.get('end_datetime'),
                "purpose": booking_data.get('purpose'),
                "materials_requested": booking_data.get('materials_requested', []),
                "notes": booking_data.get('notes', ''),
                "created_by_email": user_email,
                "event_type": "booking",
                "status": "active",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            # Inserisci evento nel database
            result = await db.calendar_events.insert_one(calendar_event)
            
            print(f"✅ Evento calendario aggiunto al database: {booking_data.get('space_name')}")
            return True
            
        except Exception as e:
            print(f"❌ Errore aggiunta evento calendario DB: {e}")
            return False
    
    async def update_booking_in_calendar(self, booking_id: str, booking_data: Dict[str, Any]) -> bool:
        """
        Aggiorna evento calendario nel database
        """
        try:
            db = await get_database()
            
            # Aggiorna evento esistente
            update_data = {
                "space_name": booking_data.get('space_name'),
                "location": booking_data.get('location'),
                "start_datetime": booking_data.get('start_datetime'),
                "end_datetime": booking_data.get('end_datetime'),
                "purpose": booking_data.get('purpose'),
                "materials_requested": booking_data.get('materials_requested', []),
                "notes": booking_data.get('notes', ''),
                "updated_at": datetime.utcnow()
            }
            
            result = await db.calendar_events.update_one(
                {"booking_id": booking_id},
                {"$set": update_data}
            )
            
            if result.modified_count > 0:
                print(f"✅ Evento calendario aggiornato: {booking_id}")
                return True
            else:
                print(f"⚠️ Nessun evento calendario trovato per: {booking_id}")
                return False
                
        except Exception as e:
            print(f"❌ Errore aggiornamento evento calendario: {e}")
            return False
    
    async def remove_booking_from_calendar(self, booking_id: str) -> bool:
        """
        Rimuove/disattiva evento calendario dal database
        """
        try:
            db = await get_database()
            
            # Marca come cancellato invece di eliminare (per cronologia)
            result = await db.calendar_events.update_one(
                {"booking_id": booking_id},
                {
                    "$set": {
                        "status": "cancelled",
                        "updated_at": datetime.utcnow()
                    }
                }
            )
            
            if result.modified_count > 0:
                print(f"✅ Evento calendario rimosso: {booking_id}")
                return True
            else:
                print(f"⚠️ Nessun evento calendario trovato per rimozione: {booking_id}")
                return False
                
        except Exception as e:
            print(f"❌ Errore rimozione evento calendario: {e}")
            return False
    
    async def get_calendar_events(self, start_date: datetime, end_date: datetime, space_id: str = None) -> List[Dict]:
        """
        Recupera eventi calendario dal database per periodo
        """
        try:
            db = await get_database()
            
            # Costruisci query
            filter_query = {
                "start_datetime": {"$gte": start_date, "$lt": end_date},
                "status": "active"
            }
            
            if space_id:
                filter_query["space_id"] = space_id
            
            # Recupera eventi
            events = []
            async for event in db.calendar_events.find(filter_query).sort("start_datetime", 1):
                events.append({
                    "id": str(event["_id"]),
                    "booking_id": event.get("booking_id"),
                    "space_id": event.get("space_id"),
                    "space_name": event.get("space_name"),
                    "location": event.get("location"),
                    "start_datetime": event.get("start_datetime"),
                    "end_datetime": event.get("end_datetime"),
                    "purpose": event.get("purpose"),
                    "materials_requested": event.get("materials_requested", []),
                    "notes": event.get("notes", ""),
                    "created_by_email": event.get("created_by_email"),
                    "event_type": event.get("event_type", "booking")
                })
            
            return events
            
        except Exception as e:
            print(f"❌ Errore recupero eventi calendario: {e}")
            return []
    
    async def get_space_availability_calendar(self, space_id: str, date: datetime) -> Dict[str, Any]:
        """
        Verifica disponibilità spazio per data specifica usando calendario database
        """
        try:
            db = await get_database()
            
            # Inizio e fine giornata
            start_of_day = datetime.combine(date.date(), datetime.min.time())
            end_of_day = datetime.combine(date.date(), datetime.max.time())
            
            # Recupera eventi per la giornata
            events = await self.get_calendar_events(start_of_day, end_of_day, space_id)
            
            # Recupera informazioni spazio
            space = await db.spaces.find_one({"_id": ObjectId(space_id)})
            if not space:
                return {"error": "Spazio non trovato"}
            
            # Genera slot orari
            available_hours = space.get("available_hours", {"start_time": "08:00", "end_time": "20:00"})
            start_hour = int(available_hours["start_time"].split(":")[0])
            end_hour = int(available_hours["end_time"].split(":")[0])
            
            time_slots = []
            for hour in range(start_hour, end_hour):
                slot_start = datetime.combine(date.date(), datetime.min.time().replace(hour=hour))
                slot_end = datetime.combine(date.date(), datetime.min.time().replace(hour=hour + 1))
                
                # Verifica se slot è occupato
                is_occupied = any(
                    event["start_datetime"] <= slot_start < event["end_datetime"] or
                    event["start_datetime"] < slot_end <= event["end_datetime"]
                    for event in events
                )
                
                # Trova evento che occupa lo slot
                occupying_event = None
                if is_occupied:
                    for event in events:
                        if (event["start_datetime"] <= slot_start < event["end_datetime"] or
                            event["start_datetime"] < slot_end <= event["end_datetime"]):
                            occupying_event = event
                            break
                
                time_slots.append({
                    "start_time": slot_start.strftime("%H:%M"),
                    "end_time": slot_end.strftime("%H:%M"),
                    "available": not is_occupied,
                    "event": occupying_event
                })
            
            return {
                "space_id": space_id,
                "space_name": space["name"],
                "date": date.strftime("%Y-%m-%d"),
                "time_slots": time_slots,
                "events": events,
                "available_hours": available_hours
            }
            
        except Exception as e:
            print(f"❌ Errore verifica disponibilità calendario: {e}")
            return {"error": str(e)}
    
    async def add_system_event(self, title: str, description: str, start_datetime: datetime, 
                              end_datetime: datetime, event_type: str = "system") -> bool:
        """
        Aggiunge eventi di sistema (manutenzioni, chiusure, etc.)
        """
        try:
            db = await get_database()
            
            system_event = {
                "booking_id": None,
                "space_id": None,
                "space_name": title,
                "location": "Sistema",
                "start_datetime": start_datetime,
                "end_datetime": end_datetime,
                "purpose": description,
                "materials_requested": [],
                "notes": "",
                "created_by_email": "sistema@classrent.edu",
                "event_type": event_type,
                "status": "active",
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow()
            }
            
            await db.calendar_events.insert_one(system_event)
            print(f"✅ Evento sistema aggiunto: {title}")
            return True
            
        except Exception as e:
            print(f"❌ Errore aggiunta evento sistema: {e}")
            return False
    
    def is_calendar_configured(self) -> bool:
        """Calendario database è sempre configurato"""
        return True

# Istanza globale del servizio
database_calendar_service = DatabaseCalendarService()