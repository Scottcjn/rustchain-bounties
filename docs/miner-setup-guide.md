# Miner Setup Guide

> Step-by-step instructions for setting up a RustChain miner on Windows, macOS, and Linux.

## Prerequisites

- A device that can run Rust (see **Hardware Requirements** below)
- A RustChain wallet address (get one via [Discord](https://discord.gg/VqVVS2CW9Q) or use the `rustchain-cli`)
- At least **1 GB RAM** and **500 MB** free disk space

## Hardware Requirements

RustChain uses **Proof-of-Antiquity**—older hardware earns higher rewards. The following architectures are supported:

| Architecture | Minimum Age Bonus | Notes |
|--------------|-------------------|-------|
| x86_64 (modern) | 1x | Standard |
| x86_64 (pre-2015) | 2x-3x | e.g., Intel Core 2 Duo, AMD Phenom |
| ARMv7 (32-bit) | 3x-5x | Raspberry Pi 2/3, old phones |
| PowerPC | 5x-10x | Legacy Mac, old gaming consoles |

## Step 1: Install Rust

```bash
# macOS / Linux
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Windows: Download from https://rustup.rs
```

> Ensure `cargo` is in your PATH after installation.

## Step 2: Clone the Miner Repository

```bash
git clone https://github.com/Scottcjn/RustChain.git
cd RustChain
```

## Step 3: Build the Miner Binary

```bash
cargo build --release --bin rustchain-miner
```

On older hardware, this may take 10–30 minutes.

## Step 4: Configure Your Wallet

Create a file named `miner.toml` in the project root:

```toml
[wallet]
address = "0xYOUR_WALLET_ADDRESS"

[node]
endpoint = "http://50.28.86.131:31415"

[mining]
threads = 2
```

## Step 5: Start Mining

```bash
./target/release/rustchain-miner --config miner.toml
```

You should see log output like:

```
[INFO] Connected to node at 50.28.86.131:31415
[INFO] Starting mining with 2 threads...
[SUCCESS] Block mined! Reward: 10.5 RTC
```

## Platform-Specific Tips

### Windows
- Use PowerShell (not CMD) for environment variables
- Install [Build Tools for Visual Studio](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022) if compilation fails
- Run miner as administrator for better performance

### macOS (ARM/M1/M2)
- Use `cargo build --release --target aarch64-apple-darwin` if on Apple Silicon
- Consider using `rosetta2` for x86_64 builds (older hardware bonus may not apply)

### Linux (Raspberry Pi / ARM)
```bash
sudo apt update && sudo apt install build-essential pkg-config libssl-dev
cargo build --release --target armv7-unknown-linux-gnueabihf
```

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `Connection refused` | Ensure node is running. Check status with `curl http://50.28.86.131:31415/api/node/health` |
| `Out of memory` | Reduce `threads` in miner.toml |
| `Build fails` | Update Rust: `rustup update` and clean: `cargo clean` |

## Further Reading

- [Node Operator Guide](node-operator-guide.md)
- [Python SDK Tutorial](python-sdk-tutorial.md)
- [RustChain Bounties](https://github.com/Scottcjn/rustchain-bounties)

---

*This guide is part of the [RustChain Documentation Sprint](https://github.com/Scottcjn/rustchain-bounties/issues/72).*