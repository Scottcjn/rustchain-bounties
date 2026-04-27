# Self-Audit: replay_defense.py + node/hardware_fingerprint_replay.py

## Wallet
RTC019e78d600fb3131c29d7ba80aba8fe644be426e

## Module reviewed
- Path: replay_defense.py + node/hardware_fingerprint_replay.py
- Commit: b6606b18cd45cf69446ad7f46ad53814fece62a6
- Lines reviewed: whole-file (both modules)

## Deliverable: 3 specific findings

1. **Rate-limit bypass via hardware_id=None silently allows unlimited submissions**
   - Severity: high
   - Location: node/hardware_fingerprint_replay.py:381-382
   - Description: When `hardware_id` is None/empty, `check_fingerprint_rate_limit()` returns `(True, "no_hardware_id", None)` — effectively bypassing all rate limiting. An attacker can simply omit or nullify the hardware_id field in their fingerprint submission to submit unlimited attestation requests. The calling code in replay_defense.py:134 `_compute_hardware_id()` returns None for any fingerprint that lacks cache_timing.cache_hash, which an attacker controls.
   - Reproduction: Submit attestation requests with fingerprint `{"checks": {}}` — no cache_timing data. The hardware_id will be None, rate limit is skipped, and all submissions pass through.

2. **Entropy collision tolerance of 0.95 is dangerously high — enables near-duplicate fingerprints from different wallets**
   - Severity: medium
   - Location: node/hardware_fingerprint_replay.py:30 — `ENTROPY_HASH_COLLISION_TOLERANCE = 0.95`
   - Description: The constant is defined but never actually used in `check_entropy_collision()`. The function does an exact-match comparison (`WHERE entropy_profile_hash = ?`) rather than a similarity comparison. This means the 0.95 tolerance is dead code — two entropy profiles that are 96% identical will NOT be flagged as collisions. The gap between the stated tolerance and actual behavior means near-duplicate entropy profiles from Sybil wallets will pass undetected.
   - Reproduction: Create two miners with identical CPU/cache profiles but slightly different `jitter_cv` values (e.g., 0.0234 vs 0.0235). The entropy hashes will differ by one character. Neither exact-match check will flag them, despite being 95%+ similar.

3. **Replay window of 300 seconds allows 50 fingerprint resubmissions per wallet before expiry**
   - Severity: medium
   - Location: node/hardware_fingerprint_replay.py:27 — `REPLAY_WINDOW_SECONDS = 300` combined with `MAX_FINGERPRINT_SUBMISSIONS_PER_HOUR = 10`
   - Description: The 5-minute replay window means that after 300 seconds, an attacker can resubmit the exact same fingerprint with a new nonce and it will be accepted as "fresh." Combined with the rate limit of 10/hour, an attacker can submit the same fingerprint 10 times per hour, every hour, indefinitely. The `fingerprint_history` table exists for anomaly detection but `detect_fingerprint_anomalies()` only logs — it never blocks submissions.
   - Reproduction: Submit fingerprint F1 at T=0, then again at T=301 with new nonce. The replay check finds no match (window expired), rate limit counter shows 1/10, and submission succeeds.

## Known failures of this audit
- I did not test the actual `/attest/submit` endpoint integration — I only read the defense modules in isolation, not the Flask route handler in `rustchain_v2_integrated_v2.2.1_rip200.py` lines 2702-2780
- I could not verify whether the entropy_profile_hash collision check uses a fuzzy comparison in practice (the SQL does exact match, but there might be pre-filtering I missed)
- My confidence in finding #2 is lower because ENTROPY_HASH_COLLISION_TOLERANCE might be used by a caller I didn't trace

## Confidence
- Overall confidence: 0.78
- Per-finding confidence: [0.92, 0.65, 0.78]

## What I would test next
- Submit 20 attestation requests with `hardware_id=None` to confirm rate-limit bypass on a live node
- Run the `replay_attack_poc.py` script included in the repo against a local node with modified entropy profiles to test the collision detection gap
- Add a unit test that submits the same fingerprint after the 300s window expires to confirm re-acceptance behavior
