// Beacon Atlas City Visualization - Main Application

class BeaconAtlasVisualization {
    constructor() {
        this.canvas = document.getElementById('cityCanvas');
        this.ctx = this.canvas.getContext('2d');
        this.tooltip = document.getElementById('tooltip');
        this.agents = [];
        this.properties = [];
        this.connections = [];
        this.selectedCity = 'all';
        this.searchTerm = '';

        this.init();
    }

    init() {
        this.resizeCanvas();
        this.loadData();
        this.bindEvents();
        this.render();
    }

    resizeCanvas() {
        this.canvas.width = this.canvas.offsetWidth;
        this.canvas.height = this.canvas.offsetHeight;
    }

    loadData() {
        // Sample data - would be fetched from API in production
        this.agents = [
            { id: 1, name: 'Agent Alpha', city: 'genesis', properties: 3, value: 15000, x: 0.3, y: 0.4 },
            { id: 2, name: 'Agent Beta', city: 'genesis', properties: 2, value: 8500, x: 0.5, y: 0.3 },
            { id: 3, name: 'Agent Gamma', city: 'aurora', properties: 5, value: 25000, x: 0.7, y: 0.5 },
            { id: 4, name: 'Agent Delta', city: 'aurora', properties: 1, value: 3000, x: 0.6, y: 0.7 },
            { id: 5, name: 'Agent Epsilon', city: 'nexus', properties: 4, value: 18000, x: 0.4, y: 0.6 },
            { id: 6, name: 'Agent Zeta', city: 'nexus', properties: 2, value: 9000, x: 0.2, y: 0.5 },
            { id: 7, name: 'Agent Eta', city: 'genesis', properties: 6, value: 35000, x: 0.8, y: 0.4 },
            { id: 8, name: 'Agent Theta', city: 'aurora', properties: 3, value: 12000, x: 0.3, y: 0.8 },
        ];

        this.properties = [
            { id: 1, agentId: 1, type: 'residential', value: 5000 },
            { id: 2, agentId: 1, type: 'commercial', value: 7000 },
            { id: 3, agentId: 1, type: 'industrial', value: 3000 },
            { id: 4, agentId: 3, type: 'residential', value: 10000 },
            { id: 5, agentId: 3, type: 'commercial', value: 15000 },
        ];

        this.connections = [
            { from: 1, to: 2 },
            { from: 1, to: 5 },
            { from: 2, to: 3 },
            { from: 3, to: 4 },
            { from: 5, to: 6 },
            { from: 7, to: 1 },
            { from: 7, to: 3 },
            { from: 8, to: 4 },
        ];

        this.updateStats();
        this.updateAgentList();
    }

    bindEvents() {
        window.addEventListener('resize', () => {
            this.resizeCanvas();
            this.render();
        });

        document.getElementById('citySelect').addEventListener('change', (e) => {
            this.selectedCity = e.target.value;
            this.render();
            this.updateStats();
            this.updateAgentList();
        });

        document.getElementById('searchInput').addEventListener('input', (e) => {
            this.searchTerm = e.target.value.toLowerCase();
            this.updateAgentList();
            this.render();
        });

        document.getElementById('refreshBtn').addEventListener('click', () => {
            this.loadData();
            this.render();
        });

        this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
        this.canvas.addEventListener('mouseleave', () => this.hideTooltip());
    }

    getFilteredAgents() {
        return this.agents.filter(agent => {
            const cityMatch = this.selectedCity === 'all' || agent.city === this.selectedCity;
            const searchMatch = !this.searchTerm || agent.name.toLowerCase().includes(this.searchTerm);
            return cityMatch && searchMatch;
        });
    }

    updateStats() {
        const filtered = this.getFilteredAgents();
        const totalAgents = filtered.length;
        const totalProperties = filtered.reduce((sum, a) => sum + a.properties, 0);
        const totalValue = filtered.reduce((sum, a) => sum + a.value, 0);

        document.getElementById('totalAgents').textContent = totalAgents;
        document.getElementById('totalProperties').textContent = totalProperties;
        document.getElementById('totalValue').textContent = '$' + totalValue.toLocaleString();
    }

    updateAgentList() {
        const list = document.getElementById('agentList');
        const filtered = this.getFilteredAgents()
            .sort((a, b) => b.value - a.value)
            .slice(0, 10);

        list.innerHTML = filtered.map(agent => `
            <li data-agent-id="${agent.id}">
                <div class="agent-name">${agent.name}</div>
                <div class="agent-info">
                    ${agent.properties} properties • $${agent.value.toLocaleString()}
                </div>
            </li>
        `).join('');

        list.querySelectorAll('li').forEach(li => {
            li.addEventListener('click', () => {
                const agentId = parseInt(li.dataset.agentId);
                this.highlightAgent(agentId);
            });
        });
    }

