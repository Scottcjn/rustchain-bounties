/**
 * wRTC Solana Bridge Dashboard
 * Real-time monitoring for wRTC bridge activity
 */

// Configuration
const CONFIG = {
    REFRESH_INTERVAL: 30000, // 30 seconds
    COUNTDOWN_INTERVAL: 1000, // 1 second
    API_ENDPOINTS: {
        rustchain: 'https://api.rustchain.org/v1',
        solana: 'https://api.mainnet-beta.solana.com',
        raydium: 'https://api.raydium.io/v2',
        dexscreener: 'https://api.dexscreener.com/latest/dex/tokens'
    },
    WRTC_TOKEN: 'wRTC_TOKEN_ADDRESS_HERE', // Replace with actual token address
    BRIDGE_CONTRACT: 'BRIDGE_CONTRACT_ADDRESS_HERE' // Replace with actual bridge contract
};

// State
let state = {
    lastUpdate: null,
    countdown: 30,
    transactions: [],
    chartData: [],
    health: {
        rustchain: { status: 'checking', detail: 'Connecting...' },
        solana: { status: 'checking', detail: 'Connecting...' }
    },
    metrics: {
        totalLocked: 0,
        totalCirculating: 0,
        price: 0,
        revenue24h: 0
    }
};

// DOM Elements
const elements = {
    lastUpdate: document.getElementById('last-update'),
    countdown: document.getElementById('countdown'),
    rustchainStatus: document.getElementById('rustchain-status'),
    rustchainDetail: document.getElementById('rustchain-detail'),
    solanaStatus: document.getElementById('solana-status'),
    solanaDetail: document.getElementById('solana-detail'),
    totalLocked: document.getElementById('total-locked'),
    totalCirculating: document.getElementById('total-circulating'),
    wrtcPrice: document.getElementById('wrtc-price'),
    bridgeRevenue: document.getElementById('bridge-revenue'),
    transactionsBody: document.getElementById('transactions-body'),
    totalWraps: document.getElementById('total-wraps'),
    totalUnwraps: document.getElementById('total-unwraps'),
    totalVolume: document.getElementById('total-volume'),
    avgFee: document.getElementById('avg-fee'),
    successRate: document.getElementById('success-rate'),
    avgTime: document.getElementById('avg-time')
};

// Chart instance
let priceChart = null;

/**
 * Initialize dashboard
 */
function init() {
    console.log('🌉 wRTC Bridge Dashboard initializing...');
    
    // Initialize chart
    initChart();
    
    // Load initial data
    refreshData();
    
    // Start refresh timer
    setInterval(refreshData, CONFIG.REFRESH_INTERVAL);
    
    // Start countdown timer
    setInterval(updateCountdown, CONFIG.COUNTDOWN_INTERVAL);
    
    // Setup event listeners
    setupEventListeners();
    
    console.log('✅ Dashboard initialized');
}

/**
 * Initialize price chart
 */
function initChart() {
    const ctx = document.getElementById('priceChart').getContext('2d');
    
    // Generate sample data (replace with real data)
    const labels = generateTimeLabels(24);
    const data = generateSamplePriceData(24);
    
    priceChart = new Chart(ctx, {
        type: 'line',
        data: {
            labels: labels,
            datasets: [{
                label: 'wRTC Price (USD)',
                data: data,
                borderColor: '#00d4aa',
                backgroundColor: 'rgba(0, 212, 170, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4,
                pointRadius: 0,
                pointHoverRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                },
                tooltip: {
                    mode: 'index',
                    intersect: false,
                    backgroundColor: '#1a1f4b',
                    titleColor: '#ffffff',
                    bodyColor: '#8b92b4',
                    borderColor: '#2d3561',
                    borderWidth: 1,
                    callbacks: {
                        label: function(context) {
                            return '$' + context.parsed.y.toFixed(4);
                        }
                    }
                }
            },
            scales: {
                x: {
                    grid: {
                        color: '#2d3561',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#8b92b4',
                        maxTicksLimit: 8
                    }
                },
                y: {
                    grid: {
                        color: '#2d3561',
                        drawBorder: false
                    },
                    ticks: {
                        color: '#8b92b4',
                        callback: function(value) {
                            return '$' + value.toFixed(4);
                        }
                    }
                }
            },
            interaction: {
                mode: 'nearest',
                axis: 'x',
                intersect: false
            }
        }
    });
}

/**
 * Generate time labels for chart
 */
function generateTimeLabels(count) {
    const labels = [];
    const now = new Date();
    for (let i = count - 1; i >= 0; i--) {
        const time = new Date(now - i * 3600000);
        labels.push(time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }));
    }
    return labels;
}

/**
 * Generate sample price data (replace with real API data)
 */
function generateSamplePriceData(count) {
    const data = [];
    let price = 0.10;
    for (let i = 0; i < count; i++) {
        price = price * (1 + (Math.random() - 0.5) * 0.05);
        data.push(price);
    }
    return data;
}

/**
 * Refresh all dashboard data
 */
