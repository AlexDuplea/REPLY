// ===== MENTAL WELLNESS JOURNAL - Frontend JavaScript =====

// ===== STATE =====
const state = {
    chatActive: false,
    currentMode: 'editor', // 'editor' or 'chat'
    chatMessages: []
};

// ===== DOM ELEMENTS =====
const elements = {
    // Editor
    editorMode: document.getElementById('editorMode'),
    journalEditor: document.getElementById('journalEditor'),
    wordCount: document.getElementById('wordCount'),
    saveBtn: document.getElementById('saveBtn'),

    // Chat
    chatMode: document.getElementById('chatMode'),
    chatToggle: document.getElementById('chatToggle'),
    closeChat: document.getElementById('closeChat'),
    chatMessages: document.getElementById('chatMessages'),
    chatInput: document.getElementById('chatInput'),
    chatSendBtn: document.getElementById('chatSendBtn'),

    // Wellness
    wellnessBtn: document.getElementById('wellnessBtn'),
    wellnessModal: document.getElementById('wellnessModal'),
    wellnessLoading: document.getElementById('wellnessLoading'),
    wellnessContent: document.getElementById('wellnessContent'),
    wellnessSummary: document.getElementById('wellnessSummary'),
    wellnessSuggestions: document.getElementById('wellnessSuggestions'),
    closeWellness: document.getElementById('closeWellness'),

    // Menu
    menuBtn: document.getElementById('menuBtn'),
    sideMenu: document.getElementById('sideMenu'),
    closeMenu: document.getElementById('closeMenu'),

    // Modals
    entriesModal: document.getElementById('entriesModal'),
    statsModal: document.getElementById('statsModal'),
    closeEntries: document.getElementById('closeEntries'),
    closeStats: document.getElementById('closeStats'),

    // Other
    overlay: document.getElementById('overlay'),
    toast: document.getElementById('toast'),
    streakNumber: document.getElementById('streakNumber')
};

// ===== UTILITY FUNCTIONS =====

function showToast(message, type = 'success') {
    elements.toast.textContent = message;
    elements.toast.className = `toast show ${type}`;

    setTimeout(() => {
        elements.toast.classList.remove('show');
    }, 3000);
}

function showOverlay() {
    elements.overlay.classList.add('active');
}

function hideOverlay() {
    elements.overlay.classList.remove('active');
}

function updateWordCount() {
    const text = elements.journalEditor.value.trim();
    const words = text ? text.split(/\s+/).length : 0;
    elements.wordCount.textContent = `${words} parole`;
}

// ===== EDITOR MODE =====

elements.journalEditor.addEventListener('input', updateWordCount);

elements.saveBtn.addEventListener('click', async () => {
    const content = elements.journalEditor.value.trim();

    if (!content) {
        showToast('Scrivi qualcosa prima di salvare!', 'error');
        return;
    }

    elements.saveBtn.disabled = true;
    elements.saveBtn.textContent = 'Salvando...';
    elements.saveBtn.classList.add('btn-pulse'); // Add pulse animation class if defined, or rely on CSS active state

    try {
        const response = await fetch('/api/save-entry', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ content })
        });

        const data = await response.json();

        if (data.success) {
            showToast('✓ Entry salvato!', 'success');

            // Update streak
            elements.streakNumber.textContent = data.streak;

            // Check for milestone
            if (data.new_milestone) showMilestoneAnimation(data.new_milestone);

            // **Non cancelliamo l'editor, lasciamo il testo**
            updateWordCount();

            elements.saveBtn.textContent = '✓ Salvato!';
            elements.saveBtn.style.background = 'var(--accent-green)';

            // Trigger confetti or visual success here if needed

            setTimeout(() => {
                elements.saveBtn.textContent = 'Salva';
                elements.saveBtn.style.background = '';
                elements.saveBtn.disabled = false;
                elements.saveBtn.classList.remove('btn-pulse');
            }, 2000);
        } else {
            showToast('Errore nel salvataggio', 'error');
            elements.saveBtn.disabled = false;
            elements.saveBtn.textContent = 'Salva';
            elements.saveBtn.classList.remove('btn-pulse');
        }
    } catch (error) {
        console.error('Error saving entry:', error);
        showToast('Errore di connessione', 'error');
        elements.saveBtn.disabled = false;
        elements.saveBtn.textContent = 'Salva';
        elements.saveBtn.classList.remove('btn-pulse');
    }
});

