#!/bin/bash

# sophia-edge-node installation and test script for ARM Linux devices

set -e

# Configuration
REPO_URL="https://github.com/Scottcjn/sophia-edge-node"
INSTALL_DIR="$HOME/sophia-edge-node"
LOG_FILE="$HOME/sophia-edge-node-test.log"
WALLET="TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu"
MINER_DURATION=3600  # 1 hour in seconds

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Error handling
error_exit() {
    log "${RED}ERROR: $1${NC}"
    exit 1
}

# Hardware detection
detect_hardware() {
    log "${YELLOW}Detecting hardware...${NC}"
    
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
    
    log "Hardware: $MODEL"
    log "RAM: $RAM"
    log "OS: $OS_VERSION"
}

# Installation
install_sophia() {
    log "${YELLOW}Starting installation...${NC}"
    
    # Clean previous installation
    if [ -d "$INSTALL_DIR" ]; then
        log "Removing previous installation..."
        rm -rf "$INSTALL_DIR"
    fi
    
    # Clone repository
    log "Cloning repository..."
    git clone "$REPO_URL" "$INSTALL_DIR" || error_exit "Failed to clone repository"
    
    cd "$INSTALL_DIR"
    
    # Run install script
    log "Running install.sh..."
    if sudo ./install.sh 2>&1 | tee -a "$LOG_FILE"; then
        log "${GREEN}Installation completed successfully${NC}"
        INSTALL_SUCCESS=true
    else
        log "${RED}Installation failed${NC}"
        INSTALL_SUCCESS=false
        return 1
    fi
}

# Run miner
run_miner() {
    log "${YELLOW}Starting miner...${NC}"
    
    # Check if miner binary exists
    MINER_BIN="$INSTALL_DIR/sophia-miner"
    if [ ! -f "$MINER_BIN" ]; then
        log "${RED}Miner binary not found at $MINER_BIN${NC}"
        return 1
    fi
    
    # Start miner in background
    log "Starting miner with wallet: $WALLET"
    $MINER_BIN --wallet "$WALLET" --daemon &
    MINER_PID=$!
    
    log "Miner started with PID: $MINER_PID"
    
    # Monitor miner for specified duration
    START_TIME=$(date +%s)
    END_TIME=$((START_TIME + MINER_DURATION))
    
    while [ $(date +%s) -lt $END_TIME ]; do
        if ! kill -0 $MINER_PID 2>/dev/null; then
            log "${RED}Miner process died unexpectedly${NC}"
            return 1
        fi
        
        # Check miner logs for attestation
        if grep -q "attestation" "$LOG_FILE" 2>/dev/null; then
            log "${GREEN}Attestation submitted successfully${NC}"
            ATTESTATION_SUCCESS=true
        fi
        
        sleep 60
        log "Miner running... ($(( (END_TIME - $(date +%s)) / 60 )) minutes remaining)"
    done
    
    # Stop miner
    log "Stopping miner..."
    kill $MINER_PID 2>/dev/null || true
    wait $MINER_PID 2>/dev/null || true
    
    log "${GREEN}Miner completed 1 hour run${NC}"
    return 0
}

# Generate report
generate_report() {
    log "${YELLOW}Generating report...${NC}"
    
    REPORT_FILE="$HOME/sophia-edge-node-report.txt"
    
    cat > "$REPORT_FILE" << EOF
========================================
Sophia Edge Node Test Report
========================================
Date: $(date)
Wallet: $WALLET

Hardware Information:
- Model: $MODEL
- RAM: $RAM
- OS: $OS_VERSION

Installation:
- Status: $([ "$INSTALL_SUCCESS" = true ] && echo "SUCCESS" || echo "FAILED")
- Errors: $(grep -i "error" "$LOG_FILE" | wc -l)

Miner Performance:
- Duration: 1 hour
- Attestation Submitted: $([ "$ATTESTATION_SUCCESS" = true ] && echo "YES" || echo "NO")
- Process Stable: $([ "$MINER_STABLE" = true ] && echo "YES" || echo "NO")

Log File: $LOG_FILE
========================================
EOF
    
    log "${GREEN}Report generated: $REPORT_FILE${NC}"
    cat "$REPORT_FILE"
}

# Main execution
main() {
    log "${GREEN}Starting Sophia Edge Node Test${NC}"
    log "========================================"
    
    detect_hardware
    
    if install_sophia; then
        if run_miner; then
            MINER_STABLE=true
        else
            MINER_STABLE=false
        fi
    fi
    
    generate_report
    
    log "${GREEN}Test completed. Check $REPORT_FILE for summary.${NC}"
}

# Run main function
main