async function refreshData() {
    console.log('🔄 Refreshing data...');
    
    try {
        // Check bridge health
        await checkBridgeHealth();
        
        // Fetch metrics
        await fetchMetrics();
        
        // Fetch transactions
        await fetchTransactions();
        
        // Update chart
        await updateChart();
        
        // Update stats
        updateStats();
        
        // Update UI
        updateUI();
        
        // Reset countdown
        state.countdown = 30;
        state.lastUpdate = new Date();
        
        console.log('✅ Data refreshed');
    } catch (error) {
        console.error('❌ Error refreshing data:', error);
        showError('Failed to refresh data. Retrying...');
    }
}

/**
 * Check bridge health status
 */
async function checkBridgeHealth() {
    // Check RustChain API
    try {
        const response = await fetch(`${CONFIG.API_ENDPOINTS.rustchain}/health`);
        if (response.ok) {
            state.health.rustchain = { status: 'healthy', detail: 'API responding normally' };
        } else {
            state.health.rustchain = { status: 'warning', detail: 'API degraded' };
        }
    } catch (error) {
        state.health.rustchain = { status: 'error', detail: 'API unreachable' };
    }
    
    // Check Solana RPC
    try {
        const response = await fetch(CONFIG.API_ENDPOINTS.solana, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                jsonrpc: '2.0',
                id: 1,
                method: 'getHealth'
            })
        });
        const data = await response.json();
        if (data.result === 'ok') {
            state.health.solana = { status: 'healthy', detail: 'RPC responding normally' };
        } else {
            state.health.solana = { status: 'warning', detail: 'RPC degraded' };
        }
    } catch (error) {
        state.health.solana = { status: 'error', detail: 'RPC unreachable' };
    }
}

/**
 * Fetch bridge metrics
 */
async function fetchMetrics() {
    // Simulate fetching metrics (replace with real API calls)
    // In production, these would be actual API calls to:
    // - RustChain API for locked RTC
    // - Solana RPC for wRTC supply
    // - Raydium/DexScreener for price data
    
    state.metrics = {
        totalLocked: 1250000 + Math.random() * 10000,
        totalCirculating: 980000 + Math.random() * 5000,
        price: 0.10 + (Math.random() - 0.5) * 0.02,
        revenue24h: 450 + Math.random() * 50
    };
}

/**
 * Fetch recent transactions
 */
async function fetchTransactions() {
    // Simulate transaction data (replace with real API data)
    const txTypes = ['wrap', 'unwrap'];
    const statuses = ['confirmed', 'confirmed', 'confirmed', 'pending'];
    
    state.transactions = [];
    for (let i = 0; i < 10; i++) {
        const type = txTypes[Math.floor(Math.random() * txTypes.length)];
        const amount = (Math.random() * 10000 + 100).toFixed(2);
        const time = new Date(Date.now() - Math.random() * 86400000);
        
        state.transactions.push({
            type: type,
            amount: amount,
            from: type === 'wrap' ? 'RTC...' + generateRandomString(4) : 'wRTC...' + generateRandomString(4),
            to: type === 'wrap' ? 'wRTC...' + generateRandomString(4) : 'RTC...' + generateRandomString(4),
            time: time,
            status: statuses[Math.floor(Math.random() * statuses.length)]
        });
    }
    
    // Sort by time (newest first)
    state.transactions.sort((a, b) => b.time - a.time);
}

/**
 * Generate random string for addresses
 */
function generateRandomString(length) {
    const chars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let result = '';
    for (let i = 0; i < length; i++) {
        result += chars.charAt(Math.floor(Math.random() * chars.length));
    }
    return result;
}

/**
 * Update price chart
 */
async function updateChart() {
    // Update with new data point
    const newPrice = state.metrics.price;
    const now = new Date();
    const timeLabel = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    
    // Add new data
    priceChart.data.labels.push(timeLabel);
    priceChart.data.datasets[0].data.push(newPrice);
    
    // Remove old data if too many points
    if (priceChart.data.labels.length > 24) {
        priceChart.data.labels.shift();
        priceChart.data.datasets[0].data.shift();
    }
    
    priceChart.update('none'); // Update without animation
}

/**
 * Update bridge statistics
 */
function updateStats() {
    const wraps = state.transactions.filter(tx => tx.type === 'wrap').length;
    const unwraps = state.transactions.filter(tx => tx.type === 'unwrap').length;
    const volume = state.transactions.reduce((sum, tx) => sum + parseFloat(tx.amount), 0);
    
    state.stats = {
        totalWraps: wraps,
        totalUnwraps: unwraps,
        totalVolume: volume,
        avgFee: (0.1 + Math.random() * 0.05).toFixed(3),
        successRate: (95 + Math.random() * 4).toFixed(1),
        avgTime: (2 + Math.random() * 3).toFixed(1)
    };
}

/**
 * Update UI elements
 */
function updateUI() {
    // Update last update time
    if (state.lastUpdate) {
        elements.lastUpdate.textContent = `Last update: ${formatTimeAgo(state.lastUpdate)}`;
    }
    
    // Update health status
    updateHealthUI();
    
    // Update metrics
    updateMetricsUI();
    
    // Update transactions table
    updateTransactionsUI();
    
    // Update stats
    updateStatsUI();
}

