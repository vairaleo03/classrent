import openai
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json
from ..config import settings

class AIService:
    def __init__(self):
        self.client = None
        self.is_configured = False
        
        # Solo inizializza OpenAI se la chiave API è valida
        if self._has_valid_config():
            try:
                self.client = openai.OpenAI(api_key=settings.openai_api_key)
                # Test di connessione
                self.client.models.list()
                self.is_configured = True
                print("✅ Servizio AI (OpenAI) configurato e connesso")
            except Exception as e:
                print(f"⚠️ Servizio AI non disponibile: {e}")
                self.client = None
                self.is_configured = False
        else:
            print("ℹ️ Servizio AI non configurato (OpenAI API key mancante)")
    
    def _has_valid_config(self) -> bool:
        """Verifica se la configurazione OpenAI è valida"""
        return (
            settings.openai_api_key is not None and
            settings.openai_api_key != "your-openai-api-key-here" and  # Esclude placeholder
            len(settings.openai_api_key) > 10  # Chiave minima valida
        )
    
    async def parse_booking_request(self, message: str, available_spaces: List[Dict]) -> Dict[str, Any]:
        """Analizza una richiesta di prenotazione in linguaggio naturale"""
        
        if not self.is_configured:
            # Fallback: parsing semplificato senza AI
            return self._simple_parse_fallback(message, available_spaces)
        
        system_prompt = f"""
        Sei un assistente per la prenotazione di aule universitarie. 
        Analizza la richiesta dell'utente e estrai le seguenti informazioni in formato JSON:
        - space_type: tipo di spazio richiesto
        - date: data richiesta (formato YYYY-MM-DD)
        - start_time: ora di inizio (formato HH:MM)
        - end_time: ora di fine (formato HH:MM)
        - capacity: numero di persone
        - materials: lista di materiali richiesti
        - purpose: scopo della prenotazione
        
        Spazi disponibili: {json.dumps(available_spaces[:3], indent=2)}
        
        Data corrente: {datetime.now().strftime('%Y-%m-%d')}
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": message}
                ],
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"❌ Errore AI parsing: {e}")
            return self._simple_parse_fallback(message, available_spaces)
    
    def _simple_parse_fallback(self, message: str, available_spaces: List[Dict]) -> Dict[str, Any]:
        """Parsing semplificato senza AI come fallback"""
        import re
        from datetime import datetime, timedelta
        
        result = {
            "space_type": "aula",  # Default
            "date": (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d'),  # Domani
            "start_time": "14:00",  # Default
            "end_time": "16:00",   # Default
            "capacity": 30,        # Default
            "materials": [],
            "purpose": message[:100] if message else "Prenotazione generica"
        }
        
        message_lower = message.lower()
        
        # Estrai tipo di spazio
        if any(word in message_lower for word in ['laboratorio', 'lab', 'computer']):
            result["space_type"] = "laboratorio"
        elif any(word in message_lower for word in ['riunione', 'meeting', 'sala']):
            result["space_type"] = "sala_riunioni"
        elif any(word in message_lower for word in ['medico', 'ambulatorio', 'visita']):
            result["space_type"] = "box_medico"
        
        # Estrai materiali comuni
        materials = []
        if any(word in message_lower for word in ['proiettore', 'proietta']):
            materials.append("Proiettore")
        if any(word in message_lower for word in ['computer', 'pc', 'postazione']):
            materials.append("PC")
        if any(word in message_lower for word in ['microfono', 'audio', 'amplifica']):
            materials.append("Microfono")
        if any(word in message_lower for word in ['lavagna', 'interactive', 'touch']):
            materials.append("Lavagna Interattiva")
        
        result["materials"] = materials
        
        # Estrai orari se presenti
        time_match = re.search(r'(\d{1,2})[:.]?(\d{0,2})', message)
        if time_match:
            hour = int(time_match.group(1))
            minute = int(time_match.group(2)) if time_match.group(2) else 0
            if 8 <= hour <= 20:  # Orario ragionevole
                result["start_time"] = f"{hour:02d}:{minute:02d}"
                result["end_time"] = f"{(hour + 2):02d}:{minute:02d}"
        
        return result
    
    async def generate_todo_list(self, activity_type: str) -> List[str]:
        """Genera una lista di cose da fare per un'attività specifica"""
        
        if not self.is_configured:
            # Fallback: liste predefinite
            return self._simple_todo_fallback(activity_type)
        
        prompt = f"""
        Genera una lista dettagliata di materiali e preparativi necessari per: {activity_type}
        Restituisci solo la lista in formato JSON array di stringhe.
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"❌ Errore AI todo list: {e}")
            return self._simple_todo_fallback(activity_type)
    
    def _simple_todo_fallback(self, activity_type: str) -> List[str]:
        """Liste predefinite come fallback"""
        todo_lists = {
            "laurea": [
                "Preparare presentazione PowerPoint",
                "Stampare copie della tesi",
                "Preparare ringraziamenti",
                "Controllare proiettore e PC",
                "Preparare backup su USB",
                "Provare la presentazione",
                "Preparare outfit formale",
                "Controllare orario e aula"
            ],
            "tesi": [
                "Completare capitoli mancanti",
                "Revisione bibliografia",
                "Controllo ortografico",
                "Impaginazione finale",
                "Stampa e rilegatura",
                "Preparare presentazione",
                "Raccogliere feedback relatore"
            ],
            "default": [
                "Preparare materiali necessari",
                "Controllare attrezzature",
                "Preparare agenda",
                "Confermare partecipanti",
                "Preparare backup",
                "Testare tecnologia"
            ]
        }
        
        activity_lower = activity_type.lower()
        if "laurea" in activity_lower:
            return todo_lists["laurea"]
        elif "tesi" in activity_lower:
            return todo_lists["tesi"]
        else:
            return todo_lists["default"]
    
    async def suggest_alternative_spaces(self, requirements: Dict, available_spaces: List[Dict]) -> List[Dict]:
        """Suggerisce spazi alternativi basati sui requisiti"""
        
        if not self.is_configured:
            # Fallback: selezione semplice
            return self._simple_suggest_fallback(requirements, available_spaces)
        
        prompt = f"""
        Basandoti sui requisiti: {json.dumps(requirements)}
        E sugli spazi disponibili: {json.dumps(available_spaces[:5])}
        
        Suggerisci i 3 spazi più adatti e spiega perché.
        Restituisci in formato JSON con array di oggetti contenenti: space_id, name, reason
        """
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3
            )
            
            content = response.choices[0].message.content
            return json.loads(content)
        except Exception as e:
            print(f"❌ Errore AI suggestions: {e}")
            return self._simple_suggest_fallback(requirements, available_spaces)
    
    def _simple_suggest_fallback(self, requirements: Dict, available_spaces: List[Dict]) -> List[Dict]:
        """Suggerimenti semplici come fallback"""
        suggestions = []
        
        req_type = requirements.get("space_type", "aula")
        req_capacity = requirements.get("capacity", 0)
        req_materials = requirements.get("materials", [])
        
        # Filtra e ordina spazi
        filtered_spaces = []
        for space in available_spaces[:10]:  # Limita per performance
            score = 0
            
            # Punteggio per tipo
            if space.get("type") == req_type:
                score += 10
            
            # Punteggio per capacità
            if space.get("capacity", 0) >= req_capacity:
                score += 5
            
            # Punteggio per materiali
            space_materials = [m.get("name", "") for m in space.get("materials", [])]
            for req_mat in req_materials:
                if any(req_mat.lower() in sm.lower() for sm in space_materials):
                    score += 3
            
            filtered_spaces.append((space, score))
        
        # Ordina per punteggio
        filtered_spaces.sort(key=lambda x: x[1], reverse=True)
        
        # Prendi i primi 3
        for space, score in filtered_spaces[:3]:
            reason = f"Punteggio compatibilità: {score}/20"
            if space.get("type") == req_type:
                reason += f" - Tipo corretto ({req_type})"
            if space.get("capacity", 0) >= req_capacity:
                reason += f" - Capacità sufficiente ({space.get('capacity')} posti)"
            
            suggestions.append({
                "space_id": space.get("id", ""),
                "name": space.get("name", ""),
                "reason": reason
            })
        
        return suggestions

ai_service = AIService()