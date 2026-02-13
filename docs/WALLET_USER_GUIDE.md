# RustChain Wallet User Guide

Complete guide for RustChain wallet usage, including all wallet editions and management features.

## Overview

RustChain offers multiple wallet options for different use cases:

| Wallet Type | Best For | Features |
|--------------|----------|----------|
| CLI Wallet | Developers | Full API access |
| Desktop App | Power users | GUI + advanced features |
| Mobile Wallet | everyday use | Touch-friendly |
| Web Wallet | Quick access | No installation |
| Hardware Wallet | Maximum security | Cold storage |

---

## CLI Wallet

### Installation

```bash
# Download CLI wallet
curl -sk https://50.28.86.131/wallet/download -o rustchain-wallet
chmod +x rustchain-wallet
sudo mv rustchain-wallet /usr/local/bin/
```

### Basic Commands

```bash
# Create new wallet
rustchain-wallet create --name "my-wallet"

# Check balance
rustchain-wallet balance --wallet "my-wallet"

# Send transaction
rustchain-wallet send \
  --from "my-wallet" \
  --to "recipient-wallet" \
  --amount 10.5

# List all wallets
rustchain-wallet list
```

### Environment Setup

```bash
export RUSTCHAIN_WALLET="my-wallet"
export RUSTCHAIN_NODE="https://50.28.86.131"
```

---

## Desktop Wallet

### Installation

#### macOS

```bash
# Download DMG
curl -sk https://50.28.86.131/wallet/desktop/dmg -o RustChain.dmg
hdiutil attach RustChain.dmg
cp -r "/Volumes/RustChain/RustChain.app" /Applications/
hdiutil detach /Volumes/RustChain
```

#### Linux

```bash
# Download AppImage
curl -sk https://50.28.86.131/wallet/desktop/appimage -o RustChain.AppImage
chmod +x RustChain.AppImage
./RustChain.AppImage
```

#### Windows

```powershell
# Download installer
Invoke-WebRequest -Uri "https://50.28.86.131/wallet/desktop.exe" -OutFile RustChain.exe
./RustChain.exe
```

### Features

- **Transaction history** - View all past transactions
- **Address book** - Save frequently used addresses
- **Multi-signature** - Require multiple approvals
- **Hardware wallet support** - Ledger, Trezor integration
- **Staking dashboard** - Track earning rewards

---

## Mobile Wallet

### Installation

| Platform | Download |
|-----------|----------|
| iOS | App Store: "RustChain Wallet" |
| Android | Play Store: "RustChain Wallet" |

### Setup

1. Download app from store
2. Create new wallet or import existing
3. Backup recovery phrase (12 words)
4. Set PIN code
5. Start using!

### Features

- **QR code scanning** - Easy address sharing
- **Biometric login** - Face ID / Fingerprint
- **Push notifications** - Transaction alerts
- **Offline mode** - Generate transactions without internet

---

## Web Wallet

### Access

Open in browser: https://wallet.rustchain.io

### Usage

```bash
# No installation required
# Connect with:
# - Browser wallet (MetaMask, Coinbase Wallet)
# - Private key
# - Keystore file
```

### Security Tips

- Always verify URL before connecting
- Use hardware wallet for large amounts
- Enable 2FA when available
- Never share private keys

---

## Wallet Editions Comparison

| Feature | CLI | Desktop | Mobile | Web |
|---------|-----|---------|--------|-----|
| Full node | ✅ | ❌ | ❌ | ❌ |
| Staking | ✅ | ✅ | ✅ | ✅ |
| Hardware wallet | ✅ | ✅ | ✅ | ✅ |
| Multi-sig | ✅ | ✅ | ❌ | ❌ |
| Gas optimization | ✅ | ❌ | ❌ | ❌ |
| Offline signing | ✅ | ✅ | ❌ | ❌ |

---

## Creating a Wallet

### Method 1: New Wallet

```bash
rustchain-wallet create my-wallet

# Output
Wallet created: my-wallet
Address: 0x7a2f3b5d4c1e9f0a8b7c6d5e4f3a2b1c
Recovery Phrase:
apple banana cherry date elderberry fig grape

⚠️ WRITE DOWN YOUR RECOVERY PHRASE!
```

