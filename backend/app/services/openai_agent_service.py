import openai
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import asyncio
import aiohttp
from ..config import settings
from ..database import get_database
from bson import ObjectId

class OpenAIAgentService:
    def __init__(self):
        self.client = None
        self.is_configured = False
        self.assistant_id = None
        self._assistant_creation_lock = asyncio.Lock()
        self._initialization_lock = asyncio.Lock()
        self._initialized = False
        
        print("🔄 Servizio AI Agent inizializzato (configurazione lazy)")
    
    async def _initialize_if_needed(self):
        """Inizializzazione lazy thread-safe"""
        if self._initialized:
            return
            
        async with self._initialization_lock:
            if self._initialized:  # Double-check
                return
                
            if not self._has_valid_config():
                print("ℹ️ Servizio AI Agent non configurato (OpenAI API key mancante)")
                return
            
            try:
                # Inizializza client OpenAI
                self.client = openai.AsyncOpenAI(api_key=settings.openai_api_key)
                
                # Test di connessione asincrono
                await self.client.models.list()
                self.is_configured = True
                self._initialized = True
                print("✅ Servizio AI Agent (OpenAI) configurato e connesso")
                
            except Exception as e:
                print(f"⚠️ Servizio AI Agent non disponibile: {e}")
                self.client = None
                self.is_configured = False
    
    def _has_valid_config(self) -> bool:
        """Verifica se la configurazione OpenAI è valida"""
        return (
            settings.openai_api_key is not None and
            settings.openai_api_key != "your-openai-api-key-here" and
            len(settings.openai_api_key) > 10
        )
    
    async def _ensure_assistant_created(self):
        """Crea l'assistente se non esiste - thread-safe con lock"""
        await self._initialize_if_needed()
        
        if not self.is_configured or self.assistant_id:
            return
        
        async with self._assistant_creation_lock:
            # Double-check dopo aver acquisito il lock
            if self.assistant_id:
                return
                
            try:
                # Definisci le funzioni che l'assistente può usare
                functions = [
                    {
                        "type": "function",
                        "function": {
                            "name": "search_available_spaces",
                            "description": "Cerca spazi disponibili basandosi sui criteri dell'utente",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "space_type": {
                                        "type": "string",
                                        "enum": ["aula", "laboratorio", "sala_riunioni", "box_medico"],
                                        "description": "Tipo di spazio richiesto"
                                    },
                                    "capacity": {
                                        "type": "integer",
                                        "description": "Numero minimo di posti richiesti"
                                    },
                                    "materials": {
                                        "type": "array",
                                        "items": {"type": "string"},
                                        "description": "Lista di materiali richiesti"
                                    },
                                    "date": {
                                        "type": "string",
                                        "format": "date",
                                        "description": "Data desiderata in formato YYYY-MM-DD"
                                    },
                                    "start_time": {
                                        "type": "string",
                                        "description": "Ora di inizio in formato HH:MM"
                                    },
                                    "duration_hours": {
                                        "type": "number",
                                        "description": "Durata in ore della prenotazione"
                                    }
                                },
                                "required": ["space_type"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "create_booking_directly",
                            "description": "Crea DIRETTAMENTE una prenotazione nel database - non solo proposta",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "space_id": {"type": "string"},
                                    "date": {"type": "string"},
                                    "start_time": {"type": "string"},
                                    "end_time": {"type": "string"},
                                    "purpose": {"type": "string"},
                                    "materials": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "notes": {"type": "string"}
                                },
                                "required": ["space_id", "date", "start_time", "end_time", "purpose"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "check_space_availability",
                            "description": "Verifica disponibilità specifica di uno spazio per data e orario",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "space_id": {"type": "string"},
                                    "date": {"type": "string"},
                                    "start_time": {"type": "string"},
                                    "end_time": {"type": "string"}
                                },
                                "required": ["space_id", "date", "start_time", "end_time"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "get_user_bookings",
                            "description": "Recupera le prenotazioni dell'utente",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "user_id": {"type": "string"},
                                    "status": {
                                        "type": "string",
                                        "enum": ["all", "upcoming", "past", "cancelled"]
                                    }
                                },
                                "required": ["user_id"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "generate_activity_checklist",
                            "description": "Genera una checklist per un'attività specifica",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "activity_type": {
                                        "type": "string",
                                        "description": "Tipo di attività (es: laurea, tesi, seminario, etc.)"
                                    },
                                    "space_type": {"type": "string"}
                                },
                                "required": ["activity_type"]
                            }
                        }
                    }
                ]
                
                # Crea l'assistente usando il client asincrono
                assistant = await self.client.beta.assistants.create(
                    name="ClassRent AI Assistant",
                    instructions="""
                    Sei l'assistente AI di ClassRent, un sistema di prenotazione aule universitarie.
                    
                    Le tue capacità principali:
                    1. Cercare spazi disponibili in base alle richieste dell'utente
                    2. CREARE DIRETTAMENTE prenotazioni nel sistema (non solo proposte!)
                    3. Verificare disponibilità di spazi specifici
                    4. Gestire le prenotazioni esistenti dell'utente
                    5. Generare checklist per eventi specifici
                    
                    IMPORTANTE:
                    - Quando l'utente chiede di prenotare, USA la funzione create_booking_directly per CREARE EFFETTIVAMENTE la prenotazione
                    - Verifica sempre la disponibilità prima di creare una prenotazione
                    - Conferma sempre i dettagli con l'utente prima di finalizzare
                    - Parla sempre in italiano in modo cordiale e professionale
                    
                    Processo di prenotazione:
                    1. Raccogli tutte le informazioni necessarie dall'utente
                    2. Cerca spazi disponibili che corrispondono ai criteri
                    3. Verifica disponibilità dello spazio scelto
                    4. Crea la prenotazione DIRETTAMENTE nel database
                    5. Conferma all'utente che la prenotazione è stata creata
                    
                    Rispondi sempre in italiano e sii proattivo nell'aiutare l'utente.
                    """,
                    model="gpt-4-1106-preview",
                    tools=functions
                )
                
                self.assistant_id = assistant.id
                print(f"✅ Assistente ClassRent creato con ID: {self.assistant_id}")
                
            except Exception as e:
                print(f"❌ Errore nella creazione dell'assistente: {e}")
                raise
    
    async def process_user_message(self, message: str, user_id: str, context: Dict = None) -> Dict[str, Any]:
        """Processa un messaggio dell'utente tramite l'assistente AI"""
        
        try:
            await self._initialize_if_needed()
            
            if not self.is_configured:
                return await self._fallback_response(message, user_id, context)
            
            # Assicurati che l'assistente sia creato
            await self._ensure_assistant_created()
            
            if not self.assistant_id:
                return await self._fallback_response(message, user_id, context)
            
            # Crea un thread per la conversazione
            thread = await self.client.beta.threads.create()
            
            # Aggiungi il messaggio dell'utente
            await self.client.beta.threads.messages.create(
                thread_id=thread.id,
                role="user",
                content=message
            )
            
            # Esegui l'assistente
            run = await self.client.beta.threads.runs.create(
                thread_id=thread.id,
                assistant_id=self.assistant_id
            )
            
            # Attendi il completamento con gestione function calls
            max_iterations = 10
            iteration = 0
            
            while run.status in ['queued', 'in_progress', 'requires_action'] and iteration < max_iterations:
                await asyncio.sleep(2)  # Attesa più lunga per ridurre calls API
                
                run = await self.client.beta.threads.runs.retrieve(
                    thread_id=thread.id,
                    run_id=run.id
                )
                
                # Gestisci le chiamate a funzione
                if run.status == 'requires_action':
                    try:
                        tool_outputs = []
                        
                        for tool_call in run.required_action.submit_tool_outputs.tool_calls:
                            try:
                                output = await self._handle_function_call(
                                    tool_call.function.name,
                                    json.loads(tool_call.function.arguments),
                                    user_id,
                                    context
                                )
                                tool_outputs.append({
                                    "tool_call_id": tool_call.id,
                                    "output": json.dumps(output, default=str, ensure_ascii=False)
                                })
                            except Exception as func_error:
                                print(f"❌ Errore nella funzione {tool_call.function.name}: {func_error}")
                                tool_outputs.append({
                                    "tool_call_id": tool_call.id,
                                    "output": json.dumps({"error": f"Errore: {str(func_error)}"}, ensure_ascii=False)
                                })
                        
                        # Invia i risultati delle funzioni
                        run = await self.client.beta.threads.runs.submit_tool_outputs(
                            thread_id=thread.id,
                            run_id=run.id,
                            tool_outputs=tool_outputs
                        )
                        
                    except Exception as submit_error:
                        print(f"❌ Errore nell'invio tool outputs: {submit_error}")
                        break
                
                iteration += 1
            
            if run.status == 'completed':
                # Recupera la risposta
                messages = await self.client.beta.threads.messages.list(
                    thread_id=thread.id
                )
                
                assistant_message = messages.data[0]
                response_text = assistant_message.content[0].text.value
                
                return {
                    "response": response_text,
                    "action": "ai_response",
                    "data": {},
                    "thread_id": thread.id
                }
            
            elif run.status == 'failed':
                error_message = getattr(run, 'last_error', {}).get('message', 'Errore sconosciuto')
                print(f"❌ Run fallito: {error_message}")
                return await self._fallback_response(message, user_id, context)
            
            else:
                print(f"❌ Run non completato. Status finale: {run.status}")
                return {
                    "response": "Mi dispiace, si è verificato un timeout nel processare la tua richiesta. Riprova.",
                    "action": "error",
                    "data": {"status": run.status, "iterations": iteration}
                }
                
        except Exception as e:
            print(f"❌ Errore nell'elaborazione del messaggio: {e}")
            return await self._fallback_response(message, user_id, context)
    
    async def _handle_function_call(self, function_name: str, arguments: Dict, user_id: str, context: Dict) -> Dict:
        """Gestisce le chiamate alle funzioni dell'assistente"""
        
        try:
            if function_name == "search_available_spaces":
                return await self._search_available_spaces(arguments)
            
            elif function_name == "create_booking_directly":
                return await self._create_booking_directly(arguments, user_id)
            
            elif function_name == "check_space_availability":
                return await self._check_space_availability(arguments)
            
            elif function_name == "get_user_bookings":
                return await self._get_user_bookings(arguments["user_id"], arguments.get("status", "all"))
            
            elif function_name == "generate_activity_checklist":
                return await self._generate_activity_checklist(arguments["activity_type"], arguments.get("space_type"))
            
            else:
                return {"error": f"Funzione {function_name} non riconosciuta"}
                
        except Exception as e:
            print(f"❌ Errore nella funzione {function_name}: {e}")
            return {"error": f"Errore nell'esecuzione della funzione: {str(e)}"}
    
    async def _create_booking_directly(self, booking_args: Dict, user_id: str) -> Dict:
        """CREA DIRETTAMENTE una prenotazione nel database"""
        try:
            # Importa il servizio di prenotazione
            from ..services.booking_service import booking_service
            
            # Costruisci i dati della prenotazione
            date_str = booking_args["date"]
            start_time = booking_args["start_time"]
            end_time = booking_args["end_time"]
            
            # Combina data e orari
            start_datetime = datetime.fromisoformat(f"{date_str}T{start_time}:00")
            end_datetime = datetime.fromisoformat(f"{date_str}T{end_time}:00")
            
            booking_data = {
                "space_id": booking_args["space_id"],
                "start_datetime": start_datetime,
                "end_datetime": end_datetime,
                "purpose": booking_args["purpose"],
                "materials_requested": booking_args.get("materials", []),
                "notes": booking_args.get("notes", "Prenotazione creata tramite AI Assistant")
            }
            
            # Crea la prenotazione effettivamente
            result = await booking_service.create_booking(booking_data, user_id)
            
            if "error" in result:
                return {
                    "success": False,
                    "error": result["error"],
                    "message": f"Impossibile creare la prenotazione: {result['error']}"
                }
            else:
                # Recupera nome spazio per conferma
                db = await get_database()
                space = await db.spaces.find_one({"_id": ObjectId(booking_args["space_id"])})
                space_name = space["name"] if space else "Spazio"
                
                return {
                    "success": True,
                    "booking_id": result["booking_id"],
                    "space_name": space_name,
                    "date": date_str,
                    "start_time": start_time,
                    "end_time": end_time,
                    "message": f"✅ Prenotazione creata con successo! {space_name} il {date_str} dalle {start_time} alle {end_time}"
                }
                
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": f"Errore nella creazione della prenotazione: {str(e)}"
            }
    
    async def _check_space_availability(self, availability_args: Dict) -> Dict:
        """Verifica disponibilità specifica di uno spazio"""
        try:
            from ..services.database_calendar_service import database_calendar_service
            
            date = datetime.strptime(availability_args["date"], "%Y-%m-%d")
            
            # Verifica disponibilità tramite calendario database
            availability = await database_calendar_service.get_space_availability_calendar(
                availability_args["space_id"], 
                date
            )
            
            if "error" in availability:
                return availability
            
            # Verifica slot specifico
            start_time = availability_args["start_time"]
            end_time = availability_args["end_time"]
            
            # Trova slot corrispondenti
            conflicting_slots = []
            for slot in availability["time_slots"]:
                if not slot["available"]:
                    if (slot["start_time"] <= start_time < slot["end_time"] or
                        slot["start_time"] < end_time <= slot["end_time"]):
                        conflicting_slots.append(slot)
            
            is_available = len(conflicting_slots) == 0
            
            return {
                "available": is_available,
                "space_name": availability["space_name"],
                "date": availability["date"],
                "requested_time": f"{start_time} - {end_time}",
                "conflicts": conflicting_slots,
                "message": "Spazio disponibile" if is_available else f"Spazio occupato in {len(conflicting_slots)} slot"
            }
            
        except Exception as e:
            return {"error": f"Errore verifica disponibilità: {str(e)}"}
    
    async def _search_available_spaces(self, criteria: Dict) -> Dict:
        """Cerca spazi disponibili"""
        try:
            db = await get_database()
            
            # Costruisci query
            filter_query = {"is_active": True}
            
            if criteria.get("space_type"):
                filter_query["type"] = criteria["space_type"]
            
            if criteria.get("capacity"):
                filter_query["capacity"] = {"$gte": criteria["capacity"]}
            
            if criteria.get("materials"):
                filter_query["materials.name"] = {"$in": criteria["materials"]}
            
            # Recupera spazi
            spaces = []
            async for space in db.spaces.find(filter_query).limit(5):
                spaces.append({
                    "id": str(space["_id"]),
                    "name": space["name"],
                    "type": space["type"],
                    "capacity": space["capacity"],
                    "location": space["location"],
                    "materials": space.get("materials", []),
                    "available_hours": space.get("available_hours", {}),
                    "description": space.get("description", "")
                })
            
            return {
                "spaces": spaces,
                "count": len(spaces),
                "criteria": criteria
            }
            
        except Exception as e:
            return {"error": f"Errore nella ricerca spazi: {str(e)}"}
    
    async def _get_user_bookings(self, user_id: str, status: str = "all") -> Dict:
        """Recupera prenotazioni utente"""
        try:
            db = await get_database()
            
            filter_query = {"user_id": user_id}
            
            if status == "upcoming":
                filter_query["start_datetime"] = {"$gte": datetime.now()}
                filter_query["status"] = {"$in": ["confirmed", "pending"]}
            elif status == "past":
                filter_query["end_datetime"] = {"$lt": datetime.now()}
            elif status == "cancelled":
                filter_query["status"] = "cancelled"
            
            bookings = []
            async for booking in db.bookings.find(filter_query).sort("start_datetime", -1).limit(10):
                space = await db.spaces.find_one({"_id": ObjectId(booking["space_id"])})
                bookings.append({
                    "id": str(booking["_id"]),
                    "space_name": space["name"] if space else "Spazio eliminato",
                    "start_datetime": booking["start_datetime"].isoformat(),
                    "end_datetime": booking["end_datetime"].isoformat(),
                    "purpose": booking["purpose"],
                    "status": booking["status"]
                })
            
            return {
                "bookings": bookings,
                "count": len(bookings),
                "status_filter": status
            }
            
        except Exception as e:
            return {"error": f"Errore nel recupero prenotazioni: {str(e)}"}
    
    async def _generate_activity_checklist(self, activity_type: str, space_type: str = None) -> Dict:
        """Genera checklist per attività"""
        checklists = {
            "laurea": [
                "Preparare presentazione PowerPoint (15-20 minuti)",
                "Stampare copie della tesi per la commissione",
                "Preparare ringraziamenti",
                "Testare proiettore e computer",
                "Preparare backup su USB",
                "Provare la presentazione",
                "Preparare outfit formale",
                "Controllare orario e ubicazione aula",
                "Portare documento di identità"
            ],
            "tesi": [
                "Completare tutti i capitoli",
                "Revisione finale con il relatore",
                "Controllo ortografico e grammaticale",
                "Impaginazione definitiva",
                "Stampa e rilegatura",
                "Preparare abstract",
                "Raccogliere feedback da correlatori",
                "Backup digitale sicuro"
            ],
            "seminario": [
                "Definire obiettivi del seminario",
                "Preparare materiale didattico",
                "Testare attrezzature audiovisive",
                "Preparare handout per partecipanti",
                "Controllare sistema di registrazione presenze",
                "Preparare domande per discussione",
                "Testare connessione internet",
                "Preparare piano B per problemi tecnici"
            ]
        }
        
        activity_lower = activity_type.lower()
        checklist = None
        
        for key, items in checklists.items():
            if key in activity_lower:
                checklist = items
                break
        
        if not checklist:
            checklist = [
                "Preparare materiali necessari",
                "Controllare attrezzature",
                "Confermare partecipanti",
                "Testare tecnologia",
                "Preparare backup",
                "Verificare orario e luogo"
            ]
        
        return {
            "activity_type": activity_type,
            "checklist": checklist,
            "space_type": space_type
        }
    
    async def _fallback_response(self, message: str, user_id: str, context: Dict) -> Dict[str, Any]:
        """Risposta di fallback quando l'AI non è disponibile"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["prenota", "prenotare", "voglio", "serve"]):
            return {
                "response": "Per prenotare uno spazio, puoi usare il form di prenotazione. Specifica il tipo di spazio, la data e l'ora desiderata.",
                "action": "booking_suggestion",
                "data": {"fallback": True}
            }
        
        elif any(word in message_lower for word in ["lista", "cosa serve", "materiali"]):
            return {
                "response": "Ecco una lista generica di materiali spesso necessari per eventi universitari:",
                "action": "todo_list",
                "data": {
                    "todo_list": [
                        "Proiettore per presentazioni",
                        "Computer o laptop",
                        "Sistema audio/microfoni",
                        "Materiale cartaceo",
                        "Connessione internet",
                        "Backup su dispositivi esterni"
                    ]
                }
            }
        
        else:
            return {
                "response": """Ciao! Sono l'assistente ClassRent (modalità semplificata). 
                
Posso aiutarti con:
• Prenotazioni: "Voglio prenotare un'aula per domani alle 14"
• Informazioni spazi: "Che aule ci sono disponibili?"
• Liste materiali: "Cosa serve per la laurea?"
• Gestione prenotazioni: "Mostrami le mie prenotazioni"

Come posso aiutarti?""",
                "action": "help",
                "data": {}
            }

    async def cleanup(self):
        """Cleanup delle risorse"""
        try:
            if self.client:
                await self.client.close()
                print("🧹 Client OpenAI chiuso correttamente")
        except Exception as e:
            print(f"⚠️ Errore durante cleanup: {e}")

# Istanza globale del servizio
ai_agent_service = OpenAIAgentService()