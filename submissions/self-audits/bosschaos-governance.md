# Self-Audit: node/governance.py

## Wallet
RTC019e78d600fb3131c29d7ba80aba8fe644be426e

## Module reviewed
- Path: `node/governance.py`
- Commit: `4fb234f`
- Lines reviewed: 1-614 (whole file)

## Deliverable: 3 specific findings

### 1. Inconsistent quorum denominator within a single vote transaction
- Severity: **high**
- Location: `node/governance.py:483`
- Description: In `cast_vote()`, after updating the vote tally inside a `sqlite3.connect()` transaction, `_count_active_miners(db_path)` is called at line 483 to determine quorum. This opens a **separate** database connection with its own `time.time()` cutoff, so the active miner count can differ from the one implicitly used in `_settle_expired_proposals()` called at line 402 at the top of the handler. A proposal can be marked `quorum_met=1` with one snapshot of active miners, while the settlement logic used a different snapshot to decide if the proposal should transition to `expired`. This means quorum decisions are non-atomic and can flip depending on timing between the two independent DB connections.
- Reproduction:
  1. Create a proposal and start voting on it from multiple miners.
  2. Just before casting a vote that should trigger quorum, have the active-miner set change (e.g., a miner's last attestation falls just outside the 48h cutoff).
  3. `cast_vote()` calls `_count_active_miners` at line 483 with a fresh `time.time()` inside a new connection, yielding a different denominator than the `_settle_expired_proposals` call at line 402.
  4. Observe `quorum_met` set to 1 while `_settle_expired_proposals` would have classified the same proposal differently.

### 2. No rate limiting on founder veto endpoint enables admin_key brute force
- Severity: **high**
- Location: `node/governance.py:544-581`
- Description: The `founder_veto()` endpoint at `/api/governance/veto/<int:proposal_id>` authenticates via `RUSTCHAIN_ADMIN_KEY` environment variable compared with a plain string equality check (line 556). There is **no rate limiting**, no exponential backoff, no account lockout, and no logging of failed attempts beyond a generic error response. An attacker can send unlimited `POST` requests with different `admin_key` values. If the admin key has low entropy (e.g., a short hex string), it is susceptible to online brute-force attack. Unlike `create_proposal` and `cast_vote`, which use ed25519 signatures with timestamps (rate-limited by the 5-minute signature window), the veto endpoint has no analogous protection.
- Reproduction:
  1. Send repeated `POST /api/governance/veto/1` requests with incrementing `admin_key` values.
  2. No HTTP 429 (Too Many Requests) is returned — only 403 with `{"error": "invalid admin_key"}`.
  3. If `RUSTCHAIN_ADMIN_KEY` is guessable, an attacker can veto any active proposal and set its status to `vetoed`.

### 3. `_sophia_evaluate` is deterministic keyword-matching mislabeled as "AI Evaluation"
- Severity: **medium**
- Location: `node/governance.py:226-252`
- Description: The `_sophia_evaluate()` function (lines 226-252) is labeled as "**Sophia AI Evaluation** (auto-generated, non-binding)" but performs purely deterministic keyword matching with zero ML/AI logic. It checks for risk words like "emergency", "halt", "freeze" in the title/description and classifies as HIGH/LOW risk. This creates a false sense of analytical depth — voters may trust the "AI evaluation" as independent analysis when it is actually trivially gameable: an attacker can include or exclude specific keywords to manipulate the risk level. For example, an emergency proposal that says "we must NOT halt the chain" would trigger the "halt" keyword and be rated HIGH risk despite not actually proposing a halt.
- Reproduction:
  1. Create a proposal with title: "We must not freeze any assets"
  2. `_sophia_evaluate` returns risk_level = "HIGH" because "freeze" is in `risk_words`, even though the proposal is the opposite of a freeze.
  3. Create a genuinely dangerous proposal that avoids all 6 risk keywords — it gets rated "LOW".

## Known failures of this audit
- I did **not** test the Flask blueprint live — no requests were sent against a running server, so runtime behavior (Flask error handling, middleware interactions) is unverified.
- I did **not** check the callers of `create_governance_blueprint()` to see if rate-limiting middleware or authentication wrappers are applied at a higher level (e.g., in `node/main.py` or via a reverse proxy like nginx).
- I did **not** verify whether `_verify_miner_signature`'s ed25519 implementation uses a constant-time comparison or is vulnerable to timing attacks.
- I did **not** check the `_is_active_miner` function's interaction with the broader attestation system — whether the `attestations` table schema matches what this query expects.
- I did **not** review the `rips/python/rustchain/governance.py` file (a separate governance module) — only `node/governance.py` was audited.

## Confidence
- Overall confidence: 0.82
- Per-finding confidence:
  - Finding 1 (inconsistent quorum): 0.90 — clear separate-DB-connection pattern
  - Finding 2 (veto brute force): 0.85 — no rate limiting is visible; actual risk depends on admin key entropy and network exposure
  - Finding 3 (sophia deterministic): 0.95 — code is trivially auditable, keyword list is explicit

## What I would test next
- Spin up a test Flask instance with an in-memory SQLite DB and fire concurrent `POST /api/governance/vote` requests to verify the quorum inconsistency race.
- Run `hydra` or a simple Python script against `/api/governance/veto/1` to measure requests-per-second and estimate time-to-compromise for various `RUSTCHAIN_ADMIN_KEY` entropy levels.
- Check `node/main.py` for any `before_request` rate-limiting or authentication middleware that might mitigate findings 2 and 3.
