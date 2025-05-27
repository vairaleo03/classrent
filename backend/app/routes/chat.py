from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import List, Dict, Any
from ..services.ai_service import ai_service
from ..database import get_database
from .auth import get_current_user

router = APIRouter()

class ChatMessage(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    action: str = "info"  # info, booking_suggestion, todo_list
    data: Dict[str, Any] = {}

@router.post("/", response_model=ChatResponse)
async def chat_with_ai(
    chat_message: ChatMessage,
    current_user: dict = Depends(get_current_user)
):
    """Chat con AI per prenotazioni in linguaggio naturale"""
    db = await get_database()
    
    # Recupera spazi disponibili
    spaces = []
    async for space in db.spaces.find({"is_active": True}):
        spaces.append({
            "id": str(space["_id"]),
            "name": space["name"],
            "type": space["type"],
            "capacity": space["capacity"],
            "materials": space.get("materials", []),
            "location": space["location"]
        })
    
    message = chat_message.message.lower()
    
    # Riconosci il tipo di richiesta
    if any(word in message for word in ["prenota", "prenotare", "voglio", "serve"]):
        # Richiesta di prenotazione
        parsed_request = await ai_service.parse_booking_request(chat_message.message, spaces)
        
        if "error" in parsed_request:
            return ChatResponse(
                response="Mi dispiace, non sono riuscito a comprendere la tua richiesta. Puoi essere più specifico?",
                action="error"
            )
        
        # Suggerisci spazi compatibili
        suggestions = await ai_service.suggest_alternative_spaces(parsed_request, spaces)
        
        return ChatResponse(
            response="Ho analizzato la tua richiesta. Ecco alcuni spazi che potrebbero fare al caso tuo:",
            action="booking_suggestion",
            data={
                "parsed_request": parsed_request,
                "suggestions": suggestions
            }
        )
    
    elif any(word in message for word in ["lista", "cosa serve", "materiali", "laurea", "tesi"]):
        # Richiesta lista materiali
        activity = "laurea" if "laurea" in message else "tesi" if "tesi" in message else "evento universitario"
        todo_list = await ai_service.generate_todo_list(activity)
        
        return ChatResponse(
            response=f"Ecco una lista di materiali necessari per {activity}:",
            action="todo_list",
            data={"todo_list": todo_list}
        )
    
    elif any(word in message for word in ["storico", "prenotazioni", "mie prenotazioni"]):
        # Richiesta storico prenotazioni
        from ..services.booking_service import booking_service
        bookings = await booking_service.get_user_bookings(str(current_user["_id"]))
        
        if not bookings:
            return ChatResponse(
                response="Non hai ancora effettuato prenotazioni.",
                action="history",
                data={"bookings": []}
            )
        
        response_text = f"Hai {len(bookings)} prenotazioni. Ecco le più recenti:"
        return ChatResponse(
            response=response_text,
            action="history",
            data={"bookings": [booking.dict() for booking in bookings[:5]]}
        )
    
    else:
        # Risposta generica di aiuto
        return ChatResponse(
            response="""Ciao! Sono l'assistente ClassRent. Posso aiutarti con:
            
• Prenotazioni: "Voglio prenotare un'aula per domani alle 14"
• Liste materiali: "Cosa serve per la laurea?"
• Storico prenotazioni: "Mostrami le mie prenotazioni"
• Informazioni spazi: "Che aule ci sono disponibili?"

Come posso aiutarti?""",
            action="help"
        )

@router.get("/spaces", response_model=List[Dict])
async def get_available_spaces():
    """Recupera tutti gli spazi disponibili"""
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
            "description": space.get("description", "")
        })
    
    return spaces