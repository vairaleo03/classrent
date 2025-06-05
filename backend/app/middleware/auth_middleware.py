from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..services.auth_service import verify_token
from ..database import get_database
from typing import Optional

security = HTTPBearer()

async def get_current_user_optional(request: Request) -> Optional[dict]:
    """
    Middleware per ottenere l'utente corrente senza forzare l'autenticazione
    SENZA controllo is_active (tutti gli utenti sono sempre attivi)
    """
    try:
        authorization: str = request.headers.get("Authorization")
        if not authorization:
            return None
            
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            return None
            
        email = verify_token(token)
        db = await get_database()
        user = await db.users.find_one({"email": email})
        
        # Ritorna l'utente se esiste, senza controllo is_active
        return user
        
    except Exception as e:
        print(f"⚠️ Errore in auth middleware (non critico): {e}")
        return None

async def get_current_user_required(request: Request) -> dict:
    """
    Middleware per ottenere l'utente corrente CON autenticazione obbligatoria
    SENZA controllo is_active (tutti gli utenti sono sempre attivi)
    """
    try:
        authorization: str = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token di autorizzazione mancante"
            )
            
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Schema di autorizzazione non valido"
            )
            
        email = verify_token(token)
        db = await get_database()
        user = await db.users.find_one({"email": email})
        
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Utente non trovato"
            )
        
        # Ritorna l'utente senza controllo is_active
        return user
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        print(f"❌ Errore in auth middleware: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Errore nella validazione del token"
        )