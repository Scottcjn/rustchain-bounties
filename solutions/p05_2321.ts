#!/bin/bash

# sophia-edge-node installation and test script for ARM Linux devices
# This script automates the installation, running, and reporting process

set -e

# Configuration
REPO_URL="https://github.com/Scottcjn/sophia-edge-node"
REPO_DIR="sophia-edge-node"
MINER_DURATION=3600  # 1 hour in seconds
REPORT_FILE="sophia_edge_node_report.txt"
WALLET="TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to log messages
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

warn() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Function to check if running as root
check_root() {
    if [[ $EUID -ne 0 ]]; then
        error "This script must be run as root (use sudo)"
        exit 1
    fi
}

# Function to detect hardware
detect_hardware() {
    log "Detecting hardware..."
    
    # Get model
    if [[ -f /proc/device-tree/model ]]; then
        MODEL=$(tr -d '\0' < /proc/device-tree/model)
    elif [[ -f /sys/firmware/devicetree/base/model ]]; then
        MODEL=$(tr -d '\0' < /sys/firmware/devicetree/base/model)
    else
        MODEL=$(uname -m)
    fi
    
    # Get RAM
    TOTAL_RAM=$(free -h | awk '/^Mem:/ {print $2}')
    
    # Get OS version
    if [[ -f /etc/os-release ]]; then
        OS_VERSION=$(grep -w "PRETTY_NAME" /etc/os-release | cut -d'"' -f2)
    elif [[ -f /etc/debian_version ]]; then
        OS_VERSION="Debian $(cat /etc/debian_version)"
    else
        OS_VERSION=$(uname -a)
    fi
    
    log "Hardware detected:"
    log "  Model: $MODEL"
    log "  RAM: $TOTAL_RAM"
    log "  OS: $OS_VERSION"
}

# Function to install dependencies
install_dependencies() {
    log "Installing dependencies..."
    
    apt-get update
    apt-get install -y git curl wget build-essential libssl-dev libzmq3-dev \
        libboost-all-dev libsodium-dev libprotobuf-dev protobuf-compiler \
        python3 python3-pip jq screen || {
        error "Failed to install dependencies"
        return 1
    }
    
    log "Dependencies installed successfully"
}

# Function to clone repository
clone_repository() {
    log "Cloning repository..."
    
    if [[ -d "$REPO_DIR" ]]; then
        warn "Directory $REPO_DIR already exists. Removing..."
        rm -rf "$REPO_DIR"
    fi
    
    git clone "$REPO_URL" || {
        error "Failed to clone repository"
        return 1
    }
    
    cd "$REPO_DIR"
    log "Repository cloned successfully"
}

# Function to run install.sh
run_install() {
    log "Running install.sh..."
    
    if [[ ! -f "install.sh" ]]; then
        error "install.sh not found in current directory"
        return 1
    fi
    
    chmod +x install.sh
    if sudo ./install.sh; then
        log "install.sh completed successfully"
        INSTALL_SUCCESS=true
    else
        error "install.sh failed"
        INSTALL_SUCCESS=false
        return 1
    fi
}

# Function to configure miner
configure_miner() {
    log "Configuring miner..."
    
    # Create config directory if it doesn't exist
    mkdir -p ~/.sophia
    
    # Create config file
    cat > ~/.sophia/config.json << EOF
{
    "wallet": "$WALLET",
    "miner": {
        "threads": $(nproc),
        "duration": $MINER_DURATION
    },
    "network": {
        "node": "mainnet.sophia.network:443",
        "protocol": "https"
    }
}
EOF
    
    log "Miner configured with wallet: $WALLET"
}

# Function to run miner
run_miner() {
    log "Starting miner for $MINER_DURATION seconds..."
    
    # Start miner in background
    if command -v sophia-miner &> /dev/null; then
        sophia-miner --config ~/.sophia/config.json > miner_output.log 2>&1 &
        MINER_PID=$!
    elif [[ -f "./sophia-miner" ]]; then
        ./sophia-miner --config ~/.sophia/config.json > miner_output.log 2>&1 &
        MINER_PID=$!
    else
        error "Miner binary not found"
        return 1
    fi
    
    log "Miner started with PID: $MINER_PID"
    
    # Monitor miner for specified duration
    local elapsed=0
    while [[ $elapsed -lt $MINER_DURATION ]]; do
        if ! kill -0 $MINER_PID 2>/dev/null; then
            error "Miner process died unexpectedly"
            return 1
        fi
        
        sleep 10
        elapsed=$((elapsed + 10))
        
        # Show progress every minute
        if [[ $((elapsed % 60)) -eq 0 ]]; then
            local remaining=$((MINER_DURATION - elapsed))
            log "Miner running... $((elapsed / 60)) minutes elapsed, $((remaining / 60)) minutes remaining"
        fi
    done
    
    # Stop miner
    kill $MINER_PID 2>/dev/null || true
    wait $MINER_PID 2>/dev/null || true
    
    log "Miner stopped after $MINER_DURATION seconds"
}

