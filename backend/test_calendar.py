import asyncio
from datetime import datetime, timedelta
from app.services.calendar_service import calendar_service

async def test_calendar():
    try:
        # Test connessione
        is_configured = calendar_service.is_calendar_configured()
        print(f"📅 Calendar configurato: {is_configured}")
        
        if is_configured:
            # Test aggiunta evento
            booking_data = {
                'booking_id': 'test-123',
                'space_name': 'Test Aula',
                'location': 'Test Location',
                'start_datetime': datetime.now() + timedelta(hours=1),
                'end_datetime': datetime.now() + timedelta(hours=3),
                'purpose': 'Test prenotazione ClassRent',
                'materials_requested': ['Proiettore'],
                'notes': 'Test evento calendario'
            }
            
            success = await calendar_service.add_booking_to_calendar(
                booking_data, 
                "leo.vaira1@gmail.com"
            )
            print(f"✅ Evento aggiunto: {success}")
        else:
            print("⚠️ Calendar non configurato")
            
    except Exception as e:
        print(f"❌ Errore calendar: {e}")

if __name__ == "__main__":
    asyncio.run(test_calendar())