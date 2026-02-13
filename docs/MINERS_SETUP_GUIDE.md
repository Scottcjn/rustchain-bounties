# RustChain Miner Setup Guide

Complete step-by-step guide to set up and run a RustChain miner on all platforms.

## Prerequisites

### System Requirements

| Requirement | Minimum | Recommended |
|------------|---------|-------------|
| CPU | 1 core | 2+ cores |
| RAM | 1 GB | 2 GB |
| Storage | 100 MB | 500 MB |
| Network | Broadband | Stable connection |
| Hardware | **Real hardware only** | No VMs allowed |

**Important:** RustChain uses RIP-200 Proof-of-Attestation consensus. Virtual machines will **not earn rewards**.

### Wallet ID

You need a RustChain wallet ID to receive rewards:
- Any string works on testnet (e.g., `my-miner-name`)
- Your wallet ID = your miner identifier
- Rewards accumulate automatically

---

## Quick Start

### 1. Download the Miner

```bash
# Option A: Clone the bounty repo
git clone https://github.com/Scottcjn/rustchain-bounties.git
cd rustchain-bounties

# Option B: Download miner script directly
curl -sk https://50.28.86.131/miner/download -o rustchain_miner.py
chmod +x rustchain_miner.py
```

### 2. Run the Miner

```bash
# Basic usage (replace YOUR_WALLET_ID with your chosen name)
python3 rustchain_miner.py --wallet YOUR_WALLET_ID --node https://50.28.86.131

# With custom port
python3 rustchain_miner.py --wallet my-miner --port 8080

# Verbose logging
python3 rustchain_miner.py --wallet my-miner --verbose
```

### 3. Verify It's Running

```bash
# Check active miners
curl -sk https://50.28.86.131/api/miners | python3 -c "import sys,json; miners=json.load(sys.stdin); print(f'Active miners: {len(miners)}'); [print(m['miner']) for m in miners if 'my-miner' in m['miner']]"

# Check your balance
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_WALLET_ID"
```

---

## Platform-Specific Setup

### Linux

#### Ubuntu/Debian

```bash
# Install Python 3
sudo apt update
sudo apt install -y python3 python3-pip curl

# Download and run
curl -sk https://50.28.86.131/miner/download -o rustchain_miner.py
chmod +x rustchain_miner.py

# Run in background
nohup python3 rustchain_miner.py --wallet YOUR_WALLET_ID > miner.log 2>&1 &

# Check logs
tail -f miner.log
```

#### Systemd Service (Recommended)

Create a systemd service for automatic startup:

```bash
sudo nano /etc/systemd/system/rustchain-miner.service
```

```ini
[Unit]
Description=RustChain Universal Miner
After=network.target

[Service]
Type=simple
User=yourusername
WorkingDirectory=/home/yourusername
ExecStart=/usr/bin/python3 /home/yourusername/rustchain_miner.py --wallet YOUR_WALLET_ID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Enable and start
sudo systemctl daemon-reload
sudo systemctl enable rustchain-miner
sudo systemctl start rustchain-miner

# Check status
sudo systemctl status rustchain-miner

# View logs
journalctl -u rustchain-miner -f
```

#### CentOS/RHEL

```bash
# Install dependencies
sudo yum install -y python3 curl

# Download and run
curl -sk https://50.28.86.131/miner/download -o rustchain_miner.py
chmod +x rustchain_miner.py

# Run in background
nohup python3 rustchain_miner.py --wallet YOUR_WALLET_ID > miner.log 2>&1 &
```

### macOS

#### Using Terminal

```bash
# Python 3 is pre-installed, or install via Homebrew
brew install python3

# Download miner
curl -sk https://50.28.86.131/miner/download -o rustchain_miner.py
chmod +x rustchain_miner.py

# Run
python3 rustchain_miner.py --wallet YOUR_WALLET_ID
```

#### LaunchDaemon (Background Service)

