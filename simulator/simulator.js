// RustChain Mining Simulator - Interactive JavaScript

// Hardware configurations
const hardwareConfigs = {
    g4: {
        name: 'PowerBook G4',
        arch: 'g4',
        multiplier: 2.5,
        simd: 'AltiVec',
        timing: 'mftb',
        endian: 'Big-Endian',
        features: ['AltiVec SIMD', 'mftb Timing', 'High Entropy']
    },
    g5: {
        name: 'Power Mac G5',
        arch: 'g5',
        multiplier: 2.0,
        simd: 'AltiVec',
        timing: 'mftb',
        endian: 'Big-Endian',
        features: ['AltiVec SIMD', '64-bit PowerPC', 'Thermal Drift']
    },
    x86: {
        name: 'Modern x86',
        arch: 'x86',
        multiplier: 1.0,
        simd: 'SSE/AVX',
        timing: 'rdtsc',
        endian: 'Little-Endian',
        features: ['SSE/AVX SIMD', 'rdtsc Timing', 'Stable']
    },
    vm: {
        name: 'Virtual Machine',
        arch: 'vm',
        multiplier: 0.000000001,
        simd: 'None',
        timing: 'Virtual',
        endian: 'Little-Endian',
        features: [],
        isVM: true
    }
};

// Fingerprint check definitions
const fingerprintChecks = [
    { id: 1, name: 'Clock-Skew & Oscillator Drift', generateResult: generateClockSkew },
    { id: 2, name: 'Cache Timing Fingerprint', generateResult: generateCacheTiming },
    { id: 3, name: 'SIMD Unit Identity', generateResult: generateSIMD },
    { id: 4, name: 'Thermal Drift Entropy', generateResult: generateThermal },
    { id: 5, name: 'Instruction Path Jitter', generateResult: generateJitter },
    { id: 6, name: 'Anti-Emulation Check', generateResult: generateAntiEmulation }
];

// State
let selectedHardware = null;
let simulationRunning = false;

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    initializeHardwareCards();
    initializeControls();
    initializeCalculator();
    updateComparisonChart();
});

// Hardware card selection
function initializeHardwareCards() {
    const cards = document.querySelectorAll('.hardware-card');
    cards.forEach(card => {
        card.addEventListener('click', () => {
            // Deselect all
            cards.forEach(c => c.classList.remove('selected'));
            // Select clicked
            card.classList.add('selected');
            selectedHardware = card.dataset.arch;
            
            // Update comparison chart highlight
            updateComparisonChart();
        });
    });
}

// Control buttons
function initializeControls() {
    document.getElementById('start-simulation').addEventListener('click', startSimulation);
    document.getElementById('reset-simulation').addEventListener('click', resetSimulation);
}

// Start simulation
async function startSimulation() {
    if (!selectedHardware) {
        alert('Please select a hardware configuration first!');
        return;
    }

    if (simulationRunning) return;
    simulationRunning = true;

    const startBtn = document.getElementById('start-simulation');
    startBtn.disabled = true;
    startBtn.textContent = '⏳ Running...';

    const config = hardwareConfigs[selectedHardware];

    // Step 1: Hardware Detection
    await runStep1(config);

    // Step 2: Attestation Submission
    await runStep2(config);

    // Step 3: Epoch Participation
    await runStep3(config);

    // Step 4: Reward Calculation
    await runStep4(config);

    startBtn.disabled = false;
    startBtn.textContent = '▶️ Start Simulation';
    simulationRunning = false;
}

