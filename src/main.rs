//! RustChain Miner - Native Rust Implementation
//! 
//! Port of rustchain_universal_miner.py with:
//! - Hardware fingerprinting (7 checks)
//! - Ed25519 signatures
//! - Attestation submission

mod hardware;
mod crypto;
mod attestation;
mod config;

use anyhow::Result;
use env_logger::Env;
use log::{info, warn, error};
use std::time::Duration;
use tokio::time::sleep;

#[tokio::main]
async fn main() -> Result<()> {
    // Initialize logging
    env_logger::Builder::from_env(Env::default().default_filter_or("info")).init();
    
    info!("🦀 RustChain Miner v0.1.0 starting...");
    
    // Load configuration
    let config = config::Config::load()?;
    
    // Generate or load Ed25519 keypair
    let keypair = crypto::load_or_generate_keypair(&config.key_path)?;
    info!("✅ Ed25519 keypair loaded");
    
    // Collect hardware fingerprint
    info!("🔍 Collecting hardware fingerprints...");
    let fingerprint = hardware::collect_all_fingerprints()?;
    
    // Validate fingerprints
    if !fingerprint.all_valid {
        warn!("⚠️  Some hardware checks failed: {}/{} passed", 
              fingerprint.checks_passed, fingerprint.checks_total);
    } else {
        info!("✅ All {} hardware checks passed", fingerprint.checks_total);
    }
    
    // Create attestation
    let attestation = attestation::Attestation::new(&keypair, &fingerprint)?;
    info!("✅ Attestation created");
    
    // Submit to network (if enabled)
    if config.submit_attestation {
        info!("📡 Submitting attestation...");
        match attestation::submit_attestation(&attestation, &config.node_url).await {
            Ok(response) => {
                info!("✅ Attestation submitted: {:?}", response);
            }
            Err(e) => {
                error!("❌ Failed to submit attestation: {}", e);
            }
        }
    }
    
    // Start mining loop
    info!("🚀 Starting mining loop...");
    loop {
        // Perform mining work
        let work_result = hardware::perform_mining_work(&fingerprint)?;
        
        // Submit work
        if config.submit_attestation {
            match attestation::submit_work(&work_result, &keypair, &config.node_url).await {
                Ok(_) => info!("✅ Work submitted"),
                Err(e) => error!("❌ Work submission failed: {}", e),
            }
        }
        
        // Wait for next epoch
        sleep(Duration::from_secs(config.epoch_duration)).await;
    }
}
