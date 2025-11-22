// ===== WEMIND STATS PAGE - JavaScript =====

// ===== CONFIG =====
const chartColors = {
    stress: '#B8786E',
    happiness: '#C8A882',
    energy: '#7A9AAD',
    sentiment: '#8B9D83',
    background: {
        stress: 'rgba(184, 120, 110, 0.2)',
        happiness: 'rgba(200, 168, 130, 0.2)',
        energy: 'rgba(122, 154, 173, 0.2)',
        sentiment: 'rgba(139, 157, 131, 0.2)'
    }
};

// ===== INIT =====
document.addEventListener('DOMContentLoaded', async () => {
    console.log('📊 WeMind Stats Page initialized');
    await loadStatsData();
    await loadSentimentData();
});

// ===== LOAD STATS DATA =====
async function loadStatsData() {
    try {
        const response = await fetch('/api/stats');
        const data = await response.json();
        
        if (data.success) {
            updateStatsCards(data.stats);
        }
    } catch (error) {
        console.error('Error loading stats:', error);
    }
}

function updateStatsCards(stats) {
    // Calculate average per week
    const avgPerWeek = stats.total_entries > 0 
        ? (stats.total_entries / Math.max(stats.longest_streak / 7, 1)).toFixed(1)
        : 0;
    
    document.getElementById('avgPerWeek').textContent = avgPerWeek;
}

// ===== LOAD SENTIMENT DATA =====
async function loadSentimentData() {
    try {
        const response = await fetch('/api/sentiment/data?days=30');
        const data = await response.json();
        
        if (data.success) {
            createCharts(data.sentiment_data);
            createActivityCalendar(data.activity_data);
        }
    } catch (error) {
        console.error('Error loading sentiment data:', error);
        // Create charts with sample data if API fails
        createChartsWithSampleData();
    }
}

// ===== CREATE CHARTS =====
function createCharts(sentimentData) {
    const labels = sentimentData.dates;
    
    // Stress Chart
    new Chart(document.getElementById('stressChart'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Livello Stress',
                data: sentimentData.stress,
                borderColor: chartColors.stress,
                backgroundColor: chartColors.background.stress,
                tension: 0.4,
                fill: true
            }]
        },
        options: getChartOptions('Stress (0-10)')
    });
    
    // Happiness Chart
    new Chart(document.getElementById('happinessChart'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Felicità',
                data: sentimentData.happiness,
                borderColor: chartColors.happiness,
                backgroundColor: chartColors.background.happiness,
                tension: 0.4,
                fill: true
            }]
        },
        options: getChartOptions('Felicità (0-10)')
    });
    
    // Energy Chart
    new Chart(document.getElementById('energyChart'), {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'Energia',
                data: sentimentData.energy,
                borderColor: chartColors.energy,
                backgroundColor: chartColors.background.energy,
                tension: 0.4,
                fill: true
            }]
        },
        options: getChartOptions('Energia (0-10)')
    });
    
    // Overall Sentiment (Radar)
    new Chart(document.getElementById('sentimentChart'), {
        type: 'radar',
        data: {
            labels: ['Felicità', 'Energia', 'Calma', 'Motivazione', 'Benessere'],
            datasets: [{
                label: 'Media Ultimo Mese',
                data: sentimentData.overall,
                borderColor: chartColors.sentiment,
                backgroundColor: chartColors.background.sentiment,
                pointBackgroundColor: chartColors.sentiment
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            scales: {
                r: {
                    beginAtZero: true,
                    max: 10,
                    ticks: {
                        stepSize: 2,
                        font: { size: 11 },
                        color: '#6B5D52'
                    },
                    grid: {
                        color: '#E8DCC8'
                    },
                    pointLabels: {
                        font: { size: 12 },
                        color: '#3E3226'
                    }
                }
            },
            plugins: {
                legend: { display: false }
            }
        }
    });
}

function getChartOptions(yAxisLabel) {
    return {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: { display: false },
            tooltip: {
                backgroundColor: '#3E3226',
                titleColor: '#F5F1E8',
                bodyColor: '#F5F1E8',
                padding: 12,
                cornerRadius: 8
            }
        },
        scales: {
            y: {
                beginAtZero: true,
                max: 10,
                ticks: {
                    stepSize: 2,
                    font: { size: 11 },
                    color: '#6B5D52'
                },
                grid: {
                    color: '#E8DCC8'
                },
                title: {
                    display: true,
                    text: yAxisLabel,
                    color: '#6B5D52',
                    font: { size: 12 }
                }
            },
            x: {
                ticks: {
                    font: { size: 11 },
                    color: '#6B5D52',
                    maxRotation: 45,
                    minRotation: 45
                },
                grid: {
                    display: false
                }
            }
        }
    };
}

