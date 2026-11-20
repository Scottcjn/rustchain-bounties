# Self-Audit: node/claims_submission.py

## Wallet
RTC4642c5ee8467f61ed91b5775b0eeba984dd776ba

## Module reviewed
- Path: node/claims_submission.py
- Commit: 7f1116642808
- Lines reviewed: whole-file (705 lines)

## Deliverable: 3 specific findings

1. **`skip_signature_verify` bypasses all cryptographic claim authentication**
   - Severity: critical
   - Location: claims_submission.py:309-310, 375-376
   - Description: The `submit_claim()` function exposes a `skip_signature_verify: bool = False` parameter. When set to `True`, the entire Ed25519 signature verification is skipped, allowing any caller to submit fraudulent reward claims without possessing the miner's private key. Although default is `False`, this is a public API — any integration that passes `True` (intentionally or via misconfiguration) completely undermines the claim authentication model.
   - Reproduction: Call `submit_claim(..., skip_signature_verify=True)` with any arbitrary `miner_id`, `epoch`, and `wallet_address` — the claim will be accepted and persisted to the database without any signature check. The test code in `__main__` (line 670) demonstrates exactly this pattern with mock signatures.

2. **No wallet address ownership verification — rewards can be redirected**
   - Severity: high
   - Location: claims_submission.py:99-108, 340-365
   - Description: `validate_wallet_address_format()` only checks that the address matches the `RTC[a-zA-Z0-9]{20,40}` regex pattern. There is no binding check between the `miner_id` and `wallet_address` — a submitter can provide any valid-format wallet address and redirect rewards away from the legitimate miner's wallet. The miner identity is verified via signature, but the destination wallet is never cross-referenced against the miner's registered wallet in `miner_attest_recent`.
   - Reproduction: Call `submit_claim()` with a valid `miner_id` that has a registered wallet in the database, but supply a different `wallet_address` controlled by the attacker. If the attacker possesses the miner's signing key (or uses `skip_signature_verify`), the claim succeeds and rewards are sent to the attacker's wallet.

3. **No timestamp freshness validation enables indefinite claim replay**
   - Severity: high
   - Location: claims_submission.py:115-127, 338-350
   - Description: The `create_claim_payload()` function includes a `timestamp` field in the signed payload, but the code never validates that this timestamp is recent or within an acceptable window. An attacker who captures a valid signed claim payload can replay it indefinitely. Additionally, the `submit_claim()` function uses `current_ts` (the caller-supplied timestamp) rather than deriving it internally, so the caller controls the timestamp value in both the signature and the database record.
   - Reproduction: (1) Capture a legitimately signed claim payload with its timestamp. (2) Re-submit the exact same payload/signature at any future time — the claim will pass signature verification since the payload hasn't changed. (3) The only protection is the `UNIQUE(miner_id, epoch)` constraint, which prevents duplicate claims for the same epoch but does not prevent replay across different epochs if the attacker controls the epoch parameter.

## Known failures of this audit
- Did not analyze `claims_eligibility.py` — the `check_claim_eligibility()` function is called but not present in this file; its logic (reward calculation, slot validation) could contain additional vulnerabilities
- Did not perform dynamic testing or fuzzing — all analysis is static/code-reading only
- Did not review the `claims_settlement.py` or `claims_audit` table handling for post-submission attack vectors (e.g., status manipulation via `update_claim_status`)
- Low confidence on whether `skip_signature_verify` is ever exposed via HTTP/REST endpoints vs. only used in tests — if exposed via an API route, severity escalates to critical exploitable
- Did not check whether the `nacl` import failure path (HAVE_NACL=False) can be triggered in production deployments, which would reject all claims (DoS vector)

## Confidence
- Overall confidence: 0.75
- Per-finding confidence: [0.90, 0.80, 0.70]

## What I would test next
- Audit `claims_eligibility.py` to determine if `reward_urtc` can be inflated by manipulating `entropy_score` or `warthog_bonus` in `miner_attest_recent`
- Trace all HTTP route handlers that call `submit_claim()` to determine if `skip_signature_verify` is ever user-controllable via API parameter
- Test whether the `UNIQUE(miner_id, epoch)` constraint combined with the claim ID format `claim_{epoch}_{miner_id}` allows collision-based claim overwriting
