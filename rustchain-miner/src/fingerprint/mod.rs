pub mod clock_drift;
pub mod cache_timing;
pub mod simd_identity;
pub mod thermal_drift;
pub mod instruction_jitter;
pub mod anti_emulation;
pub mod crt_light_attestation;

use serde::Serialize;
use std::collections::HashMap;

/// Result of a single fingerprint check.
#[derive(Debug, Clone, Serialize)]
pub struct CheckResult {
    pub passed: bool,
    pub data: serde_json::Value,
}

/// Aggregate result of all 7 fingerprint checks.
#[derive(Debug, Clone, Serialize)]
pub struct FingerprintResult {
    pub all_passed: bool,
    pub checks: HashMap<String, CheckResult>,
}

/// Run all 7 RIP-PoA fingerprint checks and return the aggregate result.
pub fn run_all_checks() -> FingerprintResult {
    let mut checks = HashMap::new();

    log::info!("Running fingerprint check 1/7: Clock-Skew & Oscillator Drift");
    checks.insert("clock_drift".to_string(), clock_drift::run());

    log::info!("Running fingerprint check 2/7: Cache Timing Fingerprint");
    checks.insert("cache_timing".to_string(), cache_timing::run());

    log::info!("Running fingerprint check 3/7: SIMD Unit Identity");
    checks.insert("simd_identity".to_string(), simd_identity::run());

    log::info!("Running fingerprint check 4/7: Thermal Drift Entropy");
    checks.insert("thermal_drift".to_string(), thermal_drift::run());

    log::info!("Running fingerprint check 5/7: Instruction Path Jitter");
    checks.insert("instruction_jitter".to_string(), instruction_jitter::run());

    log::info!("Running fingerprint check 6/7: Anti-Emulation / VM Detection");
    checks.insert("anti_emulation".to_string(), anti_emulation::run());

    log::info!("Running fingerprint check 7/7: CRT Light Attestation");
    checks.insert("crt_light_attestation".to_string(), crt_light_attestation::run());

    let all_passed = checks.values().all(|c| c.passed);

    FingerprintResult { all_passed, checks }
}