// ===== SAMPLE DATA (fallback) =====
function createChartsWithSampleData() {
    // Generate last 30 days
    const labels = [];
    const today = new Date();
    for (let i = 29; i >= 0; i--) {
        const date = new Date(today);
        date.setDate(date.getDate() - i);
        labels.push(date.toLocaleDateString('it-IT', { day: 'numeric', month: 'short' }));
    }
    
    // Generate sample data with some patterns
    const sampleData = {
        dates: labels,
        stress: Array.from({length: 30}, () => Math.random() * 4 + 3),
        happiness: Array.from({length: 30}, () => Math.random() * 3 + 6),
        energy: Array.from({length: 30}, () => Math.random() * 4 + 4),
        overall: [7.2, 6.5, 7.8, 7.0, 7.5] // happiness, energy, calm, motivation, wellbeing
    };
    
    createCharts(sampleData);
}

// ===== ACTIVITY CALENDAR =====
function createActivityCalendar(activityData) {
    const calendar = document.getElementById('activityCalendar');
    
    // Get current month
    const today = new Date();
    const year = today.getFullYear();
    const month = today.getMonth();
    
    // Create calendar grid
    const firstDay = new Date(year, month, 1).getDay();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    
    let html = '<div class="calendar-header">';
    html += `<h3>${today.toLocaleDateString('it-IT', { month: 'long', year: 'numeric' })}</h3>`;
    html += '</div>';
    
    html += '<div class="calendar-grid">';
    
    // Day headers
    const dayNames = ['Dom', 'Lun', 'Mar', 'Mer', 'Gio', 'Ven', 'Sab'];
    dayNames.forEach(day => {
        html += `<div class="calendar-day-header">${day}</div>`;
    });
    
    // Empty cells before first day
    for (let i = 0; i < firstDay; i++) {
        html += '<div class="calendar-cell empty"></div>';
    }
    
    // Days
    for (let day = 1; day <= daysInMonth; day++) {
        const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
        const hasEntry = activityData && activityData.includes(dateStr);
        const isToday = day === today.getDate();
        
        let classes = 'calendar-cell';
        if (hasEntry) classes += ' has-entry';
        if (isToday) classes += ' today';
        
        html += `<div class="${classes}">${day}</div>`;
    }
    
    html += '</div>';
    
    // Legend
    html += '<div class="calendar-legend">';
    html += '<div class="legend-item"><div class="legend-box has-entry"></div><span>Entry completato</span></div>';
    html += '<div class="legend-item"><div class="legend-box today"></div><span>Oggi</span></div>';
    html += '</div>';
    
    calendar.innerHTML = html;
}

// Add calendar styles dynamically
const calendarStyles = document.createElement('style');
calendarStyles.textContent = `
    .calendar-header {
        text-align: center;
        margin-bottom: var(--spacing-md);
    }
    
    .calendar-header h3 {
        font-family: var(--font-serif);
        font-size: 1.4rem;
        color: var(--ink-dark);
        text-transform: capitalize;
    }
    
    .calendar-grid {
        display: grid;
        grid-template-columns: repeat(7, 1fr);
        gap: 0.5rem;
    }
    
    .calendar-day-header {
        text-align: center;
        font-weight: 600;
        font-size: 0.85rem;
        color: var(--ink-medium);
        padding: 0.5rem;
    }
    
    .calendar-cell {
        aspect-ratio: 1;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--paper-bg);
        border-radius: 8px;
        font-size: 0.9rem;
        color: var(--ink-medium);
        transition: all 0.2s ease;
    }
    
    .calendar-cell.empty {
        background: transparent;
    }
    
    .calendar-cell.has-entry {
        background: var(--accent-green);
        color: var(--paper-light);
        font-weight: 600;
    }
    
    .calendar-cell.today {
        box-shadow: 0 0 0 2px var(--accent-warm);
        font-weight: 600;
    }
    
    .calendar-legend {
        display: flex;
        gap: var(--spacing-md);
        margin-top: var(--spacing-md);
        justify-content: center;
    }
    
    .legend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.85rem;
        color: var(--ink-medium);
    }
    
    .legend-box {
        width: 20px;
        height: 20px;
        border-radius: 4px;
        background: var(--paper-bg);
    }
    
    .legend-box.has-entry {
        background: var(--accent-green);
    }
    
    .legend-box.today {
        box-shadow: 0 0 0 2px var(--accent-warm);
    }
`;
document.head.appendChild(calendarStyles);

console.log('📊 Stats page scripts loaded');
