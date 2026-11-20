# Self-Audit: passport/passport_ledger.py

## Wallet
RTC00a1347cc03132990059144b41218ae4a01a5c43

## Module reviewed
- Path: passport/passport_ledger.py
- Commit: 92888df (92888df054821c3355836ae0cd442b2cf29a1280)
- Lines reviewed: 1-248 (entire file)

## Deliverable: 3 specific findings

1. **`compute_passport_hash()` excludes `owner_address` from hash**
   - Severity: high
   - Location: passport_ledger.py:119-135
   - Description: The `compute_passport_hash()` method is used for on-chain anchoring but does NOT include the `owner_address` field in the hash computation. This means a passport's ownership can be changed without the hash changing, breaking the integrity guarantee that the hash should represent. An attacker who obtains a valid passport hash could claim ownership of any machine by changing the owner address while the on-chain anchor remains valid.
   - Reproduction: 1) Create a passport with owner_address="RTC_AAA", compute hash. 2) Change owner_address to "RTC_BBB". 3) Compute hash again — both hashes are identical, despite different owners.

2. **`delete()` has no authorization check — any caller can delete any passport**
   - Severity: high
   - Location: passport_ledger.py:235-244
   - Description: The `delete()` method accepts any `machine_id` and immediately removes the passport from disk without verifying the caller's authority. There is no check that the caller is the passport owner, admin, or has any deletion rights. In a multi-user or server context (e.g., the passport_server.py HTTP API), this allows any user to delete any other user's passport.
   - Reproduction: 1) Start the passport server. 2) User A creates a passport. 3) User B calls `ledger.delete(machine_id)` — passport is deleted without any authorization check.

3. **`save()` and `_save_index()` are not atomic — race condition on concurrent writes**
   - Severity: medium
   - Location: passport_ledger.py:198-205, 193-194
   - Description: The `save()` method writes the passport file first, then updates the index file. If the process crashes between these two operations, the index will reference a file that was partially written or doesn't exist. Similarly, `_save_index()` reads the full index, modifies it in memory, and writes it back — concurrent saves will cause one write to overwrite the other's changes (lost update problem). This can lead to data corruption where a passport file exists but is not indexed, or the index references a file that was overwritten by a concurrent write.
   - Reproduction: 1) Create two threads/processes. 2) Both call `save()` with different passports simultaneously. 3) Observe that the index.json may only contain one of the two entries (lost update). Alternatively: kill the process between `filepath.write_text()` and `self._save_index()` — the file exists but the index doesn't reference it.

## Known failures of this audit
- Did not audit `passport_server.py` (the HTTP API layer) — only audited the core ledger module. The API layer may have additional vulnerabilities (e.g., input validation, authentication endpoints).
- Did not verify the Soroban smart contract integration — if this module is wrapped for on-chain use, the serialization/deserialization between Python and Soroban WASM may introduce additional issues.
- Low confidence on whether the `photo_hash` and `repair_log` fields are validated against malicious input (e.g., path traversal via filename, injection via description strings).
- Did not test the `from_dict()` / `from_json()` deserialization for unsafe type coercion (e.g., passing a list where a string is expected could cause runtime errors).

## Confidence
- Overall confidence: 0.85
- Per-finding confidence: [0.9, 0.95, 0.7]

## What I would test next
- Audit `passport_server.py` endpoints for authentication bypass and input validation (especially the routes that call `ledger.save()` and `ledger.delete()`).
- Write property-based tests (Hypothesis) for `compute_passport_hash()` to verify that all identity-critical fields are included and that hash stability is maintained across non-identity field changes.
- Test concurrent access patterns with multiple processes writing to the same ledger to confirm the race condition and measure its frequency.
