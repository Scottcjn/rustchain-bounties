# rustchain-miner

Native Rust miner for [RustChain](https://github.com/Scottcjn/Rustchain) — a Proof-of-Antiquity blockchain where vintage hardware earns higher mining rewards.

## Features

- **Single binary** — no Python, pip, or venv needed
- **Full RIP-PoA fingerprinting** — all 6 hardware fingerprint checks in native Rust
- **Inline assembly** — `rdtsc` (x86_64) / `mftb` (PowerPC) for precise timing
- **Cross-platform** — x86_64, aarch64, PowerPC targets
- **Self-signed TLS** — works with the RustChain node out of the box

## Quick Start

```bash
# Build
cargo build --release

# Start mining
./target/release/rustchain-miner --wallet YOUR_WALLET_NAME

# Run fingerprint checks only
./target/release/rustchain-miner --test-only

# Show the attestation payload (without submitting)
./target/release/rustchain-miner --wallet YOUR_WALLET --show-payload

# Dry run (build + display payload, no submission)
./target/release/rustchain-miner --wallet YOUR_WALLET --dry-run

# Use a custom node
./target/release/rustchain-miner --wallet YOUR_WALLET --node https://your-node:port
```

## RIP-PoA Fingerprint Checks

| # | Check | What It Measures |
|---|-------|-----------------|
| 1 | Clock-Skew & Oscillator Drift | Timing variance from `rdtsc`/`mftb` |
| 2 | Cache Timing Fingerprint | L1/L2/L3 latency sweep across buffer sizes |
| 3 | SIMD Unit Identity | SSE/AVX/AltiVec/NEON instruction timing |
| 4 | Thermal Drift Entropy | Entropy quality across thermal states |
| 5 | Instruction Path Jitter | Cycle-level jitter across int/FP/branch units |
| 6 | Anti-Emulation | VM/hypervisor detection |

## Architecture Detection

| CPU Pattern | Family | Arch | Multiplier |
|------------|--------|------|-----------|
| PowerPC 7450/7447/7455 | PowerPC | g4 | 2.5x |
| PowerPC 970 | PowerPC | g5 | 2.0x |
| PowerPC 750 | PowerPC | g3 | 1.8x |
| Apple M1/M2/M3 | ARM | apple_silicon | 1.2x |
| Core 2 | x86_64 | core2duo | 1.3x |
| Everything else | x86_64 | modern | 1.0x |

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Node health check |
| `/epoch` | GET | Current epoch info |
| `/attest/challenge` | POST | Request attestation nonce |
| `/attest/submit` | POST | Submit attestation payload |
| `/epoch/enroll` | POST | Enroll in current epoch |
| `/wallet/balance` | GET | Check RTC balance |

Default node: `https://50.28.86.131` (self-signed cert)

## Cross-Compilation

```bash
# Install cross
cargo install cross

# Build for targets
cross build --release --target x86_64-unknown-linux-musl
cross build --release --target aarch64-unknown-linux-musl
cross build --release --target powerpc64-unknown-linux-gnu
```

## License

MIT
