/**
 * Fossil Record Visualizer - Main Visualization Script
 * Uses D3.js to render interactive timeline
 */

// Configuration
const CONFIG = {
    margin: { top: 40, right: 30, bottom: 60, left: 100 },
    layerHeight: 40,
    epochWidth: 30,
    tooltipDelay: 200
};

// State
let processedData = null;
let visualizationLayers = null;

/**
 * Initialize the visualization
 */
async function init() {
    console.log('🦕 Initializing Fossil Record Visualizer...');
    
    // Fetch and process data
    const rawData = await fetchAttestationData();
    processedData = processAttestationData(rawData);
    visualizationLayers = prepareForVisualization(processedData);
    
    // Render components
    renderStats(processedData.stats);
    renderLegend(processedData.architectures);
    renderTimeline(visualizationLayers, processedData.stats.epochRange);
    
    console.log('✅ Visualization complete!');
}

/**
 * Render statistics panel
 */
function renderStats(stats) {
    const statsEl = document.getElementById('stats');
    statsEl.innerHTML = `
        <h3>Network Statistics</h3>
        <div class="stats-grid">
            <div class="stat-item">
                <div class="stat-value">${stats.totalAttestations}</div>
                <div class="stat-label">Total Attestations</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${stats.totalRTC.toLocaleString()}</div>
                <div class="stat-label">Total RTC Earned</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${stats.uniqueMiners}</div>
                <div class="stat-label">Unique Miners</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${stats.uniqueArchitectures}</div>
                <div class="stat-label">Architectures</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${stats.epochRange.min} - ${stats.epochRange.max}</div>
                <div class="stat-label">Epoch Range</div>
            </div>
            <div class="stat-item">
                <div class="stat-value">${(stats.avgFingerprint * 100).toFixed(1)}%</div>
                <div class="stat-label">Avg Fingerprint</div>
            </div>
        </div>
    `;
}

/**
 * Render architecture legend
 */
function renderLegend(architectures) {
    const legendEl = document.getElementById('legend');
    const legendItems = architectures.map(arch => `
        <div class="legend-item">
            <div class="legend-color" style="background-color: ${getArchColor(arch)}"></div>
            <span class="legend-name">${arch}</span>
        </div>
    `).join('');
    
    legendEl.innerHTML = `
        <h3>Architecture Layers</h3>
        <div class="legend-items">${legendItems}</div>
    `;
}

/**
 * Render main timeline visualization
 */
function renderTimeline(layers, epochRange) {
    const svg = d3.select('#timeline');
    const container = document.getElementById('visualization');
    const width = container.clientWidth - CONFIG.margin.left - CONFIG.margin.right;
    const height = (layers.length * CONFIG.layerHeight) + CONFIG.margin.top + CONFIG.margin.bottom;
    
    svg.attr('width', width + CONFIG.margin.left + CONFIG.margin.right);
    svg.attr('height', height);
    
    // Create scales
    const xScale = d3.scaleLinear()
        .domain([epochRange.min - 1, epochRange.max + 1])
        .range([0, width]);
    
    const yScale = d3.scaleBand()
        .domain(layers.map(d => d.architecture))
        .range([CONFIG.margin.top, height - CONFIG.margin.bottom])
        .padding(0.2);
    
    // Add axes
    svg.append('g')
        .attr('transform', `translate(${CONFIG.margin.left},${height - CONFIG.margin.bottom + 20})`)
        .call(d3.axisBottom(xScale).tickFormat(d => `Epoch ${d}`))
        .selectAll('text')
        .style('fill', '#888');
    
    svg.append('g')
        .attr('transform', `translate(${CONFIG.margin.left},0)`)
        .call(d3.axisLeft(yScale))
        .selectAll('text')
        .style('fill', '#aaa')
        .style('font-size', '12px');
    
    // Add epoch markers
    EPOCH_MARKERS.forEach(marker => {
        const x = xScale(marker.epoch) + CONFIG.margin.left;
        
        svg.append('line')
            .attr('class', 'epoch-line')
            .attr('x1', x)
            .attr('y1', CONFIG.margin.top)
            .attr('x2', x)
            .attr('y2', height - CONFIG.margin.bottom);
        
        svg.append('text')
            .attr('class', 'epoch-label')
            .attr('x', x + 5)
            .attr('y', CONFIG.margin.top + 15)
            .text(marker.label);
    });
    
    // Add architecture layers
    const g = svg.append('g')
        .attr('transform', `translate(${CONFIG.margin.left},0)`);
    
    layers.forEach(layer => {
        const y = yScale(layer.architecture);
        const color = getArchColor(layer.architecture);
        
        layer.stackData.forEach(d => {
            const x = xScale(d.epoch);
            const barWidth = CONFIG.epochWidth * d.count;
            
            g.append('rect')
                .attr('class', 'arch-layer')
                .attr('x', x)
                .attr('y', y)
                .attr('width', Math.max(barWidth, 8))
                .attr('height', yScale.bandwidth())
                .attr('fill', color)
                .attr('rx', 3)
                .attr('opacity', 0.8)
                .on('mouseover', function(event) {
                    showTooltip(event, d.attestations, layer.architecture);
                })
                .on('mousemove', function(event) {
                    moveTooltip(event);
                })
                .on('mouseout', hideTooltip);
        });
    });
}

/**
 * Show tooltip with attestation details
 */
function showTooltip(event, attestations, architecture) {
    const tooltip = document.getElementById('tooltip');
    const totalRTC = attestations.reduce((sum, a) => sum + a.rtc_earned, 0);
    
    let html = `<h4>${architecture}</h4>`;
    html += `<div class="row"><span class="label">Attestations:</span><span class="value">${attestations.length}</span></div>`;
    html += `<div class="row"><span class="label">Total RTC:</span><span class="value">${totalRTC}</span></div>`;
    html += `<hr style="border-color: #444; margin: 8px 0;">`;
    
    attestations.slice(0, 5).forEach(a => {
        html += `<div class="row"><span class="label">${a.miner_id}:</span><span class="value">${a.rtc_earned} RTC</span></div>`;
    });
    
    if (attestations.length > 5) {
        html += `<div style="color: #666; font-size: 12px; margin-top: 5px;">+ ${attestations.length - 5} more...</div>`;
    }
    
    tooltip.innerHTML = html;
    tooltip.classList.add('visible');
    moveTooltip(event);
}

/**
 * Move tooltip with mouse
 */
function moveTooltip(event) {
    const tooltip = document.getElementById('tooltip');
    tooltip.style.left = (event.pageX + 15) + 'px';
    tooltip.style.top = (event.pageY - 10) + 'px';
}

/**
 * Hide tooltip
 */
function hideTooltip() {
    const tooltip = document.getElementById('tooltip');
    tooltip.classList.remove('visible');
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', init);
