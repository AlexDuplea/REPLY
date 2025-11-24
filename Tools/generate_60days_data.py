#!/usr/bin/env python3
"""
Script di Generazione Dati Avanzato - Mental Wellness Journal
Genera 60 giorni di entries realistici con variazioni di mood e pattern
"""

import json
import os
from datetime import datetime, timedelta, date
import random

# Configurazione
DATA_DIR = "data_test_60days"
CONVERSATIONS_DIR = os.path.join(DATA_DIR, "conversations")
ENTRIES_DIR = os.path.join(DATA_DIR, "entries")
USER_PROFILE_PATH = os.path.join(DATA_DIR, "user_profile.json")

# ===== TEMPLATE ENTRIES REALISTICI =====

# Entries positivi
POSITIVE_ENTRIES = [
    "Oggi è stata una giornata fantastica! Ho completato il progetto di machine learning che mi stava dando problemi da settimane. Sono molto soddisfatto del risultato e il prof ha fatto i complimenti. Mi sento energico e motivato.",
    
    "Bellissima giornata! Sono uscito con gli amici, abbiamo fatto una passeggiata al parco e poi pizza insieme. Mi sono sentito davvero rilassato e felice. A volte è importante staccare dallo studio.",
    
    "Oggi ho superato l'esame difficile che mi preoccupava tanto! Ho preso anche un bel voto. Sono felicissimo e orgoglioso di me stesso. Tutto lo studio è servito.",
    
    "Giornata produttiva e positiva. Ho studiato con costanza, fatto palestra e cucinato qualcosa di buono. Mi sento in equilibrio e soddisfatto di come sto gestendo le cose.",
    
    "Ho avuto un colloquio per uno stage e penso sia andato molto bene! Sono ottimista per l'esito. Mi sento motivato e pieno di energia per il futuro.",
    
    "Weekend rilassante e rigenerante. Ho dormito bene, letto un libro interessante e guardato una serie che mi piaceva. A volte fare 'niente' è esattamente quello di cui ho bisogno.",
    
    "Ottima giornata di studio! Sono entrato nel flow e non ho sentito passare il tempo. Adoro quando succede, mi fa sentire veramente appassionato di quello che faccio.",
]

# Entries neutri
NEUTRAL_ENTRIES = [
    "Giornata normale. Lezioni all'università, studio pomeridiano, un po' di palestra. Routine che mi fa sentire stabile anche se a volte un po' monotona.",
    
    "Oggi niente di particolare. Ho studiato per l'esame di algoritmi, fatto alcune commissioni e cucinato. Una giornata tranquilla senza alti e bassi.",
    
    "Ho passato la giornata a lavorare sul mio progetto personale. Progressi lenti ma costanti. Non mi sento né super motivato né demotivato, solo continuo.",
    
    "Giornata standard. Ho seguito le lezioni online, fatto un po' di esercizio fisico a casa e preparato la cena. Tutto nella norma.",
    
    "Oggi ho fatto le solite cose: università, biblioteca, casa. Mi sento ok, niente di speciale ma nemmeno male. Solo una giornata come tante.",
    
    "Ho studiato la maggior parte del giorno. Non ero particolarmente ispirato ma ho comunque fatto progressi. A volte è questione di disciplina più che di motivazione.",
]

# Entries negativi/stressati
NEGATIVE_ENTRIES = [
    "Giornata difficile. Troppo stress con l'università e gli esami in arrivo. Ho studiato fino a tardi ma non riesco a concentrarmi come vorrei. Mi sento sopraffatto.",
    
    "Oggi non è andata bene. Ho litigato con un amico per una stupidaggine e mi sento abbattuto. Ho provato a studiare ma non riuscivo a concentrarmi. Spero domani vada meglio.",
    
    "Mi sento molto stressato per la presentazione del progetto di domani. L'ansia è forte e non riesco a rilassarmi. Ho paura di non essere preparato abbastanza.",
    
    "Giornata pesante. Troppe cose da fare e poco tempo. Mi sento in ansia e un po' frustrato. Devo imparare a gestire meglio le priorità.",
    
    "Oggi mi sono svegliato con poca energia e la giornata è andata di conseguenza. Ho provato a studiare ma ero troppo stanco. Nel pomeriggio sono andato in palestra e mi ha aiutato un po'.",
    
    "Non è stata una buona giornata. Mi sento ansioso senza un motivo particolare. Ho provato a fare meditazione e mi ha aiutato un po' ma l'inquietudine c'è ancora.",
    
    "Sono sopraffatto dagli impegni. Troppi esami, troppi progetti, poco tempo. Mi sento sotto pressione e fatico a vedere la luce in fondo al tunnel.",
]

