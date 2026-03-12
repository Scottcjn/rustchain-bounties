//! Cryptography Module - Ed25519 Signatures

use anyhow::{Result, anyhow};
use ed25519_dalek::{Signer, SigningKey, VerifyingKey, Signature, Verifier};
use rand::rngs::OsRng;
use serde::{Serialize, Deserialize};
use std::fs;
use std::path::Path;

/// Keypair for signing attestations
pub struct Keypair {
    pub signing_key: SigningKey,
    pub verifying_key: VerifyingKey,
}

impl Keypair {
    pub fn sign(&self, message: &[u8]) -> Signature {
        self.signing_key.sign(message)
    }
    
    pub fn public_key_hex(&self) -> String {
        hex::encode(self.verifying_key.as_bytes())
    }
}

/// Load or generate Ed25519 keypair
pub fn load_or_generate_keypair(key_path: &str) -> Result<Keypair> {
    let path = Path::new(key_path);
    
    if path.exists() {
        // Load existing key
        let key_bytes = fs::read(path)
            .map_err(|e| anyhow!("Failed to read key file: {}", e))?;
        
        if key_bytes.len() == 64 {
            let signing_key = SigningKey::from_bytes(
                &key_bytes[..32].try_into()
                    .map_err(|_| anyhow!("Invalid key format"))?
            );
            let verifying_key = VerifyingKey::from_bytes(
                &key_bytes[32..].try_into()
                    .map_err(|_| anyhow!("Invalid key format"))?
            )?;
            
            Ok(Keypair {
                signing_key,
                verifying_key,
            })
        } else {
            Err(anyhow!("Invalid key file size"))
        }
    } else {
        // Generate new key
        let signing_key = SigningKey::generate(&mut OsRng);
        let verifying_key = VerifyingKey::from(&signing_key);
        
        // Save key
        let mut key_bytes = Vec::with_capacity(64);
        key_bytes.extend_from_slice(signing_key.as_bytes());
        key_bytes.extend_from_slice(verifying_key.as_bytes());
        
        if let Some(parent) = path.parent() {
            fs::create_dir_all(parent)?;
        }
        
        fs::write(path, &key_bytes)
            .map_err(|e| anyhow!("Failed to save key file: {}", e))?;
        
        // Set permissions (Unix only)
        #[cfg(unix)]
        {
            use std::os::unix::fs::PermissionsExt;
            let mut perms = fs::metadata(path)?.permissions();
            perms.set_mode(0o600);
            fs::set_permissions(path, perms)?;
        }
        
        Ok(Keypair {
            signing_key,
            verifying_key,
        })
    }
}

/// Verify a signature
pub fn verify_signature(
    public_key: &VerifyingKey,
    message: &[u8],
    signature: &Signature,
) -> Result<()> {
    public_key.verify(message, signature)
        .map_err(|e| anyhow!("Signature verification failed: {}", e))
}

// Re-export hex for public key encoding
pub use hex;
