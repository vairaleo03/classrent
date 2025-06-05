import caldav
from icalendar import Calendar, Event
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from ..config import settings

class CalendarService:
    def __init__(self):
        self.caldav_url = settings.caldav_url
        self.username = settings.caldav_username
        self.password = settings.caldav_password
        self.client = None
        
        # Solo prova a connettersi se tutte le credenziali sono presenti e valide
        if self._has_valid_config():
            try:
                self.client = caldav.DAVClient(
                    url=self.caldav_url,
                    username=self.username,
                    password=self.password
                )
                self.principal = self.client.principal()
                self.calendar = self.principal.calendars()[0]  # Usa il primo calendario
                print("✅ Servizio calendario configurato e connesso")
            except Exception as e:
                print(f"⚠️ Servizio calendario non disponibile: {e}")
                self.client = None
        else:
            print("ℹ️ Servizio calendario non configurato (opzionale)")
    
    def _has_valid_config(self) -> bool:
        """Verifica se la configurazione del calendario è valida"""
        return (
            self.caldav_url is not None and
            self.caldav_url != "https://apidata.googleusercontent.com/caldav/v2/classrent2025@gmail.com/events" and  # Esclude placeholder
            self.username is not None and
            self.password is not None and
            all([self.caldav_url, self.username, self.password])
        )
    
    async def add_booking_to_calendar(self, booking_data: Dict[str, Any], user_email: str) -> bool:
        """Aggiunge una prenotazione al calendario dell'utente"""
        if not self.client:
            print("📅 Calendario non configurato - prenotazione non aggiunta al calendario")
            return False
        
        try:
            # Crea evento iCalendar
            cal = Calendar()
            cal.add('prodid', '-//ClassRent//ClassRent 1.0//EN')
            cal.add('version', '2.0')
            
            event = Event()
            event.add('summary', f"Prenotazione: {booking_data['space_name']}")
            event.add('dtstart', booking_data['start_datetime'])
            event.add('dtend', booking_data['end_datetime'])
            event.add('location', booking_data.get('location', ''))
            
            description = f"""
Prenotazione ClassRent
Spazio: {booking_data['space_name']}
Scopo: {booking_data['purpose']}
Materiali: {', '.join(booking_data.get('materials_requested', []))}
Note: {booking_data.get('notes', 'Nessuna nota')}
            """
            event.add('description', description.strip())
            
            # Aggiungi reminder 24h prima
            from icalendar import Alarm
            alarm = Alarm()
            alarm.add('action', 'DISPLAY')
            alarm.add('description', 'Promemoria prenotazione ClassRent')
            alarm.add('trigger', timedelta(hours=-24))
            event.add_component(alarm)
            
            # Aggiungi evento al calendario
            event.add('uid', f"classrent-{booking_data['booking_id']}")
            cal.add_component(event)
            
            # Salva nel calendario CalDAV
            self.calendar.add_event(cal.to_ical())
            
            print(f"✅ Evento aggiunto al calendario: {booking_data['space_name']}")
            return True
            
        except Exception as e:
            print(f"❌ Errore aggiunta evento al calendario: {e}")
            return False
    
    async def update_booking_in_calendar(self, booking_id: str, booking_data: Dict[str, Any]) -> bool:
        """Aggiorna una prenotazione nel calendario"""
        if not self.client:
            return False
        
        try:
            # Cerca l'evento esistente
            events = self.calendar.events()
            for event in events:
                if f"classrent-{booking_id}" in str(event.data):
                    # Rimuovi l'evento esistente
                    event.delete()
                    break
            
            # Aggiungi il nuovo evento aggiornato
            return await self.add_booking_to_calendar(booking_data, "")
            
        except Exception as e:
            print(f"❌ Errore aggiornamento evento calendario: {e}")
            return False
    
    async def remove_booking_from_calendar(self, booking_id: str) -> bool:
        """Rimuove una prenotazione dal calendario"""
        if not self.client:
            return False
        
        try:
            events = self.calendar.events()
            for event in events:
                if f"classrent-{booking_id}" in str(event.data):
                    event.delete()
                    print(f"✅ Evento rimosso dal calendario: {booking_id}")
                    return True
            
            return False
            
        except Exception as e:
            print(f"❌ Errore rimozione evento calendario: {e}")
            return False
    
    async def get_user_calendar_events(self, user_email: str, days_ahead: int = 30) -> list:
        """Recupera gli eventi dell'utente per i prossimi giorni"""
        if not self.client:
            return []
        
        try:
            start_date = datetime.now()
            end_date = start_date + timedelta(days=days_ahead)
            
            events = self.calendar.date_search(start_date, end_date)
            
            calendar_events = []
            for event in events:
                try:
                    cal = Calendar.from_ical(event.data)
                    for component in cal.walk():
                        if component.name == "VEVENT":
                            calendar_events.append({
                                "summary": str(component.get('summary')),
                                "start": component.get('dtstart').dt,
                                "end": component.get('dtend').dt,
                                "description": str(component.get('description', '')),
                                "location": str(component.get('location', ''))
                            })
                except Exception as e:
                    continue
            
            return calendar_events
            
        except Exception as e:
            print(f"❌ Errore recupero eventi calendario: {e}")
            return []
    
    def is_calendar_configured(self) -> bool:
        """Verifica se il servizio calendario è configurato"""
        return self.client is not None

calendar_service = CalendarService()