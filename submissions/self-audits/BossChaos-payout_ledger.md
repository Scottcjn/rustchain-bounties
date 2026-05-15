# Self-Audit: payout_ledger.py

## Wallet
RTC6d1f27d28961279f1034d9561c2403697eb55602

## Module reviewed
- Path: Rustchain/payout_ledger.py
- Commit: 7e8e1144f36
- Lines reviewed: 1–280 (full file)

## Deliverable: 3 specific findings

1. **TOCTOU race condition in ledger_update_status**
   - Severity: medium
   - Location: payout_ledger.py:122–132
   - Description: `ledger_update_status` reads the current status from the DB and then writes the new status without locking or atomic compare-and-swap. Concurrent calls can both read `queued`, and the second write wins — the first transition is silently lost. In a blockchain ledger, lost state transitions are equivalent to lost funds.
   - Reproduction:
     ```python
     import threading
     def transition(id, new_status):
         with sqlite3.connect(DB_PATH) as conn:
             row = conn.execute("SELECT status FROM payout_ledger WHERE id=?", (id,)).fetchone()
         ledger_update_status(id, new_status)
     t1 = threading.Thread(target=transition, args=(record_id, "pending"))
     t2 = threading.Thread(target=transition, args=(record_id, "voided"))
     t1.start(); t2.start()
     # Final status is non-deterministic
     ```

2. **No bounds check on amount_rtc — negative and NaN values accepted**
   - Severity: low
   - Location: payout_ledger.py:100–119, api_ledger_create route
   - Description: `ledger_create` accepts any float via `float(data["amount_rtc"])` with no validation. No check for negative amounts, zero, or NaN/Infinity. `ledger_summary()` uses `SUM(amount_rtc)` which propagates NaN silently, corrupting aggregate stats.
   - Reproduction:
     ```bash
     curl -X POST /api/ledger -d '{"bounty_id":"test","contributor":"x","amount_rtc":-999}'
     # Accepted — no validation error
     ```

3. **No authentication on any /api/ledger endpoint**
   - Severity: low
   - Location: payout_ledger.py:146–205
   - Description: All ledger CRUD routes are completely unauthenticated. Any client can create fake payout records, update any record's status to "confirmed", or void legitimate payouts.
   - Reproduction:
     ```bash
     curl -X POST /api/ledger -d '{"bounty_id":"fake","contributor":"attacker","amount_rtc":99999}'
     record_id=$(curl -s /api/ledger | jq '.[0].id')
     curl -X PATCH /api/ledger/$record_id/status -d '{"status":"confirmed"}'
     ```

## Known failures of this audit
- I did not check LEDGER_HTML for XSS — Jinja2 `|e` filters are present but not verified.
- I did not verify sqlite3 journal mode (default may allow write conflicts).
- I did not check if the Flask app has rate limiting or WAF middleware upstream.

## Confidence
- Overall confidence: 0.85
- Per-finding confidence: [0.9, 0.75, 0.95]

## What I would test next
- Fuzz /api/ledger POST with NaN, negative, and large floats; observe ledger_summary() corruption.
- Concurrent test (10+ threads transitioning same record) to observe final state divergence.
- Check if Flask app runs behind authentication middleware — if not, escalate to bounty #2867.
