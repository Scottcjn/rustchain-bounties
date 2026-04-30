# Self-Audit: `node/claims_eligibility.py`

## Wallet
4TRdrSRZvShfgxhiXjBDFaaySzbK2rH3VijoTBGWpEcL

## Module reviewed
- **Path:** `node/claims_eligibility.py`
- **Commit:** `ec72f36` (HEAD at time of review)
- **Lines reviewed:** 1–737
- **SHA:** `ec72f3618717e8e691b126e64687488d79cba6b6`

## Deliverable: 3 specific findings

### 1. `calculate_epoch_reward` silently catches ALL exceptions and returns 0
- **Severity:** HIGH
- **Location:** `node/claims_eligibility.py:340–376`
- **Description:** The function wraps the entire reward calculation in a broad `except Exception` at line 355. If `calculate_epoch_rewards_time_aged()` raises *any* error (database locked, missing module, bad math), execution falls through to a fallback that computes `PER_EPOCH_URTC // miner_count`. But the fallback *itself* is also wrapped in a second `except Exception` at line 375 which returns `0`. A legitimate miner with a valid attestation could therefore receive **0 reward** because an unrelated database lock occurred in the fallback branch, and the caller (`check_claim_eligibility`) has no way to distinguish "genuinely zero reward" from "reward computation crashed."
- **Reproduction:**
  ```python
  # Inject a broken database path
  result = calculate_epoch_reward("/nonexistent/db.sqlite3", "miner-1", 100, 20000)
  # Returns 0 silently instead of raising an error
  ```
- **Suggested fix:** Separate "could not calculate" from "calculated as zero." Return `None` on failure, or raise a dedicated `ClaimsEligibilityError` subclass. The caller can then mark the claim as "needs manual review" rather than silently underpaying.

### 2. `check_epoch_participation` query window extends BEFORE the epoch
- **Severity:** MEDIUM
- **Location:** `node/claims_eligibility.py:206–208`
- **Description:** The SQL query filters `ts_ok >= epoch_start_ts - ATTESTATION_TTL`. This means a miner who attested **24 hours before the epoch even started** is counted as having "participated" in that epoch. The docstring says the function checks "if miner was attested during the specified epoch," but the TTL buffer bleeds across epoch boundaries. On 10-minute block times, 24 hours = 144 epochs of bleed. A stale attestation from epoch N-144 could pay out for epoch N.
- **Reproduction:**
  ```python
  # epoch_start_ts = 1000, ATTESTATION_TTL = 86400
  # Query accepts ts_ok >= 1000 - 86400 = -85400
  # Any attestation in the last day counts for this epoch
  ```
- **Suggested fix:** Remove the `- ATTESTATION_TTL` offset in the epoch-participation query, or use a much smaller tolerance (e.g., one slot). The TTL check belongs in the *current* attestation validity check (`get_miner_attestation`), not in historical epoch participation.

### 3. `return rewards.get(miner_id, 0)` at line 354 uses `.get()` with default 0, masking missing miners
- **Severity:** MEDIUM
- **Location:** `node/claims_eligibility.py:354`
- **Description:** After calling `calculate_epoch_rewards_time_aged()`, which returns a dict mapping `miner_id → reward`, the code does `rewards.get(miner_id, 0)`. If the rewards calculation omitted a miner because of a transient DB error, the dict simply lacks the key and the miner gets 0 RTC instead of an error or audit flag. This interacts with Finding #1 (broad `except`) because two different failure paths both produce `0` with no logging.
- **Suggested fix:** Explicitly check membership: if `miner_id not in rewards`, log a warning or return `None`. Zero should only mean " miner was present but share rounded to zero," not "missing key."

## Known failures of this audit
- I did not review `calculate_epoch_rewards_time_aged()` itself (defined in `rewards_implementation_rip200.py`), which is the upstream dependency for Finding #1. Bugs there could make Finding #1 moot or worse.
- I did not check the RIP-0201 fleet-immune system integration in production; `HAVE_FLEET_IMMUNE` is `False` in my standalone context.
- I did not fuzz the regex in `validate_miner_id_format` (line 120) for ReDoS or unicode edge cases.

## Confidence
- **Overall:** 0.78
- **Per-finding:**
  - Finding #1: 0.91 (broad `except Exception` is unambiguous in the source)
  - Finding #2: 0.85 (query logic is explicit; impact depends on epoch length assumptions)
  - Finding #3: 0.72 (pattern is clear, but interaction with upstream rewards module reduces certainty)

## What I would test next
1. Fuzz `check_claim_eligibility` with a locked/readonly database to force the broad-exception path and observe whether `reward_rtc` is silently 0.
2. Verify `check_epoch_participation` with an attestation timestamp exactly `ATTESTATION_TTL` before `epoch_start_ts` to confirm the boundary bleed.
3. Run the module's own `__main__` test block in a CI environment where `rewards_implementation_rip200.py` is intentionally missing, to see if the fallback branch actually returns a non-zero equal share or silently crashes to 0.
