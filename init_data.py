#!/usr/bin/env python3
"""
Script per inizializzare o resettare i dati dell'applicazione
"""

import os
import json
from datetime import datetime
import shutil


def init_data_directory():
    """Crea la struttura delle directory"""
    print("📁 Creazione struttura directory...")

    directories = [
        'data',
        'data/conversations',
        'data/entries'
    ]

    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"   ✅ {directory}")


def create_user_profile():
    """Crea un nuovo profilo utente"""
    print("\n👤 Creazione profilo utente...")

    profile = {
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

    profile_path = 'data/user_profile.json'

    with open(profile_path, 'w', encoding='utf-8') as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)

    print(f"   ✅ Profilo creato: {profile_path}")


def reset_all_data():
    """Reset completo di tutti i dati (con backup)"""
    print("\n⚠️  RESET COMPLETO DEI DATI")

    if os.path.exists('data'):
        # Crea backup
        backup_name = f"data_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        print(f"\n📦 Creazione backup in: {backup_name}")

        try:
            shutil.copytree('data', backup_name)
            print(f"   ✅ Backup creato")
        except Exception as e:
            print(f"   ⚠️  Errore backup: {e}")

        # Elimina data
        shutil.rmtree('data')
        print("   ✅ Vecchi dati rimossi")

    # Ricrea tutto
    init_data_directory()
    create_user_profile()

    print("\n✅ Reset completato!")


def fix_corrupted_profile():
    """Fix solo del profilo corrotto"""
    print("\n🔧 Fix profilo corrotto...")

    profile_path = 'data/user_profile.json'

    # Prova a leggere il profilo esistente
    existing_data = {}
    if os.path.exists(profile_path):
        try:
            with open(profile_path, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            print("   ℹ️  Profilo esistente letto correttamente")
        except:
            print("   ⚠️  Profilo corrotto, verrà ricreato")

    # Crea nuovo profilo mantenendo dati se possibile
    profile = {
        "created_at": existing_data.get("created_at", datetime.now().isoformat()),
        "current_streak": existing_data.get("current_streak", 0),
        "longest_streak": existing_data.get("longest_streak", 0),
        "total_entries": existing_data.get("total_entries", 0),
        "last_entry_date": existing_data.get("last_entry_date", None),
        "milestones_achieved": existing_data.get("milestones_achieved", []),
        "preferences": existing_data.get("preferences", {
            "name": None,
            "timezone": "Europe/Rome"
        })
    }

    with open(profile_path, 'w', encoding='utf-8') as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)

    print(f"   ✅ Profilo salvato correttamente")


def main():
    print("=" * 60)
    print("MENTAL WELLNESS JOURNAL - Gestione Dati")
    print("=" * 60)

    print("\nCosa vuoi fare?\n")
    print("1. Inizializza dati (prima installazione)")
    print("2. Fix profilo corrotto (mantiene conversazioni)")
    print("3. Reset completo (con backup)")
    print("4. Esci\n")

    choice = input("Scelta: ").strip()

    if choice == '1':
        init_data_directory()
        create_user_profile()
        print("\n✅ Inizializzazione completata!")
        print("Ora puoi eseguire: python main.py")

    elif choice == '2':
        init_data_directory()
        fix_corrupted_profile()
        print("\n✅ Fix completato!")
        print("Ora puoi eseguire: python main.py")

    elif choice == '3':
        confirm = input("\n⚠️  Sicuro? Tutti i dati saranno resettati (y/n): ")
        if confirm.lower() == 'y':
            reset_all_data()
            print("Ora puoi eseguire: python main.py")
        else:
            print("Operazione annullata")

    elif choice == '4':
        print("Arrivederci!")

    else:
        print("Scelta non valida")

    print("\n" + "=" * 60 + "\n")


if __name__ == "__main__":
    main()