# RustChain Complete Miner Setup Guide

**Bounty: 20 RTC** | Covers Linux, macOS, and Windows installation

---

## Table of Contents

1. [Overview](#overview)
2. [System Requirements](#system-requirements)
3. [Linux Installation](#linux-installation)
4. [macOS Installation](#macos-installation)
5. [Windows Installation](#windows-installation)
6. [Docker Installation](#docker-installation)
7. [Wallet Creation](#wallet-creation)
8. [Node Connection](#node-connection)
9. [Service Auto-Start](#service-auto-start)
10. [Log Interpretation & Status Monitoring](#log-interpretation--status-monitoring)
11. [Troubleshooting](#troubleshooting)

---

## Overview

RustChain is a **DePIN (Decentralized Physical Infrastructure Network)** for vintage hardware, using a "Proof of Antiquity" consensus mechanism. Miners contribute real hardware resources and earn RTC tokens based on the age and authenticity of their machines.

The miner performs the following functions:
- **Hardware attestation** — Fingerprints your CPU and validates it's real hardware
- **Proof generation** — Produces Proof of Antiquity puzzles
- **Block submission** — Sends validated proofs to the RustChain network
- **Reward collection** — Earns RTC tokens for each accepted proof

---

## System Requirements

### Minimum Requirements
| Component | Requirement |
|-----------|-------------|
| CPU | Any x86_64, ARM64, or ppc64le processor |
| RAM | 256 MB |
| Disk | 50 MB free space |
| Python | 3.8 or higher |
| Network | Internet connection (outbound HTTPS) |

### Recommended Requirements
| Component | Requirement |
|-----------|-------------|
| CPU | Dual-core 2 GHz+ |
| RAM | 1 GB |
| Disk | 200 MB (for logs and cached attestations) |
| Python | 3.10+ |
| Network | Broadband (1 Mbps+) |

### Supported Operating Systems

#### Linux
- **Distributions:** Ubuntu 20.04+, Debian 11+, Fedora 38+, RHEL 8+
- **Architectures:** x86_64, aarch64 (Raspberry Pi), ppc64le (POWER)
- **Init System:** systemd (for auto-start)

#### macOS
- **Versions:** macOS 12 Monterey+, macOS 11 Big Sur (limited)
- **Architectures:** arm64 (Apple Silicon M1/M2/M3), x86_64 (Intel)
- **Auto-Start:** launchd

#### Windows
- **Versions:** Windows 10, Windows 11
- **Architectures:** x86_64
- **Python:** Python 3.8+ from python.org or Microsoft Store
- **Auto-Start:** Task Scheduler

---

## Linux Installation

### Quick Install (One-Liner)

```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

This will:
1. Auto-detect your platform (OS + architecture)
2. Install Python 3 and python3-venv if not available
3. Create an isolated virtualenv at `~/.rustchain/venv`
4. Download the appropriate miner binary
5. Prompt for wallet name (or auto-generate one)
6. Ask about auto-start on boot via systemd
7. Display wallet balance check commands

### Installation with Custom Wallet Name

```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --wallet my-vintage-miner
```

### Dry-Run Mode (Test Without Installing)

```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --dry-run
```

This shows what the installer would do without making any changes.

### Manual Installation

If the one-liner doesn't work for your distribution, follow these steps:

```bash
# 1. Ensure Python 3.8+ is installed
python3 --version

# 2. Install python3-venv if missing
# Ubuntu/Debian:
sudo apt-get install -y python3-venv python3-pip
# Fedora:
sudo dnf install -y python3-virtualenv python3-pip
# RHEL/CentOS:
sudo yum install -y python3-virtualenv python3-pip

# 3. Create installation directory
mkdir -p ~/.rustchain

# 4. Create virtualenv
python3 -m venv ~/.rustchain/venv

# 5. Install requests in virtualenv
~/.rustchain/venv/bin/pip install requests

# 6. Download miner script (use your platform's miner)
# Linux x86_64:
curl -o ~/.rustchain/rustchain_miner.py \
  https://raw.githubusercontent.com/Scottcjn/Rustchain/main/miners/linux/rustchain_linux_miner.py
# ARM64 (Raspberry Pi):
curl -o ~/.rustchain/rustchain_miner.py \
  https://raw.githubusercontent.com/Scottcjn/Rustchain/main/miners/linux/rustchain_linux_miner.py

# 7. Download fingerprint checker
curl -o ~/.rustchain/fingerprint_checks.py \
  https://raw.githubusercontent.com/Scottcjn/Rustchain/main/miners/linux/fingerprint_checks.py

# 8. Make executable
chmod +x ~/.rustchain/rustchain_miner.py

# 9. Create start script
cat > ~/.rustchain/start.sh << 'SCRIPT'
#!/bin/bash
cd ~/.rustchain
./venv/bin/python rustchain_miner.py "$@"
SCRIPT
chmod +x ~/.rustchain/start.sh

# 10. Run the miner
~/.rustchain/start.sh
```

### Verifying Installation

```bash
# Check miner version and help
~/.rustchain/start.sh --help

# Run in dry-run mode to verify setup
~/.rustchain/start.sh --dry-run

# Check the directory structure
ls -la ~/.rustchain/
```

---

## macOS Installation

### Prerequisites

```bash
# Install Command Line Tools (if not already installed)
xcode-select --install

# Verify Python 3.8+
python3 --version
```

### Quick Install

```bash
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash
```

The installer will:
1. Detect macOS and your architecture (Intel or Apple Silicon)
2. Use the existing Python 3 installation
3. Create virtualenv at `~/.rustchain/venv`
4. Download the appropriate macOS miner
5. Offer to set up launchd auto-start

### Manual macOS Installation

```bash
# Create directory
mkdir -p ~/.rustchain

# Create virtualenv
python3 -m venv ~/.rustchain/venv

# Install dependencies
~/.rustchain/venv/bin/pip install requests

# Download macOS miner
curl -o ~/.rustchain/rustchain_miner.py \
  https://raw.githubusercontent.com/Scottcjn/Rustchain/main/miners/macos/rustchain_mac_miner_v2.5.py

# Download fingerprint checker
curl -o ~/.rustchain/fingerprint_checks.py \
  https://raw.githubusercontent.com/Scottcjn/Rustchain/main/miners/linux/fingerprint_checks.py

# Make executable
chmod +x ~/.rustchain/rustchain_miner.py

# Create start script
cat > ~/.rustchain/start.sh << 'SCRIPT'
#!/bin/bash
cd ~/.rustchain
./venv/bin/python rustchain_miner.py "$@"
SCRIPT
chmod +x ~/.rustchain/start.sh

# Test run
~/.rustchain/start.sh --dry-run
```

### Docker macOS Workaround

If you prefer Docker on macOS:

```bash
# Using the Dockerfile.miner
docker build -t rustchain-miner -f Dockerfile.miner .
docker run --name rustchain-miner rustchain-miner
```

---

## Windows Installation

### Prerequisites

1. **Install Python 3.8+**
   - Download from [python.org](https://www.python.org/downloads/)
   - **IMPORTANT:** Check "Add Python to PATH" during installation

2. **Install Git for Windows** (optional, for cloning)
   - Download from [git-scm.com](https://git-scm.com/download/win)

### Installation Steps

1. **Open PowerShell as Administrator**

2. **Download the miner scripts:**
   ```powershell
   # Create RustChain directory
   mkdir $env:USERPROFILE\.rustchain -Force
   cd $env:USERPROFILE\.rustchain

   # Download Windows miner
   Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Scottcjn/Rustchain/main/miners/windows/rustchain_windows_miner.py" -OutFile "rustchain_miner.py"

   # Download fingerprint checker
   Invoke-WebRequest -Uri "https://raw.githubusercontent.com/Scottcjn/Rustchain/main/miners/windows/fingerprint_checks.py" -OutFile "fingerprint_checks.py"
   ```

3. **Create virtual environment:**
   ```powershell
   python -m venv venv
   .\venv\Scripts\pip install requests
   ```

4. **Create start script:**
   ```powershell
   @echo off
   cd /d %USERPROFILE%\.rustchain
   .\venv\Scripts\python rustchain_miner.py %*
   ```

   Save as `start.bat` in `%USERPROFILE%\.rustchain\`

5. **Test the miner:**
   ```powershell
   start.bat --dry-run
   ```

### Auto-Start on Windows (Task Scheduler)

```powershell
# Create a scheduled task to run the miner at login
$action = New-ScheduledTaskAction -Execute "$env:USERPROFILE\.rustchain\venv\Scripts\python.exe" `
  -Argument "$env:USERPROFILE\.rustchain\rustchain_miner.py" `
  -WorkingDirectory "$env:USERPROFILE\.rustchain"

$trigger = New-ScheduledTaskTrigger -AtLogOn

$settings = New-ScheduledTaskSettingsSet -AllowStartIfOnBatteries -DontStopIfGoingOnBatteries

Register-ScheduledTask -TaskName "RustChainMiner" `
  -Action $action `
  -Trigger $trigger `
  -Settings $settings `
  -RunLevel Limited `
  -Description "RustChain Vintage Hardware Miner"
```

### Windows Docker Installation

```powershell
# Clone the repo
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain

# Build and run the miner container
docker build -t rustchain-miner -f Dockerfile.miner .
docker run --name rustchain-miner rustchain-miner
```

---

## Docker Installation

### Using Dockerfile.miner

```bash
# Clone the repo
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain

# Build the miner image
docker build -t rustchain-miner -f Dockerfile.miner .

# Run the miner
docker run --name rustchain-miner \
  -e WALLET_NAME=my-miner \
  rustchain-miner
```

### Using docker-compose

```bash
# Using the provided docker-compose.miner.yml
docker-compose -f docker-compose.miner.yml up -d

# View logs
docker-compose -f docker-compose.miner.yml logs -f
```

---

## Wallet Creation

### Auto-Generated Wallet

The quick install script automatically generates a wallet name if you don't provide one. The wallet is a randomly generated string tied to your miner's identity.

### Custom Wallet Name

```bash
# During installation
curl -sSL https://raw.githubusercontent.com/Scottcjn/Rustchain/main/install-miner.sh | bash -s -- --wallet my-vintage-miner

# Or set it in the miner config
echo "WALLET_NAME=my-vintage-miner" >> ~/.rustchain/miner.env
```

### Checking Wallet Balance

```bash
# Check RTC balance
curl -s 'https://rustchain.org/wallet/balance?miner_id=my-wallet-name'

# Using the miner
~/.rustchain/start.sh --balance
```

### Faucet (Get Free RTC for Testing)

RustChain provides a faucet for new miners to get initial RTC:

```bash
# Request test tokens
curl -s -X POST https://rustchain.org/faucet \
  -H "Content-Type: application/json" \
  -d '{"wallet": "my-wallet-name"}'
```

---

## Node Connection

### Default Node

By default, the miner connects to the RustChain public node at `https://rustchain.org`.

### Custom Node

To connect to a custom node:

```bash
# Set custom node URL in environment
echo "NODE_URL=https://my-custom-node.example.com" >> ~/.rustchain/miner.env
```

Or pass it at runtime:

```bash
~/.rustchain/start.sh --node https://my-custom-node.example.com
```

### Running a Local Node

For advanced users who want to run their own node:

```bash
# Clone and start the node
git clone https://github.com/Scottcjn/Rustchain.git
cd Rustchain/node
python3 integrated_node.py --port 8545
```

Then connect your miner to the local node:

```bash
~/.rustchain/start.sh --node http://localhost:8545
```

---

## Service Auto-Start

### Linux (systemd)

The installer creates a user-level systemd service. You can manage it with:

```bash
# Check service status
systemctl --user status rustchain-miner

# Start the service
systemctl --user start rustchain-miner

# Stop the service
systemctl --user stop rustchain-miner

# Restart the service
systemctl --user restart rustchain-miner

# Enable auto-start on boot
systemctl --user enable rustchain-miner

# Disable auto-start
systemctl --user disable rustchain-miner

# View logs
journalctl --user -u rustchain-miner -f

# View last 50 lines of logs
journalctl --user -u rustchain-miner -n 50 --no-pager
```

### macOS (launchd)

```bash
# Load the service
launchctl load ~/Library/LaunchAgents/com.rustchain.miner.plist

# Start immediately
launchctl start com.rustchain.miner

# Stop
launchctl stop com.rustchain.miner

# Unload
launchctl unload ~/Library/LaunchAgents/com.rustchain.miner.plist

# Check status
launchctl list | grep rustchain

# View logs
log show --predicate 'process == "rustchain_miner"' --last 1h
```

### Windows (Task Scheduler)

```powershell
# Start the task
Start-ScheduledTask -TaskName "RustChainMiner"

# Stop the task
Stop-ScheduledTask -TaskName "RustChainMiner"

# Check status
Get-ScheduledTask -TaskName "RustChainMiner" | Get-ScheduledTaskInfo

# Disable
Disable-ScheduledTask -TaskName "RustChainMiner"

# Enable
Enable-ScheduledTask -TaskName "RustChainMiner"

# View task history
Get-WinEvent -LogName Microsoft-Windows-TaskScheduler/Operational | Where-Object { $_.Message -like "*RustChainMiner*" } | Format-Table TimeCreated, Message -AutoSize
```

---

## Log Interpretation & Status Monitoring

### Log Levels

The miner produces logs at these levels:

| Level | Indicator | Description |
|-------|-----------|-------------|
| INFO | `[INFO]` | Normal operation messages |
| SUCCESS | `[✓]` | Successful proof submission |
| WARNING | `[!]` | Minor issues (retries, slow network) |
| ERROR | `[✗]` | Critical failures (connection lost, invalid proof) |
| DEBUG | `[DEBUG]` | Detailed diagnostic information |

### Sample Log Output

```
[2025-01-15 14:30:01] [INFO] RustChain Miner v1.1.0 starting...
[2025-01-15 14:30:01] [INFO] Platform: Linux (x86_64)
[2025-01-15 14:30:02] [INFO] Wallet: my-vintage-miner
[2025-01-15 14:30:02] [INFO] Node: https://rustchain.org
[2025-01-15 14:30:02] [✓] Hardware fingerprint generated: 4e8f2a1c...
[2025-01-15 14:30:03] [✓] Connected to node
[2025-01-15 14:30:05] [INFO] Generating Proof of Antiquity...
[2025-01-15 14:30:08] [✓] Proof submitted (block #12492)
[2025-01-15 14:30:08] [INFO] Reward: +0.5 RTC
[2025-01-15 14:30:08] [INFO] Next proof in ~60 seconds
```

### Log File Location

| Platform | Log File |
|----------|----------|
| Linux | `~/.rustchain/miner.log` |
| macOS | `~/.rustchain/miner.log` |
| Windows | `%USERPROFILE%\.rustchain\miner.log` |

### Monitoring Scripts

The RustChain repo provides several monitoring tools:

```bash
# Check miner health
~/.rustchain/start.sh --status

# View recent rewards
~/.rustchain/start.sh --rewards

# Check network connectivity
~/.rustchain/start.sh --ping

# Prometheus exporter (for advanced monitoring)
python3 prometheus_exporter.py
```

### Prometheus/Grafana Monitoring

For production deployments, use the built-in Prometheus exporter:

```bash
# Start the exporter
python3 prometheus_exporter.py --port 8000

# Metrics available at http://localhost:8000/metrics
```

Key metrics exposed:
- `rustchain_miner_uptime_seconds` — How long the miner has been running
- `rustchain_proofs_submitted_total` — Total proofs submitted
- `rustchain_rewards_rtc_total` — Total RTC earned
- `rustchain_node_connection_status` — 1 if connected, 0 if disconnected
- `rustchain_last_proof_timestamp` — Timestamp of last successful proof

---

## Troubleshooting

### Common Issues

#### Issue: "Python 3 not found"
```bash
# Ubuntu/Debian
sudo apt-get install -y python3 python3-venv python3-pip
# macOS
xcode-select --install
# Windows: Download from python.org
```

#### Issue: "virtualenv: command not found"
```bash
# Ubuntu/Debian
sudo apt-get install -y python3-venv
# macOS
pip3 install virtualenv
```

#### Issue: "Connection refused: rustchain.org"
Check your internet connection and DNS:
```bash
ping rustchain.org
curl -sI https://rustchain.org
```

#### Issue: "Miner already running"
```bash
# Linux
systemctl --user status rustchain-miner
systemctl --user restart rustchain-miner
# macOS
launchctl list | grep rustchain
launchctl stop com.rustchain.miner
# Windows
Get-Process python* | Where-Object { $_.CommandLine -like "*rustchain*" }
```

#### Issue: "Proof rejected: invalid hardware fingerprint"
This can happen if your hardware configuration changed:
```bash
# Regenerate fingerprint
~/.rustchain/start.sh --refresh-fingerprint
```

#### Issue: Low RTC rewards
Rewards are proportional to CPU age and authenticity. Check:
```bash
# View your hardware score
~/.rustchain/start.sh --score

# Test fingerprint validity
~/.rustchain/start.sh --validate-fingerprint
```

### Logs for Debugging

```bash
# Linux (systemd)
journalctl --user -u rustchain-miner -n 100 --no-pager

# macOS
log show --predicate 'process == "rustchain_miner"' --last 24h

# All Platforms (file-based logs)
tail -n 100 ~/.rustchain/miner.log

# With follow (live view)
tail -f ~/.rustchain/miner.log
```

### Getting Help

- **GitHub Issues:** https://github.com/Scottcjn/Rustchain/issues
- **Discord:** Join the RustChain Discord server (link in repo)
- **Documentation:** https://github.com/Scottcjn/Rustchain
- **Explorer:** https://rustchain.org/explorer/