```xml
~/Library/LaunchAgents/com.rustchain.miner.plist
```

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.rustchain.miner</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/yourusername/rustchain_miner.py</string>
        <string>--wallet</string>
        <string>YOUR_WALLET_ID</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/Users/yourusername/miner.log</string>
    <key>StandardErrorPath</key>
    <string>/Users/yourusername/miner.error.log</string>
</dict>
</plist>
```

```bash
# Enable service
launchctl load ~/Library/LaunchAgents/com.rustchain.miner.plist

# Check status
launchctl list | grep rustchain
```

### Windows

#### PowerShell

```powershell
# Install Python 3 from https://python.org
# Or via Chocolatey
choco install python3

# Download miner
Invoke-WebRequest -Uri https://50.28.86.131/miner/download -OutFile rustchain_miner.py

# Run
python3 rustchain_miner.py --wallet YOUR_WALLET_ID
```

#### Windows Service (Optional)

```powershell
# Install as Windows Service using NSSM
choco install nssm

nssm install RustChainMiner "C:\Python39\python.exe" "C:\Users\YourName\rustchain_miner.py --wallet YOUR_WALLET_ID"
nssm set RustChainMiner AppDirectory "C:\Users\YourName"
nssm set RustChainMiner DisplayName "RustChain Miner"
nssm set RustChainMiner Start SERVICE_AUTO_START

# Start service
nssm start RustChainMiner

# Check status
nssm status RustChainMiner
```

---

## Docker Setup

### Using Docker

```bash
# Build image
docker build -t rustchain-miner https://github.com/Scottcjn/rustchain-bounties.git

# Run container
docker run -d \
  --name rustchain-miner \
  -e WALLET_ID=YOUR_WALLET_ID \
  -e NODE_URL=https://50.28.86.131 \
  rustchain-miner

# View logs
docker logs -f rustchain-miner
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'
services:
  miner:
    image: rustchain-miner
    build: .
    container_name: rustchain-miner
    environment:
      - WALLET_ID=YOUR_WALLET_ID
      - NODE_URL=https://50.28.86.131
    restart: unless-stopped
```

```bash
# Start
docker-compose up -d

# Logs
docker-compose logs -f
```

---

## Configuration Options

### Command Line Arguments

| Argument | Short | Description | Default |
|----------|-------|-------------|---------|
| `--wallet` | `-w` | Your wallet/miner ID | Required |
| `--node` | `-n` | RustChain node URL | https://50.28.86.131 |
| `--port` | `-p` | Local port to listen on | Random |
| `--verbose` | `-v` | Enable verbose logging | False |
| `--help` | `-h` | Show help message | - |

### Environment Variables

```bash
export RUSTCHAIN_WALLET="YOUR_WALLET_ID"
export RUSTCHAIN_NODE="https://50.28.86.131"
export RUSTCHAIN_VERBOSE="true"
```

---

## Verification & Troubleshooting

### Check If Mining

```bash
# List all miners and search for yours
curl -sk https://50.28.86.131/api/miners | python3 -c "
import sys,json
miners = json.load(sys.stdin)
print(f'Total miners: {len(miners)}')
for m in miners:
    if 'YOUR_WALLET_ID' in m['miner']:
        print(f'✅ Found: {m[\"miner\"]}')
        print(f'   Hardware: {m[\"hardware_type\"]}')
        print(f'   Multiplier: {m[\"antiquity_multiplier\"]}x')
        break
else:
    print('❌ Not found yet (may take a few minutes)')
"
```

### Check Balance

```bash
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_WALLET_ID"
```

### Check Node Health

```bash
curl -sk https://50.28.86.131/health
```

### Common Issues

| Issue | Solution |
|-------|----------|
| Miner not appearing in list | Wait 5-10 minutes for attestation |
| Connection refused | Check node URL and network |
| Permission denied | `chmod +x rustchain_miner.py` |
| Python not found | Install Python 3 |
| VM detected | RustChain requires real hardware |
| Port already in use | Use `--port` to specify different port |

### View Logs

```bash
# Local file (if running with nohup)
tail -f miner.log

