# Self-Audit: node/payout_preflight.py

**Bounty**: #6460 - 10 RTC
**Auditor**: tianheng
**Wallet**: TVBiBzF3ZiK4oTkqZkDAtwYMKUCL7qpBVZ

## Module Reviewed

| Field | Value |
|-------|-------|
| Path | node/payout_preflight.py |
| Repo | Scottcjn/Rustchain |
| Commit | 06a057b03cf2cc4e873478983c8bc3cd2b6a8d22 |
| Lines | 152 |
| Language | Python 3 |

## Finding 1: Floating-Point Quantization Silent Funds Loss (HIGH)

Lines: validate_wallet_transfer_admin + validate_wallet_transfer_signed

Code: amount_i64 = int(amount_rtc * 1_000_000)

_safe_float() parses as IEEE 754 binary64 float, then int(float * 1_000_000) truncates. Many decimal fractions lose precision:
- 0.02 RTC becomes 19999 uRTC (expected 20000)
- 0.07 RTC becomes 69999 uRTC (expected 70000)
- 0.29 RTC becomes 289999 uRTC (expected 290000)

Fix: int(round(amount_rtc * 1_000_000)) or switch to Decimal.

## Finding 2: Signature Field Checked But Never Verified (HIGH)

Location: validate_wallet_transfer_signed

signature and public_key are required fields but never cryptographically verified. The function only checks they exist (non-empty). A payload with signature = "AAAA" passes.

No Ed25519 verify call exists in this module.

Impact: If a caller trusts this function as sole validation, forged transactions pass.

Fix: Add Ed25519 signature verification over from_address || to_address || amount_rtc || nonce using public_key.

## Finding 3: Nonce Accepted But Not Persisted - Replay Vector (MEDIUM)

nonce_int > 0 is validated but no storage of used nonces. Same transaction replayed = same nonce re-accepted.

Combined with Finding 2, a captured valid transfer can be replayed indefinitely.

Fix: Track used nonces per-address in persistent storage. Key by (from_address, nonce).

## Summary

| Finding | Severity | Confidence |
|---------|----------|------------|
| F1: Float quantization | HIGH | 0.95 |
| F2: No sig verification | HIGH | 0.92 |
| F3: Nonce replay | MEDIUM | 0.88 |

Overall confidence: 0.90
