from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from ..services.openai_agent_service import ai_agent_service
from ..services.booking_service import booking_service
from ..database import get_database
from .auth import get_current_user

router = APIRouter()

class ChatMessage(BaseModel):
    message: str
    thread_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = {}

class ChatResponse(BaseModel):
    response: str
    action: str = "info"  # info, booking_suggestion, todo_list, booking_proposal
    data: Dict[str, Any] = {}
    thread_id: Optional[str] = None

@router.post("/", response_model=ChatResponse)
async def chat_with_ai(
    chat_message: ChatMessage,
    current_user: dict = Depends(get_current_user)
):
    """Chat con AI Agent per prenotazioni in linguaggio naturale"""
    
    try:
        # Prepara il contesto per l'AI
        context = {
            "user_id": str(current_user["_id"]),
            "user_name": current_user["full_name"],
            "user_role": current_user.get("role", "student"),
            **chat_message.context
        }
        
        # Processa il messaggio tramite l'AI Agent
        ai_response = await ai_agent_service.process_user_message(
            message=chat_message.message,
            user_id=str(current_user["_id"]),
            context=context
        )
        
        # Gestisci le azioni speciali che richiedono dati aggiuntivi
        if ai_response.get("action") == "ai_response":
            # Controlla se nella risposta ci sono proposte di prenotazione
            response_data = ai_response.get("data", {})
            
            if "proposal" in str(ai_response.get("response", "")):
                ai_response["action"] = "booking_proposal"
        
        # Aggiungi dati del database se necessario
        await _enrich_response_data(ai_response, current_user)
        
        return ChatResponse(
            response=ai_response.get("response", "Mi dispiace, non ho capito la tua richiesta."),
            action=ai_response.get("action", "info"),
            data=ai_response.get("data", {}),
            thread_id=ai_response.get("thread_id")
        )
        
    except Exception as e:
        print(f"❌ Errore nel chat AI: {e}")
        return ChatResponse(
            response="Mi dispiace, si è verificato un errore. Riprova più tardi.",
            action="error",
            data={"error": str(e)}
        )

async def _enrich_response_data(ai_response: Dict, current_user: dict):
    """Arricchisce la risposta dell'AI con dati aggiuntivi dal database"""
    
    action = ai_response.get("action")
    data = ai_response.get("data", {})
    
    if action == "booking_suggestion" or "spaces" in data:
        # Aggiungi informazioni dettagliate sugli spazi
        db = await get_database()
        if "spaces" in data:
            for space in data["spaces"]:
                # Verifica disponibilità in tempo reale se necessario
                space["available_now"] = True  # Placeholder
    
    elif action == "booking_proposal":
        # Verifica che la proposta sia valida
        if "proposal" in data:
            proposal = data["proposal"]
            # Valida disponibilità dello spazio
            # Placeholder per validazione
            data["validation"] = {"valid": True, "message": "Spazio disponibile"}
    
    elif action == "todo_list":
        # Aggiungi suggerimenti personalizzati basati sul ruolo
        if current_user.get("role") == "professor":
            if "checklist" in data:
                data["checklist"].extend([
                    "Verificare presenza assistenti",
                    "Preparare registro presenze",
                    "Controllare sistema di valutazione"
                ])

@router.get("/spaces", response_model=List[Dict])
async def get_available_spaces():
    """Recupera tutti gli spazi disponibili per l'AI"""
    db = await get_database()
    
    spaces = []
    async for space in db.spaces.find({"is_active": True}):
        spaces.append({
            "id": str(space["_id"]),
            "name": space["name"],
            "type": space["type"],
            "capacity": space["capacity"],
            "materials": space.get("materials", []),
            "location": space["location"],
            "description": space.get("description", ""),
            "available_hours": space.get("available_hours", {})
        })
    
    return spaces

@router.post("/confirm-booking", response_model=Dict)
async def confirm_ai_booking(
    booking_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Conferma una prenotazione proposta dall'AI"""
    
    try:
        # Valida i dati della prenotazione
        required_fields = ["space_id", "start_datetime", "end_datetime", "purpose"]
        for field in required_fields:
            if field not in booking_data:
                raise HTTPException(status_code=400, detail=f"Campo {field} mancante")
        
        # Crea la prenotazione tramite il servizio esistente
        result = await booking_service.create_booking(
            booking_data,
            str(current_user["_id"])
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "booking_id": result["booking_id"],
            "message": "Prenotazione confermata con successo!"
        }
        
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "message": "Errore nella conferma della prenotazione"
        }

@router.post("/feedback")
async def provide_ai_feedback(
    feedback_data: Dict[str, Any],
    current_user: dict = Depends(get_current_user)
):
    """Raccoglie feedback sull'interazione con l'AI"""
    
    # Salva feedback per migliorare l'AI
    # Placeholder per implementazione feedback
    
    return {
        "message": "Grazie per il feedback!",
        "status": "received"
    }