// Step 1: Hardware Detection with animated fingerprint checks
async function runStep1(config) {
    const stepCard = document.getElementById('step-1');
    stepCard.classList.add('active');
    updateStepStatus(stepCard, 'running');

    // Run each fingerprint check with animation
    for (const check of fingerprintChecks) {
        const checkItem = document.getElementById(`check-${check.id}`);
        checkItem.classList.add('running');
        checkItem.querySelector('.check-icon').textContent = '⏳';
        
        // Simulate processing time
        await sleep(800 + Math.random() * 500);
        
        // Generate result
        const result = check.generateResult(config);
        
        // Update check item
        if (result.passed) {
            checkItem.classList.remove('running');
            checkItem.classList.add('completed');
            checkItem.querySelector('.check-icon').textContent = '✅';
            checkItem.querySelector('.check-detail').textContent = result.detail;
        } else {
            checkItem.classList.remove('running');
            checkItem.classList.add('failed');
            checkItem.querySelector('.check-icon').textContent = '❌';
            checkItem.querySelector('.check-detail').textContent = result.detail;
        }
    }

    stepCard.classList.remove('active');
    stepCard.classList.add('completed');
    updateStepStatus(stepCard, 'completed');
}

// Step 2: Attestation Submission
async function runStep2(config) {
    const stepCard = document.getElementById('step-2');
    stepCard.classList.add('active');
    updateStepStatus(stepCard, 'running');

    await sleep(500);

    // Generate attestation payload
    const payload = generateAttestationPayload(config);
    const payloadElement = document.getElementById('attestation-payload');
    
    // Animate payload generation
    await typePayload(payloadElement, payload);

    await sleep(500);

    stepCard.classList.remove('active');
    stepCard.classList.add('completed');
    updateStepStatus(stepCard, 'completed');
}

// Step 3: Epoch Participation
async function runStep3(config) {
    const stepCard = document.getElementById('step-3');
    stepCard.classList.add('active');
    updateStepStatus(stepCard, 'running');

    await sleep(500);

    // Generate epoch data
    const epochNumber = Math.floor(Math.random() * 10000);
    const totalMiners = Math.floor(Math.random() * 50) + 50;
    const yourPosition = Math.floor(Math.random() * totalMiners);

    document.getElementById('epoch-number').textContent = `#${epochNumber}`;
    document.getElementById('enrolled-count').textContent = totalMiners;
    document.getElementById('your-position').textContent = `#${yourPosition + 1} / ${totalMiners}`;

    // Create round-robin visualization
    const vizContainer = document.getElementById('round-robin-viz');
    vizContainer.innerHTML = '';

    // Create miner dots
    for (let i = 0; i < Math.min(30, totalMiners); i++) {
        const dot = document.createElement('div');
        dot.className = 'miner-dot';
        if (i === yourPosition % 30) {
            dot.classList.add('your-position');
        }
        vizContainer.appendChild(dot);
    }

    // Animate round-robin selection
    await animateRoundRobin(vizContainer, yourPosition % 30, 15);

    stepCard.classList.remove('active');
    stepCard.classList.add('completed');
    updateStepStatus(stepCard, 'completed');
}

// Step 4: Reward Calculation
async function runStep4(config) {
    const stepCard = document.getElementById('step-4');
    stepCard.classList.add('active');
    updateStepStatus(stepCard, 'running');

    await sleep(500);

    // Calculate rewards
    const baseReward = 1.0;
    const multiplier = config.multiplier;
    const antiquityBonus = config.multiplier > 1 ? 0.5 : 0;
    const totalReward = baseReward * multiplier + antiquityBonus;

    // Animate values
    await animateValue('base-reward', 0, baseReward, 500, 'RTC');
    await animateValue('arch-multiplier', 0, multiplier, 500, 'x');
    await animateValue('antiquity-bonus', 0, antiquityBonus, 500, 'RTC');
    await animateValue('total-reward', 0, totalReward, 700, 'RTC');

    stepCard.classList.remove('active');
    stepCard.classList.add('completed');
    updateStepStatus(stepCard, 'completed');

    // Update comparison chart
    updateComparisonChart();
}

