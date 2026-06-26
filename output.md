// rustchain/src/utxo/domain_signature.rs

use crate::config::MAX_INPUTS;
use crate::crypto::{
    has_domain_payload, inject_domain, verify_signature, Signature, SignatureAlgorithm,
    VerificationError,
};
use crate::error::Error;
use crate::types::{Address, Amount};
use log::{debug, error, warn};
use serde::{Deserialize, Serialize};
use std::collections::HashSet;
use thiserror::Error;

// ---------------------------------------------------------------------------
// Module documentation
// ---------------------------------------------------------------------------

/// Domain‑separated signature verification for UTXO transfers.
///
/// This module enforces that all UTXO transfer signatures include a domain
/// string (`UTXO_SIGNATURE_DOMAIN`) in the signed payload.  Any legacy
/// account‑model signature (without domain) is rejected with a dedicated
/// error code.  This prevents cross‑endpoint signature reuse attacks.
///
/// # Security
/// - Domain injection is mandatory; legacy signatures are always rejected.
/// - Payload size is bounded by `MAX_INPUTS`.
/// - All external inputs are validated before verification.

// ---------------------------------------------------------------------------
// Constants
// ---------------------------------------------------------------------------

/// Domain string injected into every signed UTXO transfer payload.
pub const UTXO_SIGNATURE_DOMAIN: &str = "rustchain-utxo-transfer-v1";

/// Error code returned when a legacy (non‑domain) signature is used on a UTXO endpoint.
pub const UTXO_SIGNATURE_DOMAIN_REQUIRED: &str = "UTXO_SIGNATURE_DOMAIN_REQUIRED";

// ---------------------------------------------------------------------------
// Errors
// ---------------------------------------------------------------------------

/// Errors that can occur during domain‑separated signature verification.
#[derive(Error, Debug)]
#[non_exhaustive]
pub enum DomainSignatureError {
    /// A legacy (account‑model) signature was used on a UTXO endpoint.
    #[error("legacy account‑model signature detected; domain required for UTXO")]
    LegacyWalletSignature,

    /// Underlying cryptographic verification failure.
    #[error("signature verification failed: {0}")]
    VerificationFailed(#[from] VerificationError),

    /// Invalid or malformed payload (e.g. empty signature list, too many inputs).
    #[error("invalid payload: {0}")]
    InvalidPayload(String),

    /// Internal serialisation or other non‑recoverable error.
    #[error("internal error: {0}")]
    Internal(String),
}

impl From<DomainSignatureError> for Error {
    fn from(e: DomainSignatureError) -> Self {
        // Convert to a generic signature error; keep the full message.
        Error::Signature(e.to_string())
    }
}

// ---------------------------------------------------------------------------
// Payload wrapper
// ---------------------------------------------------------------------------

/// A signed UTXO transfer payload that includes the mandatory domain string.
///
/// Serialisation uses `bincode` for compactness.
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct DomainSignedPayload {
    /// Domain string (must equal `UTXO_SIGNATURE_DOMAIN`).
    pub domain: String,
    /// Recipient address.
    pub to: Address,
    /// Transfer amount.
    pub amount: Amount,
    /// Optional fee (skipped from serialisation when `None`).
    #[serde(skip_serializing_if = "Option::is_none")]
    pub fee: Option<Amount>,
    /// Nonce to prevent replay.
    pub nonce: u64,
}

impl DomainSignedPayload {
    /// Create a new payload with the correct domain.
    ///
    /// # Arguments
    /// * `to`   – Recipient address.
    /// * `amount` – Transfer amount.
    /// * `fee`    – Optional fee.
    /// * `nonce`  – Unique nonce.
    #[must_use]
    pub fn new(to: Address, amount: Amount, fee: Option<Amount>, nonce: u64) -> Self {
        Self {
            domain: UTXO_SIGNATURE_DOMAIN.to_string(),
            to,
            amount,
            fee,
            nonce,
        }
    }
}

// ---------------------------------------------------------------------------
// Signature verifier
// ---------------------------------------------------------------------------

/// Verifies UTXO transfer signatures with domain separation.
///
/// The verifier maintains a flag (`legacy_wallet_signature_seen`) and a list
/// of legacy errors from the most recent call to [`verify_signatures`].
///
/// # Thread safety
/// Instances are **not** `Sync`; create a new verifier per transaction.
pub struct UtxoSignatureVerifier {
    algorithm: SignatureAlgorithm,
    max_inputs: usize