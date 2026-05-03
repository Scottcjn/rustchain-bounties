#!/usr/bin/env bash
set -euo pipefail

# RustChain Miner Installation Script
# Usage: curl -fsSL https://rustchain.org/install.sh | bash -s -- --wallet YOUR-NAME-HERE

WALLET="${1:-}"
if [[ -z "$WALLET" ]]; then
    echo "Error: Wallet name is required. Use --wallet YOUR-NAME-HERE"
    exit 1
fi

MINER_DIR="$HOME/.rustchain"
MINER_BIN="$MINER_DIR/miner"
MINER_LOG="$MINER_DIR/miner.log"
MINER_PID="$MINER_DIR/miner.pid"
MINER_VERSION="v1.0.0"
MINER_URL="https://github.com/rustchain/miner/releases/download/$MINER_VERSION/miner-linux-amd64"

# Create directory
mkdir -p "$MINER_DIR"

# Download miner binary
echo "Downloading RustChain miner $MINER_VERSION..."
curl -fsSL "$MINER_URL" -o "$MINER_BIN"
chmod +x "$MINER_BIN"

# Generate hardware fingerprint
echo "Generating hardware fingerprint..."
FINGERPRINT=$(cat /proc/cpuinfo | grep "model name" | head -1 | cut -d: -f2 | xargs)
FINGERPRINT+="|$(cat /proc/meminfo | grep "MemTotal" | head -1 | cut -d: -f2 | xargs)"
FINGERPRINT+="|$(uname -r)"
FINGERPRINT+="|$(hostname)"
FINGERPRINT_HASH=$(echo -n "$FINGERPRINT" | sha256sum | cut -d' ' -f1)

# Write initial log
echo "=== RustChain Miner Report ===" > "$MINER_LOG"
echo "Wallet: $WALLET" >> "$MINER_LOG"
echo "Timestamp: $(date -u +"%Y-%m-%dT%H:%M:%SZ")" >> "$MINER_LOG"
echo "Device: $(uname -n)" >> "$MINER_LOG"
echo "OS: $(uname -s) $(uname -r)" >> "$MINER_LOG"
echo "CPU: $(cat /proc/cpuinfo | grep "model name" | head -1 | cut -d: -f2 | xargs)" >> "$MINER_LOG"
echo "Memory: $(cat /proc/meminfo | grep "MemTotal" | head -1 | cut -d: -f2 | xargs)" >> "$MINER_LOG"
echo "Fingerprint: $FINGERPRINT_HASH" >> "$MINER_LOG"
echo "Attestation: $(date +%s)" >> "$MINER_LOG"
echo "---" >> "$MINER_LOG"

# Start miner in background
echo "Starting miner for wallet: $WALLET"
nohup "$MINER_BIN" --wallet "$WALLET" --log-file "$MINER_LOG" > /dev/null 2>&1 &
echo $! > "$MINER_PID"

echo "Miner started with PID $(cat $MINER_PID)"
echo "Log file: $MINER_LOG"
echo "Let it run for 24 hours, then run:"
echo "cat ~/.rustchain/miner.log | grep \"device\\|attestation\\|fingerprint\" | tail -20"