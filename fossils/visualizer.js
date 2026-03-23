// RustChain Attestation Archaeology - Visualizer Module

class AttestationVisualizer {
    constructor() {
        this.dataManager = new AttestationDataManager();
        this.svg = null;
        this.chart = null;
        this.xScale = null;
        this.yScale = null;
        this.tooltip = null;
        this.margin = { top: 40, right: 30, bottom: 60, left: 60 };
        
        this.init();
    }
    
    async init() {
        this.setupSVG();
        this.setupTooltip();
        await this.loadData();
        this.setupControls();
        this.renderLegend();
    }
    
    setupSVG() {
        const container = document.getElementById('timeline-chart');
        const containerWidth = container.parentElement.clientWidth;
        
        this.width = containerWidth - this.margin.left - this.margin.right;
        this.height = 600 - this.margin.top - this.margin.bottom;
        
        this.svg = d3.select('#timeline-chart')
            .attr('width', this.width + this.margin.left + this.margin.right)
            .attr('height', this.height + this.margin.top + this.margin.bottom);
        
        this.chart = this.svg.append('g')
            .attr('transform', `translate(${this.margin.left}, ${this.margin.top})`);
    }
    
    setupTooltip() {
        this.tooltip = d3.select('#tooltip');
    }
    
    async loadData() {
        const data = await this.dataManager.loadData(true);
        this.renderChart(data);
        this.updateStats();
    }
    
