//! Attestation payload construction.
//!
//! Builds the JSON payload matching the RustChain attestation schema.

use crate::fingerprint::FingerprintResult;
use crate::hardware::HardwareInfo;
use rand::RngCore;

/// Build the attestation payload as a serde_json::Value.
///
/// This matches the exact schema required by POST /attest/submit.
pub fn build_payload(
    wallet: &str,
    nonce: &str,
pub fn build_payload(
    wallet: &str,
    nonce: &str,
    hw: &HardwareInfo,
    fp: &FingerprintResult,
) -> Result<serde_json::Value, String> {
    if wallet.is_empty() || nonce.is_empty() {
        return Err("Wallet or nonce cannot be empty".to_string());
    }
    if wallet.len() > 64 || nonce.len() > 32 {
        return Err("Wallet or nonce exceeds maximum length");
    }
    if hw.cpu_model.is_empty() || hw.os.is_empty() || hw.cpu_cores == 0 || hw.ram_gb == 0 {
        return Err("Hardware info is incomplete".to_string());
    }
    if hw.cpu_model.len() > 128 || hw.os.len() > 128 {
        return Err("Hardware info exceeds maximum length");
    }
    if fp.checks.is_empty() {
        return Err("Fingerprint checks are empty".to_string());
    }
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
    let payload = serde_json::json!({
        "miner": wallet,
        "miner_id": wallet,
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
    });
    Ok(payload)
}
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

/// Generate a random 32-character hex nonce (used as fallback if server nonce is unavailable).
pub fn generate_local_nonce() -> String {
    let mut bytes = [0u8; 16];
    rand::thread_rng().fill_bytes(&mut bytes);
    hex::encode(bytes)
}
