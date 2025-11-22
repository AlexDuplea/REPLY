"""
Wellness Agent - Agente AI per suggerimenti personalizzati sul benessere mentale
Analizza i log dell'utente e fornisce consigli basati sui pattern rilevati
"""

from openai import OpenAI
from typing import List, Dict, Optional
import config
from storage import Storage

class WellnessAgent:
    """Agente AI specializzato per analisi e suggerimenti di benessere"""
    
    def __init__(self):
        """Inizializza l'agente wellness"""
        if not config.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY non trovata!")
        
        self.client = OpenAI(api_key=config.OPENAI_API_KEY)
        self.storage = Storage()
    
    def get_personalized_suggestions(self, num_days: int = 7) -> Dict:
        """
        Genera suggerimenti personalizzati basati sui log recenti
        
        Args:
            num_days: Numero di giorni di log da analizzare
        
        Returns:
            Dict con suggerimenti, pattern identificati, e consigli
        """
        # Carica entries recenti
        recent_entries = self.storage.get_recent_entries(num_days)
        
        if not recent_entries:
            return self._get_default_suggestions()
        
        # Costruisci contesto per l'AI
        context = self._build_context(recent_entries)
        
        # Genera suggerimenti con AI
        suggestions = self._generate_ai_suggestions(context)
        
        return suggestions
    
    def _build_context(self, entries: List[Dict]) -> str:
        """Costruisce contesto dai log per l'AI"""
        context_parts = ["Analizza questi ultimi giorni di diario dell'utente:\n"]
        
        for entry_data in entries:
            date = entry_data['date']
            text = entry_data['entry']
            
            # Limita lunghezza per non superare token
            text_preview = text[:500] + "..." if len(text) > 500 else text
            
            context_parts.append(f"\n--- {date} ---")
            context_parts.append(text_preview)
            
            # Aggiungi metadata se presente
            if 'metadata' in entry_data and entry_data['metadata']:
                emotions = entry_data['metadata'].get('emotions_detected', {})
                if emotions:
                    context_parts.append(f"Emozioni: {emotions}")
        
        return "\n".join(context_parts)
    
    def _generate_ai_suggestions(self, context: str) -> Dict:
        """Chiama OpenAI per generare suggerimenti personalizzati"""
        
        system_prompt = """Sei un wellness coach esperto e empatico. 
        
Il tuo compito:
1. Analizzare i diari recenti dell'utente
2. Identificare pattern emotivi (stress, felicità, energie, problemi ricorrenti)
3. Fornire 3-4 suggerimenti CONCRETI e PERSONALIZZATI per migliorare il benessere

Regole:
- Sii empatico e non giudicante
- Suggerimenti pratici e attuabili
- Basati sui pattern specifici dell'utente, non generici
- Breve e diretto (max 2-3 frasi per suggerimento)
- Usa emoji appropriati ma con moderazione

Formato risposta JSON:
{
    "summary": "Breve osservazione su come sta l'utente (2 frasi max)",
    "patterns": ["pattern1", "pattern2"],
    "suggestions": [
        {
            "title": "Titolo suggerimento",
            "description": "Descrizione pratica"
        }
    ]
}

IMPORTANTE: NON usare emoji nei suggerimenti, solo testo pulito."""

        user_prompt = f"""{context}

Basandoti SOLO su questi diari, genera suggerimenti personalizzati.

IMPORTANTE: Rispondi SOLO con un oggetto JSON valido, senza altro testo."""

        try:
            response = self.client.chat.completions.create(
                model=config.MODEL_NAME,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                max_tokens=800,
                temperature=0.7
            )

            response_text = response.choices[0].message.content.strip()

            # Rimuovi markdown se presente
            response_text = response_text.replace("```json", "").replace("```", "").strip()

            # Parse JSON
            import json
            suggestions = json.loads(response_text)

            return suggestions

        except Exception as e:
            print(f"Errore generazione suggerimenti AI: {e}")
            return self._get_default_suggestions()

    def _get_default_suggestions(self) -> Dict:
        """Suggerimenti di default se non ci sono log o errori"""
        return {
            "summary": "Benvenuto! Non ho ancora abbastanza informazioni per suggerimenti personalizzati, ma ecco alcuni consigli universali.",
            "patterns": [],
            "suggestions": [
                {
                    "title": "Pratica la Gratitudine",
                    "description": "Prova a scrivere 3 cose per cui sei grato oggi. La ricerca mostra che questa pratica aumenta il benessere emotivo."
                },
                {
                    "title": "Respirazione 4-7-8",
                    "description": "Inspira per 4 secondi, trattieni per 7, espira per 8. Ripeti 3 volte per ridurre lo stress."
                },
                {
                    "title": "Movimento Quotidiano",
                    "description": "Anche solo 15 minuti di camminata possono migliorare l'umore e ridurre l'ansia."
                },
                {
                    "title": "Routine del Sonno",
                    "description": "Cerca di andare a dormire e svegliarti alla stessa ora ogni giorno. Il sonno regolare è fondamentale per la salute mentale."
                }
            ]
        }

    def get_quick_tip(self) -> str:
        """Genera un quick tip giornaliero"""
        tips = [
            "💧 Ricordati di bere acqua! L'idratazione influenza anche l'umore.",
            "🌤️ Prova a passare 10 minuti alla luce naturale oggi.",
            "📱 Fai una pausa dagli schermi per 20 minuti.",
            "🎵 Ascolta una canzone che ti fa stare bene.",
            "🙏 Ringrazia qualcuno oggi, anche per piccole cose.",
            "✍️ Scrivi una cosa che hai fatto bene oggi.",
            "🧘 3 respiri profondi adesso. Inspira... espira...",
            "💪 Fai stretching per 5 minuti, il tuo corpo ti ringrazierà.",
        ]

        import random
        return random.choice(tips)