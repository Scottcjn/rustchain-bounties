# RIP-309: Rotating Measurement Freshness (The Proxy Horizon)

## 🏗️ Status: Phase 1 (Core Rotation) Implemented

## 📝 Specification Summary

RIP-309 introduces **Measurement Nonces** derived from historical block hashes to rotate trust metrics every epoch. This specifically addresses the **Proxy Horizon** problem, where static trust signals become gameable targets once published.

### 🛡️ Layer 2: Fingerprint Check Rotation

The core consensus now includes a pool of 6 hardware fingerprint checks:
1. `clock_drift`
2. `cache_timing`
3. `simd_bias`
4. `thermal_drift`
5. `instruction_jitter`
6. `anti_emulation`

Each epoch, a **4-of-6 rotation** is enforced. Only the selected checks contribute to the reward weight.

### 🧠 Nonce Derivation

```python
nonce = sha256(prev_epoch_last_block_hash + b"measurement_nonce")
seed = int.from_bytes(nonce[:4], 'big')
active_checks = random.Random(seed).sample(FP_CHECK_POOL, 4)
```

## 🚀 Phase 1 Implementation Details (RIP-309.1)

- **Node Implementation**: `rip_200_round_robin_1cpu1vote.py` updated to support deterministic rotation.
- **Reward Engine**: Integrated into `finalize_epoch` in `rustchain_v2_integrated`.
- **Validation**: Strict enforcement — if an active rotating check fails, the miner weight drops to **0.000000001 (VM status)**.

## 📈 Next Phases

- **Phase 2**: Observation Window Jitter (6h - 168h).
- **Phase 3**: Behavioral Metric Rotation (5-of-10 metrics).
- **Phase 4**: Nonce-scoped Challenge-Response Protocol.

---
*Authored by Michael Sovereign (@MichaelSovereign) — 2026-04-12*
