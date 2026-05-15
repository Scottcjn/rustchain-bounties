# RustChain Miner Setup Guide (Quick Start)

> This is a quick-start supplement. For the full guide, see [MINERS_SETUP_GUIDE.md](./MINERS_SETUP_GUIDE.md).

## Prerequisites

- Real hardware (no VMs). VMs may attest, but rewards can be penalized.
- Python 3.8+
- A `miner_id` (wallet name)

## Step 1: Get Miner Scripts

```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
```

Or download directly for your platform:

```bash
# Linux (x86_64)
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/miners/linux/rustchain_linux_miner.py -o miner.py

# macOS (Intel / Apple Silicon)
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/miners/macos/rustchain_mac_miner_v2.4.py -o miner.py

# Windows
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/miners/windows/rustchain_windows_miner.py -o miner.py
```

## Step 2: Generate Miner ID

```bash
python3 miner.py --keygen
```

This creates your miner ID and keys. Save the output — this is your wallet identifier.

## Step 3: Start Mining

```bash
# Linux/macOS
python3 miner.py --miner-id YOUR_MINER_ID

# Windows
python miner.py --miner-id YOUR_MINER_ID
```

## Step 4: Monitor

```bash
# Check your balance
curl -k https://50.28.86.131/balance/YOUR_MINER_ID | jq .

# Check current epoch
curl -k https://50.28.86.131/epoch | jq .

# Check node health
curl -k https://50.28.86.131/health | jq .
```

## Common Issues

| Issue | Solution |
|-------|----------|
| SSL error | Use `-k` flag with curl |
| "not enrolled" | Enroll in epoch via miner script |
| VM detected | Use real hardware |
| Python error | Ensure Python 3.8+ |

For detailed setup including hardware requirements, reward structure, and troubleshooting, see [MINERS_SETUP_GUIDE.md](./MINERS_SETUP_GUIDE.md).
