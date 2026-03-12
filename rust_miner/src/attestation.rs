//! Attestation Module
//! 
//! Handles Ed25519 key generation and signing

use ed25519_dalek::{SigningKey, Signature, Signer};
use rand::rngs::OsRng;
use serde::{Deserialize, Serialize};
use crate::config::Config;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Attestation {
    #[serde(skip)]
    pub signing_key: SigningKey,
    pub public_key: String,
}

impl Attestation {
    pub fn new(_config: &Config) -> anyhow::Result<Self> {
        // Generate Ed25519 keypair
        let signing_key = SigningKey::generate(&mut OsRng);
        let public_key = hex::encode(signing_key.verifying_key().as_bytes());
        
        Ok(Self {
            signing_key,
            public_key,
        })
    }
    
    pub fn sign(&self, data: &[u8]) -> Signature {
        self.signing_key.sign(data)
    }
    
    pub fn attest(&self, fingerprint: &str, timestamp: u64) -> anyhow::Result<String> {
        let message = format!("{}:{}", fingerprint, timestamp);
        let signature = self.sign(message.as_bytes());
        Ok(hex::encode(signature))
    }
}
