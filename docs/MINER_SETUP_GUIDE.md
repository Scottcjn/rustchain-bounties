# RustChain Miner Setup Guide

Complete guide to setting up and running a RustChain miner on all platforms.

**Earn RTC passively** while contributing to network security through RIP-200 Proof-of-Attestation consensus.

## Table of Contents

- [Quick Start](#quick-start)
- [System Requirements](#system-requirements)
- [Installation Methods](#installation-methods)
- [Platform-Specific Setup](#platform-specific-setup)
- [Configuration](#configuration)
- [Monitoring & Troubleshooting](#monitoring--troubleshooting)
- [Hardware Optimization](#hardware-optimization)

---

## Quick Start

**Get mining in 3 commands:**

```bash
# Download the miner
curl -sk https://50.28.86.131/miner/download -o rustchain_miner.py

# Start mining (replace YOUR_WALLET_ID)
python3 rustchain_miner.py --wallet YOUR_WALLET_ID --node https://50.28.86.131

# Check your balance
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_WALLET_ID"
```

**That's it!** Your miner will start earning RTC immediately.

---

## System Requirements

### Minimum Requirements
- **CPU**: Any real (non-VM) processor
- **RAM**: 512MB available
- **Storage**: 100MB free space
- **Network**: Stable internet connection
- **Python**: 3.6+ (3.8+ recommended)

### Supported Platforms
- ✅ **Linux** (Ubuntu, Debian, CentOS, Arch, etc.)
- ✅ **macOS** (Intel & Apple Silicon)
- ✅ **Windows** (10/11, WSL recommended)
- ✅ **FreeBSD/OpenBSD**
- ✅ **Vintage Hardware** (PowerPC, old x86)

### Hardware Bonuses
| Architecture | Multiplier | Examples |
|-------------|-----------|----------|
| PowerPC G4 | **2.5x** | iMac G4, PowerMac G4 |
| PowerPC G5 | **2.0x** | PowerMac G5, iMac G5 |
| PowerPC G3 | **1.8x** | iMac G3, PowerBook G3 |
| Pentium 4 | **1.5x** | Dell Dimension, HP Pavilion |
| Apple Silicon | **1.2x** | M1/M2/M3 Macs |
| Modern x86_64 | **1.0x** | Intel Core, AMD Ryzen |

**💡 Pro Tip**: Dust off that old PowerMac G4 for 2.5x mining rewards!

---

## Installation Methods

### Method 1: Direct Download (Recommended)

```bash
# Download miner script
curl -sk https://50.28.86.131/miner/download -o rustchain_miner.py

# Make executable (Linux/macOS)
chmod +x rustchain_miner.py

# Run with your wallet ID
python3 rustchain_miner.py --wallet your-wallet-name --node https://50.28.86.131
```

### Method 2: Git Clone

```bash
# Clone the repository
git clone https://github.com/Scottcjn/rustchain-bounties.git
cd rustchain-bounties

# Run the miner
python3 rustchain_universal_miner.py --wallet your-wallet-name
```

### Method 3: Docker (Advanced)

```bash
# Pull the image
docker pull rustchain/miner:latest

# Run container
docker run -d --name rustchain-miner \
  -e WALLET_ID=your-wallet-name \
  -e NODE_URL=https://50.28.86.131 \
  rustchain/miner:latest
```

---

## Platform-Specific Setup

### Linux (Ubuntu/Debian)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Python 3 and pip
sudo apt install python3 python3-pip curl -y

# Download and run miner
curl -sk https://50.28.86.131/miner/download -o rustchain_miner.py
python3 rustchain_miner.py --wallet your-wallet-id --node https://50.28.86.131
```

**For systemd service (auto-start):**

```bash
# Create service file
sudo tee /etc/systemd/system/rustchain-miner.service > /dev/null <<EOF
[Unit]
Description=RustChain Miner
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME
ExecStart=/usr/bin/python3 $HOME/rustchain_miner.py --wallet your-wallet-id --node https://50.28.86.131
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

# Enable and start service
sudo systemctl enable rustchain-miner
sudo systemctl start rustchain-miner

# Check status
sudo systemctl status rustchain-miner
```

### macOS

```bash
# Install Homebrew (if not installed)
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3
brew install python3

# Download and run miner
curl -sk https://50.28.86.131/miner/download -o rustchain_miner.py
python3 rustchain_miner.py --wallet your-wallet-id --node https://50.28.86.131
```

**For auto-start (launchd):**

```bash
# Create plist file
cat > ~/Library/LaunchAgents/com.rustchain.miner.plist <<EOF
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.rustchain.miner</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>$HOME/rustchain_miner.py</string>
        <string>--wallet</string>
        <string>your-wallet-id</string>
        <string>--node</string>
        <string>https://50.28.86.131</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
</dict>
</plist>
EOF

# Load the service
launchctl load ~/Library/LaunchAgents/com.rustchain.miner.plist
```

### Windows

**Option 1: WSL (Recommended)**

```powershell
# Install WSL2
wsl --install

# Restart computer, then open WSL terminal
# Follow Linux instructions above
```

**Option 2: Native Windows**

```powershell
# Install Python from python.org or Microsoft Store
# Download miner in PowerShell
Invoke-WebRequest -Uri "https://50.28.86.131/miner/download" -OutFile "rustchain_miner.py" -SkipCertificateCheck

# Run miner
python rustchain_miner.py --wallet your-wallet-id --node https://50.28.86.131
```

### Vintage Hardware (PowerPC)

**macOS 10.4/10.5 (PowerPC):**

```bash
# Install Python 2.7 (if not available)
# Download miner
curl -k https://50.28.86.131/miner/download -o rustchain_miner.py

# Run with Python 2.7
python rustchain_miner.py --wallet vintage-mac-g4 --node https://50.28.86.131
```

**Linux on PowerPC:**

```bash
# Debian PowerPC or Ubuntu PowerPC
sudo apt-get install python3 curl

# Download and run
curl -sk https://50.28.86.131/miner/download -o rustchain_miner.py
python3 rustchain_miner.py --wallet powerpc-linux --node https://50.28.86.131
```

---

## Configuration

### Command Line Options

```bash
python3 rustchain_miner.py [OPTIONS]
```

**Required:**
- `--wallet WALLET_ID`: Your wallet identifier
- `--node NODE_URL`: RustChain node URL (default: https://50.28.86.131)

**Optional:**
- `--threads N`: Number of mining threads (default: auto-detect)
- `--interval N`: Attestation interval in seconds (default: 300)
- `--verbose`: Enable verbose logging
- `--config FILE`: Load config from file

### Configuration File

Create `rustchain_config.json`:

```json
{
  "wallet_id": "your-wallet-name",
  "node_url": "https://50.28.86.131",
  "threads": 4,
  "interval": 300,
  "verbose": true,
  "auto_restart": true,
  "log_file": "rustchain_miner.log"
}
```

Run with config:
```bash
python3 rustchain_miner.py --config rustchain_config.json
```

### Environment Variables

```bash
export RUSTCHAIN_WALLET=your-wallet-id
export RUSTCHAIN_NODE=https://50.28.86.131
export RUSTCHAIN_THREADS=4

python3 rustchain_miner.py
```

---

## Monitoring & Troubleshooting

### Check Mining Status

```bash
# Check your balance
curl -sk "https://50.28.86.131/wallet/balance?miner_id=your-wallet-id"

# Check if you're in the active miners list
curl -sk "https://50.28.86.131/api/miners" | grep your-wallet-id

# Check current epoch
curl -sk "https://50.28.86.131/epoch"
```

### Log Analysis

**Common log messages:**
```
✅ [INFO] Miner registered successfully
✅ [INFO] Attestation submitted (score: 0.85)
✅ [INFO] Hardware detected: PowerPC G4 (2.5x multiplier)
⚠️  [WARN] Network connection unstable
❌ [ERROR] Failed to submit attestation
```

### Common Issues & Solutions

**Issue: "Miner not found"**
```bash
# Solution: Wait 5-10 minutes after first start
# The miner needs to register with the network
```

**Issue: "Connection refused"**
```bash
# Solution: Check internet connection and node status
curl -sk https://50.28.86.131/health
```

**Issue: "Low entropy score"**
```bash
# Solution: Ensure you're running on real hardware (not VM)
# VMs get 0 entropy and earn nothing
```

**Issue: "Python not found"**
```bash
# Linux/macOS
sudo apt install python3  # or brew install python3

# Windows
# Download from python.org
```

### Performance Monitoring

**Create monitoring script:**

```bash
#!/bin/bash
# monitor_miner.sh

WALLET_ID="your-wallet-id"

while true; do
    echo "=== $(date) ==="
    
    # Check balance
    BALANCE=$(curl -sk "https://50.28.86.131/wallet/balance?miner_id=$WALLET_ID" | jq -r '.amount_rtc')
    echo "Balance: $BALANCE RTC"
    
    # Check if mining
    MINING=$(curl -sk "https://50.28.86.131/api/miners" | grep -c "$WALLET_ID")
    if [ "$MINING" -gt 0 ]; then
        echo "Status: ✅ Mining"
    else
        echo "Status: ❌ Not mining"
    fi
    
    echo "---"
    sleep 300  # Check every 5 minutes
done
```

---

## Hardware Optimization

### CPU Optimization

**For modern multi-core systems:**
```bash
# Use all CPU cores
python3 rustchain_miner.py --wallet your-id --threads $(nproc)

# Leave some cores for system
python3 rustchain_miner.py --wallet your-id --threads $(($(nproc) - 1))
```

**For vintage hardware:**
```bash
# Single-core systems
python3 rustchain_miner.py --wallet vintage-mac --threads 1

# Dual-core PowerPC
python3 rustchain_miner.py --wallet powermac-g5 --threads 2
```

### Memory Optimization

**Low-memory systems (< 1GB RAM):**
```bash
# Reduce memory usage
export PYTHONOPTIMIZE=1
python3 rustchain_miner.py --wallet low-mem-system --interval 600
```

### Network Optimization

**For unstable connections:**
```bash
# Increase retry intervals
python3 rustchain_miner.py --wallet mobile-hotspot --interval 600 --retry-delay 30
```

### Power Management

**For laptops/mobile devices:**
```bash
# Reduce CPU usage
python3 rustchain_miner.py --wallet laptop --threads 1 --interval 900
```

---

## Advanced Setup

### Multiple Miners (Same Machine)

```bash
# Run multiple instances with different wallet IDs
python3 rustchain_miner.py --wallet miner-1 --port 8001 &
python3 rustchain_miner.py --wallet miner-2 --port 8002 &
python3 rustchain_miner.py --wallet miner-3 --port 8003 &
```

### Mining Farm Setup

```bash
#!/bin/bash
# farm_setup.sh - Deploy to multiple machines

MACHINES=("192.168.1.10" "192.168.1.11" "192.168.1.12")
BASE_WALLET="farm-miner"

for i in "${!MACHINES[@]}"; do
    MACHINE="${MACHINES[$i]}"
    WALLET="${BASE_WALLET}-$((i+1))"
    
    echo "Setting up $MACHINE with wallet $WALLET"
    
    ssh root@$MACHINE "
        curl -sk https://50.28.86.131/miner/download -o rustchain_miner.py
        nohup python3 rustchain_miner.py --wallet $WALLET --node https://50.28.86.131 > miner.log 2>&1 &
    "
done
```

### Docker Swarm Deployment

```yaml
# docker-compose.yml
version: '3.8'
services:
  rustchain-miner:
    image: rustchain/miner:latest
    environment:
      - WALLET_ID=swarm-miner-${HOSTNAME}
      - NODE_URL=https://50.28.86.131
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1.0'
          memory: 512M
    restart: unless-stopped
```

---

## Security Best Practices

### Wallet Security
- **Use unique wallet IDs** - Don't reuse across projects
- **Keep wallet IDs private** - They're your mining identity
- **Backup your wallet ID** - Store it securely

### Network Security
- **Use HTTPS endpoints** - Always use `https://50.28.86.131`
- **Verify SSL certificates** - Don't use `-k` flag in production
- **Monitor for unusual activity** - Check balance regularly

### System Security
- **Keep Python updated** - Use latest stable version
- **Run as non-root** - Don't run miner as root user
- **Use firewall** - Block unnecessary ports

---

## Earnings Calculator

**Estimate your daily RTC earnings:**

```python
#!/usr/bin/env python3
# earnings_calculator.py

def calculate_earnings(hardware_multiplier, active_miners=12, epoch_reward=1.5):
    """
    Calculate estimated daily RTC earnings
    
    Args:
        hardware_multiplier: Your hardware bonus (1.0 to 2.5)
        active_miners: Current active miners on network
        epoch_reward: RTC distributed per epoch
    """
    
    # Your share of the network
    your_weight = hardware_multiplier
    total_weight = active_miners  # Simplified assumption
    your_share = your_weight / total_weight
    
    # Epochs per day (24 hours / ~24 hours per epoch = 1)
    epochs_per_day = 1
    
    daily_earnings = your_share * epoch_reward * epochs_per_day
    
    return daily_earnings

# Examples
print("Daily RTC Earnings Estimates:")
print(f"Modern x86_64 (1.0x): {calculate_earnings(1.0):.4f} RTC/day")
print(f"Apple Silicon (1.2x): {calculate_earnings(1.2):.4f} RTC/day")
print(f"Pentium 4 (1.5x): {calculate_earnings(1.5):.4f} RTC/day")
print(f"PowerPC G5 (2.0x): {calculate_earnings(2.0):.4f} RTC/day")
print(f"PowerPC G4 (2.5x): {calculate_earnings(2.5):.4f} RTC/day")

# At $0.10/RTC reference rate
print("\nDaily USD Estimates (at $0.10/RTC):")
for hw, mult in [("x86_64", 1.0), ("Apple Silicon", 1.2), ("PowerPC G4", 2.5)]:
    earnings = calculate_earnings(mult)
    usd = earnings * 0.10
    print(f"{hw}: ${usd:.4f}/day")
```

---

## FAQ

**Q: Do I need to keep my computer on 24/7?**
A: No, but more uptime = more rewards. The miner only earns when actively running.

**Q: Can I run multiple miners on one machine?**
A: Yes, but use different wallet IDs. Same wallet ID won't increase earnings.

**Q: Why is my vintage Mac earning more than my gaming PC?**
A: RustChain rewards hardware diversity. Vintage PowerPC gets 2.5x multiplier vs 1.0x for modern x86.

**Q: Can I mine in a virtual machine?**
A: No, VMs get 0 entropy score and earn nothing. RustChain requires real hardware.

**Q: How often do I get paid?**
A: Rewards are distributed at the end of each epoch (~24 hours).

**Q: Can I change my wallet ID?**
A: Yes, just restart the miner with a new `--wallet` parameter.

**Q: Is there a minimum payout?**
A: No, all earnings go directly to your wallet regardless of amount.

---

## Support & Community

- **Issues**: [GitHub Issues](https://github.com/Scottcjn/rustchain-bounties/issues)
- **Discord**: [RustChain Community](https://discord.gg/rustchain)
- **Website**: [rustchain.org](https://rustchain.org)
- **Explorer**: [rustchain.org/explorer](https://rustchain.org/explorer)

---

**Happy Mining! 🚀**

*Start earning RTC today by contributing to the RustChain network's security and decentralization.*

---

*Last updated: February 2026*  
*Guide Version: 1.0*