# Function to check miner output
check_miner_output() {
    log "Checking miner output..."
    
    if [[ ! -f "miner_output.log" ]]; then
        warn "Miner output log not found"
        MINER_CONNECTED=false
        return
    fi
    
    # Check for successful connection
    if grep -q "connected" miner_output.log || grep -q "Connected" miner_output.log; then
        log "Miner successfully connected to network"
        MINER_CONNECTED=true
    else
        warn "Miner connection status unclear"
        MINER_CONNECTED=false
    fi
    
    # Check for attestation
    if grep -q "attestation" miner_output.log || grep -q "Attestation" miner_output.log; then
        log "Miner submitted attestation"
        MINER_ATTESTED=true
    else
        warn "No attestation found in miner output"
        MINER_ATTESTED=false
    fi
    
    # Check for errors
    if grep -qi "error\|failed\|exception" miner_output.log; then
        warn "Errors found in miner output"
        MINER_ERRORS=true
    else
        MINER_ERRORS=false
    fi
}

# Function to generate report
generate_report() {
    log "Generating report..."
    
    cat > "$REPORT_FILE" << EOF
========================================
Sophia Edge Node Installation Report
========================================
Date: $(date)
Wallet: $WALLET

1. Hardware Information
----------------------
   Model: $MODEL
   RAM: $TOTAL_RAM
   OS Version: $OS_VERSION
   CPU Cores: $(nproc)
   Architecture: $(uname -m)

2. Installation Status
---------------------
   Repository cloned: Yes
   Dependencies installed: Yes
   install.sh completed: $INSTALL_SUCCESS
   Installation errors: $(if $INSTALL_SUCCESS; then echo "None"; else echo "Yes - check install.log"; fi)

3. Miner Performance
-------------------
   Mining duration: $((MINER_DURATION / 60)) minutes
   Connected to network: $MINER_CONNECTED
   Attestation submitted: $MINER_ATTESTED
   Errors during mining: $MINER_ERRORS

4. Additional Notes
------------------
   - System load during mining: $(uptime | awk -F'load average:' '{print $2}')
   - Memory usage: $(free -h | awk '/^Mem:/ {print $3 "/" $2}')
   - Disk usage: $(df -h / | awk 'NR==2 {print $5}')
   - Temperature: $(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null | awk '{print $1/1000 "°C"}' || echo "N/A")

5. Report Summary
----------------
   Status: $(if $INSTALL_SUCCESS && $MINER_CONNECTED && $MINER_ATTESTED; then echo "WORKING"; else echo "ISSUES FOUND"; fi)
   Bounty: 2 RTC
   Submitted by: $WALLET
EOF
    
    log "Report generated: $REPORT_FILE"
    cat "$REPORT_FILE"
}

# Main execution
main() {
    echo "========================================"
    echo "Sophia Edge Node Installation & Test Script"
    echo "========================================"
    echo ""
    
    # Check root
    check_root
    
    # Initialize variables
    INSTALL_SUCCESS=false
    MINER_CONNECTED=false
    MINER_ATTESTED=false
    MINER_ERRORS=false
    
    # Step 1: Detect hardware
    detect_hardware
    
    # Step 2: Install dependencies
    install_dependencies || {
        error "Failed to install dependencies. Aborting."
        exit 1
    }
    
    # Step 3: Clone repository
    clone_repository || {
        error "Failed to clone repository. Aborting."
        exit 1
    }
    
    # Step 4: Run install.sh
    run_install || {
        warn "install.sh had issues. Continuing with manual setup..."
    }
    
    # Step 5: Configure miner
    configure_miner
    
    # Step 6: Run miner
    run_miner || {
        warn "Miner execution had issues"
    }
    
    # Step 7: Check miner output
    check_miner_output
    
    # Step 8: Generate report
    generate_report
    
    # Summary
    echo ""
    echo "========================================"
    echo "Test Complete"
    echo "========================================"
    echo ""
    
    if $INSTALL_SUCCESS && $MINER_CONNECTED && $MINER_ATTESTED; then
        log "All checks passed! Sophia Edge Node is working correctly."
        log "Report saved to: $REPORT_FILE"
        log "Submit this report along with your wallet address: $WALLET"
    else
        warn "Some checks failed. Please review the report for details."
        warn "Report saved to: $REPORT_FILE"
    fi
}

# Run main function
main "$@"