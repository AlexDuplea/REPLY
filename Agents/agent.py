"""
Agente AI per Mental Wellness Journal
Gestisce le conversazioni con l'utente usando Google Gemini API
"""

import google.generativeai as genai
from typing import List, Dict, Optional
import config
from datetime import date


class MentalWellnessAgent:
    """Agente AI conversazionale per il diario del benessere mentale"""

    def __init__(self):
        """Inizializza l'agente con API Gemini"""
        if not config.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY non trovata! Controlla il file .env")

        genai.configure(api_key=config.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(
            model_name=config.MODEL_NAME,
            generation_config=config.GENERATION_CONFIG
        )
        self.conversation_history: List[Dict] = []
        self.session_started = False
        self.chat_session = None

    def start_session(self, user_name: Optional[str] = None,
                      context: Optional[str] = None) -> str:
        """
        Inizia una nuova sessione giornaliera

        Args:
            user_name: Nome dell'utente (opzionale)
            context: Contesto dalle sessioni precedenti (opzionale)

        Returns:
            Messaggio di benvenuto dell'agente
        """
        self.session_started = True
        self.conversation_history = []

        # Costruisci system prompt personalizzato
        system_prompt = config.SYSTEM_PROMPT

        if context:
            system_prompt += f"\n\nContesto dalle sessioni precedenti:\n{context}"

        # Aggiungi system message
        self.conversation_history.append({
            "role": "system",
            "content": system_prompt
        })

        # Inizia chat session con Gemini
        self.chat_session = self.model.start_chat(history=[])

        # Genera messaggio di apertura
        greeting = self._generate_greeting(user_name)

        return greeting

    def _generate_greeting(self, user_name: Optional[str] = None) -> str:
        """Genera un saluto iniziale appropriato"""
        today = date.today()

        # Determina momento della giornata
        hour = date.today().isoformat()  # Semplificato per ora

        greeting_base = "Ciao"
        if user_name:
            greeting_base = f"Ciao {user_name}"

        opening = f"{greeting_base}! 🌟 Bentornato/a!\n\nCome è andata la giornata?"

        # L'AI genera il suo primo messaggio
        self.conversation_history.append({
            "role": "assistant",
            "content": opening
        })

        return opening

    def chat(self, user_message: str) -> Dict:
        """
        Invia un messaggio e ricevi la risposta dell'agente

        Args:
            user_message: Il messaggio dell'utente

        Returns:
            Dict con:
                - response: risposta dell'agente
                - should_end: True se la conversazione dovrebbe terminare
                - crisis_detected: True se sono state rilevate parole di crisi
        """
        if not self.session_started:
            raise RuntimeError("Sessione non iniziata! Chiama start_session() prima")

        # Aggiungi messaggio utente alla history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })

        # Verifica parole di crisi
        crisis_detected = self._check_crisis_keywords(user_message)

        if crisis_detected:
            crisis_response = config.CRISIS_MESSAGE
            self.conversation_history.append({
                "role": "assistant",
                "content": crisis_response
            })
            return {
                "response": crisis_response,
                "should_end": True,
                "crisis_detected": True
            }

        # Verifica comandi di terminazione
        should_end = user_message.lower().strip() in ["fine", "basta", "stop", "termina"]

        if should_end:
            summary_prompt = self._create_summary_prompt()
            self.conversation_history.append({
                "role": "user",
                "content": summary_prompt
            })

        # Chiama Gemini API
        try:
            # Prepara il contesto per Gemini includendo il system prompt
            system_instruction = self.conversation_history[0]["content"]
            
            # Crea un nuovo modello con system instruction
            model_with_system = genai.GenerativeModel(
                model_name=config.MODEL_NAME,
                generation_config=config.GENERATION_CONFIG,
                system_instruction=system_instruction
            )
            
            # Prepara la history per Gemini (escludi system message)
            gemini_history = []
            for msg in self.conversation_history[1:-1]:  # Escludi system e ultimo messaggio utente
                if msg["role"] == "user":
                    gemini_history.append({"role": "user", "parts": [msg["content"]]})
                elif msg["role"] == "assistant":
                    gemini_history.append({"role": "model", "parts": [msg["content"]]})
            
            # Avvia chat con history
            chat = model_with_system.start_chat(history=gemini_history)
            
            # Invia messaggio
            response = chat.send_message(user_message if not should_end else summary_prompt)
            assistant_message = response.text

            # Aggiungi risposta alla history
            self.conversation_history.append({
                "role": "assistant",
                "content": assistant_message
            })

            return {
                "response": assistant_message,
                "should_end": should_end,
                "crisis_detected": False
            }

        except Exception as e:
            error_message = f"❌ Errore nella comunicazione con AI: {str(e)}"
            return {
                "response": error_message,
                "should_end": True,
                "crisis_detected": False
            }

    def _check_crisis_keywords(self, message: str) -> bool:
        """Verifica se il messaggio contiene parole che indicano crisi"""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in config.CRISIS_KEYWORDS)

    def _create_summary_prompt(self) -> str:
        """Crea un prompt per far riassumere la conversazione all'AI"""
        return """L'utente ha terminato la condivisione. Per favore:
1. Ringrazialo per aver condiviso
2. Fai un breve riassunto (2-3 frasi) dei punti chiave emersi
3. Chiedi conferma per salvare il log giornaliero
"""

    def generate_journal_entry(self, existing_entry: Optional[str] = None) -> str:
        """
        Genera un log giornaliero narrativo dalla conversazione
        
        Args:
            existing_entry: Log esistente della giornata (se presente)

        Returns:
            Testo narrativo del diario
        """
        # Conta quanti messaggi reali ha scritto l'utente (escluso "fine")
        user_messages = [msg for msg in self.conversation_history 
                        if msg["role"] == "user" and msg["content"].lower().strip() not in ["fine", "basta", "stop", "termina"]]
        
        num_user_messages = len(user_messages)
        
        # Calcola lunghezza target basata sulla conversazione
        if num_user_messages <= 2:
            target_words = "20-30"
            max_tokens = 80
        elif num_user_messages <= 4:
            target_words = "40-60"
            max_tokens = 120
        elif num_user_messages <= 7:
            target_words = "80-100"
            max_tokens = 180
        else:
            target_words = "120-150"
            max_tokens = 250
        
        # Prepara prompt per generazione log
        if existing_entry:
            # C'è già un log oggi - aggiorna combinando vecchio e nuovo
            prompt = f"""Hai già scritto questo log oggi:

"{existing_entry}"

Ora, basandoti sulla NUOVA conversazione che abbiamo appena avuto, aggiorna il log combinando le informazioni.

REGOLE CRITICHE:
- Mantieni tutto ciò che era nel log precedente
- Aggiungi SOLO le nuove informazioni dalla conversazione appena conclusa
- Scrivi in prima persona (uso "io", "mi sono sentito", ecc.)
- Lunghezza totale TARGET: {target_words} parole (MASSIMO)
- USA SOLO informazioni ESPLICITAMENTE menzionate
- NON inventare dettagli o emozioni non dette
- Stile: semplice, diretto, cronologico

Genera il log aggiornato che include sia il contenuto precedente che le nuove informazioni:
"""
        else:
            # Primo log della giornata
            prompt = f"""Basandoti SOLO sulla conversazione che abbiamo avuto, genera un log di diario in prima persona.

REGOLE CRITICHE:
- Scrivi dal punto di vista dell'utente (usa "io", "mi sono sentito", ecc.)
- Lunghezza TARGET: {target_words} parole (MASSIMO)
- USA SOLO informazioni ESPLICITAMENTE menzionate dall'utente
- NON inventare dettagli, emozioni o riflessioni non dette
- NON aggiungere interpretazioni psicologiche
- NON espandere o elaborare oltre ciò che è stato detto
- Se l'utente ha scritto poco, il log DEVE essere molto breve
- Stile: semplice, diretto, fedele alle parole dell'utente

Esempio per conversazione BREVE (2-3 messaggi):
"Oggi è andata tutto bene. Ho fatto una challenge di programmazione che mi è piaciuta."

Ora genera il log basandoti SOLO su ciò che l'utente ha effettivamente scritto:
"""

        try:
            # Crea modello con system instruction specifica
            model = genai.GenerativeModel(
                model_name=config.MODEL_NAME,
                generation_config={
                    "temperature": 0.3,  # Ridotta per essere più fedele
                    "max_output_tokens": max_tokens,
                },
                system_instruction="Sei un assistente che trascrive fedelmente ciò che l'utente ha detto, senza aggiungere nulla. Sii MOLTO conciso e letterale."
            )
            
            # Prepara il contesto della conversazione
            conversation_text = self._format_conversation_for_summary()
            full_prompt = f"Ecco la conversazione:\n\n{conversation_text}\n\n{prompt}"
            
            response = model.generate_content(full_prompt)
            return response.text.strip()

        except Exception as e:
            return f"[Errore nella generazione del log: {str(e)}]"

    def _format_conversation_for_summary(self) -> str:
        """Formatta la conversazione per il riassunto"""
        formatted = []
        for msg in self.conversation_history:
            if msg["role"] == "system":
                continue
            role = "AI" if msg["role"] == "assistant" else "User"
            formatted.append(f"{role}: {msg['content']}")
        return "\n".join(formatted)

    def get_conversation_history(self) -> List[Dict]:
        """Ritorna la storia completa della conversazione"""
        return self.conversation_history

    def extract_emotions(self) -> Dict[str, int]:
        """
        Estrae emozioni dalla conversazione (analisi semplice basata su keywords)

        Returns:
            Dict con conteggi delle emozioni rilevate
        """
        emotions = {emotion: 0 for emotion in config.EMOTION_KEYWORDS.keys()}

        # Concatena tutti i messaggi dell'utente
        user_text = " ".join([
            msg["content"].lower()
            for msg in self.conversation_history
            if msg["role"] == "user"
        ])

        # Conta occorrenze keywords
        for emotion, keywords in config.EMOTION_KEYWORDS.items():
            for keyword in keywords:
                emotions[emotion] += user_text.count(keyword)

        return emotions