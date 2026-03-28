/**
 * Data Processor for Fossil Record Visualizer
 * Processes attestation data for visualization
 */

/**
 * Process raw attestation data
 * @param {Array} data - Raw attestation data
 * @returns {Object} Processed data structure
 */
function processAttestationData(data) {
    // Group by architecture and epoch
    const grouped = groupByArchAndEpoch(data);
    
    // Calculate statistics
    const stats = calculateStats(data);
    
    // Get unique architectures in order (oldest first)
    const architectures = getArchitecturesInOrder(data);
    
    return {
        grouped,
        stats,
        architectures
    };
}

/**
 * Group data by architecture and epoch
 */
function groupByArchAndEpoch(data) {
    const grouped = {};
    
    data.forEach(attestation => {
        const { architecture, epoch } = attestation;
        
        if (!grouped[architecture]) {
            grouped[architecture] = {};
        }
        
        if (!grouped[architecture][epoch]) {
            grouped[architecture][epoch] = [];
        }
        
        grouped[architecture][epoch].push(attestation);
    });
    
    return grouped;
}

/**
 * Calculate statistics from data
 */
function calculateStats(data) {
    const totalAttestations = data.length;
    const totalRTC = data.reduce((sum, d) => sum + d.rtc_earned, 0);
    const uniqueMiners = new Set(data.map(d => d.miner_id)).size;
    const uniqueArchitectures = new Set(data.map(d => d.architecture)).size;
    const minEpoch = Math.min(...data.map(d => d.epoch));
    const maxEpoch = Math.max(...data.map(d => d.epoch));
    const avgFingerprint = data.reduce((sum, d) => sum + d.fingerprint_quality, 0) / totalAttestations;
    
    return {
        totalAttestations,
        totalRTC,
        uniqueMiners,
        uniqueArchitectures,
        epochRange: { min: minEpoch, max: maxEpoch },
        avgFingerprint: avgFingerprint.toFixed(3)
    };
}

/**
 * Get architectures in chronological order (oldest first)
 */
function getArchitecturesInOrder(data) {
    const archFirstEpoch = {};
    
    data.forEach(attestation => {
        const { architecture, epoch } = attestation;
        if (!archFirstEpoch[architecture] || epoch < archFirstEpoch[architecture]) {
            archFirstEpoch[architecture] = epoch;
        }
    });
    
    // Sort by first appearance epoch
    return Object.entries(archFirstEpoch)
        .sort((a, b) => a[1] - b[1])
        .map(([arch, _]) => arch);
}

/**
 * Prepare data for D3 visualization
 */
function prepareForVisualization(processedData) {
    const { grouped, architectures } = processedData;
    
    const layers = architectures.map(arch => {
        const epochs = Object.keys(grouped[arch] || {}).map(Number).sort((a, b) => a - b);
        
        const stackData = epochs.map(epoch => {
            const attestations = grouped[arch][epoch];
            return {
                epoch,
                count: attestations.length,
                totalRTC: attestations.reduce((sum, a) => sum + a.rtc_earned, 0),
                attestations
            };
        });
        
        return {
            architecture: arch,
            stackData
        };
    });
    
    return layers;
}

/**
 * Get tooltip data for an attestation
 */
function getTooltipData(attestation) {
    return {
        miner_id: attestation.miner_id,
        device: attestation.device,
        architecture: attestation.architecture,
        epoch: attestation.epoch,
        rtc_earned: attestation.rtc_earned,
        fingerprint_quality: (attestation.fingerprint_quality * 100).toFixed(1) + '%',
        timestamp: new Date(attestation.timestamp).toLocaleDateString()
    };
}
