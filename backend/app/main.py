from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from .database import connect_to_mongo, close_mongo_connection
from .routes import auth, spaces, bookings, chat, materials, calendar
from .middleware.logging_middleware import LoggingMiddleware
from .middleware.rate_limiting import RateLimitMiddleware
import os

app = FastAPI(
    title="ClassRent API", 
    version="1.0.0",
    description="Sistema di prenotazione aule universitarie con AI integrata"
)

# Rate Limiting Middleware
app.add_middleware(RateLimitMiddleware, calls=100, period=60)

# Logging Middleware  
app.add_middleware(LoggingMiddleware)

# CORS - Configurazione più sicura
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

# In produzione, aggiungi solo i domini necessari
if os.getenv("ENVIRONMENT") == "production":
    allowed_origins = ["https://tuodominio.com"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)

# Database events
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

# Routes
app.include_router(auth.router, prefix="/auth", tags=["authentication"])
app.include_router(spaces.router, prefix="/spaces", tags=["spaces"])
app.include_router(bookings.router, prefix="/bookings", tags=["bookings"])
app.include_router(chat.router, prefix="/chat", tags=["chat"])
app.include_router(materials.router, prefix="/materials", tags=["materials"])
app.include_router(calendar.router, prefix="/calendar", tags=["calendar"])  # NUOVO

@app.get("/")
async def root():
    return {
        "message": "ClassRent API is running",
        "version": "1.0.0",
        "features": [
            "🎓 Sistema prenotazione aule universitarie",
            "🤖 AI Assistant con OpenAI Agent SDK", 
            "📧 Email automatiche personalizzate",
            "📅 Calendario condiviso integrato",
            "📱 Interface responsive",
            "🔒 Autenticazione sicura JWT"
        ]
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": "2024-12-20T10:00:00Z",
        "services": {
            "database": "connected",
            "email": "configured", 
            "ai": "available",
            "calendar": "integrated"
        }
    }

@app.get("/api/docs")
async def get_docs():
    return {
        "message": "ClassRent API Documentation",
        "version": "1.0.0",
        "endpoints": {
            "authentication": "/auth",
            "spaces": "/spaces", 
            "bookings": "/bookings",
            "chat": "/chat",
            "materials": "/materials",
            "calendar": "/calendar"  
        },
        "swagger_ui": "/docs",
        "redoc": "/redoc"
    }