# Entries misti (iniziano male, finiscono meglio)
MIXED_ENTRIES = [
    "La giornata è iniziata male, mi sentivo stanco e demotivato. Però nel pomeriggio ho fatto una camminata e mi sono sentito meglio. A volte basta poco per cambiare prospettiva.",
    
    "Stamattina ero molto ansioso per l'esame. Alla fine è andato meglio di quanto pensassi! Devo imparare a fidarmi di più della mia preparazione.",
    
    "Oggi alti e bassi. La mattina produttiva, il pomeriggio un po' giù. Sera tranquilla con Netflix. Nel complesso una giornata ok.",
    
    "Ho iniziato la giornata stressato ma poi ho parlato con un amico e mi sono sfogato. Mi ha fatto bene condividere le mie preoccupazioni invece di tenerle dentro.",
]

# ===== PROFILI EMOTIVI =====

EMOTION_PROFILES = {
    "very_positive": {
        "stress": 0,
        "happiness": 8,
        "sadness": 0,
        "anger": 0,
        "fatigue": 0
    },
    "positive": {
        "stress": 1,
        "happiness": 6,
        "sadness": 0,
        "anger": 0,
        "fatigue": 1
    },
    "neutral": {
        "stress": 2,
        "happiness": 4,
        "sadness": 1,
        "anger": 0,
        "fatigue": 2
    },
    "negative": {
        "stress": 5,
        "happiness": 1,
        "sadness": 4,
        "anger": 1,
        "fatigue": 3
    },
    "anxious": {
        "stress": 6,
        "happiness": 2,
        "sadness": 2,
        "anger": 0,
        "fatigue": 4
    },
    "mixed": {
        "stress": 3,
        "happiness": 4,
        "sadness": 2,
        "anger": 0,
        "fatigue": 2
    }
}

# ===== CONVERSAZIONI TEMPLATE =====

CONVERSATIONS = {
    "positive": [
        [
            {"role": "assistant", "content": "Ciao Alex! Bentornato! Come è andata la giornata?"},
            {"role": "user", "content": "Ciao! È andata benissimo, ho superato l'esame!"},
            {"role": "assistant", "content": "Fantastico! Complimenti! Come ti senti?"},
            {"role": "user", "content": "Felicissimo e sollevato. Ho studiato tanto e ne è valsa la pena."},
            {"role": "assistant", "content": "È bellissimo vedere i risultati del proprio impegno. Hai festeggiato?"},
            {"role": "user", "content": "Sì, sono uscito con gli amici. È stata una bella serata."},
        ],
        [
            {"role": "assistant", "content": "Ciao Alex! Bentornato! Come è andata la giornata?"},
            {"role": "user", "content": "Molto bene! Ho fatto progressi sul mio progetto."},
            {"role": "assistant", "content": "Ottimo! Su cosa stai lavorando?"},
            {"role": "user", "content": "Un'app di machine learning. Oggi ho risolto un bug importante."},
            {"role": "assistant", "content": "Dev'essere molto soddisfacente! Ti senti motivato?"},
            {"role": "user", "content": "Sì, molto. Adoro quando le cose funzionano finalmente."},
        ],
    ],
    "neutral": [
        [
            {"role": "assistant", "content": "Ciao Alex! Bentornato! Come è andata la giornata?"},
            {"role": "user", "content": "Normale, ho studiato e fatto le solite cose."},
            {"role": "assistant", "content": "Una giornata tranquilla quindi. Come ti senti?"},
            {"role": "user", "content": "Bene, niente di particolare. Solo routine."},
            {"role": "assistant", "content": "Va bene anche avere giorni tranquilli. Hai fatto qualcosa di piacevole?"},
            {"role": "user", "content": "Ho guardato una serie la sera, mi sono rilassato."},
        ],
    ],
    "negative": [
        [
            {"role": "assistant", "content": "Ciao Alex! Bentornato! Come è andata la giornata?"},
            {"role": "user", "content": "Non benissimo, mi sento molto stressato."},
            {"role": "assistant", "content": "Mi dispiace sentirlo. Cosa ti sta preoccupando?"},
            {"role": "user", "content": "Ho troppi esami e poco tempo. Non so come farò."},
            {"role": "assistant", "content": "Capisco che possa essere opprimente. Hai provato a fare una lista delle priorità?"},
            {"role": "user", "content": "Sì, ma anche così mi sembra troppo. Mi sento sopraffatto."},
            {"role": "assistant", "content": "È normale sentirsi così in periodi intensi. Ricorda di prenderti anche delle pause. Hai dormito abbastanza?"},
            {"role": "user", "content": "Non molto, vado a letto tardi per studiare."},
        ],
        [
            {"role": "assistant", "content": "Ciao Alex! Bentornato! Come è andata la giornata?"},
            {"role": "user", "content": "Male, sono molto ansioso."},
            {"role": "assistant", "content": "Mi dispiace. Vuoi parlarne? Cosa ti sta causando ansia?"},
            {"role": "user", "content": "La presentazione di domani. Ho paura di fare brutta figura."},
            {"role": "assistant", "content": "L'ansia da prestazione è comune. Ti sei preparato bene?"},
            {"role": "user", "content": "Sì, ma ho sempre paura che non basti."},
            {"role": "assistant", "content": "Capisco. A volte la nostra mente esagera i rischi. Hai provato tecniche di respirazione?"},
            {"role": "user", "content": "Un po', mi aiutano ma l'ansia rimane."},
        ],
    ],
}

