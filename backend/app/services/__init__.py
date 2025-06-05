"""
Services package for ClassRent

Contiene tutti i servizi business logic dell'applicazione.
"""

from .auth_service import verify_password, get_password_hash, create_access_token, verify_token
from .booking_service import booking_service
from .email_service import email_service
from .calendar_service import calendar_service

# Nuovo servizio AI Agent (prioritario)
from .openai_agent_service import ai_agent_service

# Servizio AI legacy (fallback)
from .ai_service import ai_service

__all__ = [
    # Auth service
    "verify_password",
    "get_password_hash", 
    "create_access_token",
    "verify_token",
    
    # Service instances
    "booking_service",
    "email_service",
    "calendar_service",
    
    # AI services (nuovo e legacy)
    "ai_agent_service",  # Prioritario
    "ai_service"         # Fallback
]