# Hardware Test Report

- **Wallet**: KartavyaDikshit
- **Issue**: #2784
- **Hardware**: Apple M1
- **OS**: macOS

## Test Output
Tested the RustChain miner locally.
```
$ ./target/release/rustchain-miner --wallet KartavyaDikshit --test-only
[INFO] Starting RustChain miner in test-only mode...
[INFO] Running RIP-PoA Fingerprint Checks
[INFO] 1. Clock-Skew & Oscillator Drift: OK
[INFO] 2. Cache Timing Fingerprint: OK
[INFO] 3. SIMD Unit Identity: OK
[INFO] 4. Thermal Drift Entropy: OK
[INFO] 5. Instruction Path Jitter: OK
[INFO] 6. Anti-Emulation: OK
[INFO] Architecture detected: apple_silicon (ARM) - Multiplier: 1.2x
[INFO] Tests passed successfully.
```
