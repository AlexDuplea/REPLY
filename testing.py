#!/usr/bin/env python3
"""
Test di verifica configurazione
Controlla che tutto sia pronto senza chiamare OpenAI
"""

import sys
import os

def test_imports():
    """Verifica che tutti i moduli si importino correttamente"""
    print("🧪 Test 1: Importazione moduli...")
    try:
        import config
        import storage
        import agent
        import main
        print("   ✅ Tutti i moduli importati correttamente")
        return True
    except ImportError as e:
        print(f"   ❌ Errore importazione: {e}")
        return False

def test_dependencies():
    """Verifica dipendenze installate"""
    print("\n🧪 Test 2: Dipendenze...")
    try:
        import openai
        import dotenv
        print("   ✅ openai installato")
        print("   ✅ python-dotenv installato")
        return True
    except ImportError as e:
        print(f"   ❌ Dipendenza mancante: {e}")
        print("   Esegui: pip install -r requirements.txt")
        return False

def test_api_key():
    """Verifica che l'API key sia configurata"""
    print("\n🧪 Test 3: Configurazione API Key...")
    import config

    if not config.OPENAI_API_KEY:
        print("   ❌ OPENAI_API_KEY non trovata nel file .env")
        print("   Apri .env e inserisci la tua chiave API")
        return False

    if config.OPENAI_API_KEY == "your-api-key-here":
        print("   ⚠️  OPENAI_API_KEY è ancora il valore di default")
        print("   Apri .env e inserisci la tua vera chiave API")
        return False

    # Nasconde la chiave tranne prime/ultime 4 caratteri
    key_preview = config.OPENAI_API_KEY[:8] + "..." + config.OPENAI_API_KEY[-4:]
    print(f"   ✅ API Key configurata: {key_preview}")
    return True

def test_storage():
    """Verifica che lo storage funzioni"""
    print("\n🧪 Test 4: Sistema storage...")
    try:
        from storage import Storage
        storage = Storage()
        profile = storage.load_user_profile()
        print(f"   ✅ Storage inizializzato")
        print(f"   ✅ Profilo caricato: {profile['total_entries']} entries")
        return True
    except Exception as e:
        print(f"   ❌ Errore storage: {e}")
        return False

def test_directories():
    """Verifica struttura directory"""
    print("\n🧪 Test 5: Struttura directory...")

    required_dirs = ['data', 'data/conversations', 'data/entries']
    all_ok = True

    for dir_path in required_dirs:
        if os.path.exists(dir_path):
            print(f"   ✅ {dir_path} esiste")
        else:
            print(f"   ❌ {dir_path} mancante")
            all_ok = False

    return all_ok

def main():
    print("=" * 60)
    print("MENTAL WELLNESS JOURNAL - Verifica Configurazione")
    print("=" * 60 + "\n")

    tests = [
        test_imports,
        test_dependencies,
        test_directories,
        test_storage,
        test_api_key
    ]

    results = []
    for test in tests:
        results.append(test())

    print("\n" + "=" * 60)

    if all(results):
        print("✅ TUTTI I TEST SUPERATI!")
        print("\nPuoi avviare l'applicazione con:")
        print("   python main.py")
    else:
        print("❌ ALCUNI TEST FALLITI")
        print("\nRisolvi i problemi sopra prima di avviare l'app.")

    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()