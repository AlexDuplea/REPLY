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

    // Disable button
    elements.saveBtn.disabled = true;
    elements.saveBtn.textContent = 'Salvando...';

    try {
        const response = await fetch('/api/save-entry', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ content })
        });

        const data = await response.json();

        if (data.success) {
            showToast('✓ Entry salvato!', 'success');

            // Update streak
            elements.streakNumber.textContent = data.streak;

            // Check for milestone
            if (data.new_milestone) {
                showMilestoneAnimation(data.new_milestone);
            }

            // Clear editor
            elements.journalEditor.value = '';
            updateWordCount();

            // Success animation
            elements.saveBtn.textContent = '✓ Salvato!';
            elements.saveBtn.style.background = 'var(--accent-green)';

            setTimeout(() => {
                elements.saveBtn.textContent = 'Salva';
                elements.saveBtn.style.background = '';
                elements.saveBtn.disabled = false;
            }, 2000);
        } else {
            showToast('Errore nel salvataggio', 'error');
            elements.saveBtn.disabled = false;
            elements.saveBtn.textContent = 'Salva';
        }
    } catch (error) {
        console.error('Error saving entry:', error);
        showToast('Errore di connessione', 'error');
        elements.saveBtn.disabled = false;
        elements.saveBtn.textContent = 'Salva';
    }
});

function showMilestoneAnimation(milestone) {
    // TODO: Implement confetti or celebration animation
    showToast(`🎉 Milestone raggiunta: ${milestone.name}!`, 'success');
}

// ===== CHAT MODE =====

elements.chatToggle.addEventListener('click', toggleChatMode);
elements.closeChat.addEventListener('click', closeChatMode);

async function toggleChatMode() {
    if (state.currentMode === 'editor') {
        await startChatMode();
    } else {
        closeChatMode();
    }
}

async function startChatMode() {
    // Hide editor, show chat
    elements.editorMode.style.display = 'none';
    elements.chatMode.style.display = 'flex';
    elements.chatToggle.classList.add('active');
    elements.chatToggle.textContent = '✕';

    state.currentMode = 'chat';
    state.chatActive = true;

    // Clear previous messages
    elements.chatMessages.innerHTML = '';
    state.chatMessages = [];

    // Start chat session with AI
    try {
        const response = await fetch('/api/chat/start', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            addChatMessage('assistant', data.message);
        }
    } catch (error) {
        console.error('Error starting chat:', error);
        showToast('Errore avvio chat', 'error');
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
    iconDiv.textContent = role === 'assistant' ? '🤖' : '👤';

    const bubbleDiv = document.createElement('div');
    bubbleDiv.className = 'message-bubble';
    bubbleDiv.textContent = content;

    messageDiv.appendChild(iconDiv);
    messageDiv.appendChild(bubbleDiv);

    elements.chatMessages.appendChild(messageDiv);

    // Scroll to bottom
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

    // Add user message to UI
    addChatMessage('user', message);

    // Clear input
    elements.chatInput.value = '';

    // Disable input while waiting
    elements.chatInput.disabled = true;
    elements.chatSendBtn.disabled = true;

    try {
        const response = await fetch('/api/chat/message', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ message })
        });

        const data = await response.json();

        if (data.success) {
            // Add AI response
            addChatMessage('assistant', data.response);

            // Check if conversation ended
            if (data.should_end) {
                if (data.journal_entry) {
                    // Show generated journal entry
                    showToast('Diario generato!', 'success');

                    // Update streak
                    if (data.streak) {
                        elements.streakNumber.textContent = data.streak;
                    }

                    // Show journal entry in a modal or editor
                    setTimeout(() => {
                        closeChatMode();
                        elements.journalEditor.value = data.journal_entry;
                        updateWordCount();
                    }, 2000);
                }
            }
        }
    } catch (error) {
        console.error('Error sending message:', error);
        showToast('Errore invio messaggio', 'error');
    } finally {
        elements.chatInput.disabled = false;
        elements.chatSendBtn.disabled = false;
        elements.chatInput.focus();
    }
}

// ===== WELLNESS MODE =====

elements.wellnessBtn.addEventListener('click', openWellnessMode);
elements.closeWellness.addEventListener('click', closeWellnessMode);

async function openWellnessMode() {
    elements.wellnessModal.classList.add('active');
    showOverlay();

    // Show loading
    elements.wellnessLoading.style.display = 'block';
    elements.wellnessContent.style.display = 'none';

    try {
        const response = await fetch('/api/wellness/suggestions');
        const data = await response.json();

        if (data.success) {
            displayWellnessSuggestions(data);
        }
    } catch (error) {
        console.error('Error fetching wellness suggestions:', error);
        showToast('Errore caricamento suggerimenti', 'error');
    }
}

function displayWellnessSuggestions(data) {
    // Hide loading, show content
    elements.wellnessLoading.style.display = 'none';
    elements.wellnessContent.style.display = 'block';

    // Display summary
    elements.wellnessSummary.innerHTML = `<p>${data.summary}</p>`;

    // Display suggestions (senza icone)
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

// Menu item actions
document.querySelectorAll('.menu-item').forEach(item => {
    item.addEventListener('click', (e) => {
        e.preventDefault();
        const action = item.dataset.action;

        closeMenu();

        switch(action) {
            case 'calendar':
                showCalendar();
                break;
            case 'stats':
                showStats();
                break;
            case 'entries':
                showEntries();
                break;
            case 'settings':
                showToast('Impostazioni in arrivo!', 'success');
                break;
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

        if (data.success) {
            displayEntries(data.entries);
        }
    } catch (error) {
        console.error('Error fetching entries:', error);
        showToast('Errore caricamento log', 'error');
    }
}

function displayEntries(entries) {
    const entriesList = document.getElementById('entriesList');
    entriesList.innerHTML = '';

    if (entries.length === 0) {
        entriesList.innerHTML = '<p>Nessun log trovato. Inizia a scrivere!</p>';
        return;
    }

    entries.forEach(entry => {
        const entryDiv = document.createElement('div');
        entryDiv.className = 'entry-item';

        entryDiv.innerHTML = `
            <div class="entry-date">📅 ${entry.date}</div>
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
    // Redirect to dedicated stats page
    window.location.href = '/stats';
}

// ===== CALENDAR =====

async function showCalendar() {
    // TODO: Implement calendar modal
    showToast('Calendario completo in arrivo!', 'success');

    // For now, calendar is shown in side menu
}

// Load mini calendar
async function loadMiniCalendar() {
    try {
        const response = await fetch('/api/calendar');
        const data = await response.json();

        if (data.success) {
            // Simple implementation - just show completed days
            // Full calendar implementation would be more complex
            console.log('Calendar data:', data);
        }
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

// Run on page load
document.addEventListener('DOMContentLoaded', init);