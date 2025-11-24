"""
ChatAgent - Clean conversational agent (refactored from MentalWellnessAgent)

RESPONSIBILITIES:
- Generate empathetic conversational responses
- Maintain conversation history for current session
- Generate narrative journal entries from conversations
- Handle session management (start/end)

DOES NOT HANDLE:
- Crisis detection (→ CrisisAgent)
- Emotion extraction (→ SentimentAgent)
- Context building (→ ContextAgent)
- Disk persistence (→ Orchestrator/Storage)
"""

import google.generativeai as genai
from typing import List, Dict, Optional
from datetime import date
from .base_agent import BaseAgent


class ChatAgent(BaseAgent):
    """Clean conversational agent focused purely on dialogue generation."""
    
    def __init__(self, name: str = "ChatAgent", config: dict | None = None):
        super().__init__(name, config)
        
        # Configuration
        self.model_name = self.config.get("model", "models/gemini-2.0-flash")
        self.temperature = self.config.get("temperature", 0.7)
        self.max_tokens = self.config.get("max_tokens", 500)
        self.api_key = self.config.get("api_key")
        
        if not self.api_key:
            raise ValueError("API key required in config: {'api_key': '...'}")
        
        # Configure Gemini
        genai.configure(api_key=self.api_key)
        
        # Session state
        self.conversation_history: List[Dict] = []
        self.session_started = False
        self.system_instruction = None
        
    def start_session(self, user_name: Optional[str] = None, 
                     system_context: Optional[str] = None) -> str:
        """Start a new chat session.
        
        Args:
            user_name: Optional user name for personalization
            system_context: Pre-built context string from ContextAgent
            
        Returns:
            Opening greeting message
        """
        self.session_started = True
        self.conversation_history = []
        
        # Build system instruction
        base_prompt = self._get_base_system_prompt()
        
        if system_context:
            self.system_instruction = f"{base_prompt}\n\n{system_context}"
        else:
            self.system_instruction = base_prompt
        
        # Generate greeting
        greeting = self._generate_greeting(user_name)
        
        # Add to history
        self.conversation_history.append({
            "role": "assistant",
            "content": greeting
        })
        
        return greeting
    
    def _get_base_system_prompt(self) -> str:
        """Get base system prompt for the agent."""
        return """Sei un Mental Wellness Coach AI empatico e professionale.

Il tuo ruolo:
- Aiutare l'utente a riflettere sulla sua giornata attraverso domande aperte
- Essere empatico e supportivo senza essere invadente
- Fare domande di approfondimento quando l'utente è vago
- Identificare emozioni e situazioni importanti
- NON fare diagnosi mediche
- Suggerire di contattare un professionista se noti segnali di crisi

Stile conversazionale:
- Usa un tono caldo ma professionale
- Fai domande brevi e mirate
- Non più di 2-3 domande consecutive senza lasciare spazio
- Valida le emozioni dell'utente quando appropriato
- Mantieni un approccio equilibrato tra supporto e stimolo al pensiero critico
- NON usare emoji

Quando l'utente scrive "fine" o "basta":
- Ringrazia brevemente (1 riga)
- Crea un riassunto MINIMALISTA e STRETTAMENTE PROPORZIONATO alla conversazione
- Chiedi conferma per salvare"""
    
    def _generate_greeting(self, user_name: Optional[str] = None) -> str:
        """Generate opening greeting."""
        greeting_base = "Ciao"
        if user_name:
            greeting_base = f"Ciao {user_name}"
        
        return f"{greeting_base}! 🌟 Bentornato/a!\n\nCome è andata la giornata?"
    
    def chat(self, user_message: str, system_context: Optional[str] = None) -> str:
        """Process user message and generate response.
        
        This is the CORE method - simplified to focus only on conversation.
        
        Args:
            user_message: User's input
            system_context: Optional context override (if context changes mid-session)
            
        Returns:
            AI response text
        """
        if not self.session_started:
            raise RuntimeError("Session not started! Call start_session() first")
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_message
        })
        
        # Update system context if provided
        if system_context:
            self.system_instruction = f"{self._get_base_system_prompt()}\n\n{system_context}"
        
        # Check if user wants to end
        should_end = user_message.lower().strip() in ["fine", "basta", "stop", "termina"]
        
        if should_end:
            summary_prompt = self._create_summary_prompt()
            user_message = summary_prompt
        
        # Generate response via Gemini
        try:
            response_text = self._call_gemini_api(user_message)
            
            # Add to history
            self.conversation_history.append({
                "role": "assistant",
                "content": response_text
            })
            
            return response_text
            
        except Exception as e:
            error_message = f"❌ Errore nella comunicazione con AI: {str(e)}"
            return error_message
    
    def _call_gemini_api(self, user_message: str) -> str:
        """Call Gemini API with current conversation context.
        
        Args:
            user_message: Current user message
            
        Returns:
            AI response text
        """
        # Create model with system instruction
        model = genai.GenerativeModel(
            model_name=self.model_name,
            generation_config={
                "temperature": self.temperature,
                "max_output_tokens": self.max_tokens,
            },
            system_instruction=self.system_instruction
        )
        
        # Prepare Gemini history (exclude system, exclude last user message)
        gemini_history = []
        for msg in self.conversation_history[:-1]:  # Exclude last user msg (will be sent separately)
            if msg["role"] == "user":
                gemini_history.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "assistant":
                gemini_history.append({"role": "model", "parts": [msg["content"]]})
        
        # Start chat with history
        chat = model.start_chat(history=gemini_history)
        
        # Send message
        response = chat.send_message(user_message)
        
        return response.text
    
    def _create_summary_prompt(self) -> str:
        """Create prompt for conversation summary."""
        return """L'utente ha terminato la condivisione. Per favore:
1. Ringrazialo per aver condiviso
2. Fai un breve riassunto (2-3 frasi) dei punti chiave emersi
3. Chiedi conferma per salvare il log giornaliero"""
    
    def generate_journal_entry(self, existing_entry: Optional[str] = None) -> str:
        """Generate narrative journal entry from conversation.
        
        Args:
            existing_entry: Optional existing entry for today (will be combined)
            
        Returns:
            Narrative journal entry text
        """
        # Count user messages
        user_messages = [msg for msg in self.conversation_history 
                        if msg["role"] == "user" and 
                        msg["content"].lower().strip() not in ["fine", "basta", "stop", "termina"]]
        
        num_user_messages = len(user_messages)
        
        # Calculate target length
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
        
        # Build prompt
        if existing_entry:
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

Genera il log aggiornato:"""
        else:
            prompt = f"""Basandoti SOLO sulla conversazione che abbiamo avuto, genera un log di diario in prima persona.

REGOLE CRITICHE:
- Scrivi dal punto di vista dell'utente (usa "io", "mi sono sentito", ecc.)
- Lunghezza TARGET: {target_words} parole (MASSIMO)
- USA SOLO informazioni ESPLICITAMENTE menzionate dall'utente
- NON inventare dettagli, emozioni o riflessioni non dette
- Se l'utente ha scritto poco, il log DEVE essere molto breve
- Stile: semplice, diretto, fedele alle parole dell'utente

Genera il log:"""
        
        try:
            # Create model for journal generation
            model = genai.GenerativeModel(
                model_name=self.model_name,
                generation_config={
                    "temperature": 0.3,  # More deterministic
                    "max_output_tokens": max_tokens,
                },
                system_instruction="Sei un assistente che trascrive fedelmente ciò che l'utente ha detto, senza aggiungere nulla. Sii MOLTO conciso e letterale."
            )
            
            # Format conversation
            conversation_text = self._format_conversation_for_summary()
            full_prompt = f"Ecco la conversazione:\n\n{conversation_text}\n\n{prompt}"
            
            # Generate
            response = model.generate_content(full_prompt)
            return response.text.strip()
            
        except Exception as e:
            return f"[Errore nella generazione del log: {str(e)}]"
    
    def _format_conversation_for_summary(self) -> str:
        """Format conversation history for summary generation."""
        formatted = []
        for msg in self.conversation_history:
            role = "AI" if msg["role"] == "assistant" else "User"
            formatted.append(f"{role}: {msg['content']}")
        return "\n".join(formatted)
    
    def get_conversation_history(self) -> List[Dict]:
        """Get full conversation history for current session.
        
        Returns:
            List of message dictionaries with 'role' and 'content'
        """
        return self.conversation_history
    
    def reset_session(self):
        """Reset session state (for starting new session)."""
        self.conversation_history = []
        self.session_started = False
        self.system_instruction = None
    
    def run(self, message: str, context: Optional[str] = None, *args, **kwargs) -> str:
        """Standard run method for BaseAgent compatibility.
        
        Args:
            message: User's input
            context: Optional system context
            
        Returns:
            AI response string
        """
        if not self.session_started:
            # Auto-start session if not started
            self.start_session(system_context=context)
        
        return self.chat(message, system_context=context)