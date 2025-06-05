from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from .config import settings

class Database:
    client: Optional[AsyncIOMotorClient] = None

db = Database()

async def get_database():
    """Restituisce l'istanza del database"""
    if db.client is None:
        raise RuntimeError("Database non connesso. Chiama connect_to_mongo() prima.")
    return db.client[settings.database_name]

async def connect_to_mongo():
    """Connette al database MongoDB"""
    try:
        db.client = AsyncIOMotorClient(settings.mongodb_url)
        # Test della connessione
        await db.client.admin.command('ping')
        print(f"✅ Connesso a MongoDB: {settings.database_name}")
    except Exception as e:
        print(f"❌ Errore connessione MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Chiude la connessione al database"""
    if db.client:
        db.client.close()
        print("🔌 Connessione MongoDB chiusa")