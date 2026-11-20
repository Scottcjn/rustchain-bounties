# Self-Audit: rustchain-miner/src/miner.rs

## Wallet
wuxiaobinsh-gif

## Module reviewed
- Path: rustchain-miner/src/miner.rs
- Commit: 92888df054821c3355836ae0cd442b2cf29a1280
- Lines reviewed: 1-420 (full file)

## Deliverable: 3 specific findings

1. **miner_pubkey field contains wallet address instead of Ed25519 public key**
   - Severity: medium
   - Location: rustchain-miner/src/miner.rs:269
   - Description: In the enrollment payload JSON, `miner_pubkey` is set to `self.wallet` (the RTC wallet address like `RTC9a39ca2c...`) instead of `self.public_key_hex` (the Ed25519 verifying key). The field name implies it should contain a public key, and a duplicate correct field `public_key` already exists. If the node validates pubkey format, enrollment will be rejected.
   - Reproduction: Inspect the `enroll()` function at line ~260-280, observe the JSON payload construction where `miner_pubkey: self.wallet` is set alongside `public_key: self.public_key_hex`. Compare with the signing code at line ~112 which correctly generates the Ed25519 keypair.

2. **Wallet address written to world-readable temp file on multi-user systems**
   - Severity: low
   - Location: rustchain-miner/src/miner.rs:370-375
   - Description: The `run()` function saves the wallet address to `/tmp/rustchain_miner_wallet.txt` (or `C:\temp\...` on Windows) with default permissions. On shared systems, any user can read this file to obtain the miner's wallet address.
   - Reproduction: After starting the miner, run `cat /tmp/rustchain_miner_wallet.txt` as any user on the system to confirm the wallet address is exposed.

3. **Attestation TTL not validated — no upper bound check**
   - Severity: informational
   - Location: rustchain-miner/src/miner.rs:220-227
   - Description: The `attestation_valid_until` value is set to `now + self.config.attestation_ttl_secs` without validating that the TTL is within acceptable bounds. If `config.attestation_ttl_secs` is misconfigured to an extremely large value (e.g., usize::MAX), the attestation would appear valid indefinitely.
   - Reproduction: Check if `Config::attestation_ttl_secs` has bounds validation in config.rs. Search for `attestation_ttl` in the codebase to determine if upper/lower bounds are enforced.

## Known failures of this audit
- I did not verify whether the node-side enrollment endpoint actually validates the `miner_pubkey` field format. The bug report is based on API contract inspection, not live testing against a node.
- The `hardware.rs` and `attestation.rs` modules were not reviewed, only the miner loop in `miner.rs`.
- I did not check whether the `transport.probe_transport().await` call in `Miner::new()` handles timeout or error conditions that could cause a silent failure.

## Confidence
- Overall confidence: 0.75
- Per-finding confidence: [0.85, 0.8, 0.6]
  - Finding 1 has high confidence (clear code inspection showing wallet vs pubkey mismatch)
  - Finding 2 has high confidence (file permission issue is observable)
  - Finding 3 has medium confidence (depends on whether config validation exists elsewhere)

## What I would test next
- Live test: connect a miner to a testnet node and observe whether enrollment succeeds with the current `miner_pubkey` = wallet address code
- Check `config.rs` for `attestation_ttl_secs` bounds validation
- Review `transport.rs` for error handling in `probe_transport()`
