#!/bin/bash

# sophia-edge-node installation and test script for ARM Linux devices
# This script automates the installation, running, and reporting process

set -e

# Configuration
REPO_URL="https://github.com/Scottcjn/sophia-edge-node"
REPO_DIR="sophia-edge-node"
MINER_DURATION=3600  # 1 hour in seconds
REPORT_FILE="sophia_edge_report.txt"
WALLET="TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to log messages
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [ "$EUID" -ne 0 ]; then 
        error "Please run as root (use sudo)"
        exit 1
    fi
}

# Function to detect hardware
detect_hardware() {
    log "Detecting hardware..."
    
    # Get model
    if [ -f /proc/device-tree/model ]; then
        MODEL=$(tr -d '\0' < /proc/device-tree/model)
    elif command -v uname &> /dev/null; then
        MODEL=$(uname -m)
    else
        MODEL="Unknown"
    fi
    
    # Get RAM
    if command -v free &> /dev/null; then
        RAM=$(free -h | awk '/^Mem:/ {print $2}')
    else
        RAM="Unknown"
    fi
    
    # Get OS version
    if [ -f /etc/os-release ]; then
        OS_VERSION=$(grep -w "PRETTY_NAME" /etc/os-release | cut -d= -f2 | tr -d '"')
    elif command -v lsb_release &> /dev/null; then
        OS_VERSION=$(lsb_release -d | cut -f2)
    else
        OS_VERSION=$(uname -a)
    fi
    
    log "Hardware detected:"
    log "  Model: $MODEL"
    log "  RAM: $RAM"
    log "  OS: $OS_VERSION"
}

# Function to install dependencies
install_dependencies() {
    log "Installing dependencies..."
    
    # Update package list
    apt-get update -qq
    
    # Install required packages
    apt-get install -y -qq \
        git \
        build-essential \
        curl \
        wget \
        jq \
        python3 \
        python3-pip \
        libssl-dev \
        pkg-config \
        cmake \
        clang \
        llvm \
        libclang-dev \
        protobuf-compiler \
        screen \
        tmux \
        2>&1 | tail -1
    
    # Install Rust if not present
    if ! command -v rustc &> /dev/null; then
        log "Installing Rust..."
        curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
        source "$HOME/.cargo/env"
    fi
    
    log "Dependencies installed successfully"
}

# Function to clone and install sophia-edge-node
install_sophia() {
    log "Cloning sophia-edge-node repository..."
    
    # Remove existing directory if present
    if [ -d "$REPO_DIR" ]; then
        warn "Removing existing $REPO_DIR directory"
        rm -rf "$REPO_DIR"
    fi
    
    # Clone repository
    git clone "$REPO_URL" "$REPO_DIR"
    cd "$REPO_DIR"
    
    log "Running install.sh..."
    if sudo ./install.sh; then
        INSTALL_STATUS="SUCCESS"
        log "Installation completed successfully"
    else
        INSTALL_STATUS="FAILED"
        error "Installation failed"
        return 1
    fi
}

# Function to configure and run miner
run_miner() {
    log "Configuring and starting miner..."
    
    # Create configuration directory
    mkdir -p ~/.sophia
    
    # Create config file
    cat > ~/.sophia/config.toml << EOF
[network]
listen_address = "0.0.0.0:30333"
public_address = "0.0.0.0:30333"

[mining]
enabled = true
wallet = "$WALLET"
threads = $(nproc)

[storage]
path = "/var/lib/sophia"
EOF
    
    # Start miner in background
    log "Starting miner for $MINER_DURATION seconds..."
    
    # Use screen to run miner in background
    screen -dmS sophia-miner bash -c "
        cd $REPO_DIR
        ./target/release/sophia-node --config ~/.sophia/config.toml 2>&1 | tee /tmp/sophia_miner.log
    "
    
    MINER_PID=$(screen -ls | grep sophia-miner | awk '{print $1}' | cut -d. -f1)
    log "Miner started with PID: $MINER_PID"
    
    # Wait for specified duration
    log "Waiting for $MINER_DURATION seconds..."
    sleep $MINER_DURATION
    
    # Check if miner is still running
    if screen -list | grep -q "sophia-miner"; then
        MINER_STATUS="RUNNING"
        log "Miner is still running"
    else
        MINER_STATUS="STOPPED"
        warn "Miner has stopped"
    fi
    
    # Check logs for attestation
    if grep -q "attestation" /tmp/sophia_miner.log 2>/dev/null; then
        ATTESTATION_STATUS="SUCCESS"
        log "Attestation found in logs"
    else
        ATTESTATION_STATUS="NOT_FOUND"
        warn "No attestation found in logs"
    fi
    
    # Check connection status
    if grep -q "connected" /tmp/sophia_miner.log 2>/dev/null; then
        CONNECTION_STATUS="CONNECTED"
        log "Miner connected to network"
    else
        CONNECTION_STATUS="DISCONNECTED"
        warn "Miner not connected to network"
    fi
}

# Function to generate report
generate_report() {
    log "Generating report..."
    
    cat > "$REPORT_FILE" << EOF
========================================
SOPHIA EDGE NODE INSTALLATION REPORT
========================================
Date: $(date)
Wallet: $WALLET

HARDWARE INFORMATION
--------------------
Model: $MODEL
RAM: $RAM
OS Version: $OS_VERSION
CPU Cores: $(nproc)
Architecture: $(uname -m)

INSTALLATION STATUS
-------------------
Install Script: $INSTALL_STATUS
Dependencies: Installed
Rust Version: $(rustc --version 2>/dev/null || echo "Not installed")

MINER STATUS
------------
Miner Status: $MINER_STATUS
Connection Status: $CONNECTION_STATUS
Attestation Status: $ATTESTATION_STATUS
Run Duration: $MINER_DURATION seconds

LOGS SUMMARY
------------
$(tail -20 /tmp/sophia_miner.log 2>/dev/null || echo "No logs available")

RECOMMENDATIONS
---------------
$(if [ "$INSTALL_STATUS" = "FAILED" ]; then
    echo "- Check system requirements and dependencies"
    echo "- Ensure sufficient disk space and memory"
    echo "- Review install.sh for specific error messages"
elif [ "$MINER_STATUS" = "STOPPED" ]; then
    echo "- Check network connectivity"
    echo "- Verify firewall settings (port 30333)"
    echo "- Ensure sufficient system resources"
elif [ "$ATTESTATION_STATUS" = "NOT_FOUND" ]; then
    echo "- Wait longer for attestation submission"
    echo "- Check peer connections"
    echo "- Verify wallet address configuration"
else
    echo "- System is working correctly"
    echo "- Consider running miner continuously"
    echo "- Monitor system resources regularly"
fi)

========================================
EOF
    
    log "Report generated: $REPORT_FILE"
    cat "$REPORT_FILE"
}

# Function to cleanup
cleanup() {
    log "Cleaning up..."
    
    # Stop miner if running
    if screen -list | grep -q "sophia-miner"; then
        screen -S sophia-miner -X quit
        log "Miner stopped"
    fi
    
    # Kill any remaining processes
    pkill -f "sophia-node" 2>/dev/null || true
}

# Main execution
main() {
    log "Starting sophia-edge-node installation and test..."
    
    check_root
    detect_hardware
    install_dependencies
    install_sophia
    run_miner
    generate_report
    cleanup
    
    log "Script completed. Report saved to $REPORT_FILE"
}

# Trap for cleanup on exit
trap cleanup EXIT

# Run main function
main