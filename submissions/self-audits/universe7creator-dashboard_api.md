# Self-Audit: bridge/dashboard_api.py

## Wallet
RTC52d4fe5e93bda2349cb848ee33ffebeca9b2f68f

## Module reviewed
- Path: bridge/dashboard_api.py
- Commit: 92888df054821c3355836ae0cd442b2cf29a1280
- Lines reviewed: 1-520 (full file)

---

## Deliverable: 3 specific findings

### 1. Division by zero in 24h change calculation
- **Severity:** high
- **Location:** dashboard_api.py:79-80
- **Description:** `locked_change_24h = ((total_locked - locked_24h) / locked_24h * 100)` raises `ZeroDivisionError` when `locked_24h` is 0. This can occur on a fresh ledger (0 historical locks). Additionally, the 24h volume calculation in `get_dashboard_transactions` performs division without a guard check for `total_volume_24h` when there are no completed locks.
- **Reproduction:**
  ```
  # With an empty or fresh bridge_ledger.db (no completed locks):
  curl -s http://localhost:8096/bridge/dashboard/metrics | python3 -c "import json,sys; d=json.load(sys.stdin); print(d)"
  # Expected: valid JSON or graceful error
  # Actual: ZeroDivisionError crash
  ```

### 2. Unbounded memory growth in _price_cache (no TTL enforcement)
- **Severity:** medium
- **Location:** dashboard_api.py:24-25
- **Description:** `_price_cache` uses `CACHE_TTL = 30` as a comment but the value is never read or enforced. There is no `time.time()` check in `get_wrtc_price` before returning cached data, and the `_price_cache` dict never gets invalidated on time basis. A stale price can be served indefinitely if the external API call fails once. This is a silent stale-data vulnerability.
- **Reproduction:**
  ```python
  # When Raydium/DexScreener is down on first call:
  _price_cache = {"data": {...}, "timestamp": 0}  # timestamp never set or checked
  # Subsequent calls return the same stale error data forever
  ```

### 3. Inconsistent type field assignment in get_dashboard_transactions
- **Severity:** low
- **Location:** dashboard_api.py:181
- **Description:** The `type` field in the transaction response is derived from `target_chain == 'solana'` → `'wrap'` else `'unwrap'`. If a new supported chain is added to `SUPPORTED_CHAINS` in `bridge_api.py`, the dashboard would silently classify it as `'unwrap'` even if it wraps in the opposite direction. The dashboard hard-codes the wrap/unwrap logic without referencing the bridge API constants.
- **Reproduction:**
  ```python
  # If SUPPORTED_CHAINS gains a 'tron' entry for wrapping (not unwrapping):
  # All tron transactions would be mislabeled as 'unwrap' in the dashboard
  "type": "wrap" if r["target_chain"] == "solana" else "unwrap"
  ```

---

## Known failures of this audit
- I did not check the Raydium/DexScreener API response schemas in production - the JSON path access (e.g., `result["data"][0]`) assumes a specific API shape that may change.
- I did not test the SQLite ledger against concurrent write contention (multiple simultaneous `/bridge/lock` calls) during metric aggregation.
- The `/bridge/dashboard/health` endpoint's Solana RPC check sends a getHealth call but does not verify the returned `context.slot` for chain staleness.
- I did not read the bridge_api.py integration tests to confirm the database schema's exact column types.

---

## Confidence
- Overall confidence: 0.75
- Per-finding confidence: [0.92, 0.78, 0.55]
  - Finding 1 (division-by-zero) is deterministic and easy to trigger.
  - Finding 2 (cache TTL) is clearly visible in the code structure.
  - Finding 3 (hardcoded wrap/unwrap) is an architectural assumption - lower confidence that this would fail in practice.

---

## What I would test next
- Write a pytest fixture that inserts zero completed locks into the ledger and asserts `get_dashboard_metrics` returns a valid 0% change rather than raising.
- Write a test that calls `get_wrtc_price` once, sets a stale cache entry, then calls again and asserts the result is not the stale error value.
- Add a test for a new hypothetical chain (e.g., 'tron') added to `SUPPORTED_CHAINS` and verify the dashboard transaction `type` field is correct for that chain.
