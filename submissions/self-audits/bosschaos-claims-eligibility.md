# Self-Audit: node/claims_eligibility.py

## Wallet
4TRdrSRZvShfgxhiXjBDFaaySzbK2rH3VijoTBGWpEcL

## Module reviewed
- Path: `node/claims_eligibility.py`
- Commit: `2cf9640`
- Lines reviewed: 1–737 (whole file)

## Deliverable: 3 specific findings

### 1. `check_pending_claim()` only checks non-final statuses — allows duplicate settled claims
- Severity: **high**
- Location: `node/claims_eligibility.py:280–311`
- Description: The `check_pending_claim()` function queries for claims with status `IN ('pending', 'verifying', 'approved')`. This means if a claim has already been settled (`status = 'settled'`), the function returns `False` (no pending claim). The caller `check_claim_eligibility()` then proceeds to approve another claim for the same miner/epoch combination. While `get_eligible_epochs()` (line 618–627) checks for settled claims separately, that function is only used for listing — not as a gate in the eligibility check itself. This creates a race window where a miner could submit two claims for the same epoch if the first one transitions from `approved` to `settled` between checks.
- Reproduction: Insert a claim with `status = 'settled'` into the `claims` table for `miner_id = "test-miner-g4"`, `epoch = 1`. Call `check_claim_eligibility()` for the same miner/epoch — it will return `eligible: True` with `no_pending_claim: True`, allowing a second claim to be submitted.

### 2. `get_eligible_epochs()` incorrectly marks failed epochs as "claimed" — hides unclaimable epochs from miners
- Severity: **medium**
- Location: `node/claims_eligibility.py:614–615`
- Description: The `claimed` flag is set with the logic:
  ```python
  claimed = not eligibility["checks"]["no_pending_claim"] or \
            (eligibility["checks"]["no_pending_claim"] and not eligibility["eligible"])
  ```
  This means if a miner is ineligible for any reason (wallet not registered, fingerprint failed, epoch not settled), the epoch is marked as `claimed: True`. This is misleading — the miner never actually claimed the reward; they were simply blocked from claiming it. The epoch disappears from the "unclaimed" list (`total_unclaimed_urtc` only counts epochs where `not claimed and eligibility["eligible"]`), so miners cannot see which epochs they failed to claim and why. This reduces transparency and makes debugging eligibility failures difficult.
- Reproduction: Create a miner with no wallet address. Call `get_eligible_epochs()` — epochs where the miner participated will show `claimed: True` and will not appear in `total_unclaimed_urtc`, even though no reward was ever issued.

### 3. `fingerprint_passed` defaults to `1` (pass) when column is missing — silently bypasses hardware validation
- Severity: **medium**
- Location: `node/claims_eligibility.py:162, 220`
- Description: In both `get_miner_attestation()` and `check_epoch_participation()`, the `fingerprint_passed` field defaults to `1` if the column doesn't exist in the database schema:
  ```python
  "fingerprint_passed": row["fingerprint_passed"] if "fingerprint_passed" in row.keys() else 1
  ```
  This means a miner running against a database schema that lacks the `fingerprint_passed` column will always pass the fingerprint check. An attacker who controls the database or runs a node with an older schema could bypass hardware fingerprint validation entirely. The same default applies to `entropy_score` (defaults to `0.0`), which masks missing entropy data.
- Reproduction: Create a `miner_attest_recent` table without the `fingerprint_passed` column (matching an older schema). Insert attestation data. Call `check_claim_eligibility()` — it will pass the fingerprint check even though no fingerprint validation was performed.

## Known failures of this audit
- I did **not** run the `__main__` test block against an actual SQLite database with realistic attestation data. My analysis is static — I traced the logic flow but did not execute the code end-to-end.
- I did **not** review the imported modules (`rip_200_round_robin_1cpu1vote`, `fleet_immune_system`, `rewards_implementation_rip200`) that `claims_eligibility.py` depends on. The correctness of `calculate_epoch_reward()` and `get_time_aged_multiplier()` is assumed.
- I did **not** analyze SQL injection risk beyond noting that all queries use parameterized `?` placeholders. The `db_path` parameter is not sanitized — a malicious caller could pass a path like `/etc/passwd` which SQLite would create as a new database, though this is more of a caller-side responsibility.
- I did **not** evaluate the cryptographic properties of the reward calculation or the time-aged multiplier logic — those are RIP-200 concerns, not claims eligibility concerns.

## Confidence
- Overall confidence: 0.85
- Per-finding confidence:
  - Finding 1 (duplicate settled claims): 0.92
  - Finding 2 (claimed flag mislabeling): 0.88
  - Finding 3 (fingerprint default bypass): 0.90

## What I would test next
- Create a test database with both `pending` and `settled` claims for the same miner/epoch to verify whether `check_claim_eligibility()` actually allows double-claiming through the settled path.
- Patch the `claimed` logic in `get_eligible_epochs()` to distinguish between `claimed: True`, `ineligible: True`, and `unclaimed: True`, then verify miners can see why they couldn't claim.
- Test `check_claim_eligibility()` against a schema missing `fingerprint_passed` and `entropy_score` columns to confirm the silent bypass, then add an explicit schema version check.
