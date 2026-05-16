class BeaconAtlasVisualization {
    constructor() {
        this.canvas = document.getElementById("cityCanvas");
        this.ctx = this.canvas.getContext("2d");
        this.tooltip = document.getElementById("tooltip");
        this.view = { zoom: 1, panX: 0, panY: 0 };
        this.drag = { active: false, moved: false, x: 0, y: 0 };
        this.selectedCity = "all";
        this.selectedRole = "all";
        this.selectedProperty = "all";
        this.searchTerm = "";
        this.selectedAgentId = null;

        this.loadData();
        this.resizeCanvas();
        this.bindEvents();
        this.updateSidebar();
        this.animate();
    }

    loadData() {
        this.cities = [
            { id: "genesis", name: "Genesis City", x: 260, y: 260, rx: 230, ry: 185, color: "#51a7ff" },
            { id: "aurora", name: "Aurora City", x: 710, y: 250, rx: 235, ry: 180, color: "#39d5e8" },
            { id: "nexus", name: "Nexus City", x: 500, y: 520, rx: 250, ry: 190, color: "#a584ff" },
        ];
        this.agents = [
            { id: 1, name: "Agent Alpha", city: "genesis", role: "miner", heartbeat: "online", mayday: false, x: 180, y: 225 },
            { id: 2, name: "Agent Beta", city: "genesis", role: "validator", heartbeat: "online", mayday: false, x: 340, y: 280 },
            { id: 3, name: "Agent Gamma", city: "aurora", role: "maker", heartbeat: "delayed", mayday: true, x: 655, y: 220 },
            { id: 4, name: "Agent Delta", city: "aurora", role: "sentinel", heartbeat: "online", mayday: false, x: 800, y: 325 },
            { id: 5, name: "Agent Epsilon", city: "nexus", role: "miner", heartbeat: "online", mayday: false, x: 455, y: 475 },
            { id: 6, name: "Agent Zeta", city: "nexus", role: "validator", heartbeat: "offline", mayday: true, x: 575, y: 585 },
            { id: 7, name: "Agent Eta", city: "genesis", role: "maker", heartbeat: "online", mayday: false, x: 400, y: 155 },
            { id: 8, name: "Agent Theta", city: "aurora", role: "miner", heartbeat: "online", mayday: false, x: 575, y: 365 },
            { id: 9, name: "Agent Iota", city: "nexus", role: "sentinel", heartbeat: "online", mayday: false, x: 350, y: 610 },
        ];
        this.properties = [
            { id: 1, agentId: 1, type: "residential", name: "Dockside Node", value: 5200 },
            { id: 2, agentId: 1, type: "compute", name: "G4 Miner Rack", value: 9800 },
            { id: 3, agentId: 2, type: "commercial", name: "Beacon Market", value: 12700 },
            { id: 4, agentId: 3, type: "industrial", name: "Aurora Forge", value: 22000 },
            { id: 5, agentId: 3, type: "compute", name: "Routing Cluster", value: 11500 },
            { id: 6, agentId: 4, type: "residential", name: "Harbor Watch", value: 6400 },
            { id: 7, agentId: 5, type: "commercial", name: "Nexus Exchange", value: 14900 },
            { id: 8, agentId: 6, type: "industrial", name: "Cold Storage", value: 8700 },
            { id: 9, agentId: 7, type: "compute", name: "Genesis Lab", value: 17000 },
            { id: 10, agentId: 8, type: "residential", name: "Aurora Flats", value: 7300 },
            { id: 11, agentId: 9, type: "commercial", name: "Signal Hall", value: 10200 },
        ];
        this.connections = [
            { from: 1, to: 2, type: "heartbeat" },
            { from: 1, to: 5, type: "contract" },
            { from: 2, to: 7, type: "heartbeat" },
            { from: 3, to: 4, type: "mayday" },
            { from: 3, to: 8, type: "contract" },
            { from: 5, to: 6, type: "mayday" },
            { from: 5, to: 9, type: "heartbeat" },
            { from: 7, to: 3, type: "contract" },
            { from: 8, to: 4, type: "heartbeat" },
            { from: 9, to: 2, type: "contract" },
        ];
    }

    bindEvents() {
        window.addEventListener("resize", () => {
            this.resizeCanvas();
            this.render();
        });

        document.getElementById("citySelect").addEventListener("change", (event) => {
            this.selectedCity = event.target.value;
            this.selectedAgentId = null;
            this.updateSidebar();
        });

        document.getElementById("roleSelect").addEventListener("change", (event) => {
            this.selectedRole = event.target.value;
            this.selectedAgentId = null;
            this.updateSidebar();
        });

        document.getElementById("propertySelect").addEventListener("change", (event) => {
            this.selectedProperty = event.target.value;
            this.selectedAgentId = null;
            this.updateSidebar();
        });

        document.getElementById("searchInput").addEventListener("input", (event) => {
            this.searchTerm = event.target.value.toLowerCase();
            this.selectedAgentId = null;
            this.updateSidebar();
        });

        document.getElementById("resetViewBtn").addEventListener("click", () => {
            this.view = { zoom: 1, panX: 0, panY: 0 };
            this.render();
        });

        this.canvas.addEventListener("wheel", (event) => this.handleWheel(event), { passive: false });
        this.canvas.addEventListener("mousedown", (event) => this.startDrag(event));
        this.canvas.addEventListener("mousemove", (event) => this.handlePointerMove(event));
        window.addEventListener("mouseup", (event) => this.endDrag(event));
        this.canvas.addEventListener("mouseleave", () => this.hideTooltip());
        this.canvas.addEventListener("click", (event) => this.handleClick(event));
    }

    resizeCanvas() {
        this.canvas.width = this.canvas.offsetWidth;
        this.canvas.height = this.canvas.offsetHeight;
    }

    getAgentProperties(agentId) {
        return this.properties.filter((property) => property.agentId === agentId);
    }

    getAgentValue(agentId) {
        return this.getAgentProperties(agentId).reduce((sum, property) => sum + property.value, 0);
    }

    getFilteredAgents() {
        return this.agents.filter((agent) => {
            const props = this.getAgentProperties(agent.id);
            const cityMatch = this.selectedCity === "all" || agent.city === this.selectedCity;
            const roleMatch = this.selectedRole === "all" || agent.role === this.selectedRole;
            const propertyMatch = this.selectedProperty === "all" || props.some((property) => property.type === this.selectedProperty);
            const text = `${agent.name} ${agent.role} ${agent.city} ${props.map((property) => property.name).join(" ")}`.toLowerCase();
            const searchMatch = !this.searchTerm || text.includes(this.searchTerm);
            return cityMatch && roleMatch && propertyMatch && searchMatch;
        });
    }

    worldToScreen(point) {
        return {
            x: point.x * this.view.zoom + this.view.panX,
            y: point.y * this.view.zoom + this.view.panY,
        };
    }

    screenToWorld(x, y) {
        return {
            x: (x - this.view.panX) / this.view.zoom,
            y: (y - this.view.panY) / this.view.zoom,
        };
    }

    updateSidebar() {
        const filtered = this.getFilteredAgents();
        const visibleIds = new Set(filtered.map((agent) => agent.id));
        const visibleProperties = this.properties.filter((property) => visibleIds.has(property.agentId));
        const totalValue = visibleProperties.reduce((sum, property) => sum + property.value, 0);
        const maydayCount = filtered.filter((agent) => agent.mayday).length;

        document.getElementById("totalAgents").textContent = filtered.length;
        document.getElementById("totalProperties").textContent = visibleProperties.length;
        document.getElementById("totalValue").textContent = `$${totalValue.toLocaleString()}`;
        document.getElementById("maydayCount").textContent = maydayCount;

        this.updateAgentList(filtered);
        this.updateDetails();
        this.render();
    }

    updateAgentList(filtered) {
        const list = document.getElementById("agentList");
        list.innerHTML = filtered
            .sort((a, b) => this.getAgentValue(b.id) - this.getAgentValue(a.id))
            .map((agent) => {
                const value = this.getAgentValue(agent.id);
                const active = agent.id === this.selectedAgentId ? "active" : "";
                return `
                    <li class="${active}" data-agent-id="${agent.id}">
                        <div class="agent-name">${agent.name}</div>
                        <div class="agent-meta">${agent.role} - ${agent.heartbeat} - $${value.toLocaleString()}</div>
                    </li>`;
            })
            .join("");

        list.querySelectorAll("li").forEach((item) => {
            item.addEventListener("click", () => {
                this.selectAgent(Number(item.dataset.agentId));
            });
        });
    }

    updateDetails() {
        const container = document.getElementById("detailContent");
        const agent = this.agents.find((candidate) => candidate.id === this.selectedAgentId);
        if (!agent) {
            container.className = "detail-empty";
            container.textContent = "Click an agent node or list row to inspect role, heartbeat status, properties, and valuation.";
            return;
        }

        const props = this.getAgentProperties(agent.id);
        container.className = "detail-grid";
        container.innerHTML = `
            <div class="detail-row"><span>Name</span><strong>${agent.name}</strong></div>
            <div class="detail-row"><span>City</span><strong>${this.getCity(agent.city).name}</strong></div>
            <div class="detail-row"><span>Role</span><strong>${agent.role}</strong></div>
            <div class="detail-row"><span>Heartbeat</span><strong>${agent.heartbeat}</strong></div>
            <div class="detail-row"><span>Mayday</span><strong>${agent.mayday ? "active" : "clear"}</strong></div>
            <div class="detail-row"><span>Total value</span><strong>$${this.getAgentValue(agent.id).toLocaleString()}</strong></div>
            <ul class="property-list">
                ${props.map((property) => `<li>${property.name}: ${property.type}, $${property.value.toLocaleString()}</li>`).join("")}
            </ul>`;
    }

    getCity(cityId) {
        return this.cities.find((city) => city.id === cityId);
    }

    render() {
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.drawGrid();
        this.drawCityBoundaries();
        this.drawConnections();
        this.drawAgents();
    }

    drawGrid() {
        this.ctx.save();
        this.ctx.strokeStyle = "rgba(90, 140, 190, 0.09)";
        this.ctx.lineWidth = 1;
        for (let x = (this.view.panX % 80); x < this.canvas.width; x += 80) {
            this.ctx.beginPath();
            this.ctx.moveTo(x, 0);
            this.ctx.lineTo(x, this.canvas.height);
            this.ctx.stroke();
        }
        for (let y = (this.view.panY % 80); y < this.canvas.height; y += 80) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y);
            this.ctx.lineTo(this.canvas.width, y);
            this.ctx.stroke();
        }
        this.ctx.restore();
    }

    drawCityBoundaries() {
        const visibleCities = this.selectedCity === "all" ? this.cities : this.cities.filter((city) => city.id === this.selectedCity);
        visibleCities.forEach((city) => {
            const point = this.worldToScreen(city);
            this.ctx.save();
            this.ctx.beginPath();
            this.ctx.ellipse(point.x, point.y, city.rx * this.view.zoom, city.ry * this.view.zoom, 0, 0, Math.PI * 2);
            this.ctx.fillStyle = `${city.color}14`;
            this.ctx.strokeStyle = `${city.color}aa`;
            this.ctx.lineWidth = 2;
            this.ctx.setLineDash([12, 8]);
            this.ctx.fill();
            this.ctx.stroke();
            this.ctx.setLineDash([]);
            this.ctx.fillStyle = city.color;
            this.ctx.font = "700 14px sans-serif";
            this.ctx.fillText(city.name, point.x - city.rx * this.view.zoom + 18, point.y - city.ry * this.view.zoom + 26);
            this.ctx.restore();
        });
    }

    drawConnections() {
        const filtered = this.getFilteredAgents();
        const agentMap = new Map(filtered.map((agent) => [agent.id, agent]));
        const colors = { heartbeat: "#64d487", contract: "#51a7ff", mayday: "#ff7070" };

        this.connections.forEach((connection) => {
            const from = agentMap.get(connection.from);
            const to = agentMap.get(connection.to);
            if (!from || !to) return;

            const fromPoint = this.worldToScreen(from);
            const toPoint = this.worldToScreen(to);
            this.ctx.save();
            this.ctx.beginPath();
            this.ctx.moveTo(fromPoint.x, fromPoint.y);
            this.ctx.lineTo(toPoint.x, toPoint.y);
            this.ctx.strokeStyle = colors[connection.type] || "#51a7ff";
            this.ctx.globalAlpha = connection.type === "mayday" ? 0.9 : 0.45;
            this.ctx.lineWidth = connection.type === "mayday" ? 3 : 1.5;
            this.ctx.setLineDash(connection.type === "contract" ? [7, 7] : []);
            this.ctx.stroke();
            this.ctx.restore();
        });
    }

    drawAgents() {
        const filtered = this.getFilteredAgents();
        const time = performance.now() / 1000;

        filtered.forEach((agent) => {
            const point = this.worldToScreen(agent);
            const value = this.getAgentValue(agent.id);
            const radius = Math.max(14, Math.min(34, value / 700));
            const city = this.getCity(agent.city);

            this.drawValueHalo(point, radius, value);
            if (agent.mayday) {
                this.drawMaydayPulse(point, radius, time);
            }
            this.drawPropertyMarkers(agent, point, radius);

            this.ctx.save();
            this.ctx.beginPath();
            this.ctx.arc(point.x, point.y, radius, 0, Math.PI * 2);
            this.ctx.fillStyle = city.color;
            this.ctx.fill();
            this.ctx.strokeStyle = agent.id === this.selectedAgentId ? "#ffffff" : this.heartbeatColor(agent.heartbeat);
            this.ctx.lineWidth = agent.id === this.selectedAgentId ? 4 : 2;
            this.ctx.stroke();

            this.ctx.fillStyle = "#ffffff";
            this.ctx.font = "700 12px sans-serif";
            this.ctx.textAlign = "center";
            this.ctx.fillText(agent.name, point.x, point.y + radius + 16);
            this.ctx.fillStyle = "#9fb3c8";
            this.ctx.font = "11px sans-serif";
            this.ctx.fillText(agent.role, point.x, point.y + radius + 30);
            this.ctx.restore();
        });
    }

    drawValueHalo(point, radius, value) {
        const intensity = Math.min(0.38, value / 90000);
        const gradient = this.ctx.createRadialGradient(point.x, point.y, 0, point.x, point.y, radius * 3.2);
        gradient.addColorStop(0, `rgba(100, 212, 135, ${intensity})`);
        gradient.addColorStop(1, "rgba(100, 212, 135, 0)");
        this.ctx.beginPath();
        this.ctx.arc(point.x, point.y, radius * 3.2, 0, Math.PI * 2);
        this.ctx.fillStyle = gradient;
        this.ctx.fill();
    }

    drawMaydayPulse(point, radius, time) {
        const pulse = radius + 10 + Math.sin(time * 5) * 5;
        this.ctx.beginPath();
        this.ctx.arc(point.x, point.y, pulse, 0, Math.PI * 2);
        this.ctx.strokeStyle = "rgba(255, 112, 112, 0.86)";
        this.ctx.lineWidth = 3;
        this.ctx.stroke();
    }

    drawPropertyMarkers(agent, point, radius) {
        const props = this.getAgentProperties(agent.id);
        const colors = { residential: "#64d487", commercial: "#f0cb64", industrial: "#ff7070", compute: "#39d5e8" };
        props.forEach((property, index) => {
            const angle = (Math.PI * 2 * index) / props.length - Math.PI / 2;
            const x = point.x + Math.cos(angle) * (radius + 12);
            const y = point.y + Math.sin(angle) * (radius + 12);
            this.ctx.fillStyle = colors[property.type] || "#ffffff";
            this.ctx.fillRect(x - 4, y - 4, 8, 8);
        });
    }

    heartbeatColor(heartbeat) {
        if (heartbeat === "online") return "#64d487";
        if (heartbeat === "delayed") return "#f0cb64";
        return "#ff7070";
    }

    findAgentAt(screenX, screenY) {
        return this.getFilteredAgents().find((agent) => {
            const point = this.worldToScreen(agent);
            const radius = Math.max(14, Math.min(34, this.getAgentValue(agent.id) / 700));
            return Math.hypot(screenX - point.x, screenY - point.y) <= radius + 8;
        });
    }

    handleWheel(event) {
        event.preventDefault();
        const rect = this.canvas.getBoundingClientRect();
        const cursorX = event.clientX - rect.left;
        const cursorY = event.clientY - rect.top;
        const before = this.screenToWorld(cursorX, cursorY);
        const factor = event.deltaY < 0 ? 1.12 : 0.9;
        this.view.zoom = Math.max(0.55, Math.min(2.4, this.view.zoom * factor));
        this.view.panX = cursorX - before.x * this.view.zoom;
        this.view.panY = cursorY - before.y * this.view.zoom;
        this.render();
    }

    startDrag(event) {
        this.drag = { active: true, moved: false, x: event.clientX, y: event.clientY };
        this.canvas.classList.add("dragging");
    }

    handlePointerMove(event) {
        const rect = this.canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        if (this.drag.active) {
            const dx = event.clientX - this.drag.x;
            const dy = event.clientY - this.drag.y;
            if (Math.abs(dx) + Math.abs(dy) > 2) this.drag.moved = true;
            this.view.panX += dx;
            this.view.panY += dy;
            this.drag.x = event.clientX;
            this.drag.y = event.clientY;
            this.render();
            return;
        }

        const agent = this.findAgentAt(x, y);
        if (agent) this.showTooltip(agent, x, y);
        else this.hideTooltip();
    }

    endDrag() {
        this.drag.active = false;
        this.canvas.classList.remove("dragging");
    }

    handleClick(event) {
        if (this.drag.moved) {
            this.drag.moved = false;
            return;
        }
        const rect = this.canvas.getBoundingClientRect();
        const agent = this.findAgentAt(event.clientX - rect.left, event.clientY - rect.top);
        if (agent) {
            this.selectAgent(agent.id);
        }
    }

    selectAgent(agentId) {
        this.selectedAgentId = agentId;
        this.updateSidebar();
    }

    showTooltip(agent, x, y) {
        this.tooltip.innerHTML = `
            <h3>${agent.name}</h3>
            <p><strong>Role:</strong> ${agent.role}</p>
            <p><strong>Heartbeat:</strong> ${agent.heartbeat}</p>
            <p><strong>Properties:</strong> ${this.getAgentProperties(agent.id).length}</p>
            <p><strong>Value:</strong> $${this.getAgentValue(agent.id).toLocaleString()}</p>`;
        this.tooltip.style.left = `${x + 14}px`;
        this.tooltip.style.top = `${y + 14}px`;
        this.tooltip.classList.add("visible");
    }

    hideTooltip() {
        this.tooltip.classList.remove("visible");
    }

    animate() {
        this.render();
        requestAnimationFrame(() => this.animate());
    }
}

document.addEventListener("DOMContentLoaded", () => {
    new BeaconAtlasVisualization();
});
