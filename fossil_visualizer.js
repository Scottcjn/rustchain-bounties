const crypto = require('crypto');
const { Buffer } = require('buffer');

class FossilRecordVisualizer {
  /**
   * Initialize the Fossil Record Visualizer with the given attestation data.
   * @param {Uint8Array} attestationBytes - The attestation bytes.
   */
  constructor(attestationBytes) {
    this.attestationData = Attestation.decode(attestationBytes);
  }

  /**
   * Visualize the attestation record by computing the Merkle Root hash.
   * @returns {string} - The Merkle Root hash.
   */
  visualize() {
    const merkleRoot = this.attestationData.computeMerkleRoot();
    return merkleRoot;
  }
}

class Attestation {
  static decode(attestationBytes) {
    const attestationData = {};
    attestationData.version = Buffer.from(attestationBytes.slice(0, 4), 'utf8');
    attestationData.signer = Buffer.from(attestationBytes.slice(4, 20), 'utf8');
    attestationData.timestamp = Buffer.from(attestationBytes.slice(20, 44), 'utf8');
    attestationData.message = Buffer.from(attestationBytes.slice(44, 72), 'utf8');
    attestationData.signature = Buffer.from(attestationBytes.slice(72, 108), 'utf8');
    return attestationData;
  }

  computeMerkleRoot() {
    const blocks = [
      this.version,
      this.signer,
      this.timestamp,
      this.message,
      this.signature || Buffer.alloc(0),
    ];
    // Using SHA-256 for broader compatibility if BLAKE2b is not available
    const intermediateHashes = blocks.map((block) => crypto.createHash('sha256').update(block).digest());
    let merkleRootHash = intermediateHashes[0];
    for (let i = 1; i < intermediateHashes.length; i++) {
        merkleRootHash = crypto.createHash('sha256').update(merkleRootHash).update(intermediateHashes[i]).digest();
    }
    return merkleRootHash;
  }
}

module.exports = { FossilRecordVisualizer };
