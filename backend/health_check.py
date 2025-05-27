import asyncio
import sys
import os
from motor.motor_asyncio import AsyncIOMotorClient
import aiohttp
from app.config import settings

async def check_mongodb():
    """Verifica connessione MongoDB"""
    try:
        client = AsyncIOMotorClient(settings.mongodb_url)
        await client.admin.command('ping')
        db = client[settings.database_name]
        
        # Conta documenti per verificare che il DB sia inizializzato
        spaces_count = await db.spaces.count_documents({})
        users_count = await db.users.count_documents({})
        
        client.close()
        
        if spaces_count == 0 or users_count == 0:
            return {
                "status": "warning",
                "message": f"Database connesso ma non inizializzato (spazi: {spaces_count}, utenti: {users_count})"
            }
        
        return {
            "status": "ok",
            "message": f"MongoDB OK (spazi: {spaces_count}, utenti: {users_count})"
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Errore MongoDB: {str(e)}"
        }

async def check_backend_api():
    """Verifica che l'API backend risponda"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:8000/health') as response:
                if response.status == 200:
                    return {
                        "status": "ok",
                        "message": "Backend API risponde correttamente"
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Backend API errore HTTP {response.status}"
                    }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Backend API non raggiungibile: {str(e)}"
        }

async def check_frontend():
    """Verifica che il frontend sia raggiungibile"""
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('http://localhost:3000') as response:
                if response.status == 200:
                    return {
                        "status": "ok",
                        "message": "Frontend raggiungibile"
                    }
                else:
                    return {
                        "status": "error",
                        "message": f"Frontend errore HTTP {response.status}"
                    }
    except Exception as e:
        return {
            "status": "error",
            "message": f"Frontend non raggiungibile: {str(e)}"
        }

def check_environment():
    """Verifica variabili d'ambiente critiche"""
    checks = {}
    
    # MongoDB
    if not settings.mongodb_url or settings.mongodb_url == "your-mongodb-url":
        checks["mongodb_url"] = {"status": "error", "message": "MONGODB_URL non configurato"}
    else:
        checks["mongodb_url"] = {"status": "ok", "message": "MONGODB_URL configurato"}
    
    # JWT Secret
    if not settings.secret_key or len(settings.secret_key) < 16:
        checks["jwt_secret"] = {"status": "error", "message": "JWT_SECRET_KEY troppo corto o mancante"}
    else:
        checks["jwt_secret"] = {"status": "ok", "message": "JWT_SECRET_KEY configurato"}
    
    # OpenAI (opzionale)
    if settings.openai_api_key and settings.openai_api_key.startswith("sk-"):
        checks["openai"] = {"status": "ok", "message": "OpenAI API configurato"}
    else:
        checks["openai"] = {"status": "warning", "message": "OpenAI API non configurato (opzionale)"}
    
    # Email (opzionale)
    if settings.email_username and settings.email_password:
        checks["email"] = {"status": "ok", "message": "Email configurato"}
    else:
        checks["email"] = {"status": "warning", "message": "Email non configurato (opzionale)"}
    
    return checks

def print_status(component, result):
    """Stampa lo stato con colori"""
    status_icons = {
        "ok": "✅",
        "warning": "⚠️",
        "error": "❌"
    }
    
    icon = status_icons.get(result["status"], "❓")
    print(f"{icon} {component}: {result['message']}")

async def main():
    """Esegue tutti i controlli di salute"""
    print("🔍 ClassRent Health Check\n")
    
    # 1. Controllo variabili d'ambiente
    print("📋 Controllo Configurazione:")
    env_checks = check_environment()
    for component, result in env_checks.items():
        print_status(component, result)
    
    print()
    
    # 2. Controllo MongoDB
    print("🗄️  Controllo Database:")
    mongo_result = await check_mongodb()
    print_status("MongoDB", mongo_result)
    
    print()
    
    # 3. Controllo Backend API
    print("🔧 Controllo Backend:")
    backend_result = await check_backend_api()
    print_status("Backend API", backend_result)
    
    print()
    
    # 4. Controllo Frontend
    print("🌐 Controllo Frontend:")
    frontend_result = await check_frontend()
    print_status("Frontend", frontend_result)
    
    print()
    
    # Riassunto
    all_results = [mongo_result, backend_result, frontend_result] + list(env_checks.values())
    errors = [r for r in all_results if r["status"] == "error"]
    warnings = [r for r in all_results if r["status"] == "warning"]
    
    if errors:
        print("❌ ERRORI CRITICI TROVATI:")
        for error in errors:
            print(f"   - {error['message']}")
        print("\n🔧 Risolvi gli errori prima di procedere.")
        sys.exit(1)
    elif warnings:
        print("⚠️  AVVISI (funzionalità limitate):")
        for warning in warnings:
            print(f"   - {warning['message']}")
        print("\n🎉 Applicazione funzionante con limitazioni.")
    else:
        print("🎉 TUTTO OK! ClassRent è completamente funzionante.")
    
    print("\n🌐 Link utili:")
    print("   Frontend: http://localhost:3000")
    print("   Backend API: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    print("   Admin: admin@classrent.edu / admin123")
    print("   Demo: demo@università.edu / demo123")

if __name__ == "__main__":
    asyncio.run(main())