// Reset simulation
function resetSimulation() {
    if (simulationRunning) return;

    // Reset steps
    for (let i = 1; i <= 4; i++) {
        const stepCard = document.getElementById(`step-${i}`);
        stepCard.classList.remove('active', 'completed');
        updateStepStatus(stepCard, 'pending');
    }

    // Reset fingerprint checks
    for (let i = 1; i <= 6; i++) {
        const checkItem = document.getElementById(`check-${i}`);
        checkItem.classList.remove('running', 'completed', 'failed');
        checkItem.querySelector('.check-icon').textContent = '⏸️';
        checkItem.querySelector('.check-detail').textContent = '';
    }

    // Reset payload
    document.getElementById('attestation-payload').textContent = `{
  "nonce": "...",
  "wallet": "your-wallet",
  "device_arch": "...",
  "fingerprint": {
    "clock_skew": null,
    "cache_timing": null,
    "simd_unit": null,
    "thermal_entropy": null,
    "path_jitter": null,
    "anti_emulation": null
  }
}`;

    // Reset epoch data
    document.getElementById('epoch-number').textContent = '--';
    document.getElementById('enrolled-count').textContent = '--';
    document.getElementById('your-position').textContent = '--';
    document.getElementById('round-robin-viz').innerHTML = '';

    // Reset rewards
    document.getElementById('base-reward').textContent = '--';
    document.getElementById('arch-multiplier').textContent = '--';
    document.getElementById('antiquity-bonus').textContent = '--';
    document.getElementById('total-reward').textContent = '--';
}

// Helper: Update step status
function updateStepStatus(stepCard, status) {
    const statusElement = stepCard.querySelector('.step-status');
    statusElement.className = `step-status ${status}`;
    
    switch (status) {
        case 'pending':
            statusElement.textContent = '⏳ Pending';
            break;
        case 'running':
            statusElement.textContent = '⚡ Running';
            break;
        case 'completed':
            statusElement.textContent = '✅ Completed';
            break;
    }
}

// Helper: Sleep
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Fingerprint check generators
function generateClockSkew(config) {
    const baseDrift = config.timing === 'mftb' ? 0.02 : 0.001;
    const skew = (baseDrift + Math.random() * 0.01).toFixed(4);
    const passed = !config.isVM;
    return {
        passed,
        detail: passed ? `Drift: ${skew}%` : 'VM timing detected'
    };
}

function generateCacheTiming(config) {
    const latencies = {
        l1: (4 + Math.random() * 2).toFixed(1),
        l2: (12 + Math.random() * 5).toFixed(1),
        l3: (40 + Math.random() * 10).toFixed(1)
    };
    const passed = !config.isVM;
    return {
        passed,
        detail: passed ? `L1:${latencies.l1}ns L2:${latencies.l2}ns L3:${latencies.l3}ns` : 'Virtual cache detected'
    };
}

function generateSIMD(config) {
    const passed = !config.isVM;
    return {
        passed,
        detail: passed ? config.simd : 'No SIMD unit'
    };
}

function generateThermal(config) {
    const entropy = config.multiplier > 1 ? (0.85 + Math.random() * 0.1).toFixed(2) : (0.5 + Math.random() * 0.3).toFixed(2);
    const passed = !config.isVM;
    return {
        passed,
        detail: passed ? `Entropy: ${entropy}` : 'No thermal variance'
    };
}

function generateJitter(config) {
    const jitter = config.multiplier > 1 ? (50 + Math.random() * 100).toFixed(0) : (10 + Math.random() * 20).toFixed(0);
    const passed = !config.isVM;
    return {
        passed,
        detail: passed ? `${jitter} cycles variance` : 'No jitter detected'
    };
}

function generateAntiEmulation(config) {
    const passed = !config.isVM;
    return {
        passed,
        detail: passed ? 'Physical hardware' : 'VM/Hypervisor detected'
    };
}

// Generate attestation payload
function generateAttestationPayload(config) {
    const nonce = Array.from({ length: 32 }, () => 
        Math.floor(Math.random() * 16).toString(16)
    ).join('');

    const fingerprint = {
        clock_skew: {
            drift_ppm: Math.floor(Math.random() * 100),
            variance: Math.random().toFixed(6)
        },
        cache_timing: {
            l1_ns: (4 + Math.random() * 2).toFixed(1),
            l2_ns: (12 + Math.random() * 5).toFixed(1),
            l3_ns: (40 + Math.random() * 10).toFixed(1)
        },
        simd_unit: config.simd,
        thermal_entropy: (Math.random()).toFixed(4),
        path_jitter: Math.floor(Math.random() * 100),
        anti_emulation: !config.isVM
    };

    const payload = {
        nonce: nonce,
        wallet: "your-wallet-address",
        device_arch: config.arch,
        fingerprint: fingerprint,
        timestamp: new Date().toISOString(),
        multiplier: config.multiplier
    };

    return JSON.stringify(payload, null, 2);
}