# Docker
docker logs rustchain-miner

# Systemd
journalctl -u rustchain-miner -f
```

---

## Hardware Considerations

### Supported Hardware

Any **real (non-VM)** hardware can mine:

| Architecture | Multiplier | Notes |
|--------------|------------|-------|
| **PowerPC G4** | 2.5x | Highest bonus! |
| **PowerPC G5** | 2.0x | Vintage bonus |
| **PowerPC G3** | 1.8x | Legacy bonus |
| **Pentium 4** | 1.5x | Retro bonus |
| **Retro x86** | 1.4x | Older hardware |
| **Apple Silicon** | 1.2x | M1/M2/M3 |
| **Modern x86_64** | 1.0x | Standard rate |

### VM Detection

RustChain actively detects virtual machines. **VMs will not earn rewards**.

Signs your hardware is detected as VM:
- No attestation despite running
- Error messages about virtualization
- Zero rewards despite uptime

**Solution:** Run on bare metal or ask your cloud provider for bare metal instances.

---

## Security Best Practices

### 1. Secure Your Wallet ID

```bash
# Don't expose in logs
# Use environment variables instead of command line
export WALLET_ID="secure-wallet-name"
python3 rustchain_miner.py
```

### 2. Firewall Setup

```bash
# UFW (Ubuntu)
sudo ufw allow ssh
sudo ufw allow from 127.0.0.1
sudo ufw enable
```

### 3. Regular Updates

```bash
# Check for miner updates
curl -sk https://50.28.86.131/miner/version

# Update if needed
curl -sk https://50.28.86.131/miner/download -o rustchain_miner.py
```

---

## Monitoring & Alerts

### Health Check Script

```bash
#!/bin/bash
# save as check_miner.sh

WALLET_ID="YOUR_WALLET_ID"
NODE_URL="https://50.28.86.131"

# Check node health
if ! curl -sk "${NODE_URL}/health" > /dev/null; then
    echo "❌ Node unreachable"
    exit 1
fi

# Check if miner is active
if curl -sk "${NODE_URL}/api/miners" | grep -q "$WALLET_ID"; then
    echo "✅ Miner active: $WALLET_ID"
    curl -sk "${NODE_URL}/wallet/balance?miner_id=$WALLET_ID"
else
    echo "⚠️ Miner not in active list yet"
fi
```

### Cron Job for Monitoring

```bash
# Run health check every 15 minutes
crontab -e
*/15 * * * * /path/to/check_miner.sh >> /var/log/miner_check.log 2>&1
```

---

## Performance Optimization

### For High-Performance Mining

1. **Use dedicated hardware** - More CPU cores = more attestations
2. **Stable network** - Low latency to node improves sync
3. **Reduce system load** - Close unnecessary processes
4. **Cooling** - Prevent thermal throttling

### Resource Usage

```bash
# Monitor resource usage
top -p $(pgrep -f rustchain_miner)

# Disk usage
du -sh ~/.rustchain/
```

---

## Getting Help

- **Issues:** https://github.com/Scottcjn/rustchain-bounties/issues
- **Discord:** Join the RustChain community
- **FAQ:** See docs/FAQ.md

---

## Quick Reference

| Command | Purpose |
|---------|---------|
| `python3 rustchain_miner.py --wallet NAME` | Start mining |
| `curl -sk https://50.28.86.131/api/miners` | List miners |
| `curl -sk "https://50.28.86.131/wallet/balance?miner_id=NAME"` | Check balance |
| `curl -sk https://50.28.86.131/health` | Node health |
| `journalctl -u rustchain-miner -f` | View logs (systemd) |

---

*Last updated: 2026-02-12*
*For RustChain v2.2.1-rip200*
