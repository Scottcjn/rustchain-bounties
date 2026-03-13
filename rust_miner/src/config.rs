//! Configuration Module

use serde::{Deserialize, Serialize};
use std::path::Path;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Config {
    pub rpc_endpoint: String,
    pub miner_id: String,
    pub private_key: Option<String>,
    pub interval_seconds: u64,
}

impl Default for Config {
    fn default() -> Self {
        Self {
            rpc_endpoint: "https://rustchain.org/api".to_string(),
            miner_id: String::new(),
            private_key: None,
            interval_seconds: 60,
        }
    }
}

pub fn load_config() -> anyhow::Result<Config> {
    // Try to load from config file, otherwise use defaults
    let config_path = "config.toml";
    if Path::new(config_path).exists() {
        let content = std::fs::read_to_string(config_path)?;
        let config: Config = toml::from_str(&content)?;
        Ok(config)
    } else {
        Ok(Config::default())
    }
}
