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
            # Gestisci caso in cui last_entry è un datetime completo invece di solo data
            if len(last_entry) > 10:
                last_entry = last_entry[:10]
            
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

        # Se esiste già una conversazione oggi, aggiungi invece di sovrascrivere
        existing_data = None
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)

        if existing_data:
            # Aggiungi le nuove conversazioni a quelle esistenti
            data = {
                "date": entry_date,
                "timestamp": datetime.now().isoformat(),
                "messages": existing_data["messages"] + conversation,
                "sessions": existing_data.get("sessions", 1) + 1
            }
        else:
            # Prima conversazione della giornata
            data = {
                "date": entry_date,
                "timestamp": datetime.now().isoformat(),
                "messages": conversation,
                "sessions": 1
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
        Se esiste già un entry per oggi, lo sovrascrive (perché sarà già stato combinato)
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
    
    def get_today_entry_text(self) -> Optional[str]:
        """
        Ottiene il testo del log di oggi se esiste
        Returns: Il testo del log o None se non esiste
        """
        today = date.today().isoformat()
        entry_data = self.load_entry(today)
        
        if entry_data:
            return entry_data.get("entry")
        return None

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
            # Gestisci caso in cui last_entry è un datetime completo invece di solo data
            if len(last_entry) > 10:
                last_entry = last_entry[:10]
            
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

        # Se esiste già una conversazione oggi, aggiungi invece di sovrascrivere
        existing_data = None
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)

        if existing_data:
            # Aggiungi le nuove conversazioni a quelle esistenti
            data = {
                "date": entry_date,
                "timestamp": datetime.now().isoformat(),
                "messages": existing_data["messages"] + conversation,
                "sessions": existing_data.get("sessions", 1) + 1
            }
        else:
            # Prima conversazione della giornata
            data = {
                "date": entry_date,
                "timestamp": datetime.now().isoformat(),
                "messages": conversation,
                "sessions": 1
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
        Se esiste già un entry per oggi, lo sovrascrive (perché sarà già stato combinato)
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
    
    def get_today_entry_text(self) -> Optional[str]:
        """
        Ottiene il testo del log di oggi se esiste
        Returns: Il testo del log o None se non esiste
        """
        today = date.today().isoformat()
        entry_data = self.load_entry(today)
        
        if entry_data:
            return entry_data.get("entry")
        return None

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
        
        # Calcola statistiche estese
        extended_stats = self.get_extended_stats()

        return {
            "total_entries": profile["total_entries"],
            "current_streak": profile["current_streak"],
            "longest_streak": profile["longest_streak"],
            "milestones": profile["milestones_achieved"],
            "last_entry": profile["last_entry_date"],
            **extended_stats
        }

    def get_extended_stats(self) -> Dict:
        """Calcola statistiche avanzate dai dati grezzi"""
        all_entries = self.get_recent_entries(num_days=3650) # Prendi tutto
        
        total_words = 0
        entries_by_weekday = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:0} # 0=Lun
        entries_by_hour = {"Morning": 0, "Afternoon": 0, "Evening": 0, "Night": 0}
        emotions_count = {}
        
        if not all_entries:
            return {
                "total_words": 0,
                "avg_words_per_entry": 0,
                "entries_per_week": 0,
                "insights": {
                    "productive_day": "-",
                    "productive_time": "-",
                    "prevalent_emotion": "-"
                }
            }

        # Analizza ogni entry
        for entry in all_entries:
            # Word count
            text = entry.get("entry", "")
            words = len(text.split())
            total_words += words
            
            # Timestamp analysis
            try:
                dt = datetime.fromisoformat(entry["timestamp"])
                
                # Weekday
                entries_by_weekday[dt.weekday()] += 1
                
                # Time of day
                h = dt.hour
                if 5 <= h < 12: entries_by_hour["Morning"] += 1
                elif 12 <= h < 17: entries_by_hour["Afternoon"] += 1
                elif 17 <= h < 22: entries_by_hour["Evening"] += 1
                else: entries_by_hour["Night"] += 1
                
            except (ValueError, KeyError):
                pass
                
            # Emotions
            meta = entry.get("metadata", {}).get("emotions_detected", {})
            for emotion, value in meta.items():
                if value > 0:
                    emotions_count[emotion] = emotions_count.get(emotion, 0) + value

        # Calcoli finali
        days_active = (datetime.now() - datetime.fromisoformat(all_entries[-1]["date"])).days + 1
        weeks_active = max(days_active / 7, 1)
        
        # Trova massimi
        best_day_idx = max(entries_by_weekday, key=entries_by_weekday.get)
        days_map = ["Lunedì", "Martedì", "Mercoledì", "Giovedì", "Venerdì", "Sabato", "Domenica"]
        
        best_time = max(entries_by_hour, key=entries_by_hour.get)
        time_map = {
            "Morning": "Mattina", "Afternoon": "Pomeriggio", 
            "Evening": "Sera", "Night": "Notte"
        }
        
        best_emotion = max(emotions_count, key=emotions_count.get) if emotions_count else "-"

        return {
            "total_words": total_words,
            "avg_words_per_entry": int(total_words / len(all_entries)),
            "entries_per_week": round(len(all_entries) / weeks_active, 1),
            "insights": {
                "productive_day": days_map[best_day_idx],
                "productive_time": time_map.get(best_time, best_time),
                "prevalent_emotion": best_emotion
            }
        }