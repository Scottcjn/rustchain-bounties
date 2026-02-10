# RustChain Miner Setup Guide

Step-by-step guide to setting up a RustChain miner on all platforms.

## Prerequisites

### All Platforms
- Python 3.7 or higher
- Internet connection
- Real hardware (VMs earn 0 rewards)

### Linux
```bash
sudo apt update
sudo apt install python3 python3-pip curl
```

### macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3
brew install python3
```

### Windows
1. Download Python from [python.org](https://www.python.org/downloads/)
2. Run installer and check "Add Python to PATH"
3. Open Command Prompt and verify: `python --version`

## Installation

### Method 1: Direct Download (Recommended)

**Linux/macOS:**
```bash
curl -sk https://50.28.86.131/miner/download -o rustchain_miner.py
```

**Windows (PowerShell):**
```powershell
Invoke-WebRequest -Uri "https://50.28.86.131/miner/download" -OutFile "rustchain_miner.py" -SkipCertificateCheck
```

### Method 2: Clone Repository

```bash
git clone https://github.com/Scottcjn/rustchain-bounties.git
cd rustchain-bounties
```

## Configuration

### Choose a Wallet ID

Your wallet ID can be any unique string. Examples:
- `my-agent-name`
- `alice-laptop-2024`
- `vintage-g5-tower`

### Basic Usage

```bash
python3 rustchain_miner.py --wallet YOUR_WALLET_ID --node https://50.28.86.131
```

### Advanced Options

```bash
python3 rustchain_miner.py \
  --wallet YOUR_WALLET_ID \
  --node https://50.28.86.131 \
  --threads 4 \
  --interval 60
```

**Options:**
- `--wallet`: Your wallet ID (required)
- `--node`: RustChain node URL (default: https://50.28.86.131)
- `--threads`: Number of CPU threads to use (default: auto-detect)
- `--interval`: Attestation interval in seconds (default: 60)

## Running as a Service

### Linux (systemd)

Create `/etc/systemd/system/rustchain-miner.service`:

```ini
[Unit]
Description=RustChain Miner
After=network.target

[Service]
Type=simple
User=rustchain
WorkingDirectory=/home/rustchain
ExecStart=/usr/bin/python3 /home/rustchain/rustchain_miner.py --wallet YOUR_WALLET_ID --node https://50.28.86.131
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable rustchain-miner
sudo systemctl start rustchain-miner
sudo systemctl status rustchain-miner
```

### macOS (launchd)

Create `~/Library/LaunchAgents/com.rustchain.miner.plist`:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.rustchain.miner</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/YOUR_USERNAME/rustchain_miner.py</string>
        <string>--wallet</string>
        <string>YOUR_WALLET_ID</string>
        <string>--node</string>
        <string>https://50.28.86.131</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
```

Load the service:
```bash
launchctl load ~/Library/LaunchAgents/com.rustchain.miner.plist
launchctl start com.rustchain.miner
```

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Name: "RustChain Miner"
4. Trigger: "When the computer starts"
5. Action: "Start a program"
6. Program: `python.exe`
7. Arguments: `C:\path\to\rustchain_miner.py --wallet YOUR_WALLET_ID --node https://50.28.86.131`
8. Check "Run whether user is logged on or not"

## Verifying Operation

### Check Balance

```bash
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_WALLET_ID"
```

Expected output:
```json
{
  "wallet_id": "YOUR_WALLET_ID",
  "balance": 3.75,
  "pending": 0.0
}
```

### Monitor Logs

**Linux/macOS:**
```bash
tail -f rustchain_miner.log
```

**Windows:**
```powershell
Get-Content rustchain_miner.log -Wait
```

## Hardware Multipliers

Vintage hardware earns bonus rewards:

| Architecture | Multiplier | Example Hardware |
|-------------|-----------|------------------|
| PowerPC G4 | 2.5x | iMac G4, PowerBook G4 |
| PowerPC G5 | 2.0x | Power Mac G5 |
| PowerPC G3 | 1.8x | iMac G3, iBook G3 |
| Pentium 4 | 1.5x | Dell Dimension, HP Pavilion |
| Retro x86 | 1.4x | Pentium III, Athlon XP |
| Apple Silicon | 1.2x | M1, M2, M3, M4 Macs |
| Modern x86_64 | 1.0x | Intel Core, AMD Ryzen |

## Troubleshooting

### Connection Refused

**Problem:** `Connection refused` or `timeout` errors

**Solution:**
1. Check firewall settings
2. Verify node URL: `curl -sk https://50.28.86.131/health`
3. Try alternative node if available

### No Rewards

**Problem:** Balance remains 0 after mining

**Solution:**
1. Verify you're not running in a VM (VMs earn 0)
2. Check miner logs for attestation errors
3. Ensure wallet ID is correct
4. Wait for epoch completion (rewards distributed per epoch)

### High CPU Usage

**Problem:** Miner uses 100% CPU

**Solution:**
Limit threads:
```bash
python3 rustchain_miner.py --wallet YOUR_WALLET_ID --threads 2
```

### SSL Certificate Errors

**Problem:** `SSL: CERTIFICATE_VERIFY_FAILED`

**Solution:**
Use `-k` flag with curl or `SkipCertificateCheck` in PowerShell. The node uses self-signed certificates.

### Python Version Issues

**Problem:** `SyntaxError` or `ModuleNotFoundError`

**Solution:**
Upgrade Python:
```bash
python3 --version  # Must be 3.7+
```

## Optimization Tips

1. **Run on bare metal**: VMs earn nothing due to anti-emulation checks
2. **Use vintage hardware**: Earn up to 2.5x multiplier
3. **Stable connection**: Uptime matters for attestation
4. **Monitor balance**: Track earnings with API
5. **Join the community**: Check GitHub issues for bounties

## Next Steps

- [API Reference](api-reference.md) - Interact with the RustChain API
- [Wallet User Guide](wallet-user-guide.md) - Manage your RTC
- [Python SDK Tutorial](python-sdk-tutorial.md) - Programmatic access
