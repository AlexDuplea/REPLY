// ===== DOM ELEMENTS =====
const menuBtn = document.querySelector('.menu-btn');
const sideMenu = document.getElementById('sideMenu');
const closeMenuBtn = document.querySelector('.close-menu');
const wellnessBtn = document.querySelector('.wellness-btn');
const wellnessModal = document.getElementById('wellnessModal');
const closeModalBtn = document.querySelector('.close-modal');
const overlay = document.getElementById('overlay');
const journalEditor = document.querySelector('.journal-editor');
const wordCountElement = document.querySelector('.word-count');
const saveBtn = document.querySelector('.save-btn');
const chatToggle = document.querySelector('.chat-toggle');

// ===== MENU TOGGLE =====
menuBtn.addEventListener('click', () => {
    sideMenu.classList.add('active');
    overlay.classList.add('active');
});

closeMenuBtn.addEventListener('click', () => {
    sideMenu.classList.remove('active');
    overlay.classList.remove('active');
});

// ===== WELLNESS MODAL =====
wellnessBtn.addEventListener('click', () => {
    wellnessModal.classList.add('active');
    overlay.classList.add('active');
});

closeModalBtn.addEventListener('click', () => {
    wellnessModal.classList.remove('active');
    overlay.classList.remove('active');
});

// ===== OVERLAY CLICK =====
overlay.addEventListener('click', () => {
    sideMenu.classList.remove('active');
    wellnessModal.classList.remove('active');
    overlay.classList.remove('active');
});

// ===== WORD COUNT =====
journalEditor.addEventListener('input', () => {
    const text = journalEditor.value.trim();
    const words = text ? text.split(/\s+/).length : 0;
    wordCountElement.textContent = `${words} parole`;
});

// ===== SAVE BUTTON =====
saveBtn.addEventListener('click', () => {
    const text = journalEditor.value.trim();
    
    if (!text) {
        alert('Scrivi qualcosa prima di salvare! 📝');
        return;
    }
    
    // Animazione di successo
    saveBtn.textContent = '✓ Salvato!';
    saveBtn.style.background = 'var(--accent-green)';
    
    setTimeout(() => {
        saveBtn.textContent = 'Salva';
        saveBtn.style.background = 'var(--ink-dark)';
    }, 2000);
    
    // TODO: Qui andrà la chiamata al backend Flask
    console.log('Saving entry:', text);
});

// ===== CHAT TOGGLE =====
chatToggle.addEventListener('click', () => {
    alert('Chat Mode verrà implementato! 💬\n\nQui apparirà l\'interfaccia conversazionale con l\'AI.');
    // TODO: Implementare transizione a chat mode
});

// ===== STREAK ANIMATION (pulse on load) =====
window.addEventListener('load', () => {
    const streakBadge = document.querySelector('.streak-badge');
    streakBadge.style.animation = 'pulse 0.5s ease';
});

// ===== CSS ANIMATIONS (inline for demo) =====
const style = document.createElement('style');
style.textContent = `
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .editor-container {
        animation: fadeIn 0.5s ease;
    }
`;
document.head.appendChild(style);

// ===== PLACEHOLDER TIPS =====
const tips = [
    "Come è andata oggi? Scrivi liberamente i tuoi pensieri...",
    "Cosa ti ha reso felice oggi?",
    "Quali sfide hai affrontato?",
    "Come ti senti in questo momento?",
    "Cosa hai imparato di nuovo oggi?"
];

// Cambia placeholder ogni 5 secondi quando l'editor è vuoto
let tipIndex = 0;
setInterval(() => {
    if (!journalEditor.value && document.activeElement !== journalEditor) {
        tipIndex = (tipIndex + 1) % tips.length;
        journalEditor.placeholder = tips[tipIndex];
    }
}, 5000);

console.log('🌟 Mental Wellness Journal - Mockup caricato!');
