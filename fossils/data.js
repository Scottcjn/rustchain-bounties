// RustChain Attestation Archaeology - Data Module

// Architecture definitions with colors as specified
const ARCHITECTURES = {
    '68K': {
        name: 'Motorola 68K',
        color: '#ff8c00', // Deep amber
        layer: 1,
        description: 'Classic Macintosh, Amiga, Atari ST'
    },
    'G3': {
        name: 'PowerPC G3',
        color: '#cd7f32', // Warm copper
        layer: 2,
        description: 'iMac G3, Power Mac G3'
    },
    'G4': {
        name: 'PowerPC G4',
        color: '#cd7f32', // Warm copper (same as G3)
        layer: 3,
        description: 'PowerBook G4, Power Mac G4'
    },
    'G5': {
        name: 'PowerPC G5',
        color: '#b87333', // Bronze
        layer: 4,
        description: 'Power Mac G5'
    },
    'SPARC': {
        name: 'SPARC',
        color: '#8b0000', // Dark red
        layer: 5,
        description: 'Sun Microsystems workstations'
    },
    'MIPS': {
        name: 'MIPS',
        color: '#50c878', // Emerald
        layer: 6,
        description: 'SGI, DEC, various embedded'
    },
    'POWER8': {
        name: 'POWER8',
        color: '#00008b', // Dark blue
        layer: 7,
        description: 'IBM Power Systems'
    },
    'APPLE_SILICON': {
        name: 'Apple Silicon',
        color: '#c0c0c0', // Silver
        layer: 8,
        description: 'M1/M2/M3 series chips'
    },
    'X86': {
        name: 'Modern x86',
        color: '#d3d3d3', // Light gray
        layer: 9,
        description: 'Intel/AMD x86-64'
    }
};

// Generate mock attestation data
function generateMockData(numMiners = 50, numEpochs = 100) {
    const data = [];
    const archKeys = Object.keys(ARCHITECTURES);
    
    for (let miner = 0; miner < numMiners; miner++) {
        const minerId = `miner_${miner.toString().padStart(4, '0')}`;
        const arch = archKeys[Math.floor(Math.random() * archKeys.length)];
        const archInfo = ARCHITECTURES[arch];
        
        // Each miner has multiple attestations across epochs
        const startEpoch = Math.floor(Math.random() * numEpochs * 0.3);
        const endEpoch = Math.min(startEpoch + Math.floor(Math.random() * numEpochs * 0.7) + 10, numEpochs);
        
        for (let epoch = startEpoch; epoch < endEpoch; epoch++) {
            // Skip some epochs randomly (miner offline)
            if (Math.random() > 0.85) continue;
            
            const rtcEarned = (Math.random() * 10 + 1) * archInfo.layer;
            const fingerprintQuality = Math.random() * 0.3 + 0.7; // 0.7-1.0
            
            data.push({
                minerId: minerId,
                epoch: epoch,
                architecture: arch,
                archLayer: archInfo.layer,
                color: archInfo.color,
                device: getDeviceName(arch),
                rtcEarned: parseFloat(rtcEarned.toFixed(2)),
                fingerprintQuality: parseFloat(fingerprintQuality.toFixed(3)),
                timestamp: new Date(Date.now() - (numEpochs - epoch) * 3600000).toISOString()
            });
        }
    }
    
    return data;
}

// Get realistic device names for architectures
function getDeviceName(arch) {
    const devices = {
        '68K': ['Macintosh Plus', 'Amiga 500', 'Atari ST', 'Macintosh SE'],
        'G3': ['iMac G3', 'Power Mac G3', 'PowerBook G3', 'iBook G3'],
        'G4': ['PowerBook G4', 'Power Mac G4', 'iMac G4', 'eMac'],
        'G5': ['Power Mac G5', 'iMac G5', 'Xserve G5'],
        'SPARC': ['Sun Ultra 10', 'Sun Blade 100', 'SPARCstation 20'],
        'MIPS': ['SGI O2', 'SGI Octane', 'DECstation 5000'],
        'POWER8': ['IBM Power System S822', 'IBM Power System S812'],
        'APPLE_SILICON': ['MacBook Pro M1', 'Mac Mini M2', 'iMac M3', 'Mac Studio M2'],
        'X86': ['Intel i7-12700K', 'AMD Ryzen 9 5900X', 'Intel i9-13900K', 'AMD EPYC 7763']
    };
    
    const archDevices = devices[arch] || ['Unknown Device'];
    return archDevices[Math.floor(Math.random() * archDevices.length)];
}