function showMilestoneAnimation(milestone) {
    // TODO: Implement confetti or celebration animation
    showToast(`Milestone raggiunta: ${milestone.name}!`, 'success');
}

// ===== CHAT MODE =====

elements.chatToggle.addEventListener('click', () => {
    if (state.currentMode === 'editor') {
        startChatMode();
    } else {
        // La ✕ chiude la chat senza bisogno di scrivere "fine"
        closeChatMode();
    }
});

elements.closeChat.addEventListener('click', closeChatMode);

async function startChatMode() {
    elements.editorMode.style.display = 'none';
    elements.chatMode.style.display = 'flex';
    elements.chatToggle.classList.add('active');
    elements.chatToggle.textContent = '✕';

    state.currentMode = 'chat';
    state.chatActive = true;

    elements.chatMessages.innerHTML = '';
    state.chatMessages = [];

    try {
        const response = await fetch('/api/chat/start', { method: 'POST' });
        const data = await response.json();

        if (data.success) addChatMessage('assistant', data.message);
    } catch (error) {
        console.error('Error starting chat:', error);
        showToast('Errore avvio chat', 'error');
    } finally {
        // Focus input after chat starts
        setTimeout(() => elements.chatInput.focus(), 100);
    }
}

function closeChatMode() {
    elements.editorMode.style.display = 'block';
    elements.chatMode.style.display = 'none';
    elements.chatToggle.classList.remove('active');
    elements.chatToggle.textContent = '💬';

    state.currentMode = 'editor';
    state.chatActive = false;
}

function addChatMessage(role, content) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `chat-message ${role}`;

    const iconDiv = document.createElement('div');
    iconDiv.className = 'message-icon';
    // Use Phosphor icons for chat roles
    iconDiv.innerHTML = role === 'assistant'
        ? '<i class="ph-fill ph-robot"></i>'
        : '<i class="ph-fill ph-user"></i>';

    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';
    bubbleDiv.textContent = content;

    messageDiv.appendChild(iconDiv);
    messageDiv.appendChild(bubbleDiv);

    elements.chatMessages.appendChild(messageDiv);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;

    state.chatMessages.push({ role, content });
}

elements.chatSendBtn.addEventListener('click', sendChatMessage);
elements.chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendChatMessage();
    }
});

