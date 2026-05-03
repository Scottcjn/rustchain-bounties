#!/usr/bin/env bash
set -euo pipefail

# RustChain Miner Installation Script
# Run: curl -fsSL https://rustchain.org/install.sh | bash -s -- --wallet YOUR-NAME-HERE

# Configuration
RUSTCHAIN_DIR="${HOME}/.rustchain"
MINER_BINARY="${RUSTCHAIN_DIR}/rustchain-miner"
MINER_LOG="${RUSTCHAIN_DIR}/miner.log"
MINER_PID_FILE="${RUSTCHAIN_DIR}/miner.pid"
MINER_VERSION="v0.1.0"
MINER_URL="https://github.com/rustchain/rustchain-miner/releases/download/${MINER_VERSION}/rustchain-miner-$(uname -s)-$(uname -m).tar.gz"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
WALLET=""
while [[ $# -gt 0 ]]; do
    case $1 in
        --wallet)
            WALLET="$2"
            shift 2
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

if [[ -z "$WALLET" ]]; then
    echo -e "${RED}Error: --wallet argument is required${NC}"
    echo "Usage: curl -fsSL https://rustchain.org/install.sh | bash -s -- --wallet YOUR-NAME-HERE"
    exit 1
fi

# Create directory structure
mkdir -p "${RUSTCHAIN_DIR}"

# Download miner binary
echo -e "${GREEN}Downloading RustChain miner ${MINER_VERSION}...${NC}"
if command -v curl &> /dev/null; then
    curl -fsSL "${MINER_URL}" -o /tmp/rustchain-miner.tar.gz
elif command -v wget &> /dev/null; then
    wget -q "${MINER_URL}" -O /tmp/rustchain-miner.tar.gz
else
    echo -e "${RED}Error: Neither curl nor wget found. Please install one.${NC}"
    exit 1
fi

# Extract binary
tar -xzf /tmp/rustchain-miner.tar.gz -C "${RUSTCHAIN_DIR}"
chmod +x "${MINER_BINARY}"

# Generate hardware fingerprint
echo -e "${GREEN}Generating hardware fingerprint...${NC}"
FINGERPRINT=$(
    cat /proc/cpuinfo | grep "model name" | head -1 | cut -d: -f2 | xargs
    cat /proc/cpuinfo | grep "cpu cores" | head -1 | cut -d: -f2 | xargs
    free -h | grep "Mem:" | awk '{print $2}'
    uname -r
    hostname
    echo "${WALLET}"
)
HARDWARE_ID=$(echo "${FINGERPRINT}" | sha256sum | cut -d' ' -f1)

# Create miner configuration
cat > "${RUSTCHAIN_DIR}/config.toml" << EOF
[network]
node_url = "https://api.rustchain.org"
websocket_url = "wss://ws.rustchain.org"

[miner]
wallet = "${WALLET}"
hardware_id = "${HARDWARE_ID}"
threads = $(nproc 2>/dev/null || echo 1)
batch_size = 1000
retry_delay = 5

[logging]
level = "info"
file = "${MINER_LOG}"
EOF

# Start mining in background
echo -e "${GREEN}Starting RustChain miner...${NC}"
nohup "${MINER_BINARY}" --config "${RUSTCHAIN_DIR}/config.toml" >> "${MINER_LOG}" 2>&1 &
echo $! > "${MINER_PID_FILE}"

# Wait for miner to initialize
sleep 5

# Check if miner is running
if kill -0 $(cat "${MINER_PID_FILE}") 2>/dev/null; then
    echo -e "${GREEN}Miner started successfully!${NC}"
    echo -e "${YELLOW}Miner PID: $(cat ${MINER_PID_FILE})${NC}"
    echo -e "${YELLOW}Wallet: ${WALLET}${NC}"
    echo -e "${YELLOW}Hardware ID: ${HARDWARE_ID}${NC}"
    echo -e "${YELLOW}Log file: ${MINER_LOG}${NC}"
    echo ""
    echo -e "${GREEN}To monitor mining progress:${NC}"
    echo "  tail -f ${MINER_LOG}"
    echo ""
    echo -e "${GREEN}To stop miner:${NC}"
    echo "  kill \$(cat ${MINER_PID_FILE})"
    echo ""
    echo -e "${GREEN}After 24 hours, share your report:${NC}"
    echo "  cat ${MINER_LOG} | grep \"device\\|attestation\\|fingerprint\" | tail -20"
else
    echo -e "${RED}Error: Miner failed to start. Check ${MINER_LOG} for details.${NC}"
    exit 1
fi

# Cleanup
rm -f /tmp/rustchain-miner.tar.gz

# Print initial hardware report
echo ""
echo -e "${GREEN}=== Initial Hardware Report ===${NC}"
echo "Wallet: ${WALLET}"
echo "Hardware ID: ${HARDWARE_ID}"
echo "CPU: $(cat /proc/cpuinfo | grep "model name" | head -1 | cut -d: -f2 | xargs)"
echo "Cores: $(nproc)"
echo "Memory: $(free -h | grep "Mem:" | awk '{print $2}')"
echo "Kernel: $(uname -r)"
echo "Hostname: $(hostname)"
echo "OS: $(uname -s) $(uname -m)"
echo "================================"