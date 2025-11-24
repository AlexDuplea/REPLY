document.addEventListener('DOMContentLoaded', () => {
    initStats();
});

let charts = {};
let rawData = {
    entries: [],
    stats: {},
    sentiment: {}
};

async function initStats() {
    // Show skeletons/loading state if needed

    try {
        await Promise.all([
            fetchBasicStats(),
            fetchSentimentData(365), // Fetch long history for local processing
            fetchRecentEntries(365)
        ]);

        renderOverview();
        renderInsights();
        renderCharts('7'); // Default to 7 days
        renderHeatmap();
        renderMilestones();

        setupEventListeners();

    } catch (error) {
        console.error("Error initializing stats:", error);
    }
}

async function fetchBasicStats() {
    const response = await fetch('/api/stats');
    const data = await response.json();
    if (data.success) {
        rawData.stats = data.stats;
        rawData.milestones = data.milestones;
    }
}

async function fetchSentimentData(days) {
    const response = await fetch(`/api/sentiment/data?days=${days}`);
    const data = await response.json();
    if (data.success) {
        rawData.sentiment = data.sentiment_data;
    }
}

async function fetchRecentEntries(days) {
    const response = await fetch(`/api/entries/recent?days=${days}`);
    const data = await response.json();
    if (data.success) {
        rawData.entries = data.entries;
    }
}

function renderOverview() {
    // Animate numbers
    animateValue("streak-value", 0, rawData.stats.current_streak || 0, 1000);
    animateValue("longest-streak-value", 0, rawData.stats.longest_streak || 0, 1000);
    animateValue("total-entries-value", 0, rawData.stats.total_entries || 0, 1000);

    // Calculate derived stats
    const totalWords = rawData.entries.reduce((acc, entry) => acc + (entry.entry.split(/\s+/).length || 0), 0);
    animateValue("words-value", 0, totalWords, 1500);

    // Frequency (entries / weeks active)
    if (rawData.entries.length > 0) {
        const firstDate = new Date(rawData.entries[rawData.entries.length - 1].date);
        const now = new Date();
        const weeksDiff = Math.max(1, (now - firstDate) / (1000 * 60 * 60 * 24 * 7));
        const freq = (rawData.entries.length / weeksDiff).toFixed(1);
        document.getElementById("freq-value").textContent = freq;
    }
}

function renderInsights() {
    const container = document.getElementById('insights-container');
    container.innerHTML = ''; // Clear skeletons

    if (rawData.entries.length === 0) {
        container.innerHTML = '<div class="insight-item">Nessun dato sufficiente per generare insights.</div>';
        return;
    }

    const insights = [];

    // 1. Most Productive Day
    const dayCounts = {};
    const days = ['Domenica', 'Lunedì', 'Martedì', 'Mercoledì', 'Giovedì', 'Venerdì', 'Sabato'];
    rawData.entries.forEach(e => {
        const d = new Date(e.date).getDay();
        dayCounts[d] = (dayCounts[d] || 0) + 1;
    });
    const bestDayIndex = Object.keys(dayCounts).reduce((a, b) => dayCounts[a] > dayCounts[b] ? a : b);
    insights.push({ icon: 'ph-calendar-check', text: `Scrivi di più il <strong>${days[bestDayIndex]}</strong>` });

    // 2. Average Length
    const totalWords = rawData.entries.reduce((acc, entry) => acc + (entry.entry.split(/\s+/).length || 0), 0);
    const avgWords = Math.round(totalWords / rawData.entries.length);
    insights.push({ icon: 'ph-text-aa', text: `Media di <strong>${avgWords} parole</strong> per entry` });

    // 3. Prevalent Emotion (using sentiment data)
    const emotions = {
        'Stress': rawData.sentiment.stress,
        'Felicità': rawData.sentiment.happiness,
        'Energia': rawData.sentiment.energy
    };
    // Simple average
    let maxEmotion = '';
    let maxVal = -1;
    for (const [key, arr] of Object.entries(emotions)) {
        if (!arr || arr.length === 0) continue;
        const avg = arr.reduce((a, b) => a + b, 0) / arr.length;
        if (avg > maxVal) {
            maxVal = avg;
            maxEmotion = key;
        }
    }
    if (maxEmotion) {
        insights.push({ icon: 'ph-heart', text: `Emozione prevalente: <strong>${maxEmotion}</strong>` });
    }

    // Render
    insights.forEach(insight => {
        const div = document.createElement('div');
        div.className = 'insight-item';
        div.innerHTML = `<i class="ph ${insight.icon}"></i> <span>${insight.text}</span>`;
        container.appendChild(div);
    });
}

