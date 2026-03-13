//! Configuration Module

use anyhow::{Result, anyhow};
use serde::{Serialize, Deserialize};
use std::fs;
use std::path::Path;

/// Miner configuration
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    /// Path to Ed25519 key file
    pub key_path: String,
    
    /// Node URL for attestation submission
    pub node_url: String,
    
    /// Whether to submit attestations
    pub submit_attestation: bool,
    
    /// Epoch duration in seconds
    pub epoch_duration: u64,
    
    /// Log level
    pub log_level: String,
    
    /// Hardware fingerprint cache path
    pub cache_path: String,
}

impl Default for Config {
    fn default() -> Self {
        Config {
            key_path: "~/.rustchain/miner_key.bin".to_string(),
            node_url: "http://localhost:8080".to_string(),
            submit_attestation: true,
            epoch_duration: 300, // 5 minutes
            log_level: "info".to_string(),
            cache_path: "~/.rustchain/cache".to_string(),
        }
    }
}

impl Config {
    /// Load configuration from file or create default
    pub fn load() -> Result<Self> {
        let config_path = std::env::var("RUSTCHAIN_CONFIG")
            .unwrap_or_else(|_| "~/.rustchain/config.toml".to_string());
        
        let expanded_path = expand_tilde(&config_path);
        let path = Path::new(&expanded_path);
        
        if path.exists() {
            // Load from TOML file
            let content = fs::read_to_string(path)
                .map_err(|e| anyhow!("Failed to read config file: {}", e))?;
            
            let config: Config = toml::from_str(&content)
                .map_err(|e| anyhow!("Failed to parse config: {}", e))?;
            
            Ok(config)
        } else {
            // Create default config
            let config = Config::default();
            
            // Create directory
            if let Some(parent) = path.parent() {
                fs::create_dir_all(parent)?;
            }
            
            // Save default config
            let toml_content = toml::to_string_pretty(&config)
                .map_err(|e| anyhow!("Failed to serialize config: {}", e))?;
            
            fs::write(path, toml_content)?;
            
            log::info!("Created default config at {}", expanded_path);
            
            Ok(config)
        }
    }
    
    /// Save configuration to file
    pub fn save(&self) -> Result<()> {
        let config_path = std::env::var("RUSTCHAIN_CONFIG")
            .unwrap_or_else(|_| "~/.rustchain/config.toml".to_string());
        
        let expanded_path = expand_tilde(&config_path);
        let path = Path::new(&expanded_path);
        
        if let Some(parent) = path.parent() {
            fs::create_dir_all(parent)?;
        }
        
        let toml_content = toml::to_string_pretty(self)
            .map_err(|e| anyhow!("Failed to serialize config: {}", e))?;
        
        fs::write(path, toml_content)?;
        
        Ok(())
    }
}

/// Expand tilde in path
fn expand_tilde(path: &str) -> String {
    if path.starts_with('~') {
        if let Some(home) = dirs::home_dir() {
            return home.join(&path[2..]).to_string_lossy().to_string();
        }
    }
    path.to_string()
}

// Re-export toml and dirs
pub use toml;
pub use dirs;
