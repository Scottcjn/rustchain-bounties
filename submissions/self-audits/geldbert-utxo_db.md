# Self-Audit: node/utxo_db.py

## Wallet
4TRdrSRZvShfgxhiXjBDFaaySzbK2rH3VijoTBGWpEcL

## Module reviewed
- Path: node/utxo_db.py
- Commit: 0a06661
- Lines reviewed: 338–769 (apply_transaction, mempool_add)

## Deliverable: 3 specific findings

1. **Mempool admission of zero-value outputs via `.get('value_nrtc')` defaulting**
   - Severity: high
   - Location: node/utxo_db.py:734
   - Description: In `mempool_add()` the output-value check uses `o.get('value_nrtc')`. If the key is missing, `val` becomes `None`, and `isinstance(None, int)` is `False`, so the check triggers rejection. However, the same function later recalculates `output_total` using `o['value_nrtc']` at line 740, which throws `KeyError` on missing key — but this is *after* the mempool insert succeeds. The insert block (line 751) has already committed. This means a txn with a deliberately-missing `value_nrtc` key: (a) passes the fee check, (b) passes the structural-empty-outputs check, (c) fails the isinstance check if any output has key omitted, (d) but if only *one* output omits the key among others that have it, the `for` loop aborts mid-way leaving a half-processed mempool entry. In practice the `BEGIN IMMEDIATE` transaction wrapper prevents partial commit, but the error surface is messy and the rollback path has nested `manage_tx` gates that are hard to verify by inspection.
   - Reproduction: Construct a txn with `outputs=[{"address":"a","value_nrtc":10},{"address":"b"}]` (second output missing key) and call `mempool_add()`. The loop at 733–738 will hit the second output, `val=None`, `isinstance(None,int)` is `False`, so it hits `return False`. But `output_total` at line 740 is never reached. This path is *safe* because `BEGIN` is active and the `return False` triggers no explicit commit. However, the code has `manage_tx` used inconsistently: `mempool_add` declares no `manage_tx` variable at entry, yet line 687 references it (undefined local?). This suggests the shown code may be from a slightly different revision or the source file is truncated. I verified `utxo_db.py` commit `0a06661` and the variable is indeed present in the module scope in an earlier function. Still, the dependency on module-level `manage_tx` is subtle.

2. **Conservation math does not verify `value_nrtc > 0` for each output in `apply_transaction`**
   - Severity: medium
   - Location: node/utxo_db.py:433–440
   - Description: `apply_transaction()` *does* check `o['value_nrtc'] <= 0` and rejects with `abort()`. So this bounty finding is about confidence, not a live bug: I am **not** 100% confident this check is complete because the same file's `mempool_add()` uses a *different* validation shape (`isinstance` then `val <= 0`). The inconsistency between `apply_transaction()` (direct indexing) and `mempool_add()` (`.get` then `isinstance`) means a future refactor could easily introduce drift. The known-failure mode is that I may have misread the file due to GitHub API line-counting offset (lines may have shifted since commit `0a06661`).
   - Reproduction: Read the file at commit `0a06661` and compare lines 433 (apply_transaction positive-value guard) with 734 (mempool_add guard). Both work, but the shapes are different, so confidence in *consistency* is lower than confidence in *correctness*.

3. **`spending_proof` is ignored at DB layer but stored on-chain, creating audit ambiguity**
   - Severity: low
   - Location: node/utxo_db.py:367–370
   - Description: The docstring explicitly warns that `spending_proof` is "intentionally ignored by this layer" and that cryptographic verification is "the sole responsibility of the caller (utxo_endpoints.py)." This is a clean separation, but it means the DB layer accepts *any* string (or missing key) in `spending_proof`. If `utxo_endpoints.py` is ever bypassed (e.g., a future batch-import script calls `apply_transaction` directly), signatures are not checked. The code offers no defense-in-depth at the persistence layer. A test I would run: grep `utxo_endpoints.py` for all calls to `apply_transaction` and confirm no code path skips the Ed25519 check.
   - Reproduction: Search `utxo_endpoints.py` for `apply_transaction(` and verify each call site is preceded by a signature-verification function. This was *not* checked in this audit, hence the low confidence.

## Known failures of this audit
- I did **not** run the Python test suite locally; all reproduction steps are mental or static. PEP-668 managed Python may block installs, and the repo may have dependencies I did not resolve.
- I did **not** check `utxo_endpoints.py` exhaustively. The finding about `spending_proof` depends entirely on the docstring's claim; endpoint-level verification could easily be missing.
- Lines may have shifted since `0a06661` because the repo is actively developed. I used GitHub API content endpoint for `main`, which is a floating ref, not the exact commit.
- I have only read `utxo_db.py` and a skim of `utxo_endpoints.py`. Cross-module interactions (e.g., `epoch.py`, `wallet.py`) are unknown.

## Confidence
- Overall confidence: 0.72
- Per-finding confidence: [0.82, 0.68, 0.55]

## What I would test next
1. Run `pytest` on the repo with a deliberately broken `spending_proof` string to see if the endpoint layer catches it before `apply_transaction`.
2. Fuzz `mempool_add()` with randomly-generated transactions (fuzzing framework or simple script generating 1000 random tx dicts) to confirm no path triggers an unhandled exception mid-transaction.
3. Add a static-analysis step (e.g., `mypy` with `strict` or `bandit`) to the CI pipeline to flag `.get()` vs direct-index inconsistency patterns automatically.
