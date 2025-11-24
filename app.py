"""
Flask Application - Mental Wellness Journal
Backend API per interfaccia web
"""

from flask import Flask, render_template, request, jsonify, session
from datetime import date, datetime
import secrets

# Import moduli esistenti
from storage import Storage
from Agents.agent import MentalWellnessAgent
from Agents.wellness_agent import WellnessAgent
import config

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

# Inizializza storage
storage = Storage()


# ===== ROUTES - PAGES =====

@app.route('/')
def index():
    """Pagina principale"""
    # Carica profilo utente
    profile = storage.load_user_profile()

    # Prepara dati per template
    context = {
        'streak': profile['current_streak'],
        'total_entries': profile['total_entries'],
        'date': date.today().strftime('%A, %d %B %Y'),
        'user_name': profile['preferences'].get('name', None)
    }

    return render_template('index.html', **context)


@app.route('/stats')
def stats_page():
    """Pagina statistiche completa"""
    profile = storage.load_user_profile()
    stats = storage.get_stats()

    context = {
        'streak': profile['current_streak'],
        'stats': stats,
        'milestones': profile['milestones_achieved']
    }

    return render_template('stats.html', **context)


# ===== API ENDPOINTS =====

@app.route('/api/save-entry', methods=['POST'])
def save_entry():
    """
    Salva un entry dal form editor
    Body: { "content": "testo del diario" }
    """
    try:
        data = request.get_json()
        content = data.get('content', '').strip()

        if not content:
            return jsonify({'error': 'Contenuto vuoto'}), 400

        # Controlla se esiste già un log oggi
        today = date.today().isoformat()
        existing_log = storage.get_today_entry_text()

        # Se esiste già un log, aggiungi il nuovo contenuto
        if existing_log:
            # Aggiungi una separazione e il nuovo contenuto
            combined_content = existing_log + "\n\n" + content
            storage.save_entry(combined_content, metadata={'source': 'editor'}, entry_date=today)
        else:
            # Primo log della giornata
            storage.save_entry(content, metadata={'source': 'editor'}, entry_date=today)

        # Aggiorna streak
        streak_info = storage.update_streak()

        return jsonify({
            'success': True,
            'message': 'Entry salvato!',
            'streak': streak_info['current_streak'],
            'new_milestone': streak_info.get('new_milestone')
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat/start', methods=['POST'])
def start_chat():
    """
    Inizia una nuova sessione chat con l'AI
    Returns: { "message": "messaggio iniziale AI", "session_id": "..." }
    """
    try:
        # Crea nuovo agente
        agent = MentalWellnessAgent()

        # Carica contesto recente
        recent_entries = storage.get_recent_entries(num_days=3)
        context = _build_context_from_entries(recent_entries)

        # Profilo utente
        profile = storage.load_user_profile()
        user_name = profile['preferences'].get('name')

        # Avvia sessione
        greeting = agent.start_session(user_name, context)

        # Salva agente in sessione Flask
        session['chat_active'] = True
        session['chat_history'] = agent.get_conversation_history()

        return jsonify({
            'success': True,
            'message': greeting
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat/message', methods=['POST'])
def send_chat_message():
    """
    Invia messaggio all'AI chat
    Body: { "message": "..." }
    Returns: { "response": "...", "should_end": bool }
    """
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()

        if not user_message:
            return jsonify({'error': 'Messaggio vuoto'}), 400

        # Ricrea agente con history dalla sessione
        agent = MentalWellnessAgent()

        if 'chat_history' in session:
            agent.conversation_history = session['chat_history']
            agent.session_started = True
        else:
            return jsonify({'error': 'Sessione chat non trovata'}), 400

        # Invia messaggio
        result = agent.chat(user_message)

        # Aggiorna sessione
        session['chat_history'] = agent.get_conversation_history()

        # Se la conversazione ÃƒÂ¨ terminata, genera entry
        if result['should_end'] and not result['crisis_detected']:
            # Controlla se esiste giÃƒÂ  un log oggi
            today = date.today().isoformat()
            existing_log = storage.get_today_entry_text()

            # Genera entry (combinando con quello esistente se presente)
            journal_entry = agent.generate_journal_entry(existing_entry=existing_log)

            # Salva
            emotions = agent.extract_emotions()
            storage.save_entry(journal_entry, metadata={'source': 'chat', 'emotions_detected': emotions},
                               entry_date=today)
            storage.save_conversation(agent.get_conversation_history(), today)

            # Aggiorna streak
            streak_info = storage.update_streak()

            session['chat_active'] = False

            return jsonify({
                'success': True,
                'response': result['response'],
                'should_end': True,
                'journal_entry': journal_entry,
                'streak': streak_info['current_streak']
            })

        return jsonify({
            'success': True,
            'response': result['response'],
            'should_end': result['should_end'],
            'crisis_detected': result.get('crisis_detected', False)
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/chat/close', methods=['POST'])
def close_chat():
    """
    Chiude la chat e salva automaticamente il journal entry
    Returns: { "journal_entry": "...", "streak": ... }
    """
    try:
        # Ricrea agente con history dalla sessione
        agent = MentalWellnessAgent()

        if 'chat_history' not in session:
            return jsonify({'error': 'Nessuna sessione chat attiva'}), 400

        agent.conversation_history = session['chat_history']
        agent.session_started = True

        # Controlla se esiste già un log oggi
        today = date.today().isoformat()
        existing_log = storage.get_today_entry_text()

        # Genera entry (combinando con quello esistente se presente)
        journal_entry = agent.generate_journal_entry(existing_entry=existing_log)

        # Salva
        emotions = agent.extract_emotions()
        storage.save_entry(journal_entry, metadata={'source': 'chat', 'emotions_detected': emotions},
                           entry_date=today)
        storage.save_conversation(agent.get_conversation_history(), today)

        # Aggiorna streak
        streak_info = storage.update_streak()

        session['chat_active'] = False

        return jsonify({
            'success': True,
            'journal_entry': journal_entry,
            'streak': streak_info['current_streak']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/wellness/suggestions', methods=['GET'])
def get_wellness_suggestions():
    """
    Ottiene suggerimenti personalizzati basati sui log recenti
    Returns: { "summary": "...", "suggestions": [...] }
    """
    try:
        wellness_agent = WellnessAgent()
        suggestions = wellness_agent.get_personalized_suggestions(num_days=7)

        return jsonify({
            'success': True,
            **suggestions
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/wellness/quick-tip', methods=['GET'])
def get_quick_tip():
    """Ottiene un quick tip random"""
    try:
        wellness_agent = WellnessAgent()
        tip = wellness_agent.get_quick_tip()

        return jsonify({
            'success': True,
            'tip': tip
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/entries/recent', methods=['GET'])
def get_recent_entries():
    """
    Ottiene gli ultimi N entries
    Query param: ?days=7
    """
    try:
        days = request.args.get('days', 7, type=int)
        entries = storage.get_recent_entries(num_days=days)

        return jsonify({
            'success': True,
            'entries': entries
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Ottiene statistiche utente"""
    try:
        stats = storage.get_stats()
        profile = storage.load_user_profile()

        return jsonify({
            'success': True,
            'stats': stats,
            'milestones': profile['milestones_achieved']
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/calendar', methods=['GET'])
def get_calendar():
    """
    Ottiene calendario con giorni completati
    Query param: ?month=2025-11
    """
    try:
        # TODO: Implementare logica calendario
        # Per ora ritorna placeholder
        import calendar as cal
        from datetime import datetime

        month_str = request.args.get('month', datetime.now().strftime('%Y-%m'))
        year, month = map(int, month_str.split('-'))

        # Ottieni tutti gli entries
        all_entries = storage.get_recent_entries(num_days=365)  # Ultimo anno
        completed_dates = [entry['date'] for entry in all_entries]

        # Genera calendario
        cal_data = cal.monthcalendar(year, month)

        return jsonify({
            'success': True,
            'calendar': cal_data,
            'completed_dates': completed_dates,
            'month': month,
            'year': year
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/sentiment/data', methods=['GET'])
def get_sentiment_data():
    """
    Ottiene dati sentiment per grafici
    Query param: ?days=30
    """
    try:
        days = request.args.get('days', 30, type=int)
        entries = storage.get_recent_entries(num_days=days)

        # Prepara dati per grafici
        dates = []
        stress_data = []
        happiness_data = []
        energy_data = []

        # Analizza emotions da metadata
        for entry in reversed(entries):  # Ordine cronologico
            dates.append(entry['date'])

            emotions = entry.get('metadata', {}).get('emotions_detected', {})

            # Usa direttamente i valori 0-10 dal SentimentAgent
            stress = emotions.get('stress', 5)
            happiness = emotions.get('happiness', 6)
            energy = emotions.get('energy', 6)

            stress_data.append(stress)
            happiness_data.append(happiness)
            energy_data.append(energy)

        # Calcola overall (media)
        overall = [
            sum(happiness_data) / len(happiness_data) if happiness_data else 7,
            sum(energy_data) / len(energy_data) if energy_data else 6.5,
            10 - (sum(stress_data) / len(stress_data)) if stress_data else 7.5,  # Calma
            7.0,  # Motivazione (placeholder)
            (sum(happiness_data + energy_data) / (len(happiness_data) + len(energy_data))) if (
                        happiness_data or energy_data) else 7
        ]

        # Formatta date per display
        formatted_dates = []
        for d in dates:
            try:
                dt = datetime.fromisoformat(d)
                formatted_dates.append(dt.strftime('%d/%m'))
            except:
                formatted_dates.append(d[-5:])  # Fallback: ultimi 5 caratteri

        # Activity data (per calendario)
        activity_dates = [entry['date'] for entry in entries]

        return jsonify({
            'success': True,
            'sentiment_data': {
                'dates': formatted_dates,
                'stress': stress_data,
                'happiness': happiness_data,
                'energy': energy_data,
                'overall': overall
            },
            'activity_data': activity_dates
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500


# ===== HELPER FUNCTIONS =====

def _build_context_from_entries(entries: list) -> str:
    """Costruisce contesto dalle entries recenti"""
    if not entries:
        return None

    context_parts = ["Ecco cosa ha scritto recentemente l'utente:\n"]

    for entry_data in entries:
        date_str = entry_data['date']
        entry_text = entry_data['entry']
        summary = '. '.join(entry_text.split('.')[:2]) + '.'
        context_parts.append(f"- {date_str}: {summary}")

    return "\n".join(context_parts)


# ===== RUN APP =====

if __name__ == '__main__':
    print("=" * 60)
    print("ðŸŒŸ Mental Wellness Journal - Web App")
    print("=" * 60)
    print("\nðŸ“± Server avviato su: http://localhost:5000")
    print("ðŸ”’ Premi CTRL+C per fermare\n")

    app.run(debug=True, host='0.0.0.0', port=5000)