#!/bin/bash

# sophia-edge-node installation and test script
# For ARM Linux devices (RPi 4/5, SBCs)
# Bounty: 2 RTC

set -e

# Configuration
REPO_URL="https://github.com/Scottcjn/sophia-edge-node"
INSTALL_DIR="$HOME/sophia-edge-node"
MINER_DURATION=3600  # 1 hour in seconds
WALLET="TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu"
LOG_FILE="$HOME/sophia-edge-node-test.log"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging function
log() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

error_log() {
    echo -e "${RED}[ERROR]${NC} $1" | tee -a "$LOG_FILE"
}

warn_log() {
    echo -e "${YELLOW}[WARN]${NC} $1" | tee -a "$LOG_FILE"
}

# Hardware detection
detect_hardware() {
    log "Detecting hardware..."
    
    # Get CPU info
    if [ -f /proc/cpuinfo ]; then
        CPU_MODEL=$(grep "Model" /proc/cpuinfo | head -1 | cut -d: -f2 | xargs)
        CPU_CORES=$(nproc)
    else
        CPU_MODEL="Unknown"
        CPU_CORES="Unknown"
    fi
    
    # Get RAM info
    if command -v free &> /dev/null; then
        TOTAL_RAM=$(free -h | grep "Mem:" | awk '{print $2}')
    else
        TOTAL_RAM="Unknown"
    fi
    
    # Get OS info
    if [ -f /etc/os-release ]; then
        OS_NAME=$(grep "PRETTY_NAME" /etc/os-release | cut -d= -f2 | tr -d '"')
    else
        OS_NAME="Unknown"
    fi
    
    # Get kernel version
    KERNEL=$(uname -r)
    
    # Get architecture
    ARCH=$(uname -m)
    
    log "Hardware detected:"
    log "  CPU Model: $CPU_MODEL"
    log "  CPU Cores: $CPU_CORES"
    log "  Total RAM: $TOTAL_RAM"
    log "  OS: $OS_NAME"
    log "  Kernel: $KERNEL"
    log "  Architecture: $ARCH"
    
    # Save to report
    cat > "$HOME/hardware_report.txt" << EOF
Hardware Report
===============
CPU Model: $CPU_MODEL
CPU Cores: $CPU_CORES
Total RAM: $TOTAL_RAM
OS: $OS_NAME
Kernel: $KERNEL
Architecture: $ARCH
EOF
}

# Check dependencies
check_dependencies() {
    log "Checking dependencies..."
    
    # Check for git
    if ! command -v git &> /dev/null; then
        warn_log "Git not found. Installing..."
        sudo apt-get update && sudo apt-get install -y git
    fi
    
    # Check for curl
    if ! command -v curl &> /dev/null; then
        warn_log "Curl not found. Installing..."
        sudo apt-get install -y curl
    fi
    
    # Check for jq
    if ! command -v jq &> /dev/null; then
        warn_log "jq not found. Installing..."
        sudo apt-get install -y jq
    fi
    
    log "All dependencies satisfied."
}

# Clone repository
clone_repo() {
    log "Cloning sophia-edge-node repository..."
    
    if [ -d "$INSTALL_DIR" ]; then
        warn_log "Directory $INSTALL_DIR already exists. Removing..."
        rm -rf "$INSTALL_DIR"
    fi
    
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    log "Repository cloned successfully."
}

# Run installation
run_install() {
    log "Running install.sh..."
    
    if [ ! -f "$INSTALL_DIR/install.sh" ]; then
        error_log "install.sh not found in $INSTALL_DIR"
        return 1
    fi
    
    chmod +x "$INSTALL_DIR/install.sh"
    
    # Run install with sudo
    if sudo ./install.sh 2>&1 | tee -a "$LOG_FILE"; then
        log "Installation completed successfully."
        echo "INSTALL_STATUS=SUCCESS" >> "$HOME/hardware_report.txt"
        return 0
    else
        error_log "Installation failed."
        echo "INSTALL_STATUS=FAILED" >> "$HOME/hardware_report.txt"
        return 1
    fi
}

