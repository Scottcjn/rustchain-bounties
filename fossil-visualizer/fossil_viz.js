/**
 * The Fossil Record - Attestation Archaeology Visualizer
 * Bounty #2311 - 75 RTC
 * 
 * Interactive D3.js visualization of RustChain attestation history
 */

// Mock attestation data (in production, fetch from RustChain API)
const generateMockData = () => {
  const architectures = [
    { name: 'RISC-V', color: '#667eea' },
    { name: 'POWER8', color: '#764ba2' },
    { name: 'x86_64', color: '#f093fb' },
    { name: 'ARM64', color: '#4ade80' },
    { name: 'N64', color: '#fbbf24' }
  ];

  const data = [];
  const now = new Date();
  const days = 90; // 90 days of history

  for (let d = days; d >= 0; d--) {
    const date = new Date(now);
    date.setDate(date.getDate() - d);
    const dateStr = date.toISOString().split('T')[0];

    architectures.forEach(arch => {
      // Generate realistic attestation counts
      const baseCount = Math.random() * 100 + 50;
      const trend = (days - d) * 2; // Growing trend
      const noise = Math.random() * 30 - 15;
      const count = Math.floor(baseCount + trend + noise);

      data.push({
        date: dateStr,
        architecture: arch.name,
        color: arch.color,
        attestations: count
      });
    });
  }

  return { data, architectures };
};

// Initialize visualization
class FossilVisualizer {
  constructor() {
    this.data = null;
    this.architectures = null;
    this.currentMode = 'stacked';
    this.init();
  }

  init() {
    const { data, architectures } = generateMockData();
    this.data = data;
    this.architectures = architectures;

    this.setupControls();
    this.renderLegend();
    this.render();
    this.updateStats();
  }

  setupControls() {
    document.querySelectorAll('.control-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.control-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        this.currentMode = e.target.dataset.mode;
        this.render();
      });
    });
  }

  renderLegend() {
    const legend = document.getElementById('legend');
    legend.innerHTML = this.architectures.map(arch => `
      <div class="legend-item">
        <div class="legend-color" style="background: ${arch.color}"></div>
        <span>${arch.name}</span>
      </div>
    `).join('');
  }

  updateStats() {
    const total = this.data.reduce((sum, d) => sum + d.attestations, 0);
    const miners = Math.floor(total / 100); // Estimate
    const archs = this.architectures.length;
    const days = 90;

    document.getElementById('total-attestations').textContent = total.toLocaleString();
    document.getElementById('total-miners').textContent = miners.toLocaleString();
    document.getElementById('architectures').textContent = archs;
    document.getElementById('days-mining').textContent = days;
  }

  render() {
    const container = document.getElementById('viz');
    container.innerHTML = '';

    switch (this.currentMode) {
      case 'stacked':
        this.renderStackedArea();
        break;
      case 'streamgraph':
        this.renderStreamgraph();
        break;
      case 'timeline':
        this.renderTimeline();
        break;
      case 'heatmap':
        this.renderHeatmap();
        break;
    }
  }

  renderStackedArea() {
    const width = document.getElementById('viz').offsetWidth;
    const height = 500;
    const margin = { top: 20, right: 30, bottom: 40, left: 60 };

    const svg = d3.select('#viz')
      .append('svg')
      .attr('width', width)
      .attr('height', height);

    // Prepare data
    const dates = [...new Set(this.data.map(d => d.date))].sort();
    const stackData = this.architectures.map(arch => ({
      name: arch.name,
      color: arch.color,
      values: dates.map(date => {
        const d = this.data.find(x => x.date === date && x.architecture === arch.name);
        return d ? d.attestations : 0;
      })
    }));

    // Scales
    const x = d3.scalePoint()
      .domain(dates.filter((_, i) => i % 5 === 0)) // Show every 5th date
      .range([margin.left, width - margin.right]);

    const y = d3.scaleLinear()
      .domain([0, d3.max(stackData, d => d3.sum(d.values))])
      .range([height - margin.bottom, margin.top]);

    // Stack generator
    const stack = d3.stack()
      .keys(stackData.map(d => d.name));

    const stackedData = stack(this.data.reduce((acc, d) => {
      const existing = acc.find(a => a.date === d.date);
      if (existing) existing[d.architecture] = d.attestations;
      else acc.push({ date: d.date, [d.architecture]: d.attestations });
      return acc;
    }, []));

    // Area generator
    const area = d3.area()
      .x((d, i) => x(dates[i]))
      .y0(d => y(d[0]))
      .y1(d => y(d[1]));

    // Draw areas
    svg.selectAll('.layer')
      .data(stackedData)
      .join('path')
      .attr('class', 'layer')
      .attr('d', (d, i) => area(d))
      .attr('fill', (d, i) => stackData[i].color)
      .attr('opacity', 0.8);

    // Axes
    svg.append('g')
      .attr('transform', `translate(0,${height - margin.bottom})`)
      .call(d3.axisBottom(x))
      .attr('color', '#fff')
      .selectAll('text')
      .attr('transform', 'rotate(-45)')
      .style('text-anchor', 'end');

    svg.append('g')
      .attr('transform', `translate(${margin.left},0)`)
      .call(d3.axisLeft(y))
      .attr('color', '#fff');
  }

  renderStreamgraph() {
    // Simplified streamgraph
    this.renderStackedArea(); // Fallback to stacked for now
  }

  renderTimeline() {
    const width = document.getElementById('viz').offsetWidth;
    const height = 500;

    const svg = d3.select('#viz')
      .append('svg')
      .attr('width', width)
      .attr('height', height);

    const dates = [...new Set(this.data.map(d => d.date))].sort();

    const x = d3.scalePoint()
      .domain(dates.filter((_, i) => i % 5 === 0))
      .range([50, width - 50]);

    const y = d3.scalePoint()
      .domain(this.architectures.map(a => a.name))
      .range([50, height - 50]);

    // Draw points
    this.data.forEach(d => {
      svg.append('circle')
        .attr('cx', x(d.date))
        .attr('cy', y(d.architecture))
        .attr('r', Math.min(d.attestations / 50, 15))
        .attr('fill', d.color)
        .attr('opacity', 0.7);
    });

    // Axes
    svg.append('g')
      .attr('transform', `translate(0,${height - 50})`)
      .call(d3.axisBottom(x))
      .attr('color', '#fff');

    svg.append('g')
      .attr('transform', `translate(50,0)`)
      .call(d3.axisLeft(y))
      .attr('color', '#fff');
  }

  renderHeatmap() {
    const width = document.getElementById('viz').offsetWidth;
    const height = 500;

    const svg = d3.select('#viz')
      .append('svg')
      .attr('width', width)
      .attr('height', height);

    const dates = [...new Set(this.data.map(d => d.date))].sort().filter((_, i) => i % 3 === 0);
    const cellSize = Math.min(30, (width - 100) / dates.length);

    const x = d3.scalePoint()
      .domain(dates)
      .range([50, 50 + dates.length * cellSize]);

    const y = d3.scalePoint()
      .domain(this.architectures.map(a => a.name))
      .range([50, 50 + this.architectures.length * cellSize]);

    // Draw heatmap cells
    this.data.filter(d => dates.includes(d.date)).forEach(d => {
      const intensity = Math.min(d.attestations / 200, 1);
      svg.append('rect')
        .attr('x', x(d.date) - cellSize / 2)
        .attr('y', y(d.architecture) - cellSize / 2)
        .attr('width', cellSize - 2)
        .attr('height', cellSize - 2)
        .attr('fill', d.color)
        .attr('opacity', 0.3 + intensity * 0.7);
    });

    // Axes
    svg.append('g')
      .attr('transform', `translate(0,${50 + this.architectures.length * cellSize})`)
      .call(d3.axisBottom(x))
      .attr('color', '#fff')
      .selectAll('text')
      .attr('transform', 'rotate(-45)');

    svg.append('g')
      .attr('transform', `translate(50,0)`)
      .call(d3.axisLeft(y))
      .attr('color', '#fff');
  }
}

// Initialize on load
document.addEventListener('DOMContentLoaded', () => {
  new FossilVisualizer();
});