    render() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.drawConnections();
        this.drawNodes();
    }

    drawConnections() {
        const filtered = this.getFilteredAgents();
        const agentMap = new Map(filtered.map(a => [a.id, a]));

        this.connections.forEach(conn => {
            const fromAgent = agentMap.get(conn.from);
            const toAgent = agentMap.get(conn.to);

            if (fromAgent && toAgent) {
                this.ctx.beginPath();
                this.ctx.moveTo(
                    fromAgent.x * this.canvas.width,
                    fromAgent.y * this.canvas.height
                );
                this.ctx.lineTo(
                    toAgent.x * this.canvas.width,
                    toAgent.y * this.canvas.height
                );
                this.ctx.strokeStyle = 'rgba(58, 123, 213, 0.3)';
                this.ctx.lineWidth = 1;
                this.ctx.setLineDash([5, 5]);
                this.ctx.stroke();
                this.ctx.setLineDash([]);
            }
        });
    }

    drawNodes() {
        const filtered = this.getFilteredAgents();

        filtered.forEach(agent => {
            const x = agent.x * this.canvas.width;
            const y = agent.y * this.canvas.height;
            const radius = Math.max(15, Math.min(40, agent.value / 1000));

            // Glow effect
            const gradient = this.ctx.createRadialGradient(x, y, 0, x, y, radius * 2);
            gradient.addColorStop(0, 'rgba(0, 210, 255, 0.8)');
            gradient.addColorStop(0.5, 'rgba(58, 123, 213, 0.4)');
            gradient.addColorStop(1, 'rgba(58, 123, 213, 0)');

            this.ctx.beginPath();
            this.ctx.arc(x, y, radius * 2, 0, Math.PI * 2);
            this.ctx.fillStyle = gradient;
            this.ctx.fill();

            // Main node
            this.ctx.beginPath();
            this.ctx.arc(x, y, radius, 0, Math.PI * 2);
            this.ctx.fillStyle = this.getCityColor(agent.city);
            this.ctx.fill();
            this.ctx.strokeStyle = '#00d2ff';
            this.ctx.lineWidth = 2;
            this.ctx.stroke();

            // Label
            this.ctx.fillStyle = '#ffffff';
            this.ctx.font = '12px sans-serif';
            this.ctx.textAlign = 'center';
            this.ctx.fillText(agent.name, x, y + radius + 15);
        });
    }

    getCityColor(city) {
        const colors = {
            genesis: '#3a7bd5',
            aurora: '#00d2ff',
            nexus: '#9b59b6'
        };
        return colors[city] || '#3a7bd5';
    }

    handleMouseMove(e) {
        const rect = this.canvas.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const filtered = this.getFilteredAgents();
        const hoveredAgent = filtered.find(agent => {
            const ax = agent.x * this.canvas.width;
            const ay = agent.y * this.canvas.height;
            const radius = Math.max(15, Math.min(40, agent.value / 1000));
            const distance = Math.sqrt((x - ax) ** 2 + (y - ay) ** 2);
            return distance < radius;
        });

        if (hoveredAgent) {
            this.showTooltip(hoveredAgent, e.clientX, e.clientY);
        } else {
            this.hideTooltip();
        }
    }

    showTooltip(agent, mouseX, mouseY) {
        const rect = this.canvas.getBoundingClientRect();
        this.tooltip.innerHTML = `
            <h3>${agent.name}</h3>
            <p><strong>City:</strong> ${agent.city}</p>
            <p><strong>Properties:</strong> ${agent.properties}</p>
            <p><strong>Total Value:</strong> $${agent.value.toLocaleString()}</p>
        `;
        this.tooltip.style.left = (mouseX - rect.left + 10) + 'px';
        this.tooltip.style.top = (mouseY - rect.top + 10) + 'px';
        this.tooltip.classList.add('visible');
    }

    hideTooltip() {
        this.tooltip.classList.remove('visible');
    }

    highlightAgent(agentId) {
        const agent = this.agents.find(a => a.id === agentId);
        if (agent) {
            this.render();
            const x = agent.x * this.canvas.width;
            const y = agent.y * this.canvas.height;
            const radius = Math.max(15, Math.min(40, agent.value / 1000));

            this.ctx.beginPath();
            this.ctx.arc(x, y, radius + 10, 0, Math.PI * 2);
            this.ctx.strokeStyle = '#ff6b6b';
            this.ctx.lineWidth = 3;
            this.ctx.stroke();
        }
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    new BeaconAtlasVisualization();
});
