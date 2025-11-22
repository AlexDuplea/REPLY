#!/usr/bin/env python3
# Script per generare dati di test per Mental Wellness Journal

import json
import os
from datetime import datetime, timedelta
import random

# Configurazione
DATA_DIR = "data_test"
CONVERSATIONS_DIR = os.path.join(DATA_DIR, "conversations")
ENTRIES_DIR = os.path.join(DATA_DIR, "entries")
USER_PROFILE_PATH = os.path.join(DATA_DIR, "user_profile.json")

# Template di entries realistici
ENTRY_TEMPLATES = [
    "Oggi e stata una giornata produttiva. Ho completato il progetto di machine learning e mi sento soddisfatto del risultato. Un po' stanco ma contento.",

    "Giornata difficile. Troppo stress con l'universita e gli esami in arrivo. Ho studiato fino a tardi ma non riesco a concentrarmi come vorrei.",

    "Bellissima giornata! Sono uscito con gli amici, abbiamo fatto una passeggiata al parco. Mi sono sentito davvero bene, rilassato e felice.",

    "Oggi mi sono svegliato con poca energia. Ho provato a studiare ma ero troppo stanco. Nel pomeriggio sono andato in palestra e mi ha aiutato.",

    "Giornata intensa ma positiva. Ho avuto un colloquio per uno stage e penso sia andato bene. Sono un po' nervoso per l'esito ma ottimista.",

    "Non e stata una buona giornata. Litigato con un amico e mi sento abbattuto. Ho cercato di studiare ma non riuscivo a concentrarmi.",

    "Oggi ho fatto progressi sul mio progetto di tesi. E molto impegnativo ma interessante. Mi sento motivato anche se a volte e frustrante.",

    "Giornata tranquilla. Ho studiato per l'esame di algoritmi, fatto un po' di esercizio fisico e cucinato qualcosa di buono. Mi sento sereno.",

    "Sono sopraffatto dagli impegni. Troppi esami, troppi progetti, poco tempo. Devo imparare a gestire meglio le priorita.",

    "Ottima giornata! Ho superato l'esame difficile che mi preoccupava tanto. Sono felicissimo e orgoglioso di me stesso.",

    "Oggi mi sono sentito ansioso senza un motivo particolare. Ho provato a fare meditazione e mi ha aiutato un po'.",

    "Giornata normale. Lezioni all'universita, studio, palestra. Routine che mi fa sentire stabile anche se a volte monotona.",

    "Ho passato la giornata a lavorare sul mio progetto personale. Sono entrato nel flow e non ho sentito passare il tempo.",

    "Oggi ero molto stressato per la presentazione del progetto. E andata bene alla fine ma l'ansia prima era forte.",

    "Weekend rilassante. Ho dormito fino a tardi, letto un libro interessante e guardato una serie. A volte fare niente e quello di cui ho bisogno."
]

# Emozioni associate
EMOTION_PROFILES = {
    "positive": {"stress": 1, "happiness": 5, "sadness": 0, "anger": 0, "fatigue": 1},
    "neutral": {"stress": 2, "happiness": 3, "sadness": 1, "anger": 0, "fatigue": 2},
    "negative": {"stress": 4, "happiness": 1, "sadness": 3, "anger": 1, "fatigue": 3},
    "very_positive": {"stress": 0, "happiness": 6, "sadness": 0, "anger": 0, "fatigue": 0},
    "anxious": {"stress": 5, "happiness": 2, "sadness": 2, "anger": 1, "fatigue": 4}
}

# Conversazioni simulate
CONVERSATION_TEMPLATES = [
    [
        {"role": "assistant", "content": "Ciao Alex! Bentornato! Come e andata la giornata?"},
        {"role": "user", "content": "Ciao! E andata bene, ho studiato molto oggi."},
        {"role": "assistant",
         "content": "Che bello sentire che hai dedicato tempo allo studio! Cosa hai studiato? Ti sei sentito concentrato?"},
        {"role": "user", "content": "Ho studiato algoritmi. Ero concentrato ma verso sera ero molto stanco."},
        {"role": "assistant",
         "content": "E normale sentirsi stanchi dopo una sessione intensa di studio. Hai fatto delle pause durante la giornata?"},
        {"role": "user", "content": "Non molte, forse dovrei farne di piu."},
        {"role": "assistant",
         "content": "Si, le pause sono fondamentali! Aiutano il cervello a consolidare le informazioni. Oltre allo studio, cos'altro hai fatto oggi?"},
        {"role": "user", "content": "Sono andato in palestra nel pomeriggio, mi ha aiutato."},
        {"role": "assistant",
         "content": "Eccellente! L'esercizio fisico e ottimo per gestire lo stress e migliorare la concentrazione. Come ti senti ora?"},
        {"role": "user", "content": "Stanco ma soddisfatto. Domani continuo."}
    ],
    [
        {"role": "assistant", "content": "Ciao Alex! Bentornato! Come e andata la giornata?"},
        {"role": "user", "content": "Non benissimo, ero molto ansioso per l'esame di domani."},
        {"role": "assistant",
         "content": "Mi dispiace che tu ti sia sentito ansioso. E l'esame che ti preoccupa o c'e altro?"},
        {"role": "user", "content": "E un esame difficile e ho paura di non essere preparato abbastanza."},
        {"role": "assistant", "content": "L'ansia pre-esame e molto comune. Hai avuto modo di studiare come volevi?"},
        {"role": "user", "content": "Ho studiato tanto ma sento sempre che non basta."},
        {"role": "assistant",
         "content": "Capisco. A volte la sensazione di non essere mai abbastanza preparati e la nostra mente che esagera. Cosa hai fatto per gestire l'ansia?"},
        {"role": "user", "content": "Ho provato a studiare di piu ma ero troppo agitato. Poi ho fatto una camminata."},
        {"role": "assistant",
         "content": "La camminata e stata una scelta saggia. Quando siamo ansiosi, continuare a studiare puo essere controproducente. Come ti sei sentito dopo?"},
        {"role": "user", "content": "Un po' meglio, ma l'ansia e ancora li."}
    ]
]


