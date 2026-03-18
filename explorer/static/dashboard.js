class Dashboard {
    constructor() {
        this.refreshInterval = 30000; // 30 seconds
        this.charts = {};
        this.sortState = {};
        this.init();
    }

    init() {
        this.setupAutoRefresh();
        this.setupSortableTables();
        this.initializeCharts();
        this.loadInitialData();
        this.setupEventListeners();
    }

    setupAutoRefresh() {
        setInterval(() => {
            this.refreshData();
        }, this.refreshInterval);
    }

    setupEventListeners() {
        // Refresh button
        document.getElementById('refresh-btn')?.addEventListener('click', () => {
            this.refreshData();
        });

        // Auto-refresh toggle
        document.getElementById('auto-refresh-toggle')?.addEventListener('change', (e) => {
            if (e.target.checked) {
                this.setupAutoRefresh();
            } else {
                clearInterval(this.refreshInterval);
            }
        });

        // Filter inputs
        document.getElementById('miner-filter')?.addEventListener('input', (e) => {
            this.filterTable('miners-table', e.target.value);
        });

        document.getElementById('agent-filter')?.addEventListener('input', (e) => {
            this.filterTable('agents-table', e.target.value);
        });
    }

    setupSortableTables() {
        const tables = ['miners-table', 'agents-table', 'transactions-table'];
        
        tables.forEach(tableId => {
            const table = document.getElementById(tableId);
            if (!table) return;

            const headers = table.querySelectorAll('th[data-sort]');
            headers.forEach(header => {
                header.style.cursor = 'pointer';
                header.addEventListener('click', () => {
                    this.sortTable(tableId, header.dataset.sort);
                });
            });
        });
    }

    sortTable(tableId, column) {
        const table = document.getElementById(tableId);
        const tbody = table.querySelector('tbody');
        const rows = Array.from(tbody.querySelectorAll('tr'));
        
        // Toggle sort direction
        if (!this.sortState[tableId]) this.sortState[tableId] = {};
        const currentDir = this.sortState[tableId][column] || 'asc';
        const newDir = currentDir === 'asc' ? 'desc' : 'asc';
        this.sortState[tableId][column] = newDir;

        // Update header indicators
        table.querySelectorAll('th[data-sort]').forEach(th => {
            th.classList.remove('sort-asc', 'sort-desc');
        });
        table.querySelector(`th[data-sort="${column}"]`).classList.add(`sort-${newDir}`);

        // Sort rows
        rows.sort((a, b) => {
            const aVal = this.getCellValue(a, column);
            const bVal = this.getCellValue(b, column);
            
            let comparison = 0;
            if (aVal > bVal) comparison = 1;
            if (aVal < bVal) comparison = -1;
            
            return newDir === 'desc' ? comparison * -1 : comparison;
        });

        // Reappend sorted rows
        rows.forEach(row => tbody.appendChild(row));
    }

    getCellValue(row, column) {
        const cell = row.querySelector(`[data-column="${column}"]`);
        if (!cell) return '';
        
        const text = cell.textContent.trim();
        
        // Handle different data types
        if (column.includes('time') || column.includes('date')) {
            return new Date(text).getTime();
        }
        if (column.includes('amount') || column.includes('balance') || column.includes('fee')) {
            return parseFloat(text.replace(/[^\d.-]/g, '')) || 0;
        }
        if (column.includes('block') || column.includes('height') || column.includes('count')) {
            return parseInt(text) || 0;
        }
        
        return text.toLowerCase();
    }

    filterTable(tableId, filterValue) {
        const table = document.getElementById(tableId);
        const rows = table.querySelectorAll('tbody tr');
        const filter = filterValue.toLowerCase();

        rows.forEach(row => {
            const text = row.textContent.toLowerCase();
            row.style.display = text.includes(filter) ? '' : 'none';
        });
    }

    initializeCharts() {
        this.initHashrateChart();
        this.initMinerDistributionChart();
        this.initTransactionVolumeChart();
        this.initAgentActivityChart();
    }

    initHashrateChart() {
        const ctx = document.getElementById('hashrate-chart');
        if (!ctx) return;

        this.charts.hashrate = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Network Hashrate',
                    data: [],
                    borderColor: '#3B82F6',
                    backgroundColor: 'rgba(59, 130, 246, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'TH/s'
                        }
                    }
                }
            }
        });
    }

    initMinerDistributionChart() {
        const ctx = document.getElementById('miner-distribution-chart');
        if (!ctx) return;

        this.charts.minerDistribution = new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: [],
                datasets: [{
                    data: [],
                    backgroundColor: [
                        '#3B82F6', '#10B981', '#F59E0B', '#EF4444', '#8B5CF6',
                        '#EC4899', '#06B6D4', '#84CC16', '#F97316', '#6366F1'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }

    initTransactionVolumeChart() {
        const ctx = document.getElementById('transaction-volume-chart');
        if (!ctx) return;

        this.charts.transactionVolume = new Chart(ctx, {
            type: 'bar',
            data: {
                labels: [],
                datasets: [{
                    label: 'Transaction Volume',
                    data: [],
                    backgroundColor: '#10B981',
                    borderColor: '#059669',
                    borderWidth: 1
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'RTC'
                        }
                    }
                }
            }
        });
    }

    initAgentActivityChart() {
        const ctx = document.getElementById('agent-activity-chart');
        if (!ctx) return;

        this.charts.agentActivity = new Chart(ctx, {
            type: 'line',
            data: {
                labels: [],
                datasets: [{
                    label: 'Active Agents',
                    data: [],
                    borderColor: '#F59E0B',
                    backgroundColor: 'rgba(245, 158, 11, 0.1)',
                    tension: 0.4
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        display: false
                    }
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        title: {
                            display: true,
                            text: 'Active Agents'
                        }
                    }
                }
            }
        });
    }

    async loadInitialData() {
        this.showLoading();
        try {
            await Promise.all([
                this.loadNetworkStats(),
                this.loadMinersData(),
                this.loadAgentsData(),
                this.loadRecentTransactions(),
                this.loadChartData()
            ]);
        } catch (error) {
            console.error('Error loading initial data:', error);
            this.showError('Failed to load dashboard data');
        } finally {
            this.hideLoading();
        }
    }

    async refreshData() {
        this.updateLastRefreshTime();
        try {
            await this.loadInitialData();
        } catch (error) {
            console.error('Error refreshing data:', error);
        }
    }

    async loadNetworkStats() {
        try {
            const response = await fetch('/api/network/stats');
            const stats = await response.json();
            this.updateNetworkStats(stats);
        } catch (error) {
            console.error('Error loading network stats:', error);
        }
    }

    updateNetworkStats(stats) {
        this.updateElement('network-hashrate', `${stats.hashrate} TH/s`);
        this.updateElement('active-miners', stats.active_miners);
        this.updateElement('active-agents', stats.active_agents);
        this.updateElement('current-difficulty', stats.difficulty);
        this.updateElement('block-height', stats.block_height);
        this.updateElement('total-supply', `${stats.total_supply} RTC`);
    }

    async loadMinersData() {
        try {
            const response = await fetch('/api/miners');
            const miners = await response.json();
            this.updateMinersTable(miners);
        } catch (error) {
            console.error('Error loading miners data:', error);
        }
    }

    updateMinersTable(miners) {
        const tbody = document.querySelector('#miners-table tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        miners.forEach(miner => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td data-column="address">
                    <a href="/address/${miner.address}" class="text-blue-600 hover:underline">
                        ${miner.address.substring(0, 12)}...
                    </a>
                </td>
                <td data-column="hashrate">${miner.hashrate} TH/s</td>
                <td data-column="blocks_mined">${miner.blocks_mined}</td>
                <td data-column="last_block_time">${this.formatTime(miner.last_block_time)}</td>
                <td data-column="status">
                    <span class="px-2 py-1 rounded-full text-xs ${miner.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}">
                        ${miner.status}
                    </span>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    async loadAgentsData() {
        try {
            const response = await fetch('/api/agents');
            const agents = await response.json();
            this.updateAgentsTable(agents);
        } catch (error) {
            console.error('Error loading agents data:', error);
        }
    }

    updateAgentsTable(agents) {
        const tbody = document.querySelector('#agents-table tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        agents.forEach(agent => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td data-column="id">
                    <a href="/agent/${agent.id}" class="text-blue-600 hover:underline">
                        ${agent.id}
                    </a>
                </td>
                <td data-column="type">${agent.type}</td>
                <td data-column="transactions">${agent.transactions}</td>
                <td data-column="last_activity">${this.formatTime(agent.last_activity)}</td>
                <td data-column="status">
                    <span class="px-2 py-1 rounded-full text-xs ${agent.status === 'active' ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'}">
                        ${agent.status}
                    </span>
                </td>
            `;
            tbody.appendChild(row);
        });
    }

    async loadRecentTransactions() {
        try {
            const response = await fetch('/api/transactions/recent');
            const transactions = await response.json();
            this.updateTransactionsTable(transactions);
        } catch (error) {
            console.error('Error loading recent transactions:', error);
        }
    }

    updateTransactionsTable(transactions) {
        const tbody = document.querySelector('#transactions-table tbody');
        if (!tbody) return;

        tbody.innerHTML = '';
        transactions.forEach(tx => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td data-column="hash">
                    <a href="/tx/${tx.hash}" class="text-blue-600 hover:underline font-mono">
                        ${tx.hash.substring(0, 12)}...
                    </a>
                </td>
                <td data-column="type">${tx.type}</td>
                <td data-column="amount">${tx.amount} RTC</td>
                <td data-column="fee">${tx.fee} RTC</td>
                <td data-column="time">${this.formatTime(tx.timestamp)}</td>
            `;
            tbody.appendChild(row);
        });
    }

    async loadChartData() {
        try {
            const [hashrateData, minerDistData, volumeData, agentData] = await Promise.all([
                fetch('/api/charts/hashrate').then(r => r.json()),
                fetch('/api/charts/miner-distribution').then(r => r.json()),
                fetch('/api/charts/transaction-volume').then(r => r.json()),
                fetch('/api/charts/agent-activity').then(r => r.json())
            ]);

            this.updateHashrateChart(hashrateData);
            this.updateMinerDistributionChart(minerDistData);
            this.updateTransactionVolumeChart(volumeData);
            this.updateAgentActivityChart(agentData);
        } catch (error) {
            console.error('Error loading chart data:', error);
        }
    }

    updateHashrateChart(data) {
        if (!this.charts.hashrate) return;
        
        this.charts.hashrate.data.labels = data.labels;
        this.charts.hashrate.data.datasets[0].data = data.values;
        this.charts.hashrate.update();
    }

    updateMinerDistributionChart(data) {
        if (!this.charts.minerDistribution) return;
        
        this.charts.minerDistribution.data.labels = data.labels;
        this.charts.minerDistribution.data.datasets[0].data = data.values;
        this.charts.minerDistribution.update();
    }

    updateTransactionVolumeChart(data) {
        if (!this.charts.transactionVolume) return;
        
        this.charts.transactionVolume.data.labels = data.labels;
        this.charts.transactionVolume.data.datasets[0].data = data.values;
        this.charts.transactionVolume.update();
    }

    updateAgentActivityChart(data) {
        if (!this.charts.agentActivity) return;
        
        this.charts.agentActivity.data.labels = data.labels;
        this.charts.agentActivity.data.datasets[0].data = data.values;
        this.charts.agentActivity.update();
    }

    updateElement(id, content) {
        const element = document.getElementById(id);
        if (element) {
            element.textContent = content;
        }
    }

    formatTime(timestamp) {
        const date = new Date(timestamp * 1000);
        const now = new Date();
        const diff = now - date;
        
        if (diff < 60000) return 'Just now';
        if (diff < 3600000) return `${Math.floor(diff / 60000)} min ago`;
        if (diff < 86400000) return `${Math.floor(diff / 3600000)} hr ago`;
        
        return date.toLocaleDateString();
    }

    updateLastRefreshTime() {
        const element = document.getElementById('last-refresh');
        if (element) {
            element.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
        }
    }

    showLoading() {
        const loader = document.getElementById('loading-indicator');
        if (loader) loader.style.display = 'block';
    }

    hideLoading() {
        const loader = document.getElementById('loading-indicator');
        if (loader) loader.style.display = 'none';
    }

    showError(message) {
        const errorDiv = document.getElementById('error-message');
        if (errorDiv) {
            errorDiv.textContent = message;
            errorDiv.style.display = 'block';
            setTimeout(() => {
                errorDiv.style.display = 'none';
            }, 5000);
        }
    }
}

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new Dashboard();
});

// Export for testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Dashboard;
}