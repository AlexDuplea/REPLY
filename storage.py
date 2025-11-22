"""
Gestione dello storage dei dati (JSON-based)
"""

import json
import os
from datetime import datetime, date
from typing import Dict, List, Optional
import config


class Storage:
    """Gestisce il salvataggio e caricamento di tutti i dati dell'applicazione"""

    def __init__(self):
        """Inizializza le directory necessarie"""
        self._ensure_directories()
        self._ensure_user_profile()

    def _ensure_directories(self):
        """Crea le directory se non esistono"""
        os.makedirs(config.DATA_DIR, exist_ok=True)
        os.makedirs(config.CONVERSATIONS_DIR, exist_ok=True)
        os.makedirs(config.ENTRIES_DIR, exist_ok=True)

    def _ensure_user_profile(self):
        """Crea il profilo utente se non esiste"""
        if not os.path.exists(config.USER_PROFILE_PATH):
            default_profile = {
                "created_at": datetime.now().isoformat(),
                "current_streak": 0,
                "longest_streak": 0,
                "total_entries": 0,
                "last_entry_date": None,
                "milestones_achieved": [],
                "preferences": {
                    "name": None,
                    "timezone": "Europe/Rome"
                }
            }
            self.save_user_profile(default_profile)

    # ========== USER PROFILE ==========

    def load_user_profile(self) -> Dict:
        """Carica il profilo utente"""
        with open(config.USER_PROFILE_PATH, 'r', encoding='utf-8') as f:
            return json.load(f)

    def save_user_profile(self, profile: Dict):
        """Salva il profilo utente"""
        with open(config.USER_PROFILE_PATH, 'w', encoding='utf-8') as f:
            json.dump(profile, f, indent=2, ensure_ascii=False)

    def update_streak(self) -> Dict:
        """
        Aggiorna lo streak basandosi sulla data corrente.
        Returns: dict con info su streak e milestone raggiunta (se presente)
        """
        profile = self.load_user_profile()
        today = date.today().isoformat()
        last_entry = profile.get("last_entry_date")

        result = {
            "streak_continued": False,
            "streak_broken": False,
            "new_milestone": None,
            "current_streak": 0
        }

        if last_entry is None:
            # Prima entry in assoluto
            profile["current_streak"] = 1
            profile["last_entry_date"] = today
            result["streak_continued"] = True
            result["current_streak"] = 1

        elif last_entry == today:
            # Già scritto oggi
            result["current_streak"] = profile["current_streak"]
            return result

        else:
            # Calcola differenza giorni
            last_date = date.fromisoformat(last_entry)
            today_date = date.today()
            days_diff = (today_date - last_date).days

            if days_diff == 1:
                # Streak continua!
                profile["current_streak"] += 1
                profile["last_entry_date"] = today
                result["streak_continued"] = True
                result["current_streak"] = profile["current_streak"]

                # Controlla milestone
                streak = profile["current_streak"]
                if streak in config.STREAK_MILESTONES:
                    milestone_name = config.STREAK_MILESTONES[streak]
                    if milestone_name not in profile["milestones_achieved"]:
                        profile["milestones_achieved"].append(milestone_name)
                        result["new_milestone"] = {
                            "days": streak,
                            "name": milestone_name
                        }

                # Aggiorna longest streak
                if profile["current_streak"] > profile["longest_streak"]:
                    profile["longest_streak"] = profile["current_streak"]

            else:
                # Streak interrotto
                result["streak_broken"] = True
                result["previous_streak"] = profile["current_streak"]
                profile["current_streak"] = 1
                profile["last_entry_date"] = today
                result["current_streak"] = 1

        # Incrementa totale entries
        profile["total_entries"] += 1

        self.save_user_profile(profile)
        return result

    # ========== CONVERSATIONS ==========

    def save_conversation(self, conversation: List[Dict], entry_date: Optional[str] = None):
        """
        Salva una conversazione completa
        conversation: lista di dict {"role": "user/assistant", "content": "..."}
        """
        if entry_date is None:
            entry_date = date.today().isoformat()

        filename = f"conversation_{entry_date}.json"
        filepath = os.path.join(config.CONVERSATIONS_DIR, filename)

        data = {
            "date": entry_date,
            "timestamp": datetime.now().isoformat(),
            "messages": conversation
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_conversation(self, entry_date: str) -> Optional[List[Dict]]:
        """Carica una conversazione specifica"""
        filename = f"conversation_{entry_date}.json"
        filepath = os.path.join(config.CONVERSATIONS_DIR, filename)

        if not os.path.exists(filepath):
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get("messages", [])

    # ========== ENTRIES (log giornalieri narrativi) ==========

    def save_entry(self, entry_text: str, metadata: Optional[Dict] = None,
                   entry_date: Optional[str] = None):
        """
        Salva un log giornaliero narrativo generato dall'AI
        """
        if entry_date is None:
            entry_date = date.today().isoformat()

        filename = f"entry_{entry_date}.json"
        filepath = os.path.join(config.ENTRIES_DIR, filename)

        data = {
            "date": entry_date,
            "timestamp": datetime.now().isoformat(),
            "entry": entry_text,
            "metadata": metadata or {}
        }

        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    def load_entry(self, entry_date: str) -> Optional[Dict]:
        """Carica un entry specifico"""
        filename = f"entry_{entry_date}.json"
        filepath = os.path.join(config.ENTRIES_DIR, filename)

        if not os.path.exists(filepath):
            return None

        with open(filepath, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_recent_entries(self, num_days: int = 7) -> List[Dict]:
        """Ottiene gli ultimi N giorni di entries"""
        entries = []

        for filename in sorted(os.listdir(config.ENTRIES_DIR), reverse=True):
            if filename.startswith("entry_") and filename.endswith(".json"):
                filepath = os.path.join(config.ENTRIES_DIR, filename)
                with open(filepath, 'r', encoding='utf-8') as f:
                    entries.append(json.load(f))

                if len(entries) >= num_days:
                    break

        return entries

    # ========== UTILITY ==========

    def get_stats(self) -> Dict:
        """Ottiene statistiche generali"""
        profile = self.load_user_profile()

        return {
            "total_entries": profile["total_entries"],
            "current_streak": profile["current_streak"],
            "longest_streak": profile["longest_streak"],
            "milestones": profile["milestones_achieved"],
            "last_entry": profile["last_entry_date"]
        }