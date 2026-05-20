Experiment, AI-assisted review claim for code review bounty #73.

Reviewed PR: https://github.com/Scottcjn/Rustchain/pull/5922
Target issue: https://github.com/Scottcjn/Rustchain/issues/5777

Review result: no blocking issue found.

Review notes:
- The PR fixes the fresh-database failure mode by creating `miner_header_keys` in `init_db()` with `CREATE TABLE IF NOT EXISTS`.
- The regression test changes `DB_PATH` to a temporary SQLite file, calls `init_db()`, and verifies `POST /miner/headerkey` succeeds through Flask's test client.
- The test restores `DB_PATH` and Flask `TESTING` in `finally`, so the global state cleanup is accounted for.

Non-blocking follow-up: if this table later needs key rotation or audit history, add timestamp/history metadata. That is outside the current missing-table fix.

Payout preference if direct payout is available: PayPal https://www.paypal.com/paypalme/whathestock or ERC20 USDC 0x3a2719e116c9C69a2514F3F7287b4AAAb13B9726.
