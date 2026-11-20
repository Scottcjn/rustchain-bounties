/**
 * RustChain Multiplier Growth Visualization
 * Interactive web app for visualizing mining rewards growth
 *
 * Author: 小米粒 (Xiaomili) 🌾
 * Repository: github.com/zhaog100/xiaomili-skills
 */

// Configuration
const CONFIG = {
    API_BASE: 'https://rustchain.org/api',
    UPDATE_INTERVAL: 60000, // 1 minute
    MAX_STREAK: 30,
    EPOCH_DURATION: 10, // minutes
};

// State
let state = {
    minerId: null,
    hardwareMultiplier: 1.0,
    streakDays: 0,
    streakBonus: 0,
    effectiveMultiplier: 1.0,
};

// DOM Elements
const elements = {
    hardwareMult: document.querySelector('.hardware-mult'),
    streakBonus: document.querySelector('.streak-bonus'),
    effectiveMult: document.querySelector('.effective-mult'),
    progressFill: document.querySelector('.progress-fill'),
    currentStreak: document.querySelector('.current-streak'),
    streakStatus: document.querySelector('.streak-status'),
    milestones: document.querySelectorAll('.milestone'),
    projections: document.getElementById('projections'),
    comparisonInsight: document.getElementById('comparisonInsight'),
};

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeApp();
    setupEventListeners();
    loadMinerData();
});

function initializeApp() {
    // Set default start date to today
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('startDate').value = today;

    // Start auto-update
    setInterval(loadMinerData, CONFIG.UPDATE_INTERVAL);

    console.log('🌾 RustChain Multiplier Visualization initialized');
}

function setupEventListeners() {
    // Hardware type change
    document.getElementById('hardwareType').addEventListener('change', () => {
        calculateProjections();
    });

    // Start date change
    document.getElementById('startDate').addEventListener('change', () => {
        calculateProjections();
    });
}

// API Functions
async function fetchMinerStreak(minerId) {
    try {
        const response = await fetch(
            `${CONFIG.API_BASE}/miner/${minerId}/streak`,
            {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
            }
        );

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        return await response.json();
    } catch (error) {
        console.error('Failed to fetch streak data:', error);
        return null;
    }
}

async function loadMinerData() {
    // Demo data for visualization (would use real API in production)
    const demoData = generateDemoData();
    updateUI(demoData);
    drawGrowthChart(demoData);
    calculateProjections();
    updateComparison(demoData);
}

function generateDemoData() {
    // Generate realistic demo data
    const streakDays = Math.floor(Math.random() * 30);
    const hardwareAge = Math.floor(Math.random() * 10); // years

    // Hardware multiplier increases with age
    const hardwareMultiplier = 1.0 + (hardwareAge * 0.1);

    // Streak bonus: +0.5x at 7 days, +1.0x at 14 days, +1.5x at 21 days, +2.0x at 30 days
    const streakBonus = calculateStreakBonus(streakDays);

    return {
        hardwareMultiplier: hardwareMultiplier,
        streakDays: streakDays,
        streakBonus: streakBonus,
        effectiveMultiplier: hardwareMultiplier * (1 + streakBonus),
        hardwareAge: hardwareAge,
    };
}

function calculateStreakBonus(days) {
    if (days >= 30) return 2.0;
    if (days >= 21) return 1.5;
    if (days >= 14) return 1.0;
    if (days >= 7) return 0.5;
    return 0;
}

// UI Update Functions
function updateUI(data) {
    // Update state
    state = { ...state, ...data };

    // Update status cards
    elements.hardwareMult.textContent = `${data.hardwareMultiplier.toFixed(1)}x`;
    elements.streakBonus.textContent = `+${data.streakBonus.toFixed(1)}x`;
    elements.effectiveMult.textContent = `${data.effectiveMultiplier.toFixed(1)}x`;

    // Update streak progress
    const progressPercent = (data.streakDays / CONFIG.MAX_STREAK) * 100;
    elements.progressFill.style.width = `${progressPercent}%`;
    elements.currentStreak.textContent = `${data.streakDays} / ${CONFIG.MAX_STREAK} days`;

    // Update streak status message
    if (data.streakDays >= 30) {
        elements.streakStatus.textContent = '🎉 Max streak achieved!';
    } else if (data.streakDays >= 21) {
        elements.streakStatus.textContent = '🔥 Almost there!';
    } else if (data.streakDays >= 14) {
        elements.streakStatus.textContent = '💪 Great progress!';
    } else if (data.streakDays >= 7) {
        elements.streakStatus.textContent = '🔥 Keep going!';
    } else {
        elements.streakStatus.textContent = '🌱 Just getting started';
    }

    // Update milestone highlights
    updateMilestones(data.streakDays);
}

function updateMilestones(currentDays) {
    elements.milestones.forEach((milestone, index) => {
        const days = [7, 14, 21, 30][index];
        if (currentDays >= days) {
            milestone.classList.add('achieved');
        } else {
            milestone.classList.remove('achieved');
        }
    });
}

