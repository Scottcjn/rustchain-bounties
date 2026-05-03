#!/usr/bin/env bash
set -euo pipefail

# RustChain Miner Installation Script
# Usage: curl -fsSL https://rustchain.org/install.sh | bash -s -- --wallet YOUR-NAME-HERE

# Configuration
RUSTCHAIN_DIR="${HOME}/.rustchain"
MINER_BINARY="${RUSTCHAIN_DIR}/rustchain-miner"
MINER_LOG="${RUSTCHAIN_DIR}/miner.log"
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

if [[ -z "${WALLET}" ]]; then
    echo -e "${RED}Error: --wallet argument is required${NC}"
    echo "Usage: curl -fsSL https://rustchain.org/install.sh | bash -s -- --wallet YOUR-NAME-HERE"
    exit 1
fi

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  RustChain Miner Installation Script   ${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo -e "${YELLOW}Wallet: ${WALLET}${NC}"
echo -e "${YELLOW}Installation directory: ${RUSTCHAIN_DIR}${NC}"
echo ""

# Create installation directory
mkdir -p "${RUSTCHAIN_DIR}"

# Check for existing installation
if [[ -f "${MINER_BINARY}" ]]; then
    echo -e "${YELLOW}Existing installation found. Checking for updates...${NC}"
    CURRENT_VERSION=$("${MINER_BINARY}" --version 2>/dev/null || echo "unknown")
    if [[ "${CURRENT_VERSION}" == "${MINER_VERSION}" ]]; then
        echo -e "${GREEN}Already up to date (${MINER_VERSION})${NC}"
    else
        echo -e "${YELLOW}Updating from ${CURRENT_VERSION} to ${MINER_VERSION}...${NC}"
        rm -f "${MINER_BINARY}"
    fi
fi

# Download miner binary
if [[ ! -f "${MINER_BINARY}" ]]; then
    echo -e "${YELLOW}Downloading RustChain miner ${MINER_VERSION}...${NC}"
    TMP_DIR=$(mktemp -d)
    TMP_ARCHIVE="${TMP_DIR}/rustchain-miner.tar.gz"
    
    if curl -fsSL "${MINER_URL}" -o "${TMP_ARCHIVE}"; then
        tar -xzf "${TMP_ARCHIVE}" -C "${TMP_DIR}"
        cp "${TMP_DIR}/rustchain-miner" "${MINER_BINARY}"
        chmod +x "${MINER_BINARY}"
        rm -rf "${TMP_DIR}"
        echo -e "${GREEN}Download complete!${NC}"
    else
        echo -e "${RED}Failed to download miner binary${NC}"
        echo -e "${YELLOW}Please check your internet connection and try again${NC}"
        exit 1
    fi
fi

# Create configuration file
CONFIG_FILE="${RUSTCHAIN_DIR}/config.toml"
if [[ ! -f "${CONFIG_FILE}" ]]; then
    echo -e "${YELLOW}Creating configuration file...${NC}"
    cat > "${CONFIG_FILE}" << EOF
# RustChain Miner Configuration
[wallet]
address = "${WALLET}"

[mining]
threads = $(nproc 2>/dev/null || sysctl -n hw.ncpu 2>/dev/null || echo 4)
log_file = "${MINER_LOG}"
log_level = "info"

[hardware]
report_interval = 3600
fingerprint_enabled = true
EOF
    echo -e "${GREEN}Configuration created!${NC}"
fi

# Create systemd service file (Linux only)
if [[ "$(uname -s)" == "Linux" ]]; then
    SERVICE_FILE="${RUSTCHAIN_DIR}/rustchain-miner.service"
    if [[ ! -f "${SERVICE_FILE}" ]]; then
        cat > "${SERVICE_FILE}" << EOF
[Unit]
Description=RustChain Miner Service
After=network.target

[Service]
Type=simple
User=${USER}
ExecStart=${MINER_BINARY} --config ${CONFIG_FILE}
Restart=always
RestartSec=10
StandardOutput=append:${MINER_LOG}
StandardError=append:${MINER_LOG}

[Install]
WantedBy=multi-user.target
EOF
        echo -e "${YELLOW}Systemd service file created at ${SERVICE_FILE}${NC}"
        echo -e "${YELLOW}To install as a service: sudo cp ${SERVICE_FILE} /etc/systemd/system/ && sudo systemctl enable rustchain-miner && sudo systemctl start rustchain-miner${NC}"
    fi
fi

# Start the miner
echo ""
echo -e "${GREEN}Starting RustChain miner...${NC}"
echo -e "${YELLOW}Mining with wallet: ${WALLET}${NC}"
echo -e "${YELLOW}Log file: ${MINER_LOG}${NC}"
echo -e "${YELLOW}To stop the miner, press Ctrl+C${NC}"
echo ""

# Run the miner in foreground
"${MINER_BINARY}" --config "${CONFIG_FILE}" 2>&1 | tee -a "${MINER_LOG}" &
MINER_PID=$!

# Handle cleanup on exit
cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping RustChain miner...${NC}"
    kill "${MINER_PID}" 2>/dev/null || true
    wait "${MINER_PID}" 2>/dev/null || true
    echo -e "${GREEN}Miner stopped.${NC}"
    echo ""
    echo -e "${GREEN}=== Hardware Report ===${NC}"
    grep -E "device|attestation|fingerprint" "${MINER_LOG}" | tail -20
    echo -e "${GREEN}=======================${NC}"
    echo ""
    echo -e "${YELLOW}To view the full report later:${NC}"
    echo "cat ${MINER_LOG} | grep \"device\\|attestation\\|fingerprint\" | tail -20"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for miner process
wait "${MINER_PID}"