// Animate payload typing
async function typePayload(element, text) {
    element.textContent = '';
    const lines = text.split('\n');
    
    for (const line of lines) {
        element.textContent += line + '\n';
        await sleep(30);
    }
}

// Animate round-robin selection
async function animateRoundRobin(container, targetPosition, iterations) {
    const dots = container.querySelectorAll('.miner-dot');
    let currentPos = 0;

    for (let i = 0; i < iterations; i++) {
        // Remove previous selection
        dots.forEach(dot => dot.classList.remove('selected'));
        
        // Select next dot
        dots[currentPos].classList.add('selected');
        
        await sleep(150);
        
        currentPos = (currentPos + 1) % dots.length;
    }

    // Final selection at target
    dots.forEach(dot => dot.classList.remove('selected'));
    dots[targetPosition].classList.add('selected', 'your-position');
}

// Animate value
async function animateValue(elementId, start, end, duration, suffix = '') {
    const element = document.getElementById(elementId);
    const startTime = performance.now();
    
    function update() {
        const elapsed = performance.now() - startTime;
        const progress = Math.min(elapsed / duration, 1);
        
        // Easing function
        const easeOut = 1 - Math.pow(1 - progress, 3);
        const current = start + (end - start) * easeOut;
        
        element.textContent = current.toFixed(2) + ' ' + suffix;
        
        if (progress < 1) {
            requestAnimationFrame(update);
        }
    }
    
    update();
    await sleep(duration);
}

// Update comparison chart
function updateComparisonChart() {
    const baseReward = 1.0;
    const antiquityBonus = 0.5;

    Object.entries(hardwareConfigs).forEach(([arch, config]) => {
        const totalReward = baseReward * config.multiplier + (config.multiplier > 1 ? antiquityBonus : 0);
        
        // Update bar width (normalize to max reward = 3.0 for G4)
        const maxWidth = (totalReward / 3.0) * 100;
        document.getElementById(`bar-${arch}`).style.width = `${maxWidth}%`;
        
        // Update value
        document.getElementById(`value-${arch}`).textContent = `${totalReward.toFixed(2)} RTC/epoch`;
    });
}

// Calculator
function initializeCalculator() {
    document.getElementById('calculate-earnings').addEventListener('click', calculateEarnings);
}

function calculateEarnings() {
    const hardware = document.getElementById('calc-hardware').value;
    const epochs = parseInt(document.getElementById('calc-epochs').value);
    const networkHash = parseInt(document.getElementById('calc-network-hash').value);

    const config = hardwareConfigs[hardware];
    
    // Calculate chance per epoch (simplified)
    const chancePerEpoch = 1 / networkHash;
    
    // Calculate effective multiplier
    const effectiveMult = config.multiplier * (config.multiplier > 1 ? 1.5 : 1.0);
    
    // Base reward per epoch
    const baseRewardPerEpoch = 1.0;
    
    // Expected reward per epoch
    const rewardPerEpoch = baseRewardPerEpoch * effectiveMult * chancePerEpoch;
    
    // Total expected earnings
    const totalEarnings = rewardPerEpoch * epochs;

    // Display results
    document.getElementById('calculator-results').style.display = 'grid';
    
    // Animate total RTC
    animateValue('calc-total-rtc', 0, totalEarnings, 800, 'RTC');
    
    document.getElementById('calc-per-epoch').textContent = rewardPerEpoch.toFixed(6) + ' RTC';
    document.getElementById('calc-chance').textContent = (chancePerEpoch * 100).toFixed(2) + '%';
    document.getElementById('calc-effective-mult').textContent = effectiveMult.toFixed(2) + 'x';
}

// Utility: Format number with commas
function formatNumber(num) {
    return num.toString().replace(/\B(?=(\d{3})+(?!\d))/g, ",");
}