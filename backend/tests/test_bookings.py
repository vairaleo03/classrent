import pytest
from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

@pytest.fixture
def auth_headers():
    """Fixture per headers di autenticazione"""
    user_data = {
        "email": "test_booking@university.edu",
        "full_name": "Test Booking User",
        "password": "testpassword123",
        "role": "student"
    }
    
    response = client.post("/auth/register", json=user_data)
    token = response.json()["access_token"]
    
    return {"Authorization": f"Bearer {token}"}

def test_create_booking(auth_headers):
    """Test creazione prenotazione"""
    # Prima ottieni un spazio disponibile
    spaces_response = client.get("/spaces/", headers=auth_headers)
    spaces = spaces_response.json()
    
    if not spaces:
        pytest.skip("Nessuno spazio disponibile per il test")
    
    space_id = spaces[0]["id"]
    
    # Crea prenotazione
    booking_data = {
        "space_id": space_id,
        "start_datetime": (datetime.now() + timedelta(days=1)).isoformat(),
        "end_datetime": (datetime.now() + timedelta(days=1, hours=2)).isoformat(),
        "purpose": "Test booking",
        "materials_requested": ["Proiettore"],
        "notes": "Test notes"
    }
    
    response = client.post("/bookings/", json=booking_data, headers=auth_headers)
    assert response.status_code == 200
    
    data = response.json()
    assert "booking_id" in data
    assert data["status"] == "created"

def test_get_bookings(auth_headers):
    """Test recupero prenotazioni utente"""
    response = client.get("/bookings/", headers=auth_headers)
    assert response.status_code == 200
    
    bookings = response.json()
    assert isinstance(bookings, list)

def test_unauthorized_access():
    """Test accesso non autorizzato"""
    response = client.get("/bookings/")
    assert response.status_code == 401