### Method 2: Import Existing

```bash
# From recovery phrase
rustchain-wallet import \
  --phrase "apple banana cherry date elderberry fig grape" \
  --name "imported-wallet"

# From private key
rustchain-wallet import \
  --private-key "0x1234..." \
  --name "private-key-wallet"

# From keystore file
rustchain-wallet import \
  --keystore "/path/to/wallet.json" \
  --name "keystore-wallet"
```

---

## Sending Transactions

### Basic Send

```bash
rustchain-wallet send \
  --wallet "my-wallet" \
  --to "0xRecipientAddress" \
  --amount 10.0
```

### Advanced Options

```bash
# With custom gas price
rustchain-wallet send \
  --wallet "my-wallet" \
  --to "0xRecipientAddress" \
  --amount 10.0 \
  --gas-price 0.001

# Offline signing (for cold storage)
rustchain-wallet send \
  --wallet "cold-wallet" \
  --to "0xRecipientAddress" \
  --amount 10.0 \
  --offline \
  --output "signed-tx.json"

# Broadcast signed transaction
rustchain-wallet broadcast \
  --file "signed-tx.json"
```

### Batch Transactions

```bash
# Send to multiple recipients
rustchain-wallet send-batch \
  --wallet "my-wallet" \
  --recipients "0xaddr1:10,0xaddr2:20,0xaddr3:30"
```

---

## Receiving Transactions

### Get Your Address

```bash
rustchain-wallet address --wallet "my-wallet"
# Output: 0x7a2f3b5d4c1e9f0a8b7c6d5e4f3a2b1c
```

### QR Code

```bash
# Generate QR code for address
rustchain-wallet qr --wallet "my-wallet" --output address.png
```

### Request Payment

```bash
# Create payment request
rustchain-wallet request \
  --amount 25.0 \
  --memo "Payment for services" \
  --output "payment-request.json"
```

---

## Staking with Wallets

### Check Staking Status

```bash
rustchain-wallet staking status --wallet "my-wallet"
```

### Delegate Stake

```bash
# Delegate to a validator
rustchain-wallet staking delegate \
  --wallet "my-wallet" \
  --validator "validator-address" \
  --amount 100.0
```

### Undelegate Stake

```bash
# Start undelegation (21-day unbonding period)
rustchain-wallet staking undelegate \
  --wallet "my-wallet" \
  --amount 50.0
```

### Claim Rewards

```bash
# Claim staking rewards
rustchain-wallet staking claim --wallet "my-wallet"
```

---

## Security Best Practices

### Backup Your Wallet

```bash
# Export recovery phrase (keep offline!)
rustchain-wallet export phrase --wallet "my-wallet"

# Export encrypted keystore
rustchain-wallet export keystore \
  --wallet "my-wallet" \
  --output "/backup/wallet.json"
```

### Security Checklist

| Action | Importance |
|--------|------------|
| ✅ Write down recovery phrase | Critical |
| ✅ Store phrase offline | Critical |
| ✅ Use hardware wallet for large amounts | High |
| ✅ Verify URLs before connecting | High |
| ✅ Enable 2FA when available | Medium |
| ✅ Use unique passwords | High |
| ✅ Test with small amounts first | High |

### Hardware Wallet Setup

```bash
# Ledger
rustchain-wallet connect ledger

# Trezor
rustchain-wallet connect trezor
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Transaction stuck | Check network status, increase gas |
| Balance not updating | Wait for block confirmation |
| Cannot connect to node | Verify node URL, check internet |
| Recovery phrase not working | Check for typos, 12 words only |
| Wrong address used | Cannot reverse - always verify |

---

## Support

- **Help Center:** https://help.rustchain.io
- **Discord:** https://discord.gg/rustchain
- **GitHub Issues:** https://github.com/Scottcjn/rustchain-wallet/issues

---

*Last updated: 2026-02-12*
*Wallet Version: 1.5.0*
