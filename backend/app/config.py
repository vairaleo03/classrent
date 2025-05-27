from pydantic_settings import BaseSettings
from typing import Optional
import secrets

class Settings(BaseSettings):
    # Database
    mongodb_url: str
    database_name: str = "classrent"
    
    # JWT 
    secret_key: str = secrets.token_urlsafe(32)  # Auto-genera se non fornito
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # OpenAI - Default None se non configurato
    openai_api_key: Optional[str] = None
    
    # Email - Optional
    smtp_server: str = "smtp.gmail.com"
    smtp_port: int = 587
    email_username: Optional[str] = None
    email_password: Optional[str] = None
    
    # Calendar - Optional
    caldav_url: Optional[str] = None
    caldav_username: Optional[str] = None
    caldav_password: Optional[str] = None
    
    # Sicurezza
    environment: str = "development"
    debug: bool = True
    
    model_config = {
        "env_file": ".env",
        "case_sensitive": False,
        "extra": "ignore"
    }
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        
        # Validazioni di sicurezza
        if not self.mongodb_url:
            raise ValueError("MONGODB_URL è richiesto")
            
        if self.environment == "production" and self.debug:
            self.debug = False
            
        if self.environment == "production" and len(self.secret_key) < 32:
            raise ValueError("SECRET_KEY deve essere almeno 32 caratteri in produzione")

settings = Settings()