// Fetch data from RustChain API
async function fetchFromAPI(baseUrl = 'http://50.28.86.131:9100') {
    try {
        // Try to fetch miners
        const minersResponse = await fetch(`${baseUrl}/api/miners?limit=100`);
        if (!minersResponse.ok) throw new Error('API unavailable');
        
        const minersData = await minersResponse.json();
        
        // For each miner, get attestation history
        const attestationPromises = minersData.miners.map(async miner => {
            try {
                const attResponse = await fetch(`${baseUrl}/api/miners/${miner.id}/attestation`);
                if (!attResponse.ok) return null;
                
                const attData = await attResponse.json();
                return {
                    minerId: miner.id,
                    epoch: attData.epoch,
                    architecture: inferArchitecture(attData.hardware_hash),
                    rtcEarned: miner.stake || 0,
                    fingerprintQuality: attData.score || 0.9,
                    device: 'Unknown',
                    timestamp: attData.last_attestation
                };
            } catch {
                return null;
            }
        });
        
        const results = await Promise.all(attestationPromises);
        return results.filter(r => r !== null);
        
    } catch (error) {
        console.warn('API fetch failed, using mock data:', error.message);
        return null;
    }
}

// Infer architecture from hardware hash (simplified)
function inferArchitecture(hardwareHash) {
    if (!hardwareHash) return 'X86';
    
    const hash = hardwareHash.toLowerCase();
    if (hash.includes('m1') || hash.includes('m2') || hash.includes('m3')) return 'APPLE_SILICON';
    if (hash.includes('g4') || hash.includes('altivec')) return 'G4';
    if (hash.includes('g5')) return 'G5';
    if (hash.includes('g3')) return 'G3';
    if (hash.includes('ppc') || hash.includes('powerpc')) return 'G5';
    if (hash.includes('sparc')) return 'SPARC';
    if (hash.includes('mips')) return 'MIPS';
    if (hash.includes('power8')) return 'POWER8';
    if (hash.includes('68k') || hash.includes('680')) return '68K';
    
    return 'X86';
}

// Data manager
class AttestationDataManager {
    constructor() {
        this.data = [];
        this.filteredData = [];
        this.useMockData = true;
    }
    
    async loadData(useAPI = true) {
        if (useAPI) {
            const apiData = await fetchFromAPI();
            if (apiData && apiData.length > 0) {
                this.data = apiData;
                this.useMockData = false;
                console.log(`Loaded ${apiData.length} attestations from API`);
            } else {
                this.data = generateMockData(80, 100);
                this.useMockData = true;
                console.log('Using mock data (API unavailable)');
            }
        } else {
            this.data = generateMockData(80, 100);
            this.useMockData = true;
        }
        
        this.filteredData = [...this.data];
        return this.data;
    }
    
    filterByEpochRange(start, end) {
        this.filteredData = this.data.filter(d => d.epoch >= start && d.epoch <= end);
        return this.filteredData;
    }
    
    getStatistics() {
        const uniqueMiners = new Set(this.filteredData.map(d => d.minerId));
        const totalRTC = this.filteredData.reduce((sum, d) => sum + d.rtcEarned, 0);
        const archCounts = {};
        
        this.filteredData.forEach(d => {
            archCounts[d.architecture] = (archCounts[d.architecture] || 0) + 1;
        });
        
        const mostCommonArch = Object.entries(archCounts)
            .sort((a, b) => b[1] - a[1])[0];
        
        return {
            totalMiners: uniqueMiners.size,
            totalAttestations: this.filteredData.length,
            totalRTC: parseFloat(totalRTC.toFixed(2)),
            mostCommonArch: mostCommonArch ? ARCHITECTURES[mostCommonArch[0]].name : '-'
        };
    }
    
    getEpochMarkers() {
        const epochs = [...new Set(this.filteredData.map(d => d.epoch))].sort((a, b) => a - b);
        // Mark every 10th epoch as a settlement marker
        return epochs.filter(e => e % 10 === 0);
    }
    
    exportToCSV() {
        const headers = ['minerId', 'epoch', 'architecture', 'device', 'rtcEarned', 'fingerprintQuality', 'timestamp'];
        const rows = this.filteredData.map(d => 
            [d.minerId, d.epoch, d.architecture, d.device, d.rtcEarned, d.fingerprintQuality, d.timestamp].join(',')
        );
        
        return [headers.join(','), ...rows].join('\n');
    }
}

// Export
window.AttestationDataManager = AttestationDataManager;
window.ARCHITECTURES = ARCHITECTURES;