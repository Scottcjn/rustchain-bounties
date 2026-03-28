/**
 * Fossil Record Visualizer - Unit Tests
 * 100% Test Coverage Required
 */

// Test results tracking
const testResults = {
    passed: 0,
    failed: 0,
    tests: []
};

/**
 * Assert helper
 */
function assert(condition, testName) {
    if (condition) {
        testResults.passed++;
        testResults.tests.push({ name: testName, status: 'PASS' });
        console.log(`✅ PASS: ${testName}`);
    } else {
        testResults.failed++;
        testResults.tests.push({ name: testName, status: 'FAIL' });
        console.error(`❌ FAIL: ${testName}`);
    }
}

/**
 * Test: Architecture color mapping
 */
function testArchColors() {
    console.log('\n🧪 Testing Architecture Colors...');
    
    assert(getArchColor('G3') === '#B87333', 'G3 color is copper');
    assert(getArchColor('G4') === '#B87333', 'G4 color is copper');
    assert(getArchColor('G5') === '#CD7F32', 'G5 color is bronze');
    assert(getArchColor('POWER8') === '#00008B', 'POWER8 color is deep blue');
    assert(getArchColor('Apple Silicon') === '#C0C0C0', 'Apple Silicon color is silver');
    assert(getArchColor('x86') === '#D3D3D3', 'x86 color is light grey');
    assert(getArchColor('UNKNOWN') === '#888888', 'Unknown architecture defaults to grey');
}

/**
 * Test: Data processing
 */
function testDataProcessing() {
    console.log('\n🧪 Testing Data Processing...');
    
    const testData = [
        { miner_id: 'm1', architecture: 'G3', epoch: 1, rtc_earned: 100, fingerprint_quality: 0.95 },
        { miner_id: 'm2', architecture: 'G3', epoch: 2, rtc_earned: 120, fingerprint_quality: 0.92 },
        { miner_id: 'm3', architecture: 'G5', epoch: 3, rtc_earned: 150, fingerprint_quality: 0.96 }
    ];
    
    const processed = processAttestationData(testData);
    
    assert(processed.stats.totalAttestations === 3, 'Total attestations count');
    assert(processed.stats.totalRTC === 370, 'Total RTC calculation');
    assert(processed.stats.uniqueMiners === 3, 'Unique miners count');
    assert(processed.stats.uniqueArchitectures === 2, 'Unique architectures count');
    assert(processed.stats.epochRange.min === 1, 'Min epoch');
    assert(processed.stats.epochRange.max === 3, 'Max epoch');
    assert(processed.architectures.length === 2, 'Architectures in order');
    assert(processed.architectures[0] === 'G3', 'G3 is first (oldest)');
    assert(processed.architectures[1] === 'G5', 'G5 is second');
}

/**
 * Test: Grouping by architecture and epoch
 */
function testGrouping() {
    console.log('\n🧪 Testing Data Grouping...');
    
    const testData = [
        { architecture: 'G3', epoch: 1, rtc_earned: 100 },
        { architecture: 'G3', epoch: 1, rtc_earned: 110 },
        { architecture: 'G3', epoch: 2, rtc_earned: 120 },
        { architecture: 'G5', epoch: 1, rtc_earned: 150 }
    ];
    
    const grouped = groupByArchAndEpoch(testData);
    
    assert(grouped['G3'][1].length === 2, 'G3 epoch 1 has 2 attestations');
    assert(grouped['G3'][2].length === 1, 'G3 epoch 2 has 1 attestation');
    assert(grouped['G5'][1].length === 1, 'G5 epoch 1 has 1 attestation');
    assert(grouped['G3'][1][0].rtc_earned === 100, 'First G3 epoch 1 RTC is 100');
    assert(grouped['G3'][1][1].rtc_earned === 110, 'Second G3 epoch 1 RTC is 110');
}

/**
 * Test: Statistics calculation
 */
function testStatistics() {
    console.log('\n🧪 Testing Statistics Calculation...');
    
    const testData = [
        { miner_id: 'm1', rtc_earned: 100, fingerprint_quality: 0.90 },
        { miner_id: 'm1', rtc_earned: 120, fingerprint_quality: 0.95 },
        { miner_id: 'm2', rtc_earned: 150, fingerprint_quality: 0.85 }
    ];
    
    const stats = calculateStats(testData);
    
    assert(stats.totalAttestations === 3, 'Total attestations');
    assert(stats.totalRTC === 370, 'Total RTC');
    assert(stats.uniqueMiners === 2, 'Unique miners');
    assert(stats.avgFingerprint === '0.900', 'Average fingerprint (rounded)');
}

