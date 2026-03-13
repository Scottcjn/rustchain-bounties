#!/bin/bash
#
# RustChain Miner for Cray-1
# Example Run Script
#
# Usage: ./run_example.sh [wallet_address]
#

WALLET=${1:-"RTC4325af95d26d59c3ef025963656d22af638bb96b"}
NODE_URL="https://50.28.86.131"

echo "========================================"
echo "RustChain Miner for Cray-1"
echo "Example Run Script"
echo "========================================"
echo
echo "Wallet: $WALLET"
echo "Node: $NODE_URL"
echo

# Check if miner exists
if [ ! -f "bin/RUSTCHAIN_MINER" ]; then
    echo "[ERROR] Miner not found!"
    echo "Please run ./build.sh first."
    exit 1
fi

# Load the miner
echo "[LOAD] Loading RUSTCHAIN_MINER..."
LOAD RUSTCHAIN_MINER

# Run the miner
echo "[RUN] Starting miner..."
echo
RUSTCHAIN_MINER -w "$WALLET" -n "$NODE_URL" -v

echo
echo "========================================"
echo "Mining session complete."
echo "========================================"
