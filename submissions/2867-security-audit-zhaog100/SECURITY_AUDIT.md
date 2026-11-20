# RustChain Security Audit Report

**Auditor:** zhaog100 (小米辣)  
**Bounty:** #2867  
**Date:** 2026-04-29  
**Target:** OTC Bridge (`otc-bridge/app.py`)

---

## Summary

| # | Finding | Severity | Reward | Status |
|---|---------|----------|--------|--------|
| 3 | Unauthorized Order/Trade Cancellation | **CRITICAL** | 100 RTC | ✅ PoC |
| 4 | TLS Certificate Verification Disabled | **HIGH** | 50 RTC | ✅ PoC |
| 5 | Rate Limiting Bypass + Race Condition | **MEDIUM** | 25 RTC | ✅ PoC |

**Total Claimed: 175 RTC**

---

## Finding 3: Unauthorized Order/Trade Cancellation

**Severity:** CRITICAL (100 RTC)  
**File:** `otc-bridge/app.py`  
**Lines:** ~465-489 (cancel_order), ~640+ (cancel_trade)

### Description
The OTC Bridge has NO authentication or authorization on financial endpoints.
Any unauthenticated user can cancel any order or trade by knowing the ID.

### Impact
- Cancel legitimate trades, disrupting users
- Release escrow funds without authorization
- Complete denial of service for OTC operations

### PoC
```bash
python3 poc_finding3_unauthorized_cancel.py http://localhost:5000
```

### Remediation
1. Add wallet signature verification for all financial endpoints
2. Verify ownership: `request.wallet == order.wallet_address`
3. For trade cancellation: verify requester is buyer or seller
4. Add audit logging

---

## Finding 4: TLS Certificate Verification Disabled

**Severity:** HIGH (50 RTC)  
**File:** `otc-bridge/app.py`  
**Lines:** 232-238

### Description
The RustChain HTTP client disables TLS verification for the production node:
```python
if "50.28.86.131" in self.node_url:
    self.session.verify = False
```

### Impact
- Man-in-the-Middle attacks on all node communications
- Forged API responses, stolen balances, hijacked transfers
- All financial data in transit is vulnerable

### PoC
```bash
python3 poc_finding4_tls_bypass.py https://50.28.86.131
```

### Remediation
1. Never set `verify=False` in production
2. Use proper CA-signed certificates
3. Pin certificates if self-signed: `session.verify = "/path/to/cert.pem"`
4. Use mutual TLS (mTLS)

---

## Finding 5: Rate Limiting Bypass + Race Condition

**Severity:** MEDIUM (25 RTC)  
**File:** `otc-bridge/app.py`  
**Lines:** 205-229, 369-385

### Description
Rate limiter uses `IP + wallet_address` as identifier. Wallet is user-controlled.
Concurrent requests have a TOCTOU race condition.

### Impact
- DDoS, brute force, scraping of OTC endpoints
- Bypass protection via simple wallet rotation

### Remediation
1. Use fixed identifiers (IP only or authenticated user ID)
2. Add atomic operations (Redis INCR, thread locks)
3. Persist rate limit state
4. Use Flask-Limiter

---

## Wallet

RTC-wallet: zhaog100