/**
 * Update health status UI
 */
function updateHealthUI() {
    const rustchainCard = document.getElementById('rustchain-health');
    const solanaCard = document.getElementById('solana-health');
    
    // Update RustChain health
    elements.rustchainStatus.textContent = state.health.rustchain.status;
    elements.rustchainStatus.className = `status-badge ${state.health.rustchain.status}`;
    elements.rustchainDetail.textContent = state.health.rustchain.detail;
    
    // Update Solana health
    elements.solanaStatus.textContent = state.health.solana.status;
    elements.solanaStatus.className = `status-badge ${state.health.solana.status}`;
    elements.solanaDetail.textContent = state.health.solana.detail;
}

/**
 * Update metrics UI
 */
function updateMetricsUI() {
    elements.totalLocked.textContent = formatNumber(state.metrics.totalLocked);
    elements.totalCirculating.textContent = formatNumber(state.metrics.totalCirculating);
    elements.wrtcPrice.textContent = '$' + state.metrics.price.toFixed(4);
    elements.bridgeRevenue.textContent = '$' + formatNumber(state.metrics.revenue24h);
    
    // Add change indicators (simulated)
    const lockedChange = (Math.random() - 0.5) * 2;
    const circulatingChange = (Math.random() - 0.5) * 2;
    const priceChange = (Math.random() - 0.5) * 5;
    const revenueChange = (Math.random() - 0.5) * 10;
    
    updateChangeIndicator('locked-change', lockedChange);
    updateChangeIndicator('circulating-change', circulatingChange);
    updateChangeIndicator('price-change', priceChange);
    updateChangeIndicator('revenue-change', revenueChange);
}

/**
 * Update change indicator
 */
function updateChangeIndicator(elementId, change) {
    const element = document.getElementById(elementId);
    const sign = change >= 0 ? '+' : '';
    element.textContent = `${sign}${change.toFixed(2)}%`;
    element.className = `metric-change ${change >= 0 ? 'positive' : 'negative'}`;
}

/**
 * Update transactions table UI
 */
function updateTransactionsUI() {
    const tbody = elements.transactionsBody;
    tbody.innerHTML = '';
    
    state.transactions.forEach(tx => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td><span class="tx-type ${tx.type}">${tx.type.toUpperCase()}</span></td>
            <td>${formatNumber(tx.amount)}</td>
            <td class="tx-address">${tx.from}</td>
            <td class="tx-address">${tx.to}</td>
            <td>${formatTimeAgo(tx.time)}</td>
            <td><span class="tx-status ${tx.status}">${tx.status}</span></td>
        `;
        tbody.appendChild(row);
    });
}

/**
 * Update stats UI
 */
function updateStatsUI() {
    if (state.stats) {
        elements.totalWraps.textContent = state.stats.totalWraps;
        elements.totalUnwraps.textContent = state.stats.totalUnwraps;
        elements.totalVolume.textContent = formatNumber(state.stats.totalVolume);
        elements.avgFee.textContent = state.stats.avgFee + '%';
        elements.successRate.textContent = state.stats.successRate + '%';
        elements.avgTime.textContent = state.stats.avgTime + 's';
    }
}

/**
 * Update countdown timer
 */
function updateCountdown() {
    state.countdown = Math.max(0, state.countdown - 1);
    elements.countdown.textContent = state.countdown;
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Time period buttons
    document.querySelectorAll('.time-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.time-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            // In production, this would fetch data for the selected period
            console.log('Switched to period:', this.dataset.period);
        });
    });
    
    // Filter buttons
    document.querySelectorAll('.filter-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
            this.classList.add('active');
            filterTransactions(this.dataset.filter);
        });
    });
}

/**
 * Filter transactions by type
 */
function filterTransactions(filter) {
    const rows = document.querySelectorAll('#transactions-body tr');
    rows.forEach(row => {
        const typeCell = row.querySelector('.tx-type');
        if (!typeCell) return;
        
        if (filter === 'all') {
            row.style.display = '';
        } else {
            row.style.display = typeCell.classList.contains(filter) ? '' : 'none';
        }
    });
}

/**
 * Format number with commas
 */
function formatNumber(num) {
    if (num === null || num === undefined) return '--';
    return parseFloat(num).toLocaleString('en-US', {
        minimumFractionDigits: 0,
        maximumFractionDigits: 2
    });
}

/**
 * Format time ago
 */
function formatTimeAgo(date) {
    const now = new Date();
    const diff = now - new Date(date);
    const seconds = Math.floor(diff / 1000);
    const minutes = Math.floor(seconds / 60);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    
    if (seconds < 60) return 'Just now';
    if (minutes < 60) return `${minutes}m ago`;
    if (hours < 24) return `${hours}h ago`;
    if (days < 7) return `${days}d ago`;
    return new Date(date).toLocaleDateString();
}

/**
 * Show error message
 */
function showError(message) {
    console.error('❌ Error:', message);
    // Could add a toast notification here
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}