    setupControls() {
        // Epoch range controls
        const startSlider = document.getElementById('epoch-start');
        const endSlider = document.getElementById('epoch-end');
        const startLabel = document.getElementById('epoch-start-label');
        const endLabel = document.getElementById('epoch-end-label');
        
        const updateRange = () => {
            const start = parseInt(startSlider.value);
            const end = parseInt(endSlider.value);
            
            if (start > end) {
                startSlider.value = end;
                endSlider.value = start;
            }
            
            startLabel.textContent = startSlider.value;
            endLabel.textContent = endSlider.value;
            
            const filteredData = this.dataManager.filterByEpochRange(
                parseInt(startSlider.value),
                parseInt(endSlider.value)
            );
            
            this.renderChart(filteredData);
            this.updateStats();
        };
        
        startSlider.addEventListener('input', updateRange);
        endSlider.addEventListener('input', updateRange);
        
        // Refresh button
        document.getElementById('refresh-btn').addEventListener('click', async () => {
            await this.loadData();
        });
        
        // Export button
        document.getElementById('export-btn').addEventListener('click', () => {
            const csv = this.dataManager.exportToCSV();
            const blob = new Blob([csv], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'attestation_history.csv';
            a.click();
            URL.revokeObjectURL(url);
        });
    }
    
    renderLegend() {
        const legend = document.getElementById('legend');
        legend.innerHTML = '';
        
        Object.entries(ARCHITECTURES).forEach(([key, arch]) => {
            const item = document.createElement('div');
            item.className = 'legend-item';
            item.innerHTML = `
                <div class="legend-color" style="background-color: ${arch.color}"></div>
                <span>${arch.name}</span>
            `;
            legend.appendChild(item);
        });
    }
    
    renderChart(data) {
        // Clear previous chart
        this.chart.selectAll('*').remove();
        
        if (data.length === 0) {
            this.chart.append('text')
                .attr('x', this.width / 2)
                .attr('y', this.height / 2)
                .attr('text-anchor', 'middle')
                .text('No data available')
                .style('fill', '#a0a0a0');
            return;
        }
        
        // Sort data by architecture layer (oldest at bottom)
        const sortedData = [...data].sort((a, b) => a.archLayer - b.archLayer);
        
        // Group data by epoch and architecture
        const epochs = [...new Set(data.map(d => d.epoch))].sort((a, b) => a - b);
        
        // Scales
        this.xScale = d3.scaleLinear()
            .domain([d3.min(epochs), d3.max(epochs)])
            .range([0, this.width]);
        
        // Y scale for architecture layers
        const architectures = Object.keys(ARCHITECTURES).sort((a, b) => 
            ARCHITECTURES[a].layer - ARCHITECTURES[b].layer
        );
        
        this.yScale = d3.scaleBand()
            .domain(architectures)
            .range([0, this.height])
            .padding(0.1);
        
        // X Axis (Epochs)
        const xAxis = d3.axisBottom(this.xScale)
            .tickFormat(d => `Epoch ${d}`);
        
        this.chart.append('g')
            .attr('class', 'axis x-axis')
            .attr('transform', `translate(0, ${this.height})`)
            .call(xAxis)
            .selectAll('text')
            .attr('transform', 'rotate(-45)')
            .style('text-anchor', 'end');
        
        // X Axis Label
        this.chart.append('text')
            .attr('class', 'axis-label')
            .attr('x', this.width / 2)
            .attr('y', this.height + 50)
            .attr('text-anchor', 'middle')
            .text('Time (Epochs)');
        
        // Y Axis (Architecture)
        const yAxis = d3.axisLeft(this.yScale)
            .tickFormat(d => ARCHITECTURES[d].name);
        
        this.chart.append('g')
            .attr('class', 'axis y-axis')
            .call(yAxis);
        
        // Y Axis Label
        this.chart.append('text')
            .attr('class', 'axis-label')
            .attr('transform', 'rotate(-90)')
            .attr('x', -this.height / 2)
            .attr('y', -45)
            .attr('text-anchor', 'middle')
            .text('Architecture (Oldest at Bottom)');
        
        // Draw epoch settlement markers
        const epochMarkers = this.dataManager.getEpochMarkers();
        
        this.chart.selectAll('.epoch-marker')
            .data(epochMarkers)
            .enter()
            .append('line')
            .attr('class', 'epoch-marker')
            .attr('x1', d => this.xScale(d))
            .attr('x2', d => this.xScale(d))
            .attr('y1', 0)
            .attr('y2', this.height);
        
        // Add epoch marker labels
        this.chart.selectAll('.epoch-marker-label')
            .data(epochMarkers)
            .enter()
            .append('text')
            .attr('class', 'epoch-marker-label')
            .attr('x', d => this.xScale(d))
            .attr('y', -10)
            .attr('text-anchor', 'middle')
            .style('fill', '#4a9eff')
            .style('font-size', '10px')
            .text(d => `Settlement`);
        
        // Group data by epoch for stacking
        const dataByEpoch = d3.group(sortedData, d => d.epoch);
        
        // Draw attestation bars
        dataByEpoch.forEach((epochData, epoch) => {
            // Count attestations per architecture
            const archCounts = d3.rollup(
                epochData,
                v => v.length,
                d => d.architecture
            );
            
            // Draw bars for each architecture
            let currentY = 0;
            architectures.forEach(arch => {
                const count = archCounts.get(arch) || 0;
                if (count > 0) {
                    const archInfo = ARCHITECTURES[arch];
                    
                    // Calculate bar dimensions
                    const barWidth = Math.max(3, this.width / epochs.length * 0.8);
                    const barHeight = this.yScale.bandwidth() * (count / d3.max([...archCounts.values()]));
                    
                    // Get sample data for tooltip
                    const sampleData = epochData.find(d => d.architecture === arch);
                    
                    this.chart.append('rect')
                        .attr('class', 'attestation-bar')
                        .attr('x', this.xScale(epoch) - barWidth / 2)
                        .attr('y', this.yScale(arch) + (this.yScale.bandwidth() - barHeight) / 2)
                        .attr('width', barWidth)
                        .attr('height', barHeight)
                        .attr('fill', archInfo.color)
                        .attr('rx', 2)
                        .on('mouseover', (event) => this.showTooltip(event, epochData.filter(d => d.architecture === arch)))
                        .on('mousemove', (event) => this.moveTooltip(event))
                        .on('mouseout', () => this.hideTooltip());
                }
            });
        });
        
        // Draw individual attestation points for detailed view
        const circleRadius = Math.max(2, Math.min(5, 500 / data.length));
        
        this.chart.selectAll('.attestation-point')
            .data(sortedData)
            .enter()
            .append('circle')
            .attr('class', 'attestation-point')
            .attr('cx', d => this.xScale(d.epoch) + (Math.random() - 0.5) * 10)
            .attr('cy', d => this.yScale(d.architecture) + this.yScale.bandwidth() / 2 + (Math.random() - 0.5) * this.yScale.bandwidth() * 0.5)
            .attr('r', circleRadius)
            .attr('fill', d => d.color)
            .attr('opacity', 0.7)
            .style('cursor', 'pointer')
            .on('mouseover', (event, d) => this.showTooltipForAttestation(event, d))
            .on('mousemove', (event) => this.moveTooltip(event))
            .on('mouseout', () => this.hideTooltip());
    }
    
    showTooltip(event, data) {
        if (data.length === 0) return;
        
        const sample = data[0];
        const totalRTC = data.reduce((sum, d) => sum + d.rtcEarned, 0);
        const avgQuality = (data.reduce((sum, d) => sum + d.fingerprintQuality, 0) / data.length).toFixed(3);
        
        this.tooltip.html(`
            <h4>Epoch ${sample.epoch}</h4>
            <div class="tooltip-row">
                <span class="tooltip-label">Architecture:</span>
                <span class="tooltip-value">${ARCHITECTURES[sample.architecture].name}</span>
            </div>
            <div class="tooltip-row">
                <span class="tooltip-label">Attestations:</span>
                <span class="tooltip-value">${data.length}</span>
            </div>
            <div class="tooltip-row">
                <span class="tooltip-label">Total RTC:</span>
                <span class="tooltip-value">${totalRTC.toFixed(2)}</span>
            </div>
            <div class="tooltip-row">
                <span class="tooltip-label">Avg Fingerprint:</span>
                <span class="tooltip-value">${avgQuality}</span>
            </div>
        `);
        
        this.tooltip.style('opacity', 1);
        this.moveTooltip(event);
    }
    
    showTooltipForAttestation(event, data) {
        this.tooltip.html(`
            <h4>Miner: ${data.minerId}</h4>
            <div class="tooltip-row">
                <span class="tooltip-label">Device:</span>
                <span class="tooltip-value">${data.device}</span>
            </div>
            <div class="tooltip-row">
                <span class="tooltip-label">Architecture:</span>
                <span class="tooltip-value">${ARCHITECTURES[data.architecture].name}</span>
            </div>
            <div class="tooltip-row">
                <span class="tooltip-label">Epoch:</span>
                <span class="tooltip-value">${data.epoch}</span>
            </div>
            <div class="tooltip-row">
                <span class="tooltip-label">RTC Earned:</span>
                <span class="tooltip-value">${data.rtcEarned}</span>
            </div>
            <div class="tooltip-row">
                <span class="tooltip-label">Fingerprint Quality:</span>
                <span class="tooltip-value">${data.fingerprintQuality}</span>
            </div>
        `);
        
        this.tooltip.style('opacity', 1);
        this.moveTooltip(event);
    }
    
    moveTooltip(event) {
        const x = event.pageX + 15;
        const y = event.pageY - 10;
        
        this.tooltip
            .style('left', `${x}px`)
            .style('top', `${y}px`);
    }
    
    hideTooltip() {
        this.tooltip.style('opacity', 0);
    }
    
    updateStats() {
        const stats = this.dataManager.getStatistics();
        
        document.getElementById('total-miners').textContent = stats.totalMiners;
        document.getElementById('total-attestations').textContent = stats.totalAttestations;
        document.getElementById('total-rtc').textContent = stats.totalRTC.toFixed(2);
        document.getElementById('common-arch').textContent = stats.mostCommonArch;
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.visualizer = new AttestationVisualizer();
});