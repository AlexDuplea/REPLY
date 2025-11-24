#!/usr/bin/env python3
"""
Script di debug per verificare il caricamento degli entries
"""

import os
import json
from storage import Storage
import config

def debug_entries():
    print("=" * 60)
    print("DEBUG: Visualizzazione Entries")
    print("=" * 60 + "\n")
    
    # 1. Verifica directory
    print("📁 Verifica directory entries:")
    entries_dir = config.ENTRIES_DIR
    print(f"   Path: {entries_dir}")
    
    if not os.path.exists(entries_dir):
        print(f"   ❌ Directory non esiste!")
        return
    
    print(f"   ✅ Directory esiste\n")
    
    # 2. Lista file
    print("📄 File nella directory:")
    try:
        files = os.listdir(entries_dir)
        if not files:
            print("   ⚠️  Directory vuota!")
            return
        
        for f in files:
            filepath = os.path.join(entries_dir, f)
            size = os.path.getsize(filepath)
            print(f"   - {f} ({size} bytes)")
        print()
    except Exception as e:
        print(f"   ❌ Errore lettura directory: {e}")
        return
    
    # 3. Tenta caricamento manuale
    print("📖 Caricamento manuale entries:")
    entry_files = [f for f in files if f.startswith("entry_") and f.endswith(".json")]
    
    if not entry_files:
        print("   ⚠️  Nessun file entry_*.json trovato!")
        return
    
    for filename in sorted(entry_files, reverse=True):
        filepath = os.path.join(entries_dir, filename)
        print(f"\n   File: {filename}")
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            print(f"   ✅ JSON valido")
            print(f"   Data: {data.get('date', 'N/A')}")
            print(f"   Entry: {data.get('entry', 'N/A')[:50]}...")
        
        except json.JSONDecodeError as e:
            print(f"   ❌ JSON corrotto: {e}")
        except Exception as e:
            print(f"   ❌ Errore: {e}")
    
    # 4. Usa metodo Storage
    print("\n" + "=" * 60)
    print("🔧 Test metodo Storage.get_recent_entries():")
    print("=" * 60 + "\n")
    
    storage = Storage()
    
    try:
        entries = storage.get_recent_entries(num_days=10)
        
        if not entries:
            print("❌ Nessun entry ritornato dal metodo Storage!")
            print("\nPossibili cause:")
            print("1. File corrotti")
            print("2. Problema nel metodo get_recent_entries()")
            print("3. Encoding del file")
        else:
            print(f"✅ Trovati {len(entries)} entries:\n")
            
            for i, entry_data in enumerate(entries, 1):
                print(f"{i}. Data: {entry_data.get('date')}")
                entry_text = entry_data.get('entry', '')
                print(f"   Entry: {entry_text[:80]}...")
                print()
    
    except Exception as e:
        print(f"❌ Errore nel metodo get_recent_entries(): {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_entries()
