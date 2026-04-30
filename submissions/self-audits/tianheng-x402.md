# Self-Audit: node/rustchain_x402.py

**Bounty**: #6460 - 10 RTC
**Auditor**: tianheng
**Wallet**: 0xce3653a94c43a4cc5c62ce3bad48e73429e2f6a6

## Module Reviewed

| Field | Value |
|-------|-------|
| Path | node/rustchain_x402.py |
| Repo | Scottcjn/Rustchain |
| Language | Python 3 |
| Lines | 129 |
| Purpose | x402 payment integration: Coinbase wallet linking + swap info routes |

## Finding 1: Non-Constant-Time Admin Key Comparison (HIGH)

Location: L124: if admin_key != expected:

The admin key (RC_ADMIN_KEY) is compared using Python's built-in '!=' operator, which short-circuits on the first differing byte. This creates a measurable timing side-channel: an attacker can brute-force the key byte-by-byte by measuring response latency.

Impact: If RC_ADMIN_KEY is set (even to a weak default), any network attacker with the ability to measure response times can recover the full admin key within ~minutes. Once recovered, they can link arbitrary Coinbase addresses to miners, redirecting payouts and potentially bridging funds.

Fix: Replace with hmac.compare_digest(admin_key, expected) for constant-time comparison.

## Finding 2: Silent Config Fallback Creates Dual Source of Truth (MEDIUM)

Location: L19-37: try/except ImportError with inline duplicate data

When x402_config.py import fails, the module silently falls back to hardcoded inline SWAP_INFO. This means:
- A stale or failed deployment might silently use old contract addresses
- If x402_config.py exists but has a syntax error, the except silently catches it
- If x402_config.py is updated but import fails silently, the server serves stale swap info without alerting

Impact: Silent fallback to stale data means users see wrong pool addresses. Can lead to asset loss if users trust the returned swap info.

Fix: Raise or log at ERROR/warning to monitoring, not just log.warning. Validate critical contract addresses at startup.

## Finding 3: Admin Key Status Leakage via Error Response (MEDIUM)

Location: L122-123: if not expected: return jsonify({""error"": ""Admin key not configured""}), 503

An unauthenticated GET/PATCH to /wallet/link-coinbase can distinguish between:
- 503: RC_ADMIN_KEY is NOT configured (server deploying without admin protection)
- 401: RC_ADMIN_KEY is configured but the request key is wrong

This allows an attacker to probe the server's security posture without any authentication. If the server returns 503, the attacker knows the endpoint is completely unprotected.

Impact: Information leakage simplifies targeted attacks. Combined with Finding 1 (timing attack), this tells attackers exactly when to start the brute force.

Fix: Return the same error code (401 Unauthorized) regardless of whether admin key is configured or wrong. Log the detail server-side.

## Summary

| # | Severity | Finding | Confidence |
|---|----------|---------|------------|
| 1 | HIGH | Non-constant-time admin key comparison (timing attack) | 0.95 |
| 2 | MEDIUM | Silent ImportError fallback creates dual data source | 0.92 |
| 3 | MEDIUM | Admin key status leak via response code diff | 0.90 |

Confidence: 0.92
