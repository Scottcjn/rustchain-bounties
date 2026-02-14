# RustChain Miner Setup Guide

Step-by-step guide to run a RustChain miner on real hardware (RIP-200 Proof of Attestation).

## Prerequisites

- Real hardware (no VMs). VMs may attest, but rewards can be penalized or denied.
- Python 3.8+ installed.
- A `miner_id` (wallet name). This is the identifier you pass to the miner and use to check balance.

## Get The Miner Scripts

Recommended: clone the main RustChain repo (this keeps you on the latest miner updates):

```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
```

If you prefer direct downloads, use a platform-specific miner script from the repo:

```bash
# Linux (x86_64)
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/miners/linux/rustchain_linux_miner.py -o rustchain_linux_miner.py

# macOS (Intel / Apple Silicon)
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/miners/macos/rustchain_mac_miner_v2.4.py -o rustchain_mac_miner_v2.4.py

# Windows (GUI miner, run with Python)
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/miners/windows/rustchain_windows_miner.py -o rustchain_windows_miner.py
```

## Run A Miner

### Linux

From the repo:

```bash
python3 miners/linux/rustchain_linux_miner.py --wallet YOUR_MINER_ID
```

If you downloaded the script directly:

```bash
python3 rustchain_linux_miner.py --wallet YOUR_MINER_ID
```

Note: the Linux miner currently uses the default node URL configured in the script (`NODE_URL`). To point at a different node, edit that constant.

### macOS

From the repo:

```bash
python3 miners/macos/rustchain_mac_miner_v2.4.py --wallet YOUR_MINER_ID --node https://50.28.86.131
```

### Windows

Run the GUI miner from source:

```powershell
python miners\\windows\\rustchain_windows_miner.py
```

Then enter your wallet/miner ID in the UI and start mining.

## Verify It Is Working

### Check That Your Miner Is Attesting

```bash
curl -sk https://50.28.86.131/api/miners | python3 - <<'PY'
import json, sys
miners = json.load(sys.stdin)
print("active_miners:", len(miners))
PY
```

### Check Your Balance

```bash
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_MINER_ID"
```

## Autostart (Linux, systemd)

Create a service so the miner starts on boot:

```bash
sudo tee /etc/systemd/system/rustchain-miner.service >/dev/null <<'UNIT'
[Unit]
Description=RustChain Miner
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/Rustchain
ExecStart=/usr/bin/python3 /home/YOUR_USERNAME/Rustchain/miners/linux/rustchain_linux_miner.py --wallet YOUR_MINER_ID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
UNIT
```

Then:

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now rustchain-miner.service
sudo systemctl status rustchain-miner.service
```

## Hardware Multipliers (Current Defaults)

| Device | Multiplier |
|--------|------------|
| PowerPC G4 | 2.5x |
| PowerPC G5 | 2.0x |
| POWER8 | 1.5x |
| Apple Silicon | 1.2x |
| Modern x86 | 1.0x |

## Troubleshooting

- You do not show up in `/api/miners`: wait a few minutes, verify the node is reachable (`/health`), and confirm you're on real hardware.
- SSL errors: use `curl -k` / `requests(..., verify=False)` when testing against the self-signed cert.