# Start miner
start_miner() {
    log "Starting miner..."
    
    # Find miner binary
    MINER_BIN=$(find "$INSTALL_DIR" -name "sophia-miner" -o -name "miner" -type f 2>/dev/null | head -1)
    
    if [ -z "$MINER_BIN" ]; then
        error_log "Miner binary not found."
        return 1
    fi
    
    chmod +x "$MINER_BIN"
    
    # Start miner in background
    log "Starting miner with wallet: $WALLET"
    $MINER_BIN --wallet "$WALLET" --daemon &
    MINER_PID=$!
    
    log "Miner started with PID: $MINER_PID"
    echo "MINER_PID=$MINER_PID" >> "$HOME/hardware_report.txt"
    
    return 0
}

# Monitor miner
monitor_miner() {
    local start_time=$(date +%s)
    local current_time
    local elapsed_time
    local attestation_count=0
    
    log "Monitoring miner for $MINER_DURATION seconds..."
    
    while true; do
        current_time=$(date +%s)
        elapsed_time=$((current_time - start_time))
        
        if [ $elapsed_time -ge $MINER_DURATION ]; then
            log "Monitoring period completed."
            break
        fi
        
        # Check if miner is still running
        if ! kill -0 $MINER_PID 2>/dev/null; then
            error_log "Miner process died."
            return 1
        fi
        
        # Check for attestations in logs
        if grep -q "attestation" "$LOG_FILE" 2>/dev/null; then
            attestation_count=$(grep -c "attestation" "$LOG_FILE")
            log "Attestations submitted: $attestation_count"
        fi
        
        # Display progress
        local remaining=$((MINER_DURATION - elapsed_time))
        local minutes=$((remaining / 60))
        local seconds=$((remaining % 60))
        log "Time remaining: ${minutes}m ${seconds}s"
        
        sleep 60
    done
    
    echo "ATTESTATION_COUNT=$attestation_count" >> "$HOME/hardware_report.txt"
    log "Total attestations during test: $attestation_count"
    
    return 0
}

# Stop miner
stop_miner() {
    log "Stopping miner..."
    
    if [ ! -z "$MINER_PID" ]; then
        kill $MINER_PID 2>/dev/null || true
        wait $MINER_PID 2>/dev/null || true
        log "Miner stopped."
    fi
}

# Generate report
generate_report() {
    log "Generating test report..."
    
    local report_file="$HOME/sophia-edge-node-test-report.txt"
    
    cat > "$report_file" << EOF
========================================
Sophia Edge Node Test Report
========================================
Date: $(date)
Wallet: $WALLET

Hardware Information:
$(cat "$HOME/hardware_report.txt")

Test Results:
- Installation Status: $(grep "INSTALL_STATUS" "$HOME/hardware_report.txt" | cut -d= -f2)
- Miner Runtime: ${MINER_DURATION}s
- Attestations Submitted: $(grep "ATTESTATION_COUNT" "$HOME/hardware_report.txt" | cut -d= -f2)
- Miner PID: $(grep "MINER_PID" "$HOME/hardware_report.txt" | cut -d= -f2)

Log File: $LOG_FILE
========================================
EOF
    
    log "Report generated: $report_file"
    cat "$report_file"
}

# Cleanup function
cleanup() {
    log "Cleaning up..."
    stop_miner
    log "Cleanup complete."
}

# Main execution
main() {
    log "Starting sophia-edge-node test..."
    log "Bounty: 2 RTC"
    log "Wallet: $WALLET"
    
    # Trap for cleanup
    trap cleanup EXIT INT TERM
    
    # Execute steps
    detect_hardware
    check_dependencies
    clone_repo
    
    if run_install; then
        if start_miner; then
            if monitor_miner; then
                generate_report
                log "Test completed successfully!"
                log "Please submit your report with the generated file."
            else
                error_log "Miner monitoring failed."
                generate_report
                exit 1
            fi
        else
            error_log "Failed to start miner."
            generate_report
            exit 1
        fi
    else
        error_log "Installation failed."
        generate_report
        exit 1
    fi
}

# Run main function
main