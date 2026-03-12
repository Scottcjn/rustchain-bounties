# Homebrew Installation Guide - RustChain Miner (Native Rust)

> **Issue #1612**: Create a Homebrew formula for RustChain miner with install/test instructions and practical caveats.

## Overview

This Homebrew formula provides a native Rust installation method for the RustChain Proof-of-Antiquity Miner on macOS and Linux.

**Key Benefits:**
- Single binary installation (no Python runtime required)
- Automatic dependency management via Homebrew
- Native performance with full RIP-PoA fingerprinting
- Easy updates via `brew upgrade`

---

## Prerequisites

- **macOS** 10.15+ or **Linux** (glibc 2.17+)
- **Homebrew** installed:
  ```bash
  /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
  ```
- **Network access** to RustChain node

---

## Installation

### Option A: Install from Local Formula (Development)

```bash
# Clone the repository
git clone https://github.com/Scottcjn/rustchain-bounties.git
cd rustchain-bounties

# Install from formula file
brew install ./homebrew/rustchain-miner.rb
```

### Option B: Install from Tap (Production - Recommended)

```bash
# Add the RustChain tap (once)
brew tap Scottcjn/rustchain-bounties

# Install the miner
brew install rustchain-miner
```

### Option C: Install from Raw URL

```bash
brew install https://raw.githubusercontent.com/Scottcjn/rustchain-bounties/main/homebrew/rustchain-miner.rb
```

---

## Usage

### Basic Mining

```bash
# Run with auto-generated wallet
rustchain-miner

# Run with specific wallet ID
rustchain-miner --wallet YOUR_WALLET_ID

# Run in test mode (fingerprint checks only, no mining)
rustchain-miner --test-only

# Show attestation payload (without submitting)
rustchain-miner --wallet YOUR_WALLET --show-payload

# Dry run (build + display payload, no submission)
rustchain-miner --wallet YOUR_WALLET --dry-run

# Use custom node URL
rustchain-miner --wallet YOUR_WALLET --node https://your-node:port
```

### Check Status

```bash
# View miner help
rustchain-miner --help

# Check if miner is running
ps aux | grep rustchain-miner

# Check miner version
rustchain-miner --version
```

---

## Hardware Multipliers

The RustChain Proof-of-Antiquity protocol rewards vintage hardware:

| CPU Pattern | Architecture | Multiplier |
|------------|--------------|-----------|
| PowerPC 7450/7447/7455 | PowerPC G4 | 2.5x |
| PowerPC 970 | PowerPC G5 | 2.0x |
| PowerPC 750 | PowerPC G3 | 1.8x |
| Apple M1/M2/M3 | Apple Silicon | 1.2x |
| Core 2 Duo | x86_64 | 1.3x |
| Modern CPUs | x86_64/ARM64 | 1.0x |

---

## RIP-PoA Fingerprint Checks

The miner performs 6 hardware fingerprint checks:

1. **Clock-Skew & Oscillator Drift** - Timing variance from `rdtsc`/`mftb`
2. **Cache Timing Fingerprint** - L1/L2/L3 latency sweep
3. **SIMD Unit Identity** - SSE/AVX/AltiVec/NEON instruction timing
4. **Thermal Drift Entropy** - Entropy quality across thermal states
5. **Instruction Path Jitter** - Cycle-level jitter across execution units
6. **Anti-Emulation** - VM/hypervisor detection

---

## Updating

```bash
# Update Homebrew
brew update

# Upgrade rustchain-miner
brew upgrade rustchain-miner
```

---

## Uninstalling

```bash
brew uninstall rustchain-miner
```

---

## Troubleshooting

### Build fails with Rust version error

Ensure you have Rust 1.70 or later:
```bash
rustc --version
# Should be 1.70.0 or newer
```

Update Rust:
```bash
rustup update
```

### Network connection errors

The miner needs to connect to the RustChain node. Check connectivity:
```bash
curl -k https://50.28.86.131/health
```

### Permission denied errors

The miner runs as your user (no root required). If you see permission errors:
```bash
# Check Homebrew permissions
brew doctor
```

---

## Security Notes

- ⚠️ **Never share your wallet ID** - This is your mining identity
- 🔒 **Miner runs as your user** - No root/sudo required
- ✅ **Checksums verified** - Homebrew verifies download integrity
- 📦 **Source available** - Full source code at https://github.com/Scottcjn/rustchain-bounties

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Node health check |
| `/epoch` | GET | Current epoch info |
| `/attest/challenge` | POST | Request attestation nonce |
| `/attest/submit` | POST | Submit attestation payload |
| `/epoch/enroll` | POST | Enroll in current epoch |
| `/wallet/balance` | GET | Check RTC balance |

Default node: `https://50.28.86.131` (self-signed cert, use `-k` with curl)

---

## Development

### Building from Source

```bash
cd rustchain-miner
cargo build --release
```

### Running Tests

```bash
cd rustchain-miner
cargo test
```

### Cross-Compilation

```bash
# Install cross
cargo install cross

# Build for different targets
cross build --release --target x86_64-unknown-linux-musl
cross build --release --target aarch64-unknown-linux-musl
cross build --release --target powerpc64-unknown-linux-gnu
```

---

## Support

- **Issues**: https://github.com/Scottcjn/rustchain-bounties/issues
- **Documentation**: https://github.com/Scottcjn/rustchain-bounties/tree/main/rustchain-miner
- **Community**: Join RustChain Discord/Telegram

---

## License

MIT License - See [LICENSE](../rustchain-miner/LICENSE) for details.