// Chart Drawing
function drawGrowthChart(data) {
    const canvas = document.getElementById('growthChart');
    const ctx = canvas.getContext('2d');

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Set canvas size
    const container = canvas.parentElement;
    canvas.width = container.offsetWidth - 48;
    canvas.height = container.offsetHeight - 48;

    const width = canvas.width;
    const height = canvas.height;

    // Draw axes
    ctx.strokeStyle = '#3b4178';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(50, 20);
    ctx.lineTo(50, height - 30);
    ctx.lineTo(width - 20, height - 30);
    ctx.stroke();

    // Generate data points
    const days = Array.from({ length: 31 }, (_, i) => i);
    const hardwareData = days.map((day) => data.hardwareMultiplier);
    const streakData = days.map((day) => 1 + calculateStreakBonus(day));
    const totalData = days.map((day) => hardwareData[day] * streakData[day]);

    // Scale data
    const maxValue = Math.max(...totalData) * 1.1;
    const scaleY = (height - 60) / maxValue;
    const scaleX = (width - 80) / 30;

    // Draw grid
    ctx.strokeStyle = '#252b4a';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 5; i++) {
        const y = height - 30 - i * scaleY * (maxValue / 5);
        ctx.beginPath();
        ctx.moveTo(50, y);
        ctx.lineTo(width - 20, y);
        ctx.stroke();

        // Y-axis labels
        ctx.fillStyle = '#a0a4c0';
        ctx.font = '12px sans-serif';
        ctx.textAlign = 'right';
        ctx.fillText(`${(i * maxValue / 5).toFixed(1)}x`, 45, y + 4);
    }

    // Draw lines
    drawLine(ctx, days, hardwareData, scaleX, scaleY, '#f59e0b', height);
    drawLine(ctx, days, streakData, scaleX, scaleY, '#10b981', height);
    drawLine(ctx, days, totalData, scaleX, scaleY, '#6366f1', height);

    // X-axis labels
    ctx.fillStyle = '#a0a4c0';
    ctx.font = '12px sans-serif';
    ctx.textAlign = 'center';
    for (let i = 0; i <= 30; i += 5) {
        const x = 50 + i * scaleX;
        ctx.fillText(`${i}`, x, height - 10);
    }

    // X-axis title
    ctx.fillText('Days', width / 2 + 25, height - 10);
}

function drawLine(ctx, xData, yData, scaleX, scaleY, color, canvasHeight) {
    ctx.strokeStyle = color;
    ctx.lineWidth = 3;
    ctx.beginPath();

    xData.forEach((x, i) => {
        const canvasX = 50 + x * scaleX;
        const canvasY = canvasHeight - 30 - yData[i] * scaleY;

        if (i === 0) {
            ctx.moveTo(canvasX, canvasY);
        } else {
            ctx.lineTo(canvasX, canvasY);
        }
    });

    ctx.stroke();
}

// Calculator Functions
function calculateProjections() {
    const hardwareType = document.getElementById('hardwareType').value;
    const startDate = new Date(document.getElementById('startDate').value);
    const today = new Date();

    // Calculate months of mining
    const monthsSinceStart = (today - startDate) / (1000 * 60 * 60 * 24 * 30);

    // Hardware multipliers based on type
    const hardwareMultipliers = {
        cpu: { base: 1.0, growth: 0.05 },  // +5% per year
        gpu: { base: 1.2, growth: 0.08 },  // +8% per year
        asic: { base: 1.5, growth: 0.10 }, // +10% per year
        vintage: { base: 2.0, growth: 0.15 }, // +15% per year
    };

    const hw = hardwareMultipliers[hardwareType];
    const projections = [];

    // Calculate 1, 5, 10 year projections
    [1, 5, 10].forEach((years) => {
        const totalYears = (monthsSinceStart / 12) + years;
        const hardwareMult = hw.base * Math.pow(1 + hw.growth, totalYears);
        const maxStreakBonus = 2.0; // Assume max streak
        const effectiveMult = hardwareMult * (1 + maxStreakBonus);

        projections.push({
            years: years,
            hardwareMult: hardwareMult,
            effectiveMult: effectiveMult,
        });
    });

    // Update UI
    updateProjections(projections);
}

function updateProjections(projections) {
    const projectionItems = elements.projections.querySelectorAll('.projection-item');

    projections.forEach((proj, index) => {
        const item = projectionItems[index];
        const valueEl = item.querySelector('.mult-value');

        valueEl.textContent = `${proj.effectiveMult.toFixed(1)}x`;
    });
}

// Comparison Functions
function updateComparison(data) {
    const day1Earnings = 0.1; // Base earnings per epoch
    const day30Multiplier = data.effectiveMultiplier;
    const day30Earnings = day1Earnings * day30Multiplier;

    // Update day 30 values
    const day30Item = document.querySelector('.comparison-item.day30');
    day30Item.querySelector('.amount').textContent = `${day30Earnings.toFixed(2)} RTC`;
    day30Item.querySelector('.multiplier').textContent = `${day30Multiplier.toFixed(1)}x`;

    // Calculate and display insight
    const increase = ((day30Multiplier - 1) * 100).toFixed(0);
    const insight = `
        <strong>💡 Key Insight:</strong> A 30-day streak increases your earnings by 
        <span style="color: var(--accent-secondary)">${increase}%</span>! 
        That means instead of earning ${day1Earnings} RTC per epoch, you'll earn 
        <span style="color: var(--accent-primary)">${day30Earnings.toFixed(2)} RTC</span> per epoch.
    `;

    elements.comparisonInsight.innerHTML = insight;
}

// Utility Functions
function formatNumber(num) {
    return num.toLocaleString('en-US', {
        minimumFractionDigits: 1,
        maximumFractionDigits: 1,
    });
}

// Handle window resize
window.addEventListener('resize', () => {
    if (state.effectiveMultiplier) {
        drawGrowthChart(state);
    }
});

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        calculateStreakBonus,
        updateUI,
        calculateProjections,
    };
}
