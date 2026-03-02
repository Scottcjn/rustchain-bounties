# RustChain Miner Setup Guide

## Clone the Repo

```bash
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain
```

## Install Dependencies (Python)

```bash
pip install -r requirements.txt
```

### Check That Your Miner Is Attesting

Instead of using pipe commands, use separate steps:

```bash
# Step 1: Download miner data to file
curl -sk https://50.28.86.131/api/miners > miners_data.json

# Step 2: Process with Python script
python3 -c "
import json
with open('miners_data.json', 'r') as f:
    miners = json.load(f)
print('active_miners:', len(miners))
"
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

## Weekly Payout + Upgrade Scan

Maintainers can run a unified node/miner scan to decide weekly payouts and catch outdated/wrong-node miners:

```bash
python3 scripts/node_miner_weekly_scan.py
```

Useful flags:

```bash
# Save machine + human reports
python3 scripts/node_miner_weekly_scan.py \
  --out-json reports/node_miner_scan.json \
  --out-md reports/node_miner_scan.md

# Compare against expected miner IDs (flags missing miners for outreach)
python3 scripts/node_miner_weekly_scan.py \
  --expected-miners-file expected_miners.txt
```

See: `docs/NODE_MINER_WEEKLY_SCAN.md`