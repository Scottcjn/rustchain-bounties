use axum::{extract::State, Json, http::StatusCode};
use serde::Deserialize;
use chrono::Utc;
use sqlx::{PgPool, Postgres, query};
use std::sync::Arc;

#[derive(Clone)]
pub struct AppState {
    pub db: PgPool,
    pub current_epoch: Arc<std::sync::atomic::AtomicU64>,
}

#[derive(Deserialize)]
pub struct AttestRequest {
    pub pubkey: String,
    pub signature: String,
    pub hardware_fingerprint: String,
    pub timestamp: i64,
    pub nonce: String,
    pub epoch: u64,
}

#[derive(serde::Serialize)]
pub struct AttestResponse {
    pub ok: bool,
    pub message: String,
}

const TIMESTAMP_TOLERANCE_SECS: i64 = 300;

pub async fn submit_attestation(
    State(state): State<AppState>,
    Json(payload): Json<AttestRequest>,
) -> Result<Json<AttestResponse>, StatusCode> {
    // 1. Epoch validation - prevent future epoch submission
    let current_epoch = state.current_epoch.load(std::sync::atomic::Ordering::Relaxed);
    if payload.epoch != current_epoch && payload.epoch != current_epoch.saturating_sub(1) {
        return Ok(Json(AttestResponse {
            ok: false,
            message: "Invalid epoch".into(),
        }));
    }

    // 2. Timestamp freshness - prevent replay
    let now = Utc::now().timestamp();
    if (now - payload.timestamp).abs() > TIMESTAMP_TOLERANCE_SECS {
        return Ok(Json(AttestResponse {
            ok: false,
            message: "Timestamp outside tolerance".into(),
        }));
    }

    // 3. Basic input validation
    if payload.pubkey.len() != 64 || payload.nonce.is_empty() || payload.hardware_fingerprint.is_empty() {
        return Ok(Json(AttestResponse {
            ok: false,
            message: "Invalid payload".into(),
        }));
    }

    // 4. Signature verification placeholder - real implementation uses ed25519_dalek
    // verify_signature(&payload.pubkey, &payload.signature, &payload.hardware_fingerprint)?;

    // 5. Replay protection via unique nonce + hardware fingerprint + epoch
    let res = query!(
        r#"
        INSERT INTO attestations (pubkey, signature, hardware_fingerprint, timestamp, nonce, epoch, created_at)
        VALUES ($1, $2, $3, $4, $5, $6, NOW())
        ON CONFLICT (hardware_fingerprint, epoch, nonce) DO NOTHING
        "#,
        payload.pubkey,
        payload.signature,
        payload.hardware_fingerprint,
        payload.timestamp as i64,
        payload.nonce,
        payload.epoch as i64
    )
    .execute(&state.db)
    .await
    .map_err(|_| StatusCode::INTERNAL_SERVER_ERROR)?;

    if res.rows_affected() == 0 {
        return Ok(Json(AttestResponse {
            ok: false,
            message: "Duplicate attestation / replay detected".into(),
        }));
    }

    Ok(Json(AttestResponse {
        ok: true,
        message: "Attestation accepted".into(),
    }))
}
