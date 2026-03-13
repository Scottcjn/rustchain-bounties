# Install RustChain Miner via Homebrew

**Bounty**: #1612
**Value**: 5 RTC (~$0.5)

---

## Prerequisites

- macOS or Linux with Homebrew installed
- Rust installed (will be installed automatically)

---

## Installation Steps

### 1. Install Homebrew (if not installed)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Add RustChain Tap

```bash
brew tap Scottcjn/rustchain-bounties
```

### 3. Install RustChain Miner

```bash
brew install rustchain-miner
```

### 4. Verify Installation

```bash
rustchain-miner --version
```

### 5. Configure Wallet

Create a wallet address:

```bash
rustchain-miner --wallet <your-wallet-address>
```

### 6. Start Mining

```bash
rustchain-miner --wallet <your-wallet> --node https://50.28.86.131
```

---

## Configuration

Edit `~/.rustchain-miner/config.toml`:

```toml
[wallet]
address = "your-wallet-address"

[node]
url = "https://50.28.86.131"

[mining]
threads = 4
```

---

## Uninstall

```bash
brew uninstall rustchain-miner
brew untap Scottcjn/rustchain-bounties
```

---

## Troubleshooting

### Issue: Rust not found

```bash
brew install rust
```

### Issue: Permission denied

```bash
sudo chown -R $(whoami) $(brew --prefix)
```

---

## Support

- GitHub Issues: https://github.com/Scottcjn/rustchain-bounties/issues
- Documentation: https://github.com/Scottcjn/RustChain

---

**Ready for PR submission!** 🚀
