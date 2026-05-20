# Code Review Bounty Claim - #73

Claimant: `mouseos`

Bounty: Scottcjn/rustchain-bounties#73

Wallet/miner ID: `mouseos-codex-earner`

Canonical payout declaration: https://github.com/Scottcjn/rustchain-bounties/issues/6885#issuecomment-4499541075

Issue claim thread: https://github.com/Scottcjn/rustchain-bounties/issues/11521

Status: submitted for maintainer assessment. Bounty #73 issue comments are disabled after 2500 comments, so this file mirrors the issue claim in PR-claim format.

## Reviews Submitted

### 1. Scottcjn/Rustchain#5826 - Changes Requested

Review: https://github.com/Scottcjn/Rustchain/pull/5826#pullrequestreview-4325964711

Summary:
- Found that blank optional certificate IDs sent as `cert_id: null` are rejected before generated-ID fallback.
- Found that some new validation branches return HTTP 200 with `success: false`, with tests accepting both 400 and 200.
- Ran Windows syntax and diff checks for the touched badge generator files.

### 2. Scottcjn/Rustchain#5827 - Changes Requested

Review: https://github.com/Scottcjn/Rustchain/pull/5827#pullrequestreview-4325994162

Summary:
- Found the same browser-compatible `cert_id: null` regression in malformed badge payload handling.
- Ran Windows `py_compile` and diff checks for the touched badge generator files.

### 3. Scottcjn/Rustchain#5828 - Approved

Review: https://github.com/Scottcjn/Rustchain/pull/5828#pullrequestreview-4326013045

Summary:
- Verified bridge status data is written beside the dashboard.
- Ran `python -m pytest tests\test_static_bridge_update_stats.py -q --noconftest -o addopts=''` on Windows: 3 passed.

### 4. Scottcjn/Rustchain#5946 - Approved

Review: https://github.com/Scottcjn/Rustchain/pull/5946#pullrequestreview-4329613039

Summary:
- Verified consensus probe miner envelope counting.
- Ran focused Windows pytest for consensus probe tests: 14 passed.

### 5. Scottcjn/Rustchain#5947 - Approved

Review: https://github.com/Scottcjn/Rustchain/pull/5947#pullrequestreview-4329923948

Summary:
- Verified GitHub Contents API SHA lookup hardening in the tip bot.
- Ran `python -m pytest integrations\rustchain-bounties\test_tip_bot.py -q --noconftest -o addopts=''` on Windows: 66 passed.

### 6. Scottcjn/Rustchain#5948 - Approved

Review: https://github.com/Scottcjn/Rustchain/pull/5948#pullrequestreview-4329906432

Summary:
- Verified DexScreener wRTC price payload hardening.
- Ran `python -m pytest tests\test_wrtc_price_bot.py -q --noconftest -o addopts=''` on Windows: 3 passed.

### 7. Scottcjn/Rustchain#5949 - Approved

Review: https://github.com/Scottcjn/Rustchain/pull/5949#pullrequestreview-4329914319

Summary:
- Verified Locust load-test malformed JSON failure handling.
- Ran `python -m pytest tests\test_locust_load_suite.py -q --noconftest -o addopts=''` on Windows: 5 passed.

### 8. Scottcjn/Rustchain#5951 - Changes Requested

Review: https://github.com/Scottcjn/Rustchain/pull/5951#pullrequestreview-4329573977

Summary:
- Found a remaining malformed-field crash in BoTTube digest sorting for mixed numeric and malformed string values.
- Reproduced `TypeError: '<' not supported between instances of 'str' and 'int'` with malformed `views` and `videos_posted`.
- Ran focused Windows digest tests: 13 passed.

### 9. Scottcjn/Rustchain#5953 - Approved

Review: https://github.com/Scottcjn/Rustchain/pull/5953#pullrequestreview-4329598768

Summary:
- Verified vintage validator warning preservation.
- Ran `python -m pytest tests\test_validate_vintage_submission.py -q --noconftest -o addopts=''` on Windows: 7 passed.

### 10. Scottcjn/Rustchain#5954 - Approved

