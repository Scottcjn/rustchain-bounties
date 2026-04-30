# Self-Audit: node/server_proxy.py

**Bounty**: #6460 - 10 RTC
**Auditor**: tianheng
**Wallet**: TVBiBzF3ZiK4oTkqZkDAtwYMKUCL7qpBVZ

## Module Reviewed

| Field | Value |
|-------|-------|
| Path | node/server_proxy.py |
| Repo | Scottcjn/Rustchain |
| Language | Python 3 |
| Lines | 70 |
| Purpose | HTTP proxy that forwards API requests from port 8089 to localhost:8088 |

## Finding 1: No Authentication - Open Proxy (CRITICAL)

Location: app.route('/api/<path:path>')

The proxy binds to 0.0.0.0:8089 and accepts requests from ANY client. There is zero authentication, zero IP filtering, no API key, no token verification.

Impact: Anyone on the network (or internet if port is exposed) can:
- Access all internal RustChain APIs on localhost:8088
- Submit mining operations, registration, stats queries
- Potentially DoS the internal server

Fix: Add IP allowlist, API key authentication, or network-level firewall rules.

## Finding 2: Path Sanitization Missing (HIGH)

Location: @app.route('/api/<path:path>') and url = f'{LOCAL_SERVER}/api/{path}'

The path variable is injected directly into the URL without ANY sanitization. An attacker can inject path traversal sequences, query parameters, or URL fragments:

Examples:
- GET /api/../admin_secret (path traversal to non-/api routes)
- GET /api/../../etc/passwd (if local server serves file system)
- GET /api/mine?override=true (query param injection)

Fix: Validate path against an allowlist of known API endpoints, strip special characters, reject ../ sequences.

## Finding 3: Internal Error Details Leaked to Client (MEDIUM)

Location: except Exception as e: return jsonify({'error': str(e)}), 500

Full Python exception messages are returned to the client. This leaks:
- Internal file paths, network topology, dependency versions
- May reveal stack traces that help attackers craft exploits

Fix: Return a generic 500 message and log the detailed error server-side.

## Summary

| # | Severity | Finding | Confidence |
|---|----------|---------|------------|
| 1 | CRITICAL | Open proxy with no authentication | 0.97 |
| 2 | HIGH | No path sanitization - traversal/param injection | 0.95 |
| 3 | MEDIUM | Internal error info leaked to client | 0.93 |

Confidence: 0.95