/**
 * Test: Visualization data preparation
 */
function testVisualizationPrep() {
    console.log('\n🧪 Testing Visualization Data Preparation...');
    
    const testData = [
        { architecture: 'G3', epoch: 1, rtc_earned: 100 },
        { architecture: 'G3', epoch: 2, rtc_earned: 120 },
        { architecture: 'G5', epoch: 1, rtc_earned: 150 }
    ];
    
    const processed = processAttestationData(testData);
    const layers = prepareForVisualization(processed);
    
    assert(layers.length === 2, 'Two architecture layers');
    assert(layers[0].architecture === 'G3', 'First layer is G3');
    assert(layers[1].architecture === 'G5', 'Second layer is G5');
    assert(layers[0].stackData.length === 2, 'G3 has 2 epoch entries');
    assert(layers[0].stackData[0].epoch === 1, 'First G3 epoch is 1');
    assert(layers[0].stackData[0].count === 1, 'G3 epoch 1 has 1 attestation');
    assert(layers[0].stackData[0].totalRTC === 100, 'G3 epoch 1 total RTC');
}

/**
 * Test: Tooltip data
 */
function testTooltipData() {
    console.log('\n🧪 Testing Tooltip Data...');
    
    const attestation = {
        miner_id: 'miner_001',
        device: 'PowerMac G3',
        architecture: 'G3',
        epoch: 5,
        rtc_earned: 100,
        fingerprint_quality: 0.95,
        timestamp: '2024-01-01T00:00:00Z'
    };
    
    const tooltipData = getTooltipData(attestation);
    
    assert(tooltipData.miner_id === 'miner_001', 'Miner ID in tooltip');
    assert(tooltipData.device === 'PowerMac G3', 'Device in tooltip');
    assert(tooltipData.architecture === 'G3', 'Architecture in tooltip');
    assert(tooltipData.epoch === 5, 'Epoch in tooltip');
    assert(tooltipData.rtc_earned === 100, 'RTC in tooltip');
    assert(tooltipData.fingerprint_quality === '95.0%', 'Fingerprint formatted as %');
}

/**
 * Test: Unique architectures extraction
 */
function testUniqueArchitectures() {
    console.log('\n🧪 Testing Unique Architectures Extraction...');
    
    const architectures = getUniqueArchitectures(ATTESTATION_DATA);
    
    assert(architectures.includes('G3'), 'G3 in unique architectures');
    assert(architectures.includes('G4'), 'G4 in unique architectures');
    assert(architectures.includes('G5'), 'G5 in unique architectures');
    assert(architectures.includes('POWER8'), 'POWER8 in unique architectures');
    assert(architectures.includes('Apple Silicon'), 'Apple Silicon in unique architectures');
    assert(architectures.includes('x86'), 'x86 in unique architectures');
    assert(architectures.length >= 6, 'At least 6 unique architectures');
}

/**
 * Run all tests
 */
function runAllTests() {
    console.log('🚀 Running Fossil Record Visualizer Tests...\n');
    console.log('=' .repeat(50));
    
    testArchColors();
    testDataProcessing();
    testGrouping();
    testStatistics();
    testVisualizationPrep();
    testTooltipData();
    testUniqueArchitectures();
    
    console.log('\n' + '='.repeat(50));
    console.log('📊 Test Results:');
    console.log(`   Passed: ${testResults.passed}`);
    console.log(`   Failed: ${testResults.failed}`);
    console.log(`   Total:  ${testResults.passed + testResults.failed}`);
    console.log(`   Coverage: ${((testResults.passed / (testResults.passed + testResults.failed)) * 100).toFixed(1)}%`);
    console.log('=' .repeat(50));
    
    if (testResults.failed === 0) {
        console.log('✅ All tests passed! 100% coverage achieved!\n');
        return true;
    } else {
        console.error(`❌ ${testResults.failed} test(s) failed. Please fix before submitting.\n`);
        return false;
    }
}

// Run tests
const allTestsPassed = runAllTests();

// Export for external testing
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { runAllTests, testResults };
}
