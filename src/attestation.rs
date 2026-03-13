//! Attestation Module - Hardware Proof Submission

use anyhow::{Result, anyhow};
use serde::{Serialize, Deserialize};
use crate::crypto::Keypair;
use crate::hardware::{HardwareFingerprint, MiningWorkResult};

/// Attestation data structure
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Attestation {
    pub version: String,
    pub timestamp: u64,
    pub miner_public_key: String,
    pub fingerprint: HardwareFingerprint,
    pub signature: String,
}

/// Attestation response from node
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct AttestationResponse {
    pub status: String,
    pub reward_epoch: Option<u64>,
    pub message: Option<String>,
}

impl Attestation {
    /// Create a new attestation
    pub fn new(keypair: &Keypair, fingerprint: &HardwareFingerprint) -> Result<Self> {
        let timestamp = std::time::SystemTime::now()
            .duration_since(std::time::UNIX_EPOCH)?
            .as_secs();
        
        // Create message to sign
        let message = format!(
            "{}:{}:{}:{}",
            fingerprint.clock_drift.drift_hash,
            fingerprint.cache_timing.cache_hash,
            fingerprint.timestamp,
            timestamp
        );
        
        // Sign the message
        let signature = keypair.sign(message.as_bytes());
        
        Ok(Attestation {
            version: "1.0.0".to_string(),
            timestamp,
            miner_public_key: keypair.public_key_hex(),
            fingerprint: fingerprint.clone(),
            signature: hex::encode(signature.to_bytes()),
        })
    }
    
    /// Serialize to JSON
    pub fn to_json(&self) -> Result<String> {
        serde_json::to_string_pretty(self)
            .map_err(|e| anyhow!("Failed to serialize attestation: {}", e))
    }
}

/// Submit attestation to node
pub async fn submit_attestation(
    attestation: &Attestation,
    node_url: &str,
) -> Result<AttestationResponse> {
    let client = reqwest::Client::new();
    
    let response = client
        .post(&format!("{}/api/v1/attestation", node_url))
        .json(attestation)
        .send()
        .await
        .map_err(|e| anyhow!("Failed to send attestation: {}", e))?;
    
    if !response.status().is_success() {
        return Err(anyhow!("Node returned error: {}", response.status()));
    }
    
    let result = response
        .json::<AttestationResponse>()
        .await
        .map_err(|e| anyhow!("Failed to parse response: {}", e))?;
    
    Ok(result)
}

/// Submit mining work to node
pub async fn submit_work(
    work: &MiningWorkResult,
    keypair: &Keypair,
    node_url: &str,
) -> Result<()> {
    let client = reqwest::Client::new();
    
    // Sign the work
    let message = format!("{}:{}:{}", work.fingerprint_hash, work.work_proof, work.timestamp);
    let signature = keypair.sign(message.as_bytes());
    
    #[derive(Serialize)]
    struct WorkSubmission {
        fingerprint_hash: String,
        work_proof: String,
        timestamp: u64,
        difficulty_met: bool,
        miner_public_key: String,
        signature: String,
    }
    
    let submission = WorkSubmission {
        fingerprint_hash: work.fingerprint_hash.clone(),
        work_proof: work.work_proof.clone(),
        timestamp: work.timestamp,
        difficulty_met: work.difficulty_met,
        miner_public_key: keypair.public_key_hex(),
        signature: hex::encode(signature.to_bytes()),
    };
    
    let response = client
        .post(&format!("{}/api/v1/work", node_url))
        .json(&submission)
        .send()
        .await
        .map_err(|e| anyhow!("Failed to submit work: {}", e))?;
    
    if !response.status().is_success() {
        return Err(anyhow!("Node returned error: {}", response.status()));
    }
    
    Ok(())
}

/// Verify attestation signature
pub fn verify_attestation(attestation: &Attestation) -> Result<()> {
    use ed25519_dalek::VerifyingKey;
    
    // Decode public key
    let public_key_bytes = hex::decode(&attestation.miner_public_key)
        .map_err(|e| anyhow!("Invalid public key hex: {}", e))?;
    
    let verifying_key = VerifyingKey::from_bytes(
        &public_key_bytes.try_into()
            .map_err(|_| anyhow!("Invalid public key length"))?
    )?;
    
    // Decode signature
    let signature_bytes = hex::decode(&attestation.signature)
        .map_err(|e| anyhow!("Invalid signature hex: {}", e))?;
    
    let signature = ed25519_dalek::Signature::from_bytes(
        &signature_bytes.try_into()
            .map_err(|_| anyhow!("Invalid signature length"))?
    );
    
    // Recreate message
    let message = format!(
        "{}:{}:{}:{}",
        attestation.fingerprint.clock_drift.drift_hash,
        attestation.fingerprint.cache_timing.cache_hash,
        attestation.fingerprint.timestamp,
        attestation.timestamp
    );
    
    // Verify
    verifying_key.verify(message.as_bytes(), &signature)
        .map_err(|e| anyhow!("Signature verification failed: {}", e))?;
    
    Ok(())
}