function renderCharts(period) {
    const days = parseInt(period);

    // Helper to get data for current period and previous period
    const getDataForPeriod = (arr, days) => {
        const current = arr.slice(-days);
        const previous = arr.slice(-(days * 2), -days);
        return { current, previous };
    };

    const labels = rawData.sentiment.dates.slice(-days);

    // Update charts and trends
    updateChartWithTrend('stressChart', 'Stress', labels, rawData.sentiment.stress, days, 'rgb(248, 113, 113)', 'stress-trend');
    updateChartWithTrend('happinessChart', 'Felicità', labels, rawData.sentiment.happiness, days, 'rgb(251, 191, 36)', 'happiness-trend');
    updateChartWithTrend('energyChart', 'Energia', labels, rawData.sentiment.energy, days, 'rgb(96, 165, 250)', 'energy-trend');

    renderRadarChart();
    renderConsistencyChart(days);
}

function updateChartWithTrend(canvasId, label, labels, fullData, days, color, trendId) {
    const currentData = fullData.slice(-days);
    const previousData = fullData.slice(-(days * 2), -days);

    // Calculate trend
    const currentAvg = currentData.length ? (currentData.reduce((a, b) => a + b, 0) / currentData.length) : 0;
    const previousAvg = previousData.length ? (previousData.reduce((a, b) => a + b, 0) / previousData.length) : 0;

    let trendHtml = '<span class="text-gray-400">--</span>';
    if (previousAvg > 0) {
        const diff = currentAvg - previousAvg;
        const pct = ((diff / previousAvg) * 100).toFixed(1);
        const icon = diff > 0 ? 'ph-trend-up' : 'ph-trend-down';
        // For stress, up is bad. For others, up is good.
        const isPositive = label === 'Stress' ? diff < 0 : diff > 0;
        const colorClass = isPositive ? 'text-green-500' : 'text-red-500'; // Using Tailwind-like classes or style
        const colorStyle = isPositive ? 'var(--stat-positive)' : 'var(--stat-negative)';

        trendHtml = `<span style="color: ${colorStyle}; font-size: 0.9rem; font-weight: 500;">
            <i class="ph ${icon}"></i> ${Math.abs(pct)}%
        </span>`;
    }

    document.getElementById(trendId).innerHTML = trendHtml;

    updateChart(canvasId, label, labels, currentData, color);
}

function updateChart(canvasId, label, labels, data, color) {
    const ctx = document.getElementById(canvasId).getContext('2d');

    if (charts[canvasId]) {
        charts[canvasId].destroy();
    }

    charts[canvasId] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: label,
                data: data,
                borderColor: color,
                backgroundColor: color.replace('rgb', 'rgba').replace(')', ', 0.1)'),
                tension: 0.4,
                fill: true,
                pointRadius: 4,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    max: 12,
                    grid: { display: false }
                },
                x: {
                    grid: { display: false },
                    ticks: { maxTicksLimit: 7 }
                }
            }
        }
    });
}

function renderRadarChart() {
    const ctx = document.getElementById('radarChart').getContext('2d');
    const overall = rawData.sentiment.overall; // [Happy, Energy, Calm, Motivation, Overall]

    if (charts['radarChart']) charts['radarChart'].destroy();

    charts['radarChart'] = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: ['Felicità', 'Energia', 'Calma', 'Motivazione', 'Generale'],
            datasets: [{
                label: 'Media Periodo',
                data: overall,
                fill: true,
                backgroundColor: 'rgba(52, 211, 153, 0.2)',
                borderColor: 'rgb(52, 211, 153)',
                pointBackgroundColor: 'rgb(52, 211, 153)',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: 'rgb(52, 211, 153)'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            elements: {
                line: { borderWidth: 3 }
            },
            scales: {
                r: {
                    angleLines: { display: true },
                    suggestedMin: 0,
                    suggestedMax: 12,
                    layout: { padding: { top: 20, bottom: 20, left: 20, right: 20 } }
                }
            }
        }
    });
}

function renderConsistencyChart(days) {
    const ctx = document.getElementById('consistencyChart').getContext('2d');

    const labels = rawData.sentiment.dates.slice(-days);
    // Use actual entries to determine consistency
    // Map dates to entry counts
    const entryCounts = labels.map(dateLabel => {
        // dateLabel is DD/MM, need to match with rawData.entries
        // This is a bit fuzzy, but for now we check if any entry ends with this date string
        // Better: use full dates in labels if possible, or just check existence
        return 1; // Placeholder
    });

    if (charts['consistencyChart']) charts['consistencyChart'].destroy();

    charts['consistencyChart'] = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Entries',
                data: entryCounts,
                backgroundColor: 'rgba(16, 185, 129, 0.6)',
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { display: false },
                x: { grid: { display: false } }
            }
        }
    });
}

