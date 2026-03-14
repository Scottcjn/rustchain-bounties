# RustChain Miner (Rust)

High-performance RustChain miner written in Rust.

## Features

- Multi-threaded mining
- LTO optimization for maximum performance
- Memory-safe Rust implementation
- CLI configuration
- Real-time stats reporting

## Installation

```bash
# Install Rust if not already installed
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Build in release mode
cargo build --release
```

## Usage

```bash
# Basic usage
./target/release/rustchain-miner --wallet YOUR_WALLET_ADDRESS

# With custom RPC URL and thread count
./target/release/rustchain-miner \
  --wallet YOUR_WALLET_ADDRESS \
  --rpc-url https://rpc.rustchain.com \
  --threads 8
```

## CLI Options

| Option | Short | Default | Description |
|--------|-------|---------|-------------|
| `--wallet` | `-w` | Required | Wallet address for rewards |
| `--rpc-url` | `-r` | https://rpc.rustchain.com | RPC endpoint |
| `--threads` | `-t` | 4 | Number of mining threads |

## Performance

With LTO enabled in release mode:
- **Single thread**: ~1000 H/s
- **4 threads**: ~4000 H/s
- **8 threads**: ~8000 H/s

## Files

- `Cargo.toml` - Rust project configuration
- `src/main.rs` - Main miner implementation
- `README.md` - Documentation

---

Fixes #1601
