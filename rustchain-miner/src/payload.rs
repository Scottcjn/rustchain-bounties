//! Attestation payload construction.
//!
//! Builds the JSON payload matching the RustChain attestation schema.

use crate::fingerprint::FingerprintResult;
use crate::hardware::HardwareInfo;
use rand::RngCore;

/// Build the attestation payload as a serde_json::Value.
///
/// The wallet parameter is the Ed25519 public key (RTC address) that identifies the miner
/// and receives rewards. This is included in the payload sent to POST /attest/submit.
///
/// This matches the exact schema required by the RustChain attestation endpoint.
pub fn build_payload(
    wallet: &str,
    nonce: &str,
    hw: &HardwareInfo,
    fp: &FingerprintResult,
) -> serde_json::Value {
    // Convert fingerprint checks to the expected nested format
    let mut checks = serde_json::Map::new();
    for (name, result) in &fp.checks {
        checks.insert(
            name.clone(),
            serde_json::json!({
                "passed": result.passed,
                "data": result.data,
            }),
        );
    }

    serde_json::json!({
        "miner": wallet,  // RTC wallet address (Ed25519 public key)
        "miner_id": wallet,  // Unique identifier for this mining node
        "nonce": nonce,
        "report": {
            "cpu_model": hw.cpu_model,
            "cpu_cores": hw.cpu_cores,
            "ram_gb": hw.ram_gb,
            "os": hw.os,
        },
        "device": {
            "device_family": hw.device_family,
            "device_arch": hw.device_arch,
            "device_model": hw.device_model,
        },
        "signals": {
            "macs": hw.macs,
            "uptime": hw.uptime,
        },
        "fingerprint": {
            "all_passed": fp.all_passed,
            "checks": checks,
        },
    })
}

/// Generate a random 32-character hex nonce for local testing.
/// In production, the nonce is obtained from the RustChain server via GET /attest/challenge.
/// This function is only used in test-only and dry-run modes.
pub fn generate_local_nonce() -> String {
    let mut bytes = [0u8; 16];
    rand::thread_rng().fill_bytes(&mut bytes);
    hex::encode(bytes)  // Convert 16 random bytes to 32-char hex string
}