function renderHeatmap() {
    const container = document.getElementById('heatmap-container');
    container.innerHTML = '';

    // Generate last 52 weeks (approx 365 days)
    const today = new Date();
    // Start from 52 weeks ago, aligned to Sunday
    const startDate = new Date(today);
    startDate.setDate(today.getDate() - 365);
    while (startDate.getDay() !== 0) {
        startDate.setDate(startDate.getDate() - 1);
    }

    // Create map of date -> count
    const activityMap = {};
    rawData.entries.forEach(e => {
        const d = e.date.split('T')[0]; // YYYY-MM-DD
        activityMap[d] = (activityMap[d] || 0) + 1;
    });

    let currentDate = new Date(startDate);

    // Create columns (weeks)
    for (let w = 0; w < 53; w++) {
        const col = document.createElement('div');
        col.className = 'heatmap-col';

        for (let d = 0; d < 7; d++) {
            const dateStr = currentDate.toISOString().split('T')[0];
            const count = activityMap[dateStr] || 0;
            const level = Math.min(count, 4);

            const cell = document.createElement('div');
            cell.className = `heatmap-cell level-${level}`;
            cell.title = `${dateStr}: ${count} entries`;

            // Interaction
            if (count > 0) {
                cell.addEventListener('click', () => openEntryModal(dateStr));
            }

            col.appendChild(cell);

            // Increment date
            currentDate.setDate(currentDate.getDate() + 1);
            if (currentDate > today && w === 52) break; // Stop if future
        }
        container.appendChild(col);
    }
}

function renderMilestones() {
    const container = document.getElementById('milestones-container');
    container.innerHTML = '';

    const milestones = [
        { target: 3, label: 'Primi Passi', icon: 'ph-footprints' },
        { target: 7, label: 'Una Settimana', icon: 'ph-star' },
        { target: 30, label: 'Abitudine Mensile', icon: 'ph-calendar' },
        { target: 100, label: 'Centenario', icon: 'ph-crown' }
    ];

    const currentStreak = rawData.stats.current_streak || 0;

    milestones.forEach(m => {
        const progress = Math.min(100, (currentStreak / m.target) * 100);
        const isCompleted = currentStreak >= m.target;

        const div = document.createElement('div');
        div.className = 'milestone-card';
        div.innerHTML = `
            <div class="milestone-header">
                <span class="milestone-title"><i class="ph ${m.icon}"></i> ${m.label}</span>
                ${isCompleted ? '<i class="ph ph-check-circle" style="color: var(--stat-positive)"></i>' : ''}
            </div>
            <div class="milestone-progress-bg">
                <div class="milestone-progress-bar" style="width: ${progress}%"></div>
            </div>
            <div class="milestone-meta">
                <span>${currentStreak} / ${m.target} giorni</span>
                <span>${Math.round(progress)}%</span>
            </div>
        `;
        container.appendChild(div);
    });
}

function setupEventListeners() {
    // Time filters
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            e.target.classList.add('active');
            renderCharts(e.target.dataset.period);
        });
    });

    // Modal close
    document.querySelector('.close-modal').addEventListener('click', () => {
        document.getElementById('entry-modal').style.display = 'none';
    });

    // Export buttons
    document.getElementById('export-csv').addEventListener('click', exportCSV);
    document.getElementById('export-pdf').addEventListener('click', () => window.print());
}

function openEntryModal(dateStr) {
    const modal = document.getElementById('entry-modal');
    const entry = rawData.entries.find(e => e.date.startsWith(dateStr));

    if (entry) {
        document.getElementById('modal-date').textContent = new Date(dateStr).toLocaleDateString('it-IT', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' });
        document.getElementById('modal-body').innerHTML = entry.entry.replace(/\n/g, '<br>');
        modal.style.display = 'block';
    }
}

function animateValue(id, start, end, duration) {
    if (start === end) return;
    const range = end - start;
    let current = start;
    const increment = end > start ? 1 : -1;
    const stepTime = Math.abs(Math.floor(duration / range));
    const obj = document.getElementById(id);

    const timer = setInterval(function () {
        current += increment;
        obj.innerHTML = current;
        if (current == end) {
            clearInterval(timer);
        }
    }, Math.max(stepTime, 10)); // Min 10ms
}

function exportCSV() {
    let csvContent = "data:text/csv;charset=utf-8,";
    csvContent += "Date,Entry,Stress,Happiness,Energy\n";

    rawData.entries.forEach(e => {
        const meta = e.metadata?.emotions_detected || {};
        const row = [
            e.date,
            `"${e.entry.replace(/"/g, '""')}"`, // Escape quotes
            meta.stress || 0,
            meta.happiness || 0,
            meta.fatigue ? (10 - meta.fatigue) : 0
        ].join(",");
        csvContent += row + "\n";
    });

    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "wemind_export.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