async function sendChatMessage() {
    const message = elements.chatInput.value.trim();
    if (!message) return;

    addChatMessage('user', message);
    elements.chatInput.value = '';
    elements.chatInput.disabled = true;
    elements.chatSendBtn.disabled = true;

    // Show typing indicator
    showTypingIndicator();

    try {
        const response = await fetch('/api/chat/message', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        // Remove typing indicator
        removeTypingIndicator();

        if (data.success) {
            addChatMessage('assistant', data.response);

            if (data.should_end && data.journal_entry) {
                showToast('Diario generato!', 'success');

                if (data.streak) elements.streakNumber.textContent = data.streak;

                // **Appendiamo al diario esistente**
                elements.journalEditor.value += '\n' + data.journal_entry;
                updateWordCount();

                setTimeout(() => {
                    closeChatMode();
                }, 2000);
            }
        }
    } catch (error) {
        removeTypingIndicator();
        console.error('Error sending message:', error);
        showToast('Errore invio messaggio', 'error');
    } finally {
        elements.chatInput.disabled = false;
        elements.chatSendBtn.disabled = false;
        elements.chatInput.focus();
    }
}

function showTypingIndicator() {
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.id = 'typingIndicator';
    typingDiv.innerHTML = `
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
        <div class="typing-dot"></div>
    `;
    elements.chatMessages.appendChild(typingDiv);
    elements.chatMessages.scrollTop = elements.chatMessages.scrollHeight;
}

function removeTypingIndicator() {
    const typingDiv = document.getElementById('typingIndicator');
    if (typingDiv) typingDiv.remove();
}

// ===== WELLNESS MODE =====

elements.wellnessBtn.addEventListener('click', openWellnessMode);
elements.closeWellness.addEventListener('click', closeWellnessMode);

async function openWellnessMode() {
    elements.wellnessModal.classList.add('active');
    showOverlay();
    elements.wellnessLoading.style.display = 'block';
    elements.wellnessContent.style.display = 'none';

    try {
        const response = await fetch('/api/wellness/suggestions');
        const data = await response.json();
        if (data.success) displayWellnessSuggestions(data);
    } catch (error) {
        console.error('Error fetching wellness suggestions:', error);
        showToast('Errore caricamento suggerimenti', 'error');
    }
}

function displayWellnessSuggestions(data) {
    elements.wellnessLoading.style.display = 'none';
    elements.wellnessContent.style.display = 'block';

    elements.wellnessSummary.innerHTML = `<p>${data.summary}</p>`;
    elements.wellnessSuggestions.innerHTML = '';

    data.suggestions.forEach(suggestion => {
        const card = document.createElement('div');
        card.className = 'wellness-card';
        card.innerHTML = `
            <div class="card-content">
                <h3>${suggestion.title}</h3>
                <p>${suggestion.description}</p>
            </div>
        `;
        elements.wellnessSuggestions.appendChild(card);
    });
}

function closeWellnessMode() {
    elements.wellnessModal.classList.remove('active');
    hideOverlay();
}

// ===== MENU =====

elements.menuBtn.addEventListener('click', () => {
    elements.sideMenu.classList.add('active');
    showOverlay();
});

elements.closeMenu.addEventListener('click', closeMenu);

function closeMenu() {
    elements.sideMenu.classList.remove('active');
    hideOverlay();
}

document.querySelectorAll('.menu-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        const action = item.dataset.action;
        closeMenu();

        switch (action) {
            case 'calendar': showCalendar(); break;
            case 'stats': showStats(); break;
            case 'entries': showEntries(); break;
            case 'settings': showToast('Impostazioni in arrivo!', 'success'); break;
        }
    });
});

// ===== ENTRIES =====

async function showEntries() {
    elements.entriesModal.classList.add('active');
    showOverlay();

    try {
        const response = await fetch('/api/entries/recent?days=30');
        const data = await response.json();
        if (data.success) displayEntries(data.entries);
    } catch (error) {
        console.error('Error fetching entries:', error);
        showToast('Errore caricamento log', 'error');
    }
}

function displayEntries(entries) {
    const entriesList = document.getElementById('entriesList');
    entriesList.innerHTML = '';

    if (entries.length === 0) {
        entriesList.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon"><i class="ph-duotone ph-pencil-slash"></i></div>
                <div class="empty-text">Non hai ancora scritto nulla. <br>Inizia oggi il tuo diario!</div>
            </div>
        `;
        return;
    }

    entries.forEach(entry => {
        const entryDiv = document.createElement('div');
        entryDiv.className = 'entry-item';
        entryDiv.innerHTML = `
            <div class="entry-date"><i class="ph-bold ph-calendar-blank"></i> ${entry.date}</div>
            <div class="entry-text">${entry.entry}</div>
        `;
        entriesList.appendChild(entryDiv);
    });
}

elements.closeEntries.addEventListener('click', () => {
    elements.entriesModal.classList.remove('active');
    hideOverlay();
});

// ===== STATS =====

async function showStats() {
    window.location.href = '/stats';
}

// ===== CALENDAR =====

async function showCalendar() {
    showToast('Calendario completo in arrivo!', 'success');
}

async function loadMiniCalendar() {
    try {
        const response = await fetch('/api/calendar');
        const data = await response.json();
        if (data.success) console.log('Calendar data:', data);
    } catch (error) {
        console.error('Error loading calendar:', error);
    }
}

// ===== OVERLAY CLICK =====

elements.overlay.addEventListener('click', () => {
    closeMenu();
    closeWellnessMode();
    elements.entriesModal.classList.remove('active');
    elements.statsModal.classList.remove('active');
    hideOverlay();
});

// ===== INIT =====

function init() {
    console.log('🌟 Mental Wellness Journal initialized');
    updateWordCount();
    loadMiniCalendar();
}

document.addEventListener('DOMContentLoaded', init);
