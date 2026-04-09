#!/bin/bash
set -e

echo "========================================"
echo "RustChain Proof-of-Antiquity Miner"
echo "Docker Container Edition v1.0.0"
echo "========================================"

# Validate WALLET_NAME is set
if [ -z "$WALLET_NAME" ] || [ "$WALLET_NAME" = "your_wallet_name_here" ]; then
    echo "[ERROR] WALLET_NAME environment variable is required!"
    echo "Example: docker run -e WALLET_NAME=my_wallet ..."
    exit 1
fi

echo "[CONFIG] Wallet: $WALLET_NAME"
echo "[CONFIG] Node URL: $NODE_URL"

# Warn about reduced rewards in Docker
echo ""
echo "[WARN] ==========================================="
echo "[WARN] Docker miners receive REDUCED REWARDS"
echo "[WARN] due to anti-VM detection in RustChain."
echo "[WARN] For maximum rewards, run on physical hardware."
echo "[WARN] ==========================================="
echo ""

# Execute the miner
exec "$@"