Review: https://github.com/Scottcjn/Rustchain/pull/5954#pullrequestreview-4329625477

Summary:
- Verified empty interaction metadata preservation.
- Ran `python -m pytest tests\test_interactions.py -q --noconftest -o addopts=''` on Windows: 27 passed.

### 11. Scottcjn/Rustchain#5955 - Changes Requested

Review: https://github.com/Scottcjn/Rustchain/pull/5955#pullrequestreview-4329857690

Summary:
- Found that the focused parasocial test suite leaves SQLite temp DB files locked on Windows.
- Reproduced 19 failures from `PermissionError: [WinError 32]` during cleanup.

### 12. Scottcjn/Rustchain#5956 - Approved

Review: https://github.com/Scottcjn/Rustchain/pull/5956#pullrequestreview-4329848843

Summary:
- Verified low-verbosity personality text truncation chooses the earliest sentence terminator.
- Ran `python -m pytest tests\test_personality.py -q --noconftest -o addopts=''` on Windows: 29 passed.

### 13. Scottcjn/Rustchain#5957 - Changes Requested

Review: https://github.com/Scottcjn/Rustchain/pull/5957#pullrequestreview-4329809272

Summary:
- Found a remaining `max_agents` bypass where a third agent can still add a collaboration fragment after the voter cap is reached.
- Reproduced Windows teardown errors from locked SQLite temp DB files.
- Ran focused collab tests: 24 passed, 24 teardown errors.

### 14. Scottcjn/Rustchain#5958 - Approved

Review: https://github.com/Scottcjn/Rustchain/pull/5958#pullrequestreview-4329795174

Summary:
- Verified discovery tag matching treats `%` and `_` literally.
- Ran `python -m pytest tests\test_discovery.py -q --noconftest -o addopts=''` on Windows: 28 passed.

### 15. Scottcjn/Rustchain#5959 - Approved

Review: https://github.com/Scottcjn/Rustchain/pull/5959#pullrequestreview-4329820434

Summary:
- Verified invalid onboarding metadata JSON returns a controlled error.
- Ran `python -m pytest tests\test_bottube_onboarding_example.py -q --noconftest -o addopts=''` on Windows: 5 passed.

### 16. Scottcjn/Rustchain#5960 - Approved

Review: https://github.com/Scottcjn/Rustchain/pull/5960#pullrequestreview-4329868297

Summary:
- Verified duplicate GreenTracker registration preserves existing mining session history.
- Ran `python -m pytest tests\test_green_tracker.py -q --noconftest -o addopts=''` on Windows: 20 passed.

### 17. Scottcjn/Rustchain#5961 - Approved

Review: https://github.com/Scottcjn/Rustchain/pull/5961#pullrequestreview-4329941538

Summary:
- Verified phone-only miner alert subscription upsert behavior.
- Ran `python -m pytest tests\test_miner_alerts_db.py tests\test_miner_alerts.py -q --noconftest -o addopts=''` on Windows: 11 passed.

### 18. Scottcjn/Rustchain#5962 - Approved

Review: https://github.com/Scottcjn/Rustchain/pull/5962#pullrequestreview-4329951048

Summary:
- Verified enveloped mining video miner payload parsing.
- Ran `python -m pytest tests\test_mining_video_pipeline.py -q --noconftest -o addopts=''` on Windows: 2 passed.

### 19. Scottcjn/Rustchain#5979 - Approved

Review: https://github.com/Scottcjn/Rustchain/pull/5979#pullrequestreview-4331466123

Summary:
- Verified miner checklist process-exit exceptions are no longer swallowed as node reachability failures.
- Verified macOS v2.5 miner checksum refresh matches the current file hash.
- Ran `python -m pytest tests\test_miner_checklist.py tests\test_install_miner_checksums.py tests\test_setup_miner_downloads.py -q --noconftest -o addopts=''` on Windows: 11 passed.

### 20. Scottcjn/Rustchain#5983 - Changes Requested

Review: https://github.com/Scottcjn/Rustchain/pull/5983#pullrequestreview-4331577173

