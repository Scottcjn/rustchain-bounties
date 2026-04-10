#!/bin/bash
# ============================================================
# RustChain Miner Docker Entrypoint
# ============================================================

set -e

echo "============================================"
echo "  RustChain Miner — Docker Edition"
echo "============================================"
echo "  WALLET_NAME : ${WALLET_NAME:-NOT SET}"
echo "  NODE_URL    : ${NODE_URL:-https://50.28.86.131}"
echo "  BLOCK_TIME  : ${BLOCK_TIME:-600}"
echo "  LOG_LEVEL   : ${LOG_LEVEL:-INFO}"
echo "============================================"

# Validate required env
if [ -z "$WALLET_NAME" ]; then
    echo "ERROR: WALLET_NAME is required. Set -e WALLET_NAME=your_wallet_id"
    exit 1
fi

# Auto-detect miner script
MINER_SCRIPT=""

if [ -f "/app/miners/rustchain_linux_miner.py" ]; then
    MINER_SCRIPT="/app/miners/rustchain_linux_miner.py"
elif [ -f "/app/miners/rustchain_universal_miner.py" ]; then
    MINER_SCRIPT="/app/miners/rustchain_universal_miner.py"
elif [ -f "/app/miners/vintage_miner_client.py" ]; then
    MINER_SCRIPT="/app/miners/vintage_miner_client.py"
else
    echo "ERROR: No miner script found in /app/miners/"
    ls -la /app/miners/
    exit 1
fi

echo "Using miner script: $MINER_SCRIPT"

# Run the miner
cd /app
exec python3 "$MINER_SCRIPT" \
    --wallet "$WALLET_NAME" \
    --node-url "${NODE_URL:-https://50.28.86.131}" \
    --block-time "${BLOCK_TIME:-600}" \
    --log-level "${LOG_LEVEL:-INFO}"
