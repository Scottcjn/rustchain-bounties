//! RustChain Miner - Native Rust Implementation
//! 
//! Features:
//! - 7 hardware fingerprint checks
//! - Ed25519 attestation
//! - Cross-platform support (Windows, macOS, Linux)

mod hardware;
mod fingerprint;
mod attestation;
mod config;
mod network;

use anyhow::Result;
use log::info;

#[tokio::main]
async fn main() -> Result<()> {
    env_logger::init();
    info!("RustChain Miner starting...");
    
    // Load configuration
    let config = config::load_config()?;
    
    // Generate hardware fingerprint
    let fingerprint = fingerprint::generate_fingerprint()?;
    info!("Hardware fingerprint: {}", fingerprint);
    
    // Initialize attestation
    let attestation = attestation::Attestation::new(&config)?;
    
    // Start mining loop
    network::run_miner(&config, &attestation, &fingerprint).await?;
    
    Ok(())
}
