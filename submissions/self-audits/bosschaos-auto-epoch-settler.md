# Self-Audit: sophia_governor.py

**Bounty:** #6460 (Self-Audit, 10 RTC)
**File:** `node/sophia_governor.py` (982 lines)
**Wallet:** RTC019e78d600fb3131c29d7ba80aba8fe644be426e
**Auditor:** BossChaos

---

## Finding 1 — Unauthenticated Read Endpoints Expose Governance State (High)

**Location:** `register_sophia_governor_endpoints()` — lines 943–953

The `/sophia/governor/status` (GET) and `/sophia/governor/recent` (GET) endpoints have **no authentication guard**. They return:

- Total event counts, escalation counts, and risk-level summaries (`get_governor_status`)
- Up to 200 recent governor events with full risk assessments, stances, routes, and LLM summaries (`get_recent_governor_events`)

The `/sophia/governor/review` (POST) and `/sophia/governor/retry` (POST) endpoints correctly check `_is_admin()`, but the read-only leaks let an unauthenticated attacker profile the governor's decision history, risk thresholds, and escalation patterns. This reconnaissance data could be used to craft events that bypass the heuristic triage or to time attacks against pending escalations.

**Recommendation:** Apply the same `_is_admin()` guard to the GET endpoints, or at minimum add a read-only API key check.

---

## Finding 2 — Phone-Home Sends Sensitive Payloads Without Transport Validation (Medium)

**Location:** `_phone_home()` and `_deliver_http_target()` — lines 705–758, 667–679

The `_phone_home_targets()` function accepts arbitrary URLs from environment variables (`SOPHIA_GOVERNOR_PHONE_HOME_TARGETS`, `SOPHIA_GOVERNOR_INBOX_URL`, `SOPHIA_GOVERNOR_PHONE_HOME_URLS`) with **no scheme validation or allowlist**. The `_deliver_http_target()` function POSTs full event envelopes — including payloads, decisions, and continuity context — to these targets with:

- No HTTPS enforcement (`http://` endpoints are accepted)
- No TLS certificate pinning or hostname verification override
- No URL allowlist check (any domain reachable from the node will receive data)
- Response bodies from external servers are truncated and stored in the local SQLite DB (line 677), creating a reflection risk where a malicious target could inject data into the governor's own records

Additionally, `_phone_home_headers()` attaches `RC_ADMIN_KEY` as `X-Admin-Key` (line 647) to outbound requests, potentially leaking the admin secret to untrusted phone-home targets.

**Recommendation:** Enforce `https://` scheme, maintain a domain allowlist, strip admin credentials from outbound requests, and sanitize stored response bodies.

---

## Finding 3 — Hardcoded Developer Paths Create Operational Failure Modes (Low)

**Location:** Lines 47–53

```python
DB_PATH = os.getenv("RUSTCHAIN_DB_PATH", "/root/rustchain/rustchain_v2.db")
DEFAULT_CONTINUITY_PACKET_PATH = Path(
    os.getenv(
        "SOPHIA_GOVERNOR_CONTINUITY_PACKET",
        "/home/scott/chatgpt-live-analysis/portable/sophiacore_portable_packet.json",
    )
)
```

Two default paths embed developer-specific filesystem assumptions:

1. **`/root/rustchain/rustchain_v2.db`** — assumes the process runs as `root` with a specific directory structure. On a non-root deployment or container, the governor silently fails to initialize its schema on first call (the `sqlite3.connect` will create an empty DB at the wrong path or fail entirely).

2. **`/home/scott/chatgpt-live-analysis/...`** — a hardcoded personal path that will never exist in production. The `_load_continuity_packet()` function silently falls back to an empty `{}` context, degrading the LLM prompt's continuity anchors without any visible warning beyond a log message.

These defaults mean a fresh deployment without explicit environment variable configuration will appear to function normally (no exceptions) while operating with an incorrect database and no continuity context.

**Recommendation:** Use sensible production defaults (e.g., relative paths or `/var/lib/rustchain/`), and add a startup health check that validates DB write access and logs a warning when continuity packet defaults are not overridden.
