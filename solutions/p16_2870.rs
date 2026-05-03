#!/usr/bin/env bash
set -euo pipefail

# RustChain Miner - 24h Hardware Report Generator
# Wallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu

MINER_DIR="$HOME/.rustchain"
MINER_LOG="$MINER_DIR/miner.log"
WALLET="TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu"

# Step 1: Install miner if not present
if ! command -v rustchain-miner &>/dev/null; then
    echo "[*] Installing RustChain miner..."
    curl -fsSL https://rustchain.org/install.sh | bash -s -- --wallet "$WALLET"
fi

# Step 2: Start mining (background)
echo "[*] Starting miner for 24 hours..."
nohup rustchain-miner --wallet "$WALLET" --daemon > "$MINER_LOG" 2>&1 &
MINER_PID=$!
echo "[*] Miner PID: $MINER_PID"

# Step 3: Wait 24 hours (86400 seconds)
echo "[*] Waiting 24 hours..."
sleep 86400

# Step 4: Stop miner
kill "$MINER_PID" 2>/dev/null || true
echo "[*] Miner stopped."

# Step 5: Extract hardware report
echo ""
echo "=== HARDWARE FINGERPRINT REPORT ==="
echo "Wallet: $WALLET"
echo "Timestamp: $(date -u)"
echo ""

if [[ -f "$MINER_LOG" ]]; then
    grep -E "device|attestation|fingerprint" "$MINER_LOG" | tail -20
else
    echo "[!] Miner log not found at $MINER_LOG"
    echo "[!] Attempting to read from journalctl..."
    journalctl -u rustchain-miner --since "24 hours ago" | grep -E "device|attestation|fingerprint" | tail -20
fi

echo ""
echo "=== END REPORT ==="