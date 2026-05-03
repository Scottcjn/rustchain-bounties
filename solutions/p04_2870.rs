#!/usr/bin/env bash
set -euo pipefail

# RustChain Miner Installation Script
# Usage: curl -fsSL https://rustchain.org/install.sh | bash -s -- --wallet YOUR-NAME-HERE

WALLET="${1:-}"
if [[ -z "$WALLET" ]]; then
    echo "Error: --wallet argument is required"
    echo "Usage: curl -fsSL https://rustchain.org/install.sh | bash -s -- --wallet YOUR-NAME-HERE"
    exit 1
fi

# Configuration
MINER_VERSION="1.0.0"
MINER_DIR="$HOME/.rustchain"
MINER_BIN="$MINER_DIR/rustchain-miner"
MINER_LOG="$MINER_DIR/miner.log"
MINER_PID="$MINER_DIR/miner.pid"
MINER_CONFIG="$MINER_DIR/config.toml"

# Detect architecture
ARCH=$(uname -m)
OS=$(uname -s | tr '[:upper:]' '[:lower:]')

case "$ARCH" in
    x86_64|amd64) ARCH="x86_64" ;;
    aarch64|arm64) ARCH="aarch64" ;;
    *) echo "Unsupported architecture: $ARCH"; exit 1 ;;
esac

case "$OS" in
    linux) OS="linux" ;;
    darwin) OS="darwin" ;;
    *) echo "Unsupported OS: $OS"; exit 1 ;;
esac

# Create directory structure
mkdir -p "$MINER_DIR"
mkdir -p "$MINER_DIR/data"
mkdir -p "$MINER_DIR/keys"

# Download miner binary
DOWNLOAD_URL="https://github.com/rustchain/miner/releases/download/v${MINER_VERSION}/rustchain-miner-${OS}-${ARCH}.tar.gz"
echo "Downloading RustChain miner v${MINER_VERSION} for ${OS}/${ARCH}..."
curl -fsSL "$DOWNLOAD_URL" -o /tmp/rustchain-miner.tar.gz

# Extract binary
tar -xzf /tmp/rustchain-miner.tar.gz -C /tmp
mv /tmp/rustchain-miner "$MINER_BIN"
chmod +x "$MINER_BIN"
rm -f /tmp/rustchain-miner.tar.gz

# Generate wallet keys if not exist
if [[ ! -f "$MINER_DIR/keys/wallet.key" ]]; then
    echo "Generating wallet keys..."
    "$MINER_BIN" keygen --output "$MINER_DIR/keys/wallet.key" --pubkey "$MINER_DIR/keys/wallet.pub"
fi

# Create config file
cat > "$MINER_CONFIG" << EOF
[network]
node = "mainnet.rustchain.org:8333"
max_peers = 50

[mining]
threads = $(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
wallet = "$WALLET"
data_dir = "$MINER_DIR/data"

[attestation]
enabled = true
interval_seconds = 3600
output_file = "$MINER_DIR/attestation.log"

[reporting]
device_fingerprint = true
hardware_report = true
EOF

# Start miner in background
echo "Starting RustChain miner..."
nohup "$MINER_BIN" --config "$MINER_CONFIG" >> "$MINER_LOG" 2>&1 &
echo $! > "$MINER_PID"

echo ""
echo "============================================"
echo "RustChain Miner Started Successfully!"
echo "============================================"
echo "Wallet: $WALLET"
echo "PID: $(cat $MINER_PID)"
echo "Log: $MINER_LOG"
echo ""
echo "Run for 24 hours, then share your report:"
echo "cat ~/.rustchain/miner.log | grep \"device\\|attestation\\|fingerprint\" | tail -20"
echo "============================================"

# Wait for initial startup
sleep 5

# Show initial status
echo ""
echo "Initial status:"
tail -5 "$MINER_LOG" 2>/dev/null || echo "Waiting for first block..."