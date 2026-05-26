# Self-Audit: node/claims_eligibility.py

## Wallet
RTC99e36a40635b8527979fd1c4e6280fdfa176e715

## Module reviewed
- Path: node/claims_eligibility.py
- Commit: 35b89c87
- Lines reviewed: 1-490 (whole file)

## Deliverable: 3 specific findings

### 1. TOCTOU race condition in claim eligibility → submission gap
- Severity: high
- Location: claims_eligibility.py:323-329 (check_pending_claim) and its caller
- Description: `check_pending_claim()` verifies no duplicate claim exists, but the caller is expected to insert the claim afterward. Between the check and the insert, a concurrent process can submit the same claim, bypassing duplicate prevention. No transaction or advisory lock wraps the check-then-insert sequence.
- Reproduction:
  1. Open two connections to the same node.db
  2. Connection A: call `check_claim_eligibility()` → returns `eligible: true`, `no_pending_claim: true`
  3. Connection B: call `check_claim_eligibility()` → also returns `eligible: true` (A hasn't inserted yet)
  4. Both A and B proceed to insert claims for the same miner/epoch
  5. If the claims table lacks a UNIQUE(miner_id, epoch) constraint, both inserts succeed → double payout

### 2. Silently swallowed OperationalError masks schema drift in get_wallet_address
- Severity: medium
- Location: claims_eligibility.py:194-218 (get_wallet_address, both try/except blocks)
- Description: Both the `miner_wallets` table check and the `miner_attest_recent` fallback catch `sqlite3.OperationalError` and silently return `None`. This means if the schema changes (e.g., column renamed from `wallet_address` to `payout_address`), wallet addresses silently become "not found" for all miners. No warning is logged — the function degrades to always returning `None`, which in turn makes `check_claim_eligibility()` reject all claims with `wallet_not_registered`. This is a silent catastrophic degradation that could halt all bounty payouts without any error surfaced to operators.
- Reproduction:
  1. Run a migration that renames `wallet_address` to `payout_address` in `miner_wallets`
  2. Call `get_wallet_address(db_path, "any-valid-miner")`
  3. Function returns `None` with no error logged
  4. `check_claim_eligibility()` fails with `wallet_not_registered`
  5. Check logs: no schema error appears — only "not registered" results

### 3. calculate_epoch_reward fallback performs duplicate COUNT query on import failure
- Severity: low
- Location: claims_eligibility.py:279-293 (calculate_epoch_reward, except block)
- Description: When `calculate_epoch_rewards_time_aged` import fails, the fallback opens a new database connection and runs `SELECT COUNT(DISTINCT miner) FROM miner_attest_recent`. This duplicates the connection pattern — the caller already has access patterns established. More critically, the fallback connection is opened without `conn.row_factory = sqlite3.Row` (unlike `get_miner_attestation`), so `cursor.fetchone()[0]` indexing may return a tuple that behaves unexpectedly if the schema has fewer columns than expected. Additionally, if `miner_count` is 0 (no miners in the epoch window), `PER_EPOCH_URTC // max(1, miner_count)` distributes the full epoch reward to a single miner — this is inconsistent with the primary path which would distribute among actual miners.
- Reproduction:
  1. Set up an environment where `rewards_implementation_rip200` cannot be imported (e.g., deployment path issue)
  2. Call `calculate_epoch_reward` for an epoch with 0 attested miners
  3. Observe: miner_count = 0, max(1, 0) = 1, reward = PER_EPOCH_URTC // 1 = 150 RTC
  4. Compare: primary path would return 0 for a non-participating miner
  5. Result: a miner can claim full epoch rewards via the fallback path when they shouldn't receive anything

## Known failures of this audit
- I did not test against a live RustChain node database — all findings are from static analysis. The `epoch_enroll` table structure was inferred from the query, but the actual schema may differ.
- I did not trace all callers of `check_claim_eligibility()` to verify whether any of them DO wrap the eligibility check + claim insert in a transaction. It's possible (but unlikely) that all callers already handle this.
- The fleet detection integration (RIP-0201) was not reviewed — `fleet_immune_system.py` may have its own vulnerabilities that compound with the TOCTOU finding.

## Confidence
- Overall confidence: 0.75
- Per-finding confidence: [0.85, 0.80, 0.60]

Finding 1 (TOCTOU) is high-confidence because the function signature and docstring explicitly describe it as a standalone check with no transaction requirement. Finding 2 (silent error swallowing) is high-confidence because the bare `except sqlite3.OperationalError: pass` is visible in the source. Finding 3 (fallback reward calculation) has lower confidence because it depends on whether `rewards_implementation_rip200` is reliably importable in production — if it always imports successfully, this code path is dead.

## What I would test next
- Write an integration test that spawns two concurrent `check_claim_eligibility` + claim insert sequences and verifies only one claim succeeds for the same (miner_id, epoch) pair.
- Run a schema migration test: rename `wallet_address` column → verify `get_wallet_address` logs a warning instead of silently returning None.
- Deploy the fallback path of `calculate_epoch_reward` against a test database with 0 attested miners → verify reward is 0, not PER_EPOCH_URTC.
