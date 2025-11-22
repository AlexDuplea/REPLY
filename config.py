"""
Configurazione dell'applicazione Mental Wellness Journal
"""

import os
from dotenv import load_dotenv

# Carica variabili d'ambiente
load_dotenv()

# API Configuration
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
MODEL_NAME = "gpt-4o-mini"  # Più economico, ottimo per conversazioni
MAX_TOKENS = 500
TEMPERATURE = 0.7  # Bilanciamento creatività/coerenza

# Paths
DATA_DIR = "data"
CONVERSATIONS_DIR = os.path.join(DATA_DIR, "conversations")
ENTRIES_DIR = os.path.join(DATA_DIR, "entries")
USER_PROFILE_PATH = os.path.join(DATA_DIR, "user_profile.json")

# Agent Behavior
SYSTEM_PROMPT = """Sei un Mental Wellness Coach AI empatico e professionale.

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
- Valida le emozioni dell'utente quando appropriato, ma non essere automaticamente d'accordo con tutto
- Offri prospettive alternative quando può essere utile alla riflessione
- Mantieni un approccio equilibrato tra supporto e stimolo al pensiero critico
- NON usare emoji

Quando l'utente scrive "fine" o "basta":
- Ringrazia brevemente (1 riga)
- Crea un riassunto MINIMALISTA e STRETTAMENTE PROPORZIONATO:
  * 1-2 scambi: UNA frase semplice (max 15 parole)
  * 3-4 scambi: 2 frasi brevi (max 25 parole totali)
  * 5-7 scambi: 3 frasi concise (max 40 parole totali)
  * 8+ scambi: 1 breve paragrafo (max 60 parole)
- Usa SOLO le parole chiave e i fatti concreti menzionati dall'utente
- VIETATO aggiungere:
  * Interpretazioni psicologiche
  * Emozioni non esplicitamente nominate
  * Contesto o dettagli inventati
  * Consigli o riflessioni
  * Elaborazioni o parafrasi lunghe
- Se l'utente ha scritto poco, il riassunto deve essere CORTISSIMO
- Chiedi conferma per salvare
"""

# Streak Configuration
STREAK_MILESTONES = {
    3: "🔥 Impegno",
    7: "⭐ Prima Settimana",
    14: "💪 Due Settimane",
    30: "🏆 Mese di Consapevolezza",
    60: "🎯 Due Mesi",
    100: "👑 Maestro del Benessere"
}

# Emotional Keywords (per analisi semplice)
EMOTION_KEYWORDS = {
    "stress": ["stressato", "stress", "stressante", "ansia", "ansioso", "preoccupato", "nervoso"],
    "happiness": ["felice", "contento", "gioioso", "bene", "ottimo", "fantastico", "benissimo"],
    "sadness": ["triste", "tristezza", "male", "giù", "depresso", "abbattuto"],
    "anger": ["arrabbiato", "rabbia", "furioso", "irritato", "frustrato"],
    "fatigue": ["stanco", "esausto", "affaticato", "spossato", "sfinito"]
}

# Safety Keywords (da escalare a professionista)
CRISIS_KEYWORDS = [
    "suicidio", "uccidermi", "farla finita", "non voglio vivere",
    "autolesionismo", "farmi male", "voglio morire"
]

CRISIS_MESSAGE = """
⚠️ IMPORTANTE: Ho notato che stai attraversando un momento molto difficile.

Ti prego di contattare immediatamente:
- Telefono Amico: 02 2327 2327 (tutti i giorni 10-24)
- Emergenza: 112
- Centro di Salute Mentale della tua zona

Non sei solo/a. Ci sono professionisti pronti ad aiutarti.
Questo strumento non può sostituire il supporto umano professionale.
"""

# Colors per terminale (opzionale)
class Colors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'