Summary:
- Found that inserting `msg_id` into `p2p_seen_messages` before signature verification lets an invalid-signature packet poison the dedup table.
- Reproduced that a cloned `PING` with `signature = "bad-signature"` returns `invalid_signature`, then the original valid message returns `duplicate`.
- Ran `python -m pytest node\tests\test_p2p_hardening_phase2.py node\tests\test_p2p_handshake_negotiation.py -q --noconftest -o addopts=''` on Windows: 14 passed.

### 21. Scottcjn/Rustchain#5981 - Approved

Review: https://github.com/Scottcjn/Rustchain/pull/5981#pullrequestreview-4331619804

Summary:
- Verified webhook `Content-Length` parsing returns the existing 400 path for missing, malformed, zero, and negative values.
- Verified the macOS v2.5 miner checksum refresh matches the current file hash.
- Ran `python -m pytest tests\test_webhook_client_helpers.py tests\test_install_miner_checksums.py tests\test_setup_miner_downloads.py -q --noconftest -o addopts=''` on Windows: 12 passed.

### 22. Scottcjn/Rustchain#5984 - Approved

Review: https://github.com/Scottcjn/Rustchain/pull/5984#pullrequestreview-4331655530

Summary:
- Verified the RustChain health CLI counts `/api/miners` responses wrapped in an `items` envelope.
- Confirmed the regression test checks both miner count and returned rows.
- Ran `python -m pytest tests\test_rustchain_health.py tests\test_rustchain_health_cli.py -q --noconftest -o addopts=''` on Windows: 13 passed.

### 23. Scottcjn/Rustchain#5980 - Changes Requested

Review: https://github.com/Scottcjn/Rustchain/pull/5980#pullrequestreview-4331710058

Summary:
- Found that the two new pending-confirm regression tests leave SQLite temp DB files locked on Windows.
- Reproduced `PermissionError: [WinError 32]` at `db_path.unlink()` in both new tests after endpoint assertions pass.
- Ran `python -m pytest tests\test_signed_transfer_replay.py -q` on Windows after installing declared test dependencies: 5 passed, 2 failed.

### 24. Scottcjn/Rustchain#5925 - Approved

Review: https://github.com/Scottcjn/Rustchain/pull/5925#pullrequestreview-4331729657

Summary:
- Verified the updated async SDK head still applies object-response validation only to dict-typed public methods.
- Confirmed list/generic methods remain on `_request()` and transfer preserves the public `TransferError` wrapping contract.
- Ran `PYTHONPATH=sdk python -m pytest sdk\tests\test_async_client.py -q` on Windows: 27 passed.

### 25. Scottcjn/Rustchain#5982 - Approved

Review: https://github.com/Scottcjn/Rustchain/pull/5982#pullrequestreview-4331781127

Summary:
- Verified the Darwin `setup_miner.py` pin and `miners/checksums.sha256` now match the checked-in macOS v2.5 miner artifact.
- Confirmed the artifact SHA256 is `163fafcf751d8fbd41bf936facaeb366c042f467fa34b79f2c4c0a45472ef70f`.
- Ran `python -m pytest tests\test_install_miner_checksums.py tests\test_setup_miner_downloads.py -q --noconftest -o addopts=''` on Windows: 5 passed.

### 26. Scottcjn/Rustchain#5966 - Approved

Review: https://github.com/Scottcjn/Rustchain/pull/5966#pullrequestreview-4331831635

Summary:
- Verified low-entropy validator runs remove stale `relic_rewards.json` output from earlier qualifying runs.
- Confirmed the high-entropy badge path remains covered by the focused tests.
- Ran `python -m pytest tests\test_validator_core_with_badge.py -q --noconftest -o addopts=''` on Windows: 6 passed.

## Local Verification Evidence

All reviews include direct review links with detailed validation notes. Commands were run on Windows where applicable and included focused pytest, `py_compile`, and `git diff --check` runs for touched files.

## Reward Request

Please assess under bounty #73's code review reward structure.

At the posted minimum of 5 RTC per accepted review, 26 accepted reviews equal 130 RTC, or $13.00 equivalent at the posted reference rate of 1 RTC = $0.10 USD.
