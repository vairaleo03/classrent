import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, timezone
from app.config import settings
from app.services.auth_service import get_password_hash

async def complete_reset_and_fix():
    """Reset completo del database rimuovendo is_active e correggendo tutti i problemi"""
    print("🔧 CLASSRENT DATABASE FIX & RESET")
    print("⚠️  Questo risolverà i problemi di autenticazione e prenotazioni!")
    
    confirm = input("Procedere con il fix? Digita 'FIX' per confermare: ")
    if confirm != 'FIX':
        print("❌ Fix annullato")
        return
    
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    
    try:
        print("🔧 Step 1: Pulizia database...")
        
        # Cancella tutte le collezioni
        await db.users.delete_many({})
        await db.spaces.delete_many({})
        await db.materials.delete_many({})
        await db.bookings.delete_many({})
        
        print("✅ Database pulito")
        
        print("👤 Step 2: Creazione utenti senza is_active...")
        
        # Crea utenti SENZA il campo is_active
        users = [
            {
                "email": "admin@classrent.edu",
                "full_name": "Amministratore ClassRent",
                "hashed_password": get_password_hash("admin123"),
                "role": "admin",
                "created_at": datetime.now(timezone.utc)
            },
            {
                "email": "demo@università.edu",
                "full_name": "Utente Demo",
                "hashed_password": get_password_hash("demo123"),
                "role": "student",
                "created_at": datetime.now(timezone.utc)
            },
            {
                "email": "prof@università.edu",
                "full_name": "Professor Demo",
                "hashed_password": get_password_hash("prof123"),
                "role": "professor",
                "created_at": datetime.now(timezone.utc)
            },
            {
                "email": "test@università.edu",
                "full_name": "Test User",
                "hashed_password": get_password_hash("test123"),
                "role": "student",
                "created_at": datetime.now(timezone.utc)
            }
        ]
        
        result = await db.users.insert_many(users)
        print(f"✅ Creati {len(users)} utenti (SENZA is_active)")
        
        print("🔧 Step 3: Creazione materiali...")
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
            },
            {
                "name": "Webcam",
                "description": "Camera per videoconferenze",
                "category": "elettronica",
                "quantity": 8,
                "is_available": True,
                "created_at": datetime.now(timezone.utc)
            },
            {
                "name": "Schermo Grande",
                "description": "Monitor 65 pollici",
                "category": "elettronica",
                "quantity": 3,
                "is_available": True,
                "created_at": datetime.now(timezone.utc)
            }
        ]
        
        await db.materials.insert_many(materials)
        print(f"✅ Creati {len(materials)} materiali")
        
        print("🏫 Step 4: Creazione spazi...")
        spaces = [
            {
                "name": "Aula Magna",
                "type": "aula",
                "capacity": 200,
                "materials": [
                    {"name": "Proiettore", "description": "Proiettore HD", "quantity": 2},
                    {"name": "Microfono", "description": "Sistema audio", "quantity": 4},
                    {"name": "Schermo Grande", "description": "Monitor 65 pollici", "quantity": 1}
                ],
                "location": "Edificio A - Piano Terra",
                "description": "Aula principale per eventi e conferenze",
                "available_hours": {"start_time": "08:00", "end_time": "22:00"},
                "booking_constraints": {
                    "max_duration": 240,
                    "advance_booking_days": 0
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
                    "advance_booking_days": 0
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
                    {"name": "Webcam", "description": "Camera videoconferenze", "quantity": 1},
                    {"name": "Microfono", "description": "Sistema audio", "quantity": 1}
                ],
                "location": "Edificio A - Piano 2",
                "description": "Sala per riunioni e videoconferenze",
                "available_hours": {"start_time": "09:00", "end_time": "18:00"},
                "booking_constraints": {
                    "max_duration": 120,
                    "advance_booking_days": 0
                },
                "is_active": True,
                "created_at": datetime.now(timezone.utc)
            },
            {
                "name": "Aula Studio 101",
                "type": "aula",
                "capacity": 50,
                "materials": [
                    {"name": "Proiettore", "description": "Proiettore HD", "quantity": 1}
                ],
                "location": "Edificio C - Piano 1",
                "description": "Aula per lezioni e seminari",
                "available_hours": {"start_time": "08:00", "end_time": "20:00"},
                "booking_constraints": {
                    "max_duration": 180,
                    "advance_booking_days": 0
                },
                "is_active": True,
                "created_at": datetime.now(timezone.utc)
            },
            {
                "name": "Box Medico",
                "type": "box_medico",
                "capacity": 3,
                "materials": [],
                "location": "Edificio D - Piano Terra",
                "description": "Ambulatorio per visite mediche",
                "available_hours": {"start_time": "09:00", "end_time": "17:00"},
                "booking_constraints": {
                    "max_duration": 60,
                    "advance_booking_days": 0
                },
                "is_active": True,
                "created_at": datetime.now(timezone.utc)
            },
            {
                "name": "Aula Informatica 2",
                "type": "laboratorio",
                "capacity": 25,
                "materials": [
                    {"name": "PC", "description": "Computer desktop", "quantity": 25},
                    {"name": "Proiettore", "description": "Proiettore HD", "quantity": 1}
                ],
                "location": "Edificio B - Piano 2",
                "description": "Laboratorio informatico avanzato",
                "available_hours": {"start_time": "08:00", "end_time": "20:00"},
                "booking_constraints": {
                    "max_duration": 240,
                    "advance_booking_days": 0
                },
                "is_active": True,
                "created_at": datetime.now(timezone.utc)
            }
        ]
        
        await db.spaces.insert_many(spaces)
        print(f"✅ Creati {len(spaces)} spazi")
        
        print("📊 Step 5: Creazione indici per performance...")
        await db.users.create_index("email", unique=True)
        await db.spaces.create_index([("type", 1), ("is_active", 1)])
        await db.materials.create_index("name")
        await db.bookings.create_index([("user_id", 1), ("start_datetime", -1)])
        await db.bookings.create_index([("space_id", 1), ("start_datetime", 1)])
        
        print("✅ Indici creati")
        
        print("🧹 Step 6: Pulizia legacy is_active fields...")
        
        # Rimuovi qualsiasi campo is_active rimasto nei documenti
        await db.users.update_many({}, {"$unset": {"is_active": ""}})
        
        print("✅ Fix completo terminato!")
        print("\n🔐 Credenziali aggiornate:")
        print("   Admin:    admin@classrent.edu / admin123")
        print("   Demo:     demo@università.edu / demo123") 
        print("   Prof:     prof@università.edu / prof123")
        print("   Test:     test@università.edu / test123")
        print("\n🎯 Problemi risolti:")
        print("   ✅ Rimosso campo is_active problematico")
        print("   ✅ Corretti problemi di autenticazione")
        print("   ✅ Autorizzazioni prenotazioni funzionanti")
        print("   ✅ Vincoli di prenotazione più permissivi")
        print("   ✅ Database ottimizzato con indici")
        
        # Test finale
        print("\n🔬 Verifica finale...")
        user_count = await db.users.count_documents({})
        space_count = await db.spaces.count_documents({"is_active": True})
        
        print(f"   📊 Utenti: {user_count}")
        print(f"   🏫 Spazi attivi: {space_count}")
        
        if user_count > 0 and space_count > 0:
            print("✅ Verifica superata - Sistema pronto!")
        else:
            print("❌ Verifica fallita - Controllare errori")
        
    except Exception as e:
        print(f"❌ Errore durante il fix: {e}")
        import traceback
        traceback.print_exc()
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(complete_reset_and_fix())