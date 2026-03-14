# Installation Guide

## Quick Install

```bash
brew tap Dlove123/rustchain
brew install rustchain-miner
```

## Manual Installation

1. Download the formula:
   ```bash
   curl -O https://raw.githubusercontent.com/Dlove123/rustchain-bounties/main/1612-homebrew-formula/rustchain-miner.rb
   ```

2. Install:
   ```bash
   brew install ./rustchain-miner.rb
   ```

3. Verify:
   ```bash
   rustchain-miner --version
   ```

## Troubleshooting

### Rust not installed
```bash
brew install rust
```

### OpenSSL errors
```bash
brew install openssl
export OPENSSL_DIR=$(brew --prefix openssl)
```

---

Part of Bounty #1612
