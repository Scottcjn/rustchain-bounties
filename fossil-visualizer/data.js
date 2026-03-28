/**
 * Fossil Record Data
 * Sample attestation data for visualization
 * 
 * In production, this would be fetched from RustChain database API
 */

// Architecture color mapping
const ARCHITECTURE_COLORS = {
    '68K': '#FFBF00',        // Dark amber
    'G3': '#B87333',         // Warm copper
    'G4': '#B87333',         // Warm copper
    'G5': '#CD7F32',         // Bronze
    'SPARC': '#DC143C',      // Crimson
    'MIPS': '#00A86B',       // Jade
    'POWER8': '#00008B',     // Deep blue
    'Apple Silicon': '#C0C0C0', // Silver
    'x86': '#D3D3D3'         // Light grey
};

// Sample attestation data (simulated from RustChain database)
const ATTESTATION_DATA = [
    // Epoch 0-10: Early days (G3/G4)
    { miner_id: 'miner_001', device: 'PowerMac G3', architecture: 'G3', epoch: 1, rtc_earned: 100, fingerprint_quality: 0.95, timestamp: '2024-01-01T00:00:00Z' },
    { miner_id: 'miner_002', device: 'PowerMac G4', architecture: 'G4', epoch: 2, rtc_earned: 120, fingerprint_quality: 0.92, timestamp: '2024-01-02T00:00:00Z' },
    { miner_id: 'miner_003', device: 'PowerMac G4', architecture: 'G4', epoch: 3, rtc_earned: 115, fingerprint_quality: 0.94, timestamp: '2024-01-03T00:00:00Z' },
    
    // Epoch 10-30: G5 era
    { miner_id: 'miner_004', device: 'PowerMac G5', architecture: 'G5', epoch: 12, rtc_earned: 150, fingerprint_quality: 0.96, timestamp: '2024-01-15T00:00:00Z' },
    { miner_id: 'miner_005', device: 'PowerMac G5', architecture: 'G5', epoch: 15, rtc_earned: 145, fingerprint_quality: 0.93, timestamp: '2024-01-20T00:00:00Z' },
    { miner_id: 'miner_006', device: 'PowerMac G5', architecture: 'G5', epoch: 20, rtc_earned: 160, fingerprint_quality: 0.97, timestamp: '2024-02-01T00:00:00Z' },
    
    // Epoch 30-50: SPARC/MIPS
    { miner_id: 'miner_007', device: 'SPARC Station', architecture: 'SPARC', epoch: 35, rtc_earned: 180, fingerprint_quality: 0.91, timestamp: '2024-03-01T00:00:00Z' },
    { miner_id: 'miner_008', device: 'MIPS Router', architecture: 'MIPS', epoch: 40, rtc_earned: 170, fingerprint_quality: 0.89, timestamp: '2024-03-15T00:00:00Z' },
    { miner_id: 'miner_009', device: 'SPARC Server', architecture: 'SPARC', epoch: 45, rtc_earned: 190, fingerprint_quality: 0.94, timestamp: '2024-04-01T00:00:00Z' },
    
    // Epoch 50-70: POWER8
    { miner_id: 'miner_010', device: 'POWER8 Server', architecture: 'POWER8', epoch: 55, rtc_earned: 220, fingerprint_quality: 0.98, timestamp: '2024-05-01T00:00:00Z' },
    { miner_id: 'miner_011', device: 'POWER8 Server', architecture: 'POWER8', epoch: 60, rtc_earned: 230, fingerprint_quality: 0.97, timestamp: '2024-05-15T00:00:00Z' },
    { miner_id: 'miner_012', device: 'POWER8 Cluster', architecture: 'POWER8', epoch: 65, rtc_earned: 250, fingerprint_quality: 0.99, timestamp: '2024-06-01T00:00:00Z' },
    
    // Epoch 70-90: Apple Silicon
    { miner_id: 'miner_013', device: 'M1 Mac Mini', architecture: 'Apple Silicon', epoch: 75, rtc_earned: 280, fingerprint_quality: 0.96, timestamp: '2024-07-01T00:00:00Z' },
    { miner_id: 'miner_014', device: 'M2 MacBook Pro', architecture: 'Apple Silicon', epoch: 80, rtc_earned: 300, fingerprint_quality: 0.98, timestamp: '2024-07-15T00:00:00Z' },
    { miner_id: 'miner_015', device: 'M3 iMac', architecture: 'Apple Silicon', epoch: 85, rtc_earned: 320, fingerprint_quality: 0.97, timestamp: '2024-08-01T00:00:00Z' },
    
    // Epoch 90-100: Modern x86
    { miner_id: 'miner_016', device: 'Intel Xeon', architecture: 'x86', epoch: 92, rtc_earned: 350, fingerprint_quality: 0.95, timestamp: '2024-08-15T00:00:00Z' },
    { miner_id: 'miner_017', device: 'AMD EPYC', architecture: 'x86', epoch: 95, rtc_earned: 360, fingerprint_quality: 0.96, timestamp: '2024-09-01T00:00:00Z' },
    { miner_id: 'miner_018', device: 'Intel Core i9', architecture: 'x86', epoch: 98, rtc_earned: 340, fingerprint_quality: 0.94, timestamp: '2024-09-15T00:00:00Z' },
    
    // Legacy: 68K (oldest)
    { miner_id: 'miner_019', device: 'Macintosh II', architecture: '68K', epoch: 5, rtc_earned: 50, fingerprint_quality: 0.85, timestamp: '2024-01-10T00:00:00Z' },
    { miner_id: 'miner_020', device: 'Macintosh SE', architecture: '68K', epoch: 8, rtc_earned: 55, fingerprint_quality: 0.87, timestamp: '2024-01-12T00:00:00Z' },
];

// Epoch settlement markers
const EPOCH_MARKERS = [
    { epoch: 10, label: 'Era 1: G3/G4' },
    { epoch: 30, label: 'Era 2: G5' },
    { epoch: 50, label: 'Era 3: SPARC/MIPS' },
    { epoch: 70, label: 'Era 4: POWER8' },
    { epoch: 90, label: 'Era 5: Apple Silicon' },
    { epoch: 100, label: 'Current: x86' },
];

/**
 * Fetch attestation data from RustChain API
 * In production, replace with actual API call
 */
async function fetchAttestationData() {
    // TODO: Replace with actual API call
    // const response = await fetch('https://api.rustchain.org/attestations');
    // return await response.json();
    
    // Return sample data for now
    return ATTESTATION_DATA;
}

/**
 * Get architecture color
 */
function getArchColor(architecture) {
    return ARCHITECTURE_COLORS[architecture] || '#888888';
}

/**
 * Get unique architectures from data
 */
function getUniqueArchitectures(data) {
    return [...new Set(data.map(d => d.architecture))];
}
