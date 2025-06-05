import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime, time
from app.config import settings

async def init_database():
    """Inizializza il database con dati di esempio"""
    client = AsyncIOMotorClient(settings.mongodb_url)
    db = client[settings.database_name]
    
    # Cancella collezioni esistenti
    await db.spaces.delete_many({})
    await db.materials.delete_many({})
    
    # Materiali di esempio
    materials = [
        {"name": "Proiettore", "description": "Proiettore HD per presentazioni"},
        {"name": "PC", "description": "Computer desktop"},
        {"name": "Lavagna Interattiva", "description": "Lavagna multimediale touch"},
        {"name": "Microfono", "description": "Sistema audio amplificato"},
        {"name": "Webcam", "description": "Camera per videoconferenze"},
        {"name": "Schermo Grande", "description": "Monitor 65 pollici"},
    ]
    
    # Spazi di esempio
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
                "max_duration": 240,  # 4 ore
                "advance_booking_days": 7
            },
            "is_active": True
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
                "max_duration": 180,  # 3 ore
                "advance_booking_days": 3
            },
            "is_active": True
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
                "max_duration": 120,  # 2 ore
                "advance_booking_days": 1
            },
            "is_active": True
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
                "max_duration": 180,  # 3 ore
                "advance_booking_days": 2
            },
            "is_active": True
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
                "max_duration": 60,  # 1 ora
                "advance_booking_days": 1
            },
            "is_active": True
        }
    ]
    
    # Inserisci spazi
    await db.spaces.insert_many(spaces)
    
    print("Database inizializzato con successo!")
    print(f"Inseriti {len(spaces)} spazi")
    
    client.close()

if __name__ == "__main__":
    asyncio.run(init_database())