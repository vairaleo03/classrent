import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from app.config import settings
from app.services.auth_service import get_password_hash

async def complete_reset():
    """Reset completo del database con struttura corretta"""
    print("🗑️  RESET COMPLETO DATABASE CLASSRENT")
    print("⚠️  Questo cancellerà TUTTI i dati esistenti!")
    
    confirm = input("Sei sicuro? Digita 'RESET' per confermare: ")
    if confirm != 'RESET':
        print("❌ Reset annullato")
        return
    
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    
    try:
        print("🗑️  Cancellazione completa database...")
        
        # Cancella tutte le collezioni
        await db.users.delete_many({})
        await db.spaces.delete_many({})
        await db.materials.delete_many({})
        await db.bookings.delete_many({})
        
        print("✅ Database pulito")
        
        # Ricrea utenti con struttura corretta
        print("👤 Creazione utenti...")
        
        users = [
            {
                "email": "admin@classrent.edu",
                "full_name": "Amministratore ClassRent",
                "hashed_password": get_password_hash("admin123"),
                "is_active": True,
                "role": "admin",
                "created_at": datetime.now(timezone.utc)
            },
            {
                "email": "demo@università.edu",
                "full_name": "Utente Demo",
                "hashed_password": get_password_hash("demo123"),
                "is_active": True,
                "role": "student",
                "created_at": datetime.now(timezone.utc)
            },
            {
                "email": "prof@università.edu",
                "full_name": "Professor Demo",
                "hashed_password": get_password_hash("prof123"),
                "is_active": True,
                "role": "professor",
                "created_at": datetime.now(timezone.utc)
            }
        ]
        
        await db.users.insert_many(users)
        print(f"✅ Creati {len(users)} utenti")
        
        # Ricrea materiali
        print("🔧 Creazione materiali...")
        materials = [
            {
                "name": "Proiettore",
                "description": "Proiettore HD per presentazioni",
                "category": "elettronica",
                "quantity": 10,
                "is_available": True,
                "created_at": datetime.now(timezone.utc)
            },
            {
                "name": "PC",
                "description": "Computer desktop",
                "category": "elettronica",
                "quantity": 50,
                "is_available": True,
                "created_at": datetime.now(timezone.utc)
            },
            {
                "name": "Lavagna Interattiva",
                "description": "Lavagna multimediale touch",
                "category": "didattica",
                "quantity": 5,
                "is_available": True,
                "created_at": datetime.now(timezone.utc)
            },
            {
                "name": "Microfono",
                "description": "Sistema audio amplificato",
                "category": "audio",
                "quantity": 15,
                "is_available": True,
                "created_at": datetime.now(timezone.utc)
            }
        ]
        
        await db.materials.insert_many(materials)
        print(f"✅ Creati {len(materials)} materiali")
        
        # Ricrea spazi
        print("🏫 Creazione spazi...")
        spaces = [
            {
                "name": "Aula Magna",
                "type": "aula",
                "capacity": 200,
                "materials": [
                    {"name": "Proiettore", "description": "Proiettore HD", "quantity": 2},
                    {"name": "Microfono", "description": "Sistema audio", "quantity": 4}
                ],
                "location": "Edificio A - Piano Terra",
                "description": "Aula principale per eventi e conferenze",
                "available_hours": {"start_time": "08:00", "end_time": "22:00"},
                "booking_constraints": {
                    "max_duration": 240,
                    "advance_booking_days": 7
                },
                "is_active": True,
                "created_at": datetime.now(timezone.utc)
            },
            {
                "name": "Lab Informatica 1",
                "type": "laboratorio",
                "capacity": 30,
                "materials": [
                    {"name": "PC", "description": "Computer desktop", "quantity": 30},
                    {"name": "Proiettore", "description": "Proiettore HD", "quantity": 1}
                ],
                "location": "Edificio B - Piano 1",
                "description": "Laboratorio con postazioni informatiche",
                "available_hours": {"start_time": "08:00", "end_time": "20:00"},
                "booking_constraints": {
                    "max_duration": 180,
                    "advance_booking_days": 3
                },
                "is_active": True,
                "created_at": datetime.now(timezone.utc)
            },
            {
                "name": "Sala Riunioni Docenti",
                "type": "sala_riunioni",
                "capacity": 15,
                "materials": [
                    {"name": "Lavagna Interattiva", "description": "Lavagna touch", "quantity": 1},
                    {"name": "Microfono", "description": "Sistema audio", "quantity": 1}
                ],
                "location": "Edificio A - Piano 2",
                "description": "Sala per riunioni e videoconferenze",
                "available_hours": {"start_time": "09:00", "end_time": "18:00"},
                "booking_constraints": {
                    "max_duration": 120,
                    "advance_booking_days": 1
                },
                "is_active": True,
                "created_at": datetime.now(timezone.utc)
            }
        ]
        
        await db.spaces.insert_many(spaces)
        print(f"✅ Creati {len(spaces)} spazi")
        
        # Crea indici
        print("📊 Creazione indici...")
        await db.users.create_index("email", unique=True)
        await db.spaces.create_index([("type", 1), ("is_active", 1)])
        await db.materials.create_index("name")
        
        print("✅ Reset completo terminato!")
        print("\n🔐 Credenziali disponibili:")
        print("   Admin: admin@classrent.edu / admin123")
        print("   Demo:  demo@università.edu / demo123")
        print("   Prof:  prof@università.edu / prof123")
        
    except Exception as e:
        print(f"❌ Errore durante reset: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(complete_reset())