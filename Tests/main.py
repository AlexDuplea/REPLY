
    def __init__(self):
        self.storage = Storage()
        self.agent = None

    def print_header(self):
        """Stampa l'intestazione dell'app"""
        print("\n" + "=" * 60)
        print("🌟  MENTAL WELLNESS JOURNAL  🌟")
        print("=" * 60)
        print()

    def print_stats(self):
        """Mostra statistiche streak"""
        stats = self.storage.get_stats()

        print(f"📊 Le tue statistiche:")
        print(f"   🔥 Streak corrente: {stats['current_streak']} giorni")
        print(f"   🏆 Streak più lungo: {stats['longest_streak']} giorni")
        print(f"   📝 Totale entries: {stats['total_entries']}")

        if stats['milestones']:
            print(f"   ⭐ Milestone raggiunte: {', '.join(stats['milestones'])}")

        print()

    def update_and_show_streak(self):
        """Aggiorna e mostra info sullo streak"""
        streak_info = self.storage.update_streak()

        if streak_info.get('new_milestone'):
            milestone = streak_info['new_milestone']
            print(f"\n🎉 CONGRATULAZIONI! 🎉")
            print(f"Hai raggiunto: {milestone['name']}")
            print(f"({milestone['days']} giorni consecutivi!)\n")

        elif streak_info['streak_continued']:
            print(f"🔥 Streak: {streak_info['current_streak']} giorni! Ottimo lavoro!\n")

        elif streak_info.get('streak_broken'):
            print(f"⚠️  Lo streak si è interrotto (era a {streak_info['previous_streak']} giorni)")
            print(f"Nessun problema! Ripartiamo da oggi 💪\n")

    def get_user_name(self) -> str:
        """Ottiene il nome dell'utente se non impostato"""
        profile = self.storage.load_user_profile()

        if profile['preferences']['name']:
            return profile['preferences']['name']

        print("👋 Sembra la tua prima volta!")
        name = input("Come ti chiami? (opzionale, premi INVIO per saltare): ").strip()

        if name:
            profile['preferences']['name'] = name
            self.storage.save_user_profile(profile)
            return name

        return None

    def run_journal_session(self):
        """Esegue una sessione completa di journaling"""
        # Header
        self.print_header()

        # Stats e streak
        self.print_stats()
        self.update_and_show_streak()
        
        # Controlla se c'è già un log oggi
        existing_log = self.storage.get_today_entry_text()
        if existing_log:
            print(f"{config.Colors.OKCYAN}ℹ️  Hai già scritto un log oggi. Le nuove informazioni verranno aggiunte.{config.Colors.ENDC}\n")

        # Nome utente
        user_name = self.get_user_name()

        # Inizializza agente
        print("💭 Avvio sessione...\n")
        self.agent = MentalWellnessAgent()

        # Carica contesto (ultimi 3 giorni)
        context = self._build_context()

        # Inizia conversazione
        greeting = self.agent.start_session(user_name, context)
        print(f"{config.Colors.OKCYAN}AI: {greeting}{config.Colors.ENDC}\n")

        # Loop conversazionale
        while True:
            try:
                user_input = input(f"{config.Colors.OKGREEN}Tu: {config.Colors.ENDC}").strip()

                if not user_input:
                    continue

                # Invia messaggio all'agente
                result = self.agent.chat(user_input)

                print(f"\n{config.Colors.OKCYAN}AI: {result['response']}{config.Colors.ENDC}\n")

                # Termina se richiesto o crisi
                if result['should_end']:
                    if result['crisis_detected']:
                        print(f"{config.Colors.WARNING}Sessione terminata per sicurezza.{config.Colors.ENDC}\n")
                        return
                    else:
                        # Chiedi conferma salvataggio
                        self._end_session()
                        return

            except KeyboardInterrupt:
                print(f"\n\n{config.Colors.WARNING}Sessione interrotta.{config.Colors.ENDC}")
                save = input("Vuoi salvare la conversazione? (s/n): ").lower()
                if save == 's':
                    self._save_session()
                return

            except Exception as e:
                print(f"\n{config.Colors.FAIL}Errore: {str(e)}{config.Colors.ENDC}\n")
                return

    def _build_context(self) -> str:
        """Costruisce contesto dalle ultime entries"""
        recent_entries = self.storage.get_recent_entries(num_days=3)

        if not recent_entries:
            return None

        context_parts = ["Ecco cosa ha scritto recentemente l'utente:\n"]

        for entry_data in recent_entries:
            date_str = entry_data['date']
            entry_text = entry_data['entry']
            # Prendi solo le prime 2 frasi per non sovraccaricare
            summary = '. '.join(entry_text.split('.')[:2]) + '.'
            context_parts.append(f"- {date_str}: {summary}")

        return "\n".join(context_parts)

    def _end_session(self):
        """Termina la sessione salvando tutto"""
        print("\n" + "-" * 60)
        print("📝 Generazione log giornaliero...\n")

        # Controlla se esiste già un log oggi
        existing_log = self.storage.get_today_entry_text()
        
        # Genera entry narrativo (combinando con quello esistente se presente)
        journal_entry = self.agent.generate_journal_entry(existing_entry=existing_log)

        print(f"{config.Colors.BOLD}Il tuo diario di oggi:{config.Colors.ENDC}\n")
        print(f"{config.Colors.OKCYAN}{journal_entry}{config.Colors.ENDC}\n")

        # Chiedi conferma
        save = input(f"\n{config.Colors.BOLD}Salvare questo log? (s/n): {config.Colors.ENDC}").lower()

        if save == 's':
            self._save_session(journal_entry)
            print(f"\n{config.Colors.OKGREEN}✅ Log salvato con successo!{config.Colors.ENDC}")
        else:
            print(f"\n{config.Colors.WARNING}Log non salvato.{config.Colors.ENDC}")

        print("\n" + "=" * 60)
        print("Grazie per aver usato Mental Wellness Journal! 💙")
        print("Ci vediamo domani! 🌟")
        print("=" * 60 + "\n")

    def _save_session(self, journal_entry: str = None):
        """Salva conversazione ed entry"""
        today = date.today().isoformat()

        # Salva conversazione
        conversation = self.agent.get_conversation_history()
        self.storage.save_conversation(conversation, today)

        # Salva entry se fornito
        if journal_entry:
            # Estrai emozioni
            emotions = self.agent.extract_emotions()

            metadata = {
                "emotions_detected": emotions,
                "message_count": len([m for m in conversation if m["role"] == "user"])
            }

            self.storage.save_entry(journal_entry, metadata, today)

    def show_menu(self):
        """Mostra menu principale"""
        self.print_header()

        print("Cosa vuoi fare?\n")
        print("1. 📝 Nuova sessione di journaling")
        print("2. 📊 Visualizza statistiche")
        print("3. 📖 Leggi entries passati")
        print("4. ❌ Esci\n")

        choice = input("Scelta: ").strip()
        return choice

    def view_past_entries(self):
        """Visualizza entries passati"""
        print("\n" + "=" * 60)
        print("📖  ENTRIES PASSATI")
        print("=" * 60 + "\n")

        num = input("Quanti giorni vuoi vedere? (max 30): ").strip()
        try:
            num = int(num)
            num = min(num, 30)
        except:
            num = 7

        entries = self.storage.get_recent_entries(num)

        if not entries:
            print("Nessun entry trovato.\n")
            return

        for entry_data in entries:
            print(f"\n{config.Colors.BOLD}📅 {entry_data['date']}{config.Colors.ENDC}")
            print("-" * 60)
            print(entry_data['entry'])
            print()

        input("\nPremi INVIO per tornare al menu...")

    def run(self):
        """Main loop dell'applicazione"""
        while True:
            choice = self.show_menu()

            if choice == '1':
                self.run_journal_session()

            elif choice == '2':
                self.print_header()
                self.print_stats()
                input("\nPremi INVIO per tornare al menu...")

            elif choice == '3':
                self.view_past_entries()

            elif choice == '4':
                print(f"\n{config.Colors.OKGREEN}Arrivederci! 💙{config.Colors.ENDC}\n")
                break

            else:
                print(f"\n{config.Colors.WARNING}Scelta non valida.{config.Colors.ENDC}\n")


def main():
    """Entry point"""
    try:
        app = TerminalInterface()
        app.run()
    except KeyboardInterrupt:
        print(f"\n\n{config.Colors.OKGREEN}Arrivederci! 💙{config.Colors.ENDC}\n")
        sys.exit(0)
    except Exception as e:
        print(f"\n{config.Colors.FAIL}Errore critico: {str(e)}{config.Colors.ENDC}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()