"""
Agente AI per Mental Wellness Journal
Gestisce le conversazioni con l'utente usando OpenAI API
"""

from openai import OpenAI
from typing import List, Dict, Optional
import config
from datetime import date


class MentalWellnessAgent:
    """Agente AI conversazionale per il diario del benessere mentale"""

    def __init__(self):
        """Inizializza l'agente con API OpenAI"""
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY non trovata! Controlla il file .env")

        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.conversation_history: List[Dict] = []
        self.session_started = False

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

        # Chiama OpenAI API
        try:
            response = self.client.chat.completions.create(
                model=config.MODEL_NAME,
                messages=self.conversation_history,
                max_tokens=config.MAX_TOKENS,
                temperature=config.TEMPERATURE
            )

            assistant_message = response.choices[0].message.content

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

    def generate_journal_entry(self) -> str:
        """
        Genera un log giornaliero narrativo dalla conversazione

        Returns:
            Testo narrativo del diario
        """
        # Prepara prompt per generazione log
        prompt = """Basandoti sulla conversazione che abbiamo avuto, genera un log di diario in prima persona.

Requisiti:
- Scrivi dal punto di vista dell'utente (usa "io", "mi sono sentito", ecc.)
- Stile narrativo, fluido e naturale
- Includi emozioni, eventi e riflessioni emerse
- Lunghezza: 150-250 parole
- Non menzionare che questo è un riassunto AI
- Non usare elenchi puntati, scrivi in forma narrativa

Esempio di stile:
"Oggi è stata una giornata intensa. Mi sono svegliato sentendomi già stanco, probabilmente per il poco sonno della notte scorsa. Al lavoro ho dovuto gestire una scadenza importante, e questo mi ha messo sotto pressione. Tuttavia, sono riuscito a completare il progetto e questo mi ha dato una certa soddisfazione..."

Ora genera il log basandoti sulla nostra conversazione:
"""

        # Crea una nuova conversazione solo per questo task
        messages = [
            {"role": "system", "content": "Sei un assistente che aiuta a scrivere diari personali in prima persona."},
            {"role": "user",
             "content": f"Ecco la conversazione:\n\n{self._format_conversation_for_summary()}\n\n{prompt}"}
        ]

        try:
            response = self.client.chat.completions.create(
                model=config.MODEL_NAME,
                messages=messages,
                max_tokens=400,
                temperature=0.7
            )

            return response.choices[0].message.content.strip()

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