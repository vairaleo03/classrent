from fastapi import HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from ..services.auth_service import verify_token
from ..database import get_database
from typing import Optional

security = HTTPBearer()

async def get_current_user_optional(request: Request) -> Optional[dict]:
    """
    Middleware per ottenere l'utente corrente senza forzare l'autenticazione
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
        return user
    except:
        return None