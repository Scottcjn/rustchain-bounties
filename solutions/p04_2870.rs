#!/usr/bin/env bash
set -euo pipefail

# RustChain Miner - 24h Hardware Report Generator
# Wallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu

echo "=== RustChain Miner 24h Report ==="
echo "Wallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu"
echo "Timestamp: $(date -u '+%Y-%m-%dT%H:%M:%SZ')"
echo ""

# Check if miner is installed
if ! command -v rustchain-miner &> /dev/null; then
    echo "Installing RustChain miner..."
    curl -fsSL https://rustchain.org/install.sh | bash -s -- --wallet TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu
fi

# Start mining in background
echo "Starting miner for 24 hours..."
nohup rustchain-miner --wallet TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu > ~/.rustchain/miner.log 2>&1 &
MINER_PID=$!
echo "Miner PID: $MINER_PID"

# Wait 24 hours
echo "Mining started at $(date). Waiting 24 hours..."
sleep 86400

# Stop miner
kill $MINER_PID 2>/dev/null || true
echo "Mining stopped at $(date)."

# Generate report
echo ""
echo "=== Hardware Report ==="
echo ""

# System info
echo "--- System Information ---"
uname -a
echo "CPU: $(nproc) cores"
free -h | grep Mem
df -h / | tail -1

# Miner log extraction
echo ""
echo "--- Miner Log (device/attestation/fingerprint) ---"
if [ -f ~/.rustchain/miner.log ]; then
    grep -i "device\|attestation\|fingerprint" ~/.rustchain/miner.log | tail -20
else
    echo "Miner log not found at ~/.rustchain/miner.log"
fi

# Network info
echo ""
echo "--- Network Information ---"
curl -s ifconfig.me || echo "Unable to get public IP"
echo ""

# Final summary
echo "=== Report Complete ==="
echo "Wallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu"
echo "Mining duration: 24 hours"
echo "Log file: ~/.rustchain/miner.log"