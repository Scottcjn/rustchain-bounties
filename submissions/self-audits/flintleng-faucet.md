# Self-Audit: faucet.py

## Wallet
RTC019e78d600fb3131c29d7ba80aba8fe644be426e

## Module reviewed
- Path: faucet.py
- Commit: 0a06661
- Lines reviewed: whole-file (247 lines)

## Deliverable: 3 specific findings

1. **Race condition in rate-limit check-then-act (TOCTOU)**
   - Severity: high
   - Location: faucet.py:159–176 (drip endpoint)
   - Description: The `can_drip()` check and `record_drip()` write are not atomic. Between the SELECT in `can_drip()` and the INSERT in `record_drip()`, a concurrent request can pass the same rate-limit check. SQLite's default journal mode allows concurrent reads but serializes writes — however, the read-then-write window is unprotected by any transaction or `BEGIN IMMEDIATE`, so two parallel POST /faucet/drip requests from the same IP or wallet can both pass `can_drip()` before either writes.
   - Reproduction: `for i in $(seq 1 10); do curl -s -X POST http://localhost:8090/faucet/drip -H 'Content-Type: application/json' -d '{"wallet":"0xAABBCCDD"}' &; done; wait` — expect some requests to succeed in excess of the rate limit.

2. **Wallet validation accepts trivially forgeable addresses**
   - Severity: medium
   - Location: faucet.py:161–162
   - Description: Validation only checks `wallet.startswith('0x') and len(wallet) >= 10`. An attacker can generate unlimited valid-looking addresses (e.g., `0x0000000000`, `0x0000000001`, …) to bypass the per-wallet rate limit entirely. There is no checksum or format validation (e.g., EIP-55 checksum for EVM-style, or the `RTC` prefix that RustChain actually uses per its documentation). The comment says "should start with 0x" but RustChain wallets use the `RTC` prefix, meaning legitimate wallets may be rejected while arbitrary `0x` strings pass.
   - Reproduction: `curl -X POST http://localhost:8090/faucet/drip -H 'Content-Type: application/json' -d '{"wallet":"0xAAAAAAAAAA"}'` — succeeds despite being a fabricated address. Meanwhile `curl -X POST ... -d '{"wallet":"RTC019e78d600fb3131c29d7ba80aba8fe644be426e"}'` — rejected as "Invalid wallet address".

3. **Database path relative and unconfigurable; no WAL mode**
   - Severity: low
   - Location: faucet.py:19 (`DATABASE = 'faucet.db'`)
   - Description: The database path is hardcoded as a relative filename. When run from different working directories (common in container deployments), the faucet silently creates or uses a different `faucet.db`, losing all rate-limit history. Additionally, SQLite is used in default delete-journal mode rather than WAL mode, which under concurrent access causes "database is locked" errors (sqlite3.OperationalError) that are unhandled — the server will return a 500 to the user but the drip may or may not have been recorded, creating inconsistency.
   - Reproduction: (a) `cd /tmp && python faucet.py &` then `curl …/drip` — rate-limit state differs from `cd /home/user && python faucet.py`. (b) With concurrent requests: watch for `OperationalError: database is locked` in Flask stderr.

## Known failures of this audit
- Did not test the actual token transfer logic — the code says "For now, we simulate the drip" so there is no on-chain interaction to audit; production deployment would need a separate audit of the signing/broadcast path.
- Did not review ProxyFix configuration depth — `x_for=1` trusts one proxy layer; if deployed behind multiple reverse proxies (e.g., CloudFlare + nginx), IP spoofing is possible. Confidence on ProxyFix correctness is low without knowing the deployment topology.
- Did not check for SSRF or header injection in the HTML template — `render_template_string` is used with static content only (no user input in template vars), so XSS risk is low, but this was not exhaustively verified against all Jinja2 auto-escaping edge cases.

## Confidence
- Overall confidence: 0.78
- Per-finding confidence: [0.90, 0.82, 0.62]

## What I would test next
- Load-test the `/faucet/drip` endpoint with 50+ concurrent requests from the same IP using `hey` or `wrk` to confirm the TOCTOU race condition and measure how many excess drips succeed.
- Add a fuzzer that generates `0x` + random hex strings of length 10–42 to measure the per-wallet rate limit bypass rate.
- Set `PRAGMA journal_mode=WAL` in `init_db()` and re-run concurrent tests to confirm lock errors disappear, then add `BEGIN IMMEDIATE` around the check+write pair.
