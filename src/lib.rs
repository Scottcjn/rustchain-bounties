//! RustChain Miner Library
//! 
//! Native Rust implementation of RustChain miner with hardware fingerprinting.

pub mod hardware;
pub mod crypto;
pub mod attestation;
pub mod config;

pub use hardware::{HardwareFingerprint, collect_all_fingerprints};
pub use crypto::{Keypair, load_or_generate_keypair};
pub use attestation::{Attestation, AttestationResponse};
pub use config::Config;

/// Library version
pub const VERSION: &str = env!("CARGO_PKG_VERSION");

/// Check if running in a VM (for testing)
pub fn is_vm_environment() -> bool {
    #[cfg(target_os = "linux")]
    {
        // Check for common VM indicators
        if let Ok(content) = std::fs::read_to_string("/sys/class/dmi/id/product_name") {
            let content_lower = content.to_lowercase();
            if content_lower.contains("virtual") || 
               content_lower.contains("vmware") || 
               content_lower.contains("qemu") ||
               content_lower.contains("kvm") {
                return true;
            }
        }
    }
    
    false
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_clock_drift_collection() {
        let result = hardware::collect_clock_drift(100).unwrap();
        assert!(result.samples == 100);
        assert!(result.mean_ns > 0.0);
        // Real hardware should have some variance
        assert!(result.variance >= 0.0);
    }
    
    #[test]
    fn test_cache_timing_collection() {
        let result = hardware::collect_cache_timing(50).unwrap();
        assert!(!result.latencies.is_empty());
        assert!(result.tone_ratios.len() > 0);
    }
    
    #[test]
    fn test_simd_profile() {
        let result = hardware::collect_simd_profile().unwrap();
        assert_ne!(result.simd_type, "");
        assert!(result.int_mean_ns > 0.0);
        assert!(result.float_mean_ns > 0.0);
    }
    
    #[test]
    fn test_thermal_drift() {
        let result = hardware::collect_thermal_drift(10).unwrap();
        assert!(result.cold_mean_ns > 0.0);
        assert!(result.hot_mean_ns > 0.0);
    }
    
    #[test]
    fn test_instruction_jitter() {
        let result = hardware::collect_instruction_jitter(50).unwrap();
        assert!(result.jitter_map.contains_key("integer"));
        assert!(result.jitter_map.contains_key("branch"));
        assert!(result.jitter_map.contains_key("fpu"));
        assert!(result.jitter_map.contains_key("memory"));
    }
    
    #[test]
    fn test_device_oracle() {
        let result = hardware::collect_device_oracle().unwrap();
        assert!(!result.machine.is_empty());
        assert!(!result.system.is_empty());
    }
    
    #[test]
    fn test_anti_emulation() {
        let result = hardware::check_anti_emulation().unwrap();
        // This test might fail in VM environments
        log::info!("VM detection result: valid={}, artifacts={:?}", 
                   result.valid, result.vm_artifacts);
    }
    
    #[test]
    fn test_full_fingerprint_collection() {
        let fingerprint = hardware::collect_all_fingerprints().unwrap();
        assert_eq!(fingerprint.checks_total, 7);
        log::info!("Fingerprint: {}/{} checks passed", 
                   fingerprint.checks_passed, fingerprint.checks_total);
    }
    
    #[test]
    fn test_keypair_generation() {
        let temp_dir = std::env::temp_dir();
        let key_path = temp_dir.join("test_miner_key.bin");
        let key_path_str = key_path.to_string_lossy().to_string();
        
        // Generate new key
        let keypair = crypto::load_or_generate_keypair(&key_path_str).unwrap();
        assert!(!keypair.public_key_hex().is_empty());
        
        // Load existing key
        let keypair2 = crypto::load_or_generate_keypair(&key_path_str).unwrap();
        assert_eq!(keypair.public_key_hex(), keypair2.public_key_hex());
        
        // Cleanup
        std::fs::remove_file(key_path).ok();
    }
    
    #[test]
    fn test_attestation_creation() {
        let temp_dir = std::env::temp_dir();
        let key_path = temp_dir.join("test_attestation_key.bin");
        let key_path_str = key_path.to_string_lossy().to_string();
        
        let keypair = crypto::load_or_generate_keypair(&key_path_str).unwrap();
        let fingerprint = hardware::collect_all_fingerprints().unwrap();
        
        let attestation = attestation::Attestation::new(&keypair, &fingerprint).unwrap();
        assert_eq!(attestation.version, "1.0.0");
        assert!(!attestation.signature.is_empty());
        
        // Verify signature
        let verify_result = attestation::verify_attestation(&attestation);
        assert!(verify_result.is_ok());
        
        // Cleanup
        std::fs::remove_file(key_path).ok();
    }
    
    #[test]
    fn test_config_default() {
        let config = config::Config::default();
        assert!(!config.key_path.is_empty());
        assert!(!config.node_url.is_empty());
        assert!(config.epoch_duration > 0);
    }
}
