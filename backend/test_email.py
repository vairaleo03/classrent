import asyncio
from app.services.email_service import email_service

async def test_email():
    try:
        success = await email_service.send_email(
            to_email="classrent2025@gmail.com",
            subject="Test ClassRent",
            body="<h2>Email funziona!</h2><p>Configurazione Gmail completata.</p>"
        )
        print(f"✅ Email inviata: {success}")
    except Exception as e:
        print(f"❌ Errore email: {e}")

if __name__ == "__main__":
    asyncio.run(test_email())