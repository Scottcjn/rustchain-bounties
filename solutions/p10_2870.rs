#!/usr/bin/env bash
set -euo pipefail

# RustChain Miner - 24 Hour Hardware Report Generator
# Wallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu

echo "=== RustChain Miner 24h Report ==="
echo "Wallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu"
echo "Timestamp: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""

# Check if miner is installed
if ! command -v rustchain-miner &> /dev/null; then
    echo "Installing RustChain miner..."
    curl -fsSL https://rustchain.org/install.sh | bash -s -- --wallet TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu
fi

# Start mining in background
echo "Starting miner for 24 hours..."
nohup rustchain-miner --wallet TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu --daemon > ~/.rustchain/miner.log 2>&1 &
MINER_PID=$!

# Wait 24 hours
echo "Mining PID: $MINER_PID"
echo "Mining will run for 24 hours. You can check progress with: tail -f ~/.rustchain/miner.log"
sleep 86400

# Stop miner
kill $MINER_PID 2>/dev/null || true

# Generate report
echo ""
echo "=== Hardware Report ==="
echo ""

# System info
echo "--- System Information ---"
uname -a
echo ""

# CPU info
echo "--- CPU Information ---"
if command -v lscpu &> /dev/null; then
    lscpu | grep -E "Model name|CPU\(s\)|Thread|Core|Socket"
elif [[ "$(uname)" == "Darwin" ]]; then
    sysctl -n machdep.cpu.brand_string
    sysctl -n hw.ncpu
    sysctl -n hw.physicalcpu
fi
echo ""

# Memory info
echo "--- Memory Information ---"
if command -v free &> /dev/null; then
    free -h
elif [[ "$(uname)" == "Darwin" ]]; then
    vm_stat | head -10
    sysctl hw.memsize | awk '{print $2/1073741824 " GB"}'
fi
echo ""

# Disk info
echo "--- Disk Information ---"
df -h / 2>/dev/null || df -h .
echo ""

# Network info
echo "--- Network Information ---"
if command -v ifconfig &> /dev/null; then
    ifconfig | grep -E "inet |inet6" | head -5
elif command -v ip &> /dev/null; then
    ip addr show | grep -E "inet |inet6" | head -5
fi
echo ""

# Miner log extraction
echo "--- Miner Log (last 20 lines with device/attestation/fingerprint) ---"
if [ -f ~/.rustchain/miner.log ]; then
    grep -i "device\|attestation\|fingerprint" ~/.rustchain/miner.log | tail -20
else
    echo "Miner log not found at ~/.rustchain/miner.log"
fi
echo ""

# Summary
echo "=== Summary ==="
echo "Wallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu"
echo "Mining Duration: 24 hours"
echo "Miner PID: $MINER_PID"
echo "Log File: ~/.rustchain/miner.log"
echo "Report Generated: $(date -u +%Y-%m-%dT%H:%M:%SZ)"
echo ""
echo "To claim reward, share this report in the GitHub issue."
echo "Reward: 1 RTC (~$0.10 USD) — Multi-claim: first 50 people"