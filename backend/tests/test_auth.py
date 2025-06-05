import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_register_user():
    """Test registrazione nuovo utente"""
    user_data = {
        "email": "test@university.edu",
        "full_name": "Test User",
        "password": "testpassword123",
        "role": "student"
    }
    
    response = client.post("/auth/register", json=user_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_user():
    """Test login utente esistente"""
    # Prima registra un utente
    user_data = {
        "email": "test_login@university.edu",
        "full_name": "Test Login User",
        "password": "testpassword123",
        "role": "student"
    }
    client.post("/auth/register", json=user_data)
    
    # Poi prova il login
    login_data = {
        "email": "test_login@university.edu",
        "password": "testpassword123"
    }
    
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 200
    
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_invalid_login():
    """Test login con credenziali non valide"""
    login_data = {
        "email": "nonexistent@university.edu",
        "password": "wrongpassword"
    }
    
    response = client.post("/auth/login", json=login_data)
    assert response.status_code == 401

def test_get_current_user():
    """Test recupero informazioni utente corrente"""
    # Registra e ottieni token
    user_data = {
        "email": "test_current@university.edu",
        "full_name": "Test Current User",
        "password": "testpassword123",
        "role": "professor"
    }
    
    register_response = client.post("/auth/register", json=user_data)
    token = register_response.json()["access_token"]
    
    # Usa token per ottenere info utente
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/auth/me", headers=headers)
    
    assert response.status_code == 200
    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["full_name"] == user_data["full_name"]
    assert data["role"] == user_data["role"]