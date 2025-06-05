"""
ClassRent Backend Application

Sistema di prenotazione aule universitarie con AI integrata.
"""

__version__ = "1.0.0"
__author__ = "ClassRent Team"
__description__ = "Sistema di prenotazione aule universitarie"

# Imports principali per facilitare l'accesso
from .main import app
from .config import settings
from .database import get_database

__all__ = ["app", "settings", "get_database"]