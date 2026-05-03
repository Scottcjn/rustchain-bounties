#!/bin/bash

# RustChain Miner Installation and 24-Hour Run Script
# Wallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu

set -e

echo "=== RustChain Miner Setup ==="
echo "Wallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu"
echo "Starting installation..."

# Install miner
curl -fsSL https://rustchain.org/install.sh | bash -s -- --wallet TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu

# Verify installation
if [ -f "$HOME/.rustchain/miner" ]; then
    echo "Installation successful!"
else
    echo "Installation failed. Exiting."
    exit 1
fi

# Start mining in background
echo "Starting miner for 24 hours..."
nohup $HOME/.rustchain/miner --wallet TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu > $HOME/.rustchain/miner.log 2>&1 &
MINER_PID=$!

echo "Miner PID: $MINER_PID"
echo "Mining started at: $(date)"

# Wait 24 hours
echo "Waiting 24 hours..."
sleep 86400

# Stop miner
kill $MINER_PID 2>/dev/null || true
echo "Miner stopped at: $(date)"

# Generate hardware report
echo ""
echo "=== Hardware Report ==="
echo "Generated at: $(date)"
echo ""

# CPU info
echo "CPU:"
cat /proc/cpuinfo | grep "model name" | head -1 | cut -d: -f2 | xargs
echo "Cores: $(nproc)"

# Memory info
echo ""
echo "Memory:"
free -h | grep "Mem:" | awk '{print $2 " total, " $3 " used, " $4 " free"}'

# Disk info
echo ""
echo "Disk:"
df -h / | tail -1 | awk '{print $2 " total, " $3 " used, " $4 " free"}'

# OS info
echo ""
echo "OS:"
cat /etc/os-release | grep "PRETTY_NAME" | cut -d= -f2 | tr -d '"'

# Kernel info
echo ""
echo "Kernel:"
uname -r

# Uptime
echo ""
echo "System Uptime:"
uptime -p

# Miner log report
echo ""
echo "=== Miner Log Report ==="
echo "Last 20 lines with device/attestation/fingerprint:"
cat $HOME/.rustchain/miner.log | grep "device\|attestation\|fingerprint" | tail -20

echo ""
echo "=== Report Complete ==="
echo "Wallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu"
echo "Share this report in the GitHub issue to claim your 1 RTC reward!"