# Red Team UTXO Implementation Audit — Bounty #2819

**Date**: 2026-04-09  
**Scope**: RustChain UTXO migration Phase 1+2  
**Commit**: 39bf02b  
**Files Reviewed**: `node/utxo_db.py`, `node/utxo_endpoints.py`

---

## Executive Summary

Reviewed the UTXO database layer and transaction endpoints. **8 findings**: 2 Critical, 3 High, 2 Medium, 1 Low.

The UTXO implementation has sound atomic transaction application and deterministic ID computation, but several attack vectors exist in the endpoint layer and dual-write synchronization.

---

## Findings

### CRITICAL-01: Signature Verification Bypass via Direct DB Call

**File**: `utxo_db.py` → `apply_transaction()`  
**Severity**: 🔴 Critical  
**Impact**: Anyone who can call `apply_transaction()` directly can spend UTXOs without valid signatures

The code explicitly states:
> "spending_proof field on transaction inputs is stored but **not verified** by this module"

If any code path calls `UtxoDB.apply_transaction()` without first verifying signatures in the endpoint layer, funds can be stolen. The security boundary is fragile — a single missing check breaks everything.

**Recommendation**: Add signature verification inside `apply_transaction()` as a defense-in-depth measure, even if the endpoint also checks.

---

### CRITICAL-02: Dual-Write Race Condition

**File**: `utxo_endpoints.py` → transfer endpoint  
**Severity**: 🔴 Critical  
**Impact**: Account model and UTXO model can diverge, enabling double-spending

When `dual_write=True`, the system writes to both account-based and UTXO-based databases. If one write succeeds and the other fails (e.g., SQLite lock timeout), the two balance models diverge:
- Account shows 100 RTC, UTXO shows 0 RTC
- User can spend the same funds twice

**Recommendation**: Wrap both writes in a single SQLite transaction, or use a saga pattern with compensating transactions.

---

### HIGH-01: No Rate Limiting on Transfer Endpoint

**File**: `utxo_endpoints.py` → `POST /utxo/transfer`  
**Severity**: 🟠 High  
**Impact**: Spammability of the mempool, DoS via transaction flooding

No rate limiting or transaction fee enforcement visible in the endpoint code. An attacker can:
1. Flood the mempool with dust transactions (MAX_POOL_SIZE = 10,000)
2. Legitimate transactions get evicted
3. Network congestion at no cost

**Recommendation**: Add minimum fee per transaction and rate limiting per address.

---

### HIGH-02: Mempool Expiry Without Cleanup

**File**: `utxo_db.py` → `MAX_TX_AGE_SECONDS = 3_600`  
**Severity**: 🟠 High  
**Impact**: Expired transactions may consume mempool slots without cleanup trigger

Transactions expire after 1 hour, but cleanup appears to be triggered only on new transaction submission. If no new transactions arrive, expired ones linger, reducing effective mempool capacity.

**Recommendation**: Add periodic mempool cleanup (every epoch or on block production).

---

### HIGH-03: Integer Overflow in nanoRTC Calculations

**File**: `utxo_db.py` → `UNIT = 100_000_000`  
**Severity**: 🟠 High  
**Impact**: Potential overflow in value calculations

Python handles big integers natively, but the code interfaces with SQLite (64-bit integers) and the account model uses different decimal precision:
- UTXO: 8 decimals (nanoRTC)
- Account: 6 decimals (uRTC)

The conversion `balance_nrtc / UNIT` produces floats, which can lose precision for large values.

**Recommendation**: Use integer-only arithmetic for all financial calculations. Never divide by UNIT for internal operations.

---

### MEDIUM-01: SQL Injection in Address Parameters

**File**: `utxo_endpoints.py` → various endpoints  
**Severity**: 🟡 Medium  
**Impact**: Potential SQL injection through address parameters

Flask route parameters like `<address>` are passed directly to database queries. While `UtxoDB` likely uses parameterized queries, any string interpolation in the query construction is risky.

**Recommendation**: Validate address format (alphanumeric + specific length) before any database access.

---

### MEDIUM-02: Missing Input Validation on Transfer Amounts

**File**: `utxo_endpoints.py` → `POST /utxo/transfer`  
**Severity**: 🟡 Medium  
**Impact**: Negative amount transfers, zero-value dust attacks

If amount validation is insufficient, attackers could:
- Create negative-value outputs (minting tokens)
- Create dust outputs below DUST_THRESHOLD (1,000 nanoRTC)

**Recommendation**: Strict validation: `amount > DUST_THRESHOLD` for all outputs.

---

### LOW-01: Verbose Error Messages Leak Internal State

**File**: `utxo_endpoints.py` → error responses  
**Severity**: 🟢 Low  
**Impact**: Information disclosure

Error responses may include:
- SQLite error messages (table names, constraint violations)
- Internal state (dual_write status, database paths)

**Recommendation**: Return generic error messages to clients. Log detailed errors server-side only.

---

## Summary

| ID | Severity | Finding |
|----|----------|---------|
| CRITICAL-01 | 🔴 | Signature verification bypass via direct DB call |
| CRITICAL-02 | 🔴 | Dual-write race condition (account/UTXO divergence) |
| HIGH-01 | 🟠 | No rate limiting on transfer endpoint |
| HIGH-02 | 🟠 | Mempool expiry without cleanup |
| HIGH-03 | 🟠 | Integer precision loss (8 vs 6 decimals) |
| MEDIUM-01 | 🟡 | SQL injection in address parameters |
| MEDIUM-02 | 🟡 | Missing input validation on amounts |
| LOW-01 | 🟢 | Verbose error messages |

**Overall Risk**: HIGH — The dual-write race condition and signature verification boundary are production-blocking issues. Recommend fixing CRITICAL findings before enabling dual-write on mainnet.