def create_directories():
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(CONVERSATIONS_DIR, exist_ok=True)
    os.makedirs(ENTRIES_DIR, exist_ok=True)
    print(f"Creato directory: {DATA_DIR}")


def generate_user_profile():
    profile = {
        "created_at": (datetime.now() - timedelta(days=30)).isoformat(),
        "current_streak": 5,
        "longest_streak": 12,
        "total_entries": 25,
        "last_entry_date": (datetime.now() - timedelta(days=1)).isoformat(),
        "milestones_achieved": ["Impegno", "Prima Settimana"],
        "preferences": {"name": "Alex", "timezone": "Europe/Rome"}
    }

    with open(USER_PROFILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(profile, f, indent=2, ensure_ascii=False)

    print(f"Creato profilo utente: {USER_PROFILE_PATH}")
    return profile


def generate_entries(num_days=20):
    print(f"\nGenerazione di {num_days} entries...")
    today = datetime.now().date()

    for i in range(num_days):
        date = today - timedelta(days=i)
        date_str = date.isoformat()
        entry_text = random.choice(ENTRY_TEMPLATES)

        # Scegli profilo emotivo
        if any(word in entry_text.lower() for word in ["felice", "ottima", "bellissima", "soddisfatto"]):
            emotion_profile = "positive"
        elif any(word in entry_text.lower() for word in ["difficile", "stress", "nervoso", "ansioso"]):
            emotion_profile = "anxious"
        elif any(word in entry_text.lower() for word in ["male", "abbattuto", "sopraffatto"]):
            emotion_profile = "negative"
        elif any(word in entry_text.lower() for word in ["ottima", "felicissimo", "orgoglioso"]):
            emotion_profile = "very_positive"
        else:
            emotion_profile = "neutral"

        emotions = EMOTION_PROFILES[emotion_profile].copy()
        for emotion in emotions:
            emotions[emotion] = max(0, emotions[emotion] + random.randint(-1, 1))

        entry_data = {
            "date": date_str,
            "timestamp": (datetime.combine(date, datetime.min.time()) + timedelta(hours=20, minutes=random.randint(0,
                                                                                                                   59))).isoformat(),
            "entry": entry_text,
            "metadata": {
                "source": "chat" if i % 3 == 0 else "editor",
                "emotions_detected": emotions,
                "message_count": random.randint(5, 12)
            }
        }

        filepath = os.path.join(ENTRIES_DIR, f"entry_{date_str}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(entry_data, f, indent=2, ensure_ascii=False)

        print(f"  {date_str}: {entry_text[:50]}...")

    print(f"Creati {num_days} entries")


def generate_conversations(num_conversations=10):
    print(f"\nGenerazione di {num_conversations} conversazioni...")
    today = datetime.now().date()

    for i in range(num_conversations):
        date = today - timedelta(days=i * 2)
        date_str = date.isoformat()
        conversation = random.choice(CONVERSATION_TEMPLATES)

        conv_data = {
            "date": date_str,
            "timestamp": (datetime.combine(date, datetime.min.time()) + timedelta(hours=19, minutes=random.randint(0,
                                                                                                                   59))).isoformat(),
            "messages": conversation,
            "sessions": 1
        }

        filepath = os.path.join(CONVERSATIONS_DIR, f"conversation_{date_str}.json")
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(conv_data, f, indent=2, ensure_ascii=False)

        print(f"  {date_str}: {len(conversation)} messaggi")

    print(f"Create {num_conversations} conversazioni")


def print_summary():
    print("\n" + "=" * 60)
    print("RIEPILOGO DATI GENERATI")
    print("=" * 60)

    num_entries = len([f for f in os.listdir(ENTRIES_DIR) if f.endswith('.json')])
    num_conversations = len([f for f in os.listdir(CONVERSATIONS_DIR) if f.endswith('.json')])

    print(f"\nDirectory: {DATA_DIR}")
    print(f"  Entries: {num_entries}")
    print(f"  Conversazioni: {num_conversations}")
    print(f"  Profilo utente: OK")

    print("\nCOME USARE I DATI:")
    print("1. Copia i dati: cp -r data_test data")
    print("2. Oppure modifica config.py: DATA_DIR = 'data_test'")
    print("3. Avvia l'app: python app.py")
    print("4. Visita: http://localhost:5000")
    print("=" * 60)


def main():
    print("=" * 60)
    print("GENERATORE DATI DI TEST - Mental Wellness Journal")
    print("=" * 60)

    create_directories()
    generate_user_profile()
    generate_entries(num_days=20)
    generate_conversations(num_conversations=10)
    print_summary()

    print("\nGenerazione completata con successo!\n")


if __name__ == "__main__":
    main()