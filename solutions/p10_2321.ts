#!/bin/bash

# sophia-edge-node installation and test script for ARM Linux devices
# This script automates the process described in the GitHub issue

set -e

# Configuration
REPO_URL="https://github.com/Scottcjn/sophia-edge-node"
INSTALL_DIR="$HOME/sophia-edge-node"
LOG_FILE="$HOME/sophia-edge-node-test.log"
WALLET="TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu"
MINER_DURATION=3600  # 1 hour in seconds

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check if running on ARM
check_arm() {
    if [[ $(uname -m) != "armv7l" && $(uname -m) != "aarch64" ]]; then
        log "ERROR: This script is intended for ARM Linux devices only"
        exit 1
    fi
    log "ARM architecture detected: $(uname -m)"
}

# Function to collect hardware info
collect_hardware_info() {
    log "=== Hardware Information ==="
    log "Model: $(cat /proc/device-tree/model 2>/dev/null || echo 'Unknown')"
    log "Architecture: $(uname -m)"
    log "Kernel: $(uname -r)"
    log "OS: $(cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d'"' -f2 || echo 'Unknown')"
    log "Total RAM: $(free -h | grep Mem | awk '{print $2}')"
    log "Available RAM: $(free -h | grep Mem | awk '{print $7}')"
    log "CPU: $(cat /proc/cpuinfo | grep 'model name' | head -1 | cut -d':' -f2 | xargs || echo 'Unknown')"
    log "CPU Cores: $(nproc)"
    log "Disk Usage: $(df -h / | tail -1 | awk '{print $3 " used / " $2 " total (" $5 " used)"}')"
    log "Temperature: $(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null | awk '{print $1/1000 "°C"}' || echo 'N/A')"
    log "============================"
}

# Function to install dependencies
install_dependencies() {
    log "Installing dependencies..."
    sudo apt-get update -qq
    sudo apt-get install -y -qq git curl wget build-essential libssl-dev pkg-config
    log "Dependencies installed successfully"
}

# Function to clone and install sophia-edge-node
install_sophia_edge() {
    log "Cloning sophia-edge-node repository..."
    if [ -d "$INSTALL_DIR" ]; then
        log "Directory exists, updating..."
        cd "$INSTALL_DIR"
        git pull
    else
        git clone "$REPO_URL" "$INSTALL_DIR"
        cd "$INSTALL_DIR"
    fi
    
    log "Running install.sh..."
    if sudo ./install.sh 2>&1 | tee -a "$LOG_FILE"; then
        log "install.sh completed successfully"
        return 0
    else
        log "ERROR: install.sh failed"
        return 1
    fi
}

# Function to run the miner
run_miner() {
    log "Starting miner for $MINER_DURATION seconds (1 hour)..."
    log "Using wallet: $WALLET"
    
    # Start miner in background
    cd "$INSTALL_DIR"
    if [ -f "./sophia-miner" ]; then
        ./sophia-miner --wallet "$WALLET" --daemon &
        MINER_PID=$!
    elif [ -f "./miner" ]; then
        ./miner --wallet "$WALLET" --daemon &
        MINER_PID=$!
    else
        log "ERROR: Miner binary not found"
        return 1
    fi
    
    log "Miner started with PID: $MINER_PID"
    
    # Monitor miner for specified duration
    local elapsed=0
    while [ $elapsed -lt $MINER_DURATION ]; do
        if ! kill -0 $MINER_PID 2>/dev/null; then
            log "ERROR: Miner process died unexpectedly"
            return 1
        fi
        
        # Log miner status every 5 minutes
        if [ $((elapsed % 300)) -eq 0 ]; then
            log "Miner running for $((elapsed / 60)) minutes..."
            # Check for attestation submissions
            if grep -q "attestation" "$LOG_FILE" 2>/dev/null; then
                log "Attestation submissions detected"
            fi
        fi
        
        sleep 60
        elapsed=$((elapsed + 60))
    done
    
    # Stop miner
    kill $MINER_PID 2>/dev/null || true
    wait $MINER_PID 2>/dev/null || true
    log "Miner stopped after 1 hour"
    return 0
}

# Function to generate report
generate_report() {
    log "=== Final Report ==="
    echo ""
    echo "=========================================="
    echo "  sophia-edge-node Test Report"
    echo "=========================================="
    echo ""
    echo "Wallet: $WALLET"
    echo ""
    echo "Hardware Information:"
    echo "  Model: $(cat /proc/device-tree/model 2>/dev/null || echo 'Unknown')"
    echo "  RAM: $(free -h | grep Mem | awk '{print $2}')"
    echo "  OS: $(cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d'"' -f2 || echo 'Unknown')"
    echo "  Architecture: $(uname -m)"
    echo ""
    echo "Installation Status:"
    if grep -q "install.sh completed successfully" "$LOG_FILE" 2>/dev/null; then
        echo "  ✓ install.sh completed without errors"
    else
        echo "  ✗ install.sh encountered errors (check log)"
    fi
    echo ""
    echo "Miner Status:"
    if grep -q "Miner stopped after 1 hour" "$LOG_FILE" 2>/dev/null; then
        echo "  ✓ Miner ran for 1 hour successfully"
    else
        echo "  ✗ Miner did not complete 1 hour run"
    fi
    echo ""
    echo "Attestation:"
    if grep -q "attestation" "$LOG_FILE" 2>/dev/null; then
        echo "  ✓ Miner connected and submitted attestation"
    else
        echo "  ? Attestation status unknown (check log)"
    fi
    echo ""
    echo "Log file: $LOG_FILE"
    echo "=========================================="
}

# Main execution
main() {
    log "Starting sophia-edge-node installation and test"
    log "============================================"
    
    check_arm
    collect_hardware_info
    install_dependencies
    
    if install_sophia_edge; then
        log "Installation successful, starting miner..."
        if run_miner; then
            log "Miner completed successfully"
        else
            log "Miner encountered issues"
        fi
    else
        log "Installation failed, cannot start miner"
    fi
    
    generate_report
    log "Test completed. See $LOG_FILE for details"
}

# Run main function
main