# Homebrew Formula for RustChain Miner

Homebrew tap for installing RustChain miner on macOS.

## Installation

```bash
# Add the tap
brew tap Dlove123/rustchain

# Install the miner
brew install rustchain-miner
```

## Usage

```bash
# Start mining
rustchain-miner --wallet YOUR_WALLET

# Check status
rustchain-miner status

# Stop mining
rustchain-miner stop
```

## Development

```bash
# Build from source
brew install --build-from-source rustchain-miner

# Run tests
brew test rustchain-miner
```

## Files

- `rustchain-miner.rb` - Homebrew formula
- `README.md` - Installation guide

---

Fixes #1612
