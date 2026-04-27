# Self-Audit: node/beacon_x402.py

## Wallet
fengqiankun

## Module reviewed
- Path: node/beacon_x402.py
- Commit: 0b2a091 (Rustchain local repo, April 16 2026 snapshot)
- Lines reviewed: 366 (entire file)

## Deliverable: 3 specific findings

1. **CORS wildcard on admin-protected endpoint — XSS vector**
   - Severity: high
   - Location: beacon_x402.py:100, `_cors_json` usage
   - Description: The POST `/api/agents/<agent_id>/wallet` endpoint uses `Access-Control-Allow-Origin: *` on a sensitive admin-protected route. Even though an admin key is checked, the wildcard CORS allows any origin to send requests. In combination with a reflected agent_id in the response body, this enables cross-site scripting if the endpoint is accessed via a browser.
   - Reproduction:
     ```bash
     curl -X POST https://beacon.example.com/api/agents/<script>alert(1)</script>/wallet \
       -H "X-Admin-Key: <valid_key>" \
       -H "Origin: https://evil.com"
     # Response will contain CORS header: Access-Control-Allow-Origin: https://evil.com
     # allowing that origin to read the response.
     ```

2. **Payment logging silently fails — no audit trail for paid endpoints**
   - Severity: medium
   - Location: beacon_x402.py:126-136, `_check_x402_payment`
   - Description: When x402 payment is detected, the payment logging block always inserts `payer_address = "unknown"` because the actual payer address is never extracted from the payment header. Additionally, if `g.get("db")` returns None or the commit fails, the exception is caught and silently discarded — no fallback logging, no error returned to caller.
   - Reproduction:
     ```python
     # When payment_header exists but is malformed:
     payment_header = "invalid-base64"
     # The function returns (True, None) — payment accepted
     # but no record of who paid or how much is kept
     ```

3. **TOCTOU race in `set_agent_wallet` — wallet overwrite via concurrent requests**
   - Severity: medium
   - Location: beacon_x402.py:183-193, `set_agent_wallet`
   - Description: The wallet insert uses `ON CONFLICT(agent_id) DO UPDATE` which is atomic in SQLite. However, the flow first fetches `beacon_wallets` to check existence (lines ~197-213), then constructs a separate response. Between the GET check and the INSERT, two concurrent requests for the same `agent_id` could race. More critically, the relay_agents fallback lookup in GET has no equivalent UPSERT — a concurrent POST might race with the relay coinbase_address check. Additionally, the `coinbase_address` validation is not applied consistently to the relay path.
   - Reproduction:
     ```bash
     # Two concurrent POSTs for same agent_id
     curl -X POST /api/agents/agent_123/wallet -d '{"coinbase_address":"0xAAAA..."}' &
     curl -X POST /api/agents/agent_123/wallet -d '{"coinbase_address":"0xBBBB..."}' &
     # Depending on timing, both might be accepted with different addresses
     ```

## Known failures of this audit
- Did not test the Flask app integration — the `init_app` wiring was not run in a live environment
- Did not test x402 payment header parsing (Base64 decoding, signature verification) — only read the code
- `has_cdp_credentials()` and `create_agentkit_wallet()` are imported conditionally — could not verify their correctness
- SWAP_INFO exposure in GET responses was not reviewed for information disclosure concerns
- `PRAGMA table_info` for migration detection could silently fail on certain SQLite versions

## Confidence
- Overall confidence: 0.75
- Per-finding confidence: [0.7, 0.8, 0.65]

## What I would test next
- Intercept a live x402 payment header and verify whether the payer_address is actually extractable from it, or if it's always "unknown" in practice
- Run a concurrent POST race condition against `set_agent_wallet` to confirm whether double-write is possible despite the ON CONFLICT guard
- Check whether the wildcard CORS on the admin endpoint can be exploited via a browser-based attack chaining a reflected agent_id in the JSON response