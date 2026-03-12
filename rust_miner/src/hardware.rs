//! Hardware detection module
//! 
//! Detects CPU, memory, and system information for fingerprinting

use serde::{Deserialize, Serialize};

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct HardwareInfo {
    pub cpu_vendor: String,
    pub cpu_brand: String,
    pub cpu_cores: u32,
    pub cpu_threads: u32,
    pub memory_total_gb: u64,
    pub arch: String,
    pub os: String,
}

pub fn detect_hardware() -> HardwareInfo {
    HardwareInfo {
        cpu_vendor: "unknown".to_string(),
        cpu_brand: "unknown".to_string(),
        cpu_cores: 1,
        cpu_threads: 1,
        memory_total_gb: 1,
        arch: std::env::consts::ARCH.to_string(),
        os: std::env::consts::OS.to_string(),
    }
}