# ===== FUNZIONI UTILITY =====

def create_directories():
    """Crea la struttura directory"""
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(CONVERSATIONS_DIR, exist_ok=True)
    os.makedirs(ENTRIES_DIR, exist_ok=True)
    print(f"✅ Creata directory: {DATA_DIR}")

def generate_user_profile(num_days: int):
    """Genera profilo utente realistico"""
    # Calcola streak realistico (non tutti i giorni)
    expected_entries = num_days - random.randint(5, 15)  # Qualche giorno saltato
    current_streak = random.randint(3, 12)
    longest_streak = max(current_streak, random.randint(10, 25))
    
    profile = {
        "created_at": (datetime.now() - timedelta(days=num_days)).isoformat(),
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "total_entries": expected_entries,
        "last_entry_date": datetime.now().date().isoformat(),
        "milestones_achieved": [],
        "preferences": {
            "name": "Alex",
            "timezone": "Europe/Rome"
        }
    }
    
    # Aggiungi milestones in base allo streak
    milestones = [
        (3, "🔥 Impegno"),
        (7, "⭐ Prima Settimana"),
        (14, "💪 Due Settimane"),
        (30, "🏆 Mese di Consapevolezza"),
    ]
    
    for days, name in milestones:
        if longest_streak >= days:
            profile["milestones_achieved"].append(name)
    
    with open(USER_PROFILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Profilo utente creato: {USER_PROFILE_PATH}")
    return profile

def select_entry_by_mood_pattern(day_offset: int):
    """
    Seleziona entry basandosi su pattern realistici:
    - Weekend più rilassati
    - Picchi di stress durante settimana
    - Variazioni naturali
    """
    day_of_week = (datetime.now() - timedelta(days=day_offset)).weekday()
    
    # Weekend (5=sabato, 6=domenica) più positivi
    if day_of_week in [5, 6]:
        weights = {
            "positive": 50,
            "very_positive": 20,
            "neutral": 20,
            "mixed": 5,
            "negative": 5
        }
    # Lunedì e martedì più neutrali/negativi
    elif day_of_week in [0, 1]:
        weights = {
            "positive": 15,
            "very_positive": 5,
            "neutral": 40,
            "mixed": 20,
            "negative": 20
        }
    # Metà settimana equilibrata
    else:
        weights = {
            "positive": 30,
            "very_positive": 10,
            "neutral": 30,
            "mixed": 15,
            "negative": 15
        }
    
    # Aggiungi variazione casuale
    mood_types = list(weights.keys())
    mood_weights = list(weights.values())
    mood = random.choices(mood_types, weights=mood_weights)[0]
    
    # Seleziona entry template
    if mood == "very_positive":
        return random.choice(POSITIVE_ENTRIES), "very_positive"
    elif mood == "positive":
        return random.choice(POSITIVE_ENTRIES), "positive"
    elif mood == "neutral":
        return random.choice(NEUTRAL_ENTRIES), "neutral"
    elif mood == "negative":
        return random.choice(NEGATIVE_ENTRIES), "negative"
    else:  # mixed
        return random.choice(MIXED_ENTRIES), "mixed"

def generate_entries(num_days: int, skip_probability: float = 0.15):
    """
    Genera entries per N giorni con pattern realistici
    skip_probability: probabilità di saltare un giorno
    """
    print(f"\n📝 Generazione di {num_days} giorni di entries...")
    today = datetime.now().date()
    entries_created = 0
    
    for i in range(num_days):
        # Salta alcuni giorni randomicamente (realistico)
        if random.random() < skip_probability:
            continue
        
        date_obj = today - timedelta(days=i)
        date_str = date_obj.isoformat()
        
        # Seleziona entry basata su pattern
        entry_text, mood = select_entry_by_mood_pattern(i)
        
        # Aggiungi variazioni al testo
        variations = [
            f"Oggi è {date_obj.strftime('%A %d %B')}. {entry_text}",
            entry_text,
            f"{entry_text} È stato comunque un giorno importante.",
        ]
        final_text = random.choice(variations)
        
        # Genera emozioni
        emotions = EMOTION_PROFILES[mood].copy()
        # Aggiungi variazione random ±1
        for emotion in emotions:
            emotions[emotion] = max(0, emotions[emotion] + random.randint(-1, 1))
        
        # Determina source (chat o editor)
        source = "chat" if random.random() < 0.6 else "editor"
        
        entry_data = {
            "date": date_str,
            "timestamp": (datetime.combine(date_obj, datetime.min.time()) + 
                         timedelta(hours=random.randint(18, 23), 
                                 minutes=random.randint(0, 59))).isoformat(),
            "entry": final_text,
            "metadata": {
                "source": source,
                "emotions_detected": emotions,
                "message_count": random.randint(5, 12) if source == "chat" else 0
            }
        }
        
        filepath = os.path.join(ENTRIES_DIR, f"entry_{date_str}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(entry_data, f, indent=2, ensure_ascii=False)
        
        entries_created += 1
        if entries_created % 10 == 0:
            print(f"  ✓ {entries_created} entries creati...")
    
    print(f"✅ Creati {entries_created} entries su {num_days} giorni")
    return entries_created

def generate_conversations(num_conversations: int = 20):
    """Genera conversazioni realistiche"""
    print(f"\n💬 Generazione di {num_conversations} conversazioni...")
    today = datetime.now().date()
    
    for i in range(num_conversations):
        date_obj = today - timedelta(days=i * 3)  # Una conv ogni 3 giorni
        date_str = date_obj.isoformat()
        
        # Seleziona tipo conversazione
        mood_type = random.choice(["positive", "positive", "neutral", "negative"])
        conversation = random.choice(CONVERSATIONS.get(mood_type, CONVERSATIONS["neutral"]))
        
        conv_data = {
            "date": date_str,
            "timestamp": (datetime.combine(date_obj, datetime.min.time()) + 
                         timedelta(hours=19, minutes=random.randint(0, 59))).isoformat(),
            "messages": conversation,
            "sessions": 1
        }
        
        filepath = os.path.join(CONVERSATIONS_DIR, f"conversation_{date_str}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(conv_data, f, indent=2, ensure_ascii=False)
    
    print(f"✅ Create {num_conversations} conversazioni")

def print_summary(num_days: int, entries_created: int):
    """Stampa riepilogo generazione"""
    print("\n" + "=" * 60)
    print("📊 RIEPILOGO DATI GENERATI")
    print("=" * 60)
    
    num_entries = len([f for f in os.listdir(ENTRIES_DIR) if f.endswith('.json')])
    num_conversations = len([f for f in os.listdir(CONVERSATIONS_DIR) if f.endswith('.json')])
    
    print(f"\n📁 Directory: {DATA_DIR}")
    print(f"  📝 Entries: {num_entries}/{num_days} giorni ({(num_entries/num_days)*100:.1f}%)")
    print(f"  💬 Conversazioni: {num_conversations}")
    print(f"  👤 Profilo utente: OK")
    
    # Statistiche emozioni
    print(f"\n📈 Distribuzione Mood (approssimata):")
    print(f"  😊 Positivo: ~35%")
    print(f"  😐 Neutrale: ~30%")
    print(f"  😟 Negativo: ~20%")
    print(f"  🎭 Misto: ~15%")
    
    print("\n🚀 COME USARE I DATI:")
    print("1. Backup dati esistenti (se presenti):")
    print("   mv data data_backup")
    print("2. Usa i nuovi dati:")
    print("   mv data_test_60days data")
    print("3. Oppure modifica config.py:")
    print("   DATA_DIR = 'data_test_60days'")
    print("4. Avvia l'app:")
    print("   python app.py")
    print("5. Visita: http://localhost:5000")
    print("=" * 60 + "\n")

def main():
    """Main function"""
    print("=" * 60)
    print("🎯 GENERATORE DATI AVANZATO - 60 GIORNI")
    print("   Mental Wellness Journal")
    print("=" * 60)
    
    NUM_DAYS = 60
    NUM_CONVERSATIONS = 20
    
    # Step 1: Crea directory
    create_directories()
    
    # Step 2: Genera entries
    entries_created = generate_entries(NUM_DAYS, skip_probability=0.15)
    
    # Step 3: Genera conversazioni
    generate_conversations(NUM_CONVERSATIONS)
    
    # Step 4: Genera profilo utente
    generate_user_profile(NUM_DAYS)
    
    # Step 5: Riepilogo
    print_summary(NUM_DAYS, entries_created)
    
    print("✅ Generazione completata con successo!\n")

if __name__ == "__main__":
    main()
