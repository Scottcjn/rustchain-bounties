# RustChain Miner - Native Rust Implementation

A native Rust implementation of the RustChain miner with enhanced security features.

## Features

- **7 Hardware Fingerprint Checks:**
  1. CPU Architecture detection
  2. CPU Vendor ID verification
  3. Cache timing analysis
  4. Clock drift detection
  5. Instruction timing jitter
  6. Thermal characteristics
  7. Anti-emulation checks

- **Ed25519 Attestation:** Secure cryptographic signing
- **Cross-Platform:** Windows, macOS, Linux support
- **High Performance:** Native Rust with LTO optimization

## Building

```bash
cargo build --release
```

## Usage

```bash
# Create configuration
cp config.example.toml config.toml
# Edit config.toml with your miner_id

# Run the miner
cargo run --release
```

## Configuration

Edit `config.toml`:

```toml
rpc_endpoint = "https://rustchain.org/api"
miner_id = "your_miner_id_here"
interval_seconds = 60
```

## License

MIT
