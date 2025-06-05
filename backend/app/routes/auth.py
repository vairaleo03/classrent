from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from bson import ObjectId
from ..database import get_database
from ..models.user import UserCreate, UserLogin, UserResponse
from ..services.auth_service import (
    get_password_hash, 
    verify_password, 
    create_access_token,
    verify_token
)

router = APIRouter()
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    email = verify_token(token)
    
    db = await get_database()
    user = await db.users.find_one({"email": email})
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user

@router.post("/register", response_model=dict)
async def register(user: UserCreate):
    db = await get_database()
    
    # Verifica se l'utente esiste già
    existing_user = await db.users.find_one({"email": user.email})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Crea nuovo utente - SEMPRE ATTIVO
    hashed_password = get_password_hash(user.password)
    user_data = {
        "email": user.email,
        "full_name": user.full_name,
        "hashed_password": hashed_password,
        "role": user.role,
        "created_at": user.created_at if hasattr(user, 'created_at') else None
    }
    
    result = await db.users.insert_one(user_data)
    
    # Crea token
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(result.inserted_id)
    }

@router.post("/login", response_model=dict)
async def login(user: UserLogin):
    db = await get_database()
    
    # Verifica utente
    db_user = await db.users.find_one({"email": user.email})
    if not db_user or not verify_password(user.password, db_user["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )
    
    # Crea token
    access_token = create_access_token(data={"sub": user.email})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user_id": str(db_user["_id"])
    }

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    return UserResponse(
        id=str(current_user["_id"]),
        email=current_user["email"],
        full_name=current_user["full_name"],
        is_active=True,  # SEMPRE ATTIVO
        role=current_user.get("role", "student")  # Default role se mancante
    )