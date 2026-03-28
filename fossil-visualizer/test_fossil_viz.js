/**
 * Fossil Visualizer Test Suite
 * Bounty #2311 - 75 RTC
 */

const fs = require('fs');

console.log('='.repeat(50));
console.log('Fossil Visualizer Test Suite');
console.log('Bounty #2311 - 75 RTC');
console.log('='.repeat(50));
console.log('');

const tests = [
  { name: 'index.html exists', fn: () => {
    if (!fs.existsSync('index.html')) throw new Error('index.html not found');
  }},
  { name: 'fossil_viz.js exists', fn: () => {
    if (!fs.existsSync('fossil_viz.js')) throw new Error('fossil_viz.js not found');
  }},
  { name: 'Uses D3.js', fn: () => {
    const html = fs.readFileSync('index.html', 'utf8');
    if (!html.includes('d3.js') && !html.includes('d3js.org')) throw new Error('D3.js not loaded');
  }},
  { name: 'Has 4 visualization modes', fn: () => {
    const html = fs.readFileSync('index.html', 'utf8');
    const modes = ['stacked', 'streamgraph', 'timeline', 'heatmap'];
    modes.forEach(mode => {
      if (!html.includes(mode)) throw new Error(`Missing mode: ${mode}`);
    });
  }},
  { name: 'Has architecture legend', fn: () => {
    const html = fs.readFileSync('index.html', 'utf8');
    if (!html.includes('legend')) throw new Error('Missing legend');
  }},
  { name: 'Has statistics cards', fn: () => {
    const html = fs.readFileSync('index.html', 'utf8');
    if (!html.includes('stat-card')) throw new Error('Missing stats');
  }},
  { name: 'JS has FossilVisualizer class', fn: () => {
    const js = fs.readFileSync('fossil_viz.js', 'utf8');
    if (!js.includes('class FossilVisualizer')) throw new Error('Missing class');
  }},
  { name: 'JS has render methods', fn: () => {
    const js = fs.readFileSync('fossil_viz.js', 'utf8');
    const methods = ['renderStackedArea', 'renderStreamgraph', 'renderTimeline', 'renderHeatmap'];
    methods.forEach(m => {
      if (!js.includes(m)) throw new Error(`Missing method: ${m}`);
    });
  }},
  { name: 'JS has data generation', fn: () => {
    const js = fs.readFileSync('fossil_viz.js', 'utf8');
    if (!js.includes('generateMockData')) throw new Error('Missing data generation');
  }},
  { name: 'Supports 5 architectures', fn: () => {
    const js = fs.readFileSync('fossil_viz.js', 'utf8');
    const archs = ['RISC-V', 'POWER8', 'x86_64', 'ARM64', 'N64'];
    archs.forEach(arch => {
      if (!js.includes(arch)) throw new Error(`Missing architecture: ${arch}`);
    });
  }}
];

let passed = 0;
let failed = 0;

tests.forEach(test => {
  try {
    test.fn();
    console.log(`✅ ${test.name}`);
    passed++;
  } catch (e) {
    console.log(`❌ ${test.name}: ${e.message}`);
    failed++;
  }
});

console.log('');
console.log('='.repeat(50));
console.log(`Tests: ${passed + failed} | Passed: ${passed} | Failed: ${failed}`);
console.log('='.repeat(50));

process.exit(failed > 0 ? 1 : 0);
