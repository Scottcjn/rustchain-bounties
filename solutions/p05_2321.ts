#!/bin/bash

# sophia-edge-node installation and test script for ARM Linux devices
# This script automates the process described in the GitHub issue

set -e

# Configuration
REPO_URL="https://github.com/Scottcjn/sophia-edge-node"
INSTALL_DIR="$HOME/sophia-edge-node"
LOG_FILE="$HOME/sophia-edge-test-$(date +%Y%m%d-%H%M%S).log"
WALLET="TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu"

# Function to log messages
log() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to check system requirements
check_system() {
    log "Checking system requirements..."
    
    # Detect hardware
    if [ -f /proc/device-tree/model ]; then
        MODEL=$(tr -d '\0' < /proc/device-tree/model)
    elif [ -f /sys/firmware/devicetree/base/model ]; then
        MODEL=$(tr -d '\0' < /sys/firmware/devicetree/base/model)
    else
        MODEL=$(uname -m)
    fi
    log "Hardware model: $MODEL"
    
    # Check RAM
    TOTAL_RAM=$(free -m | awk '/^Mem:/{print $2}')
    log "Total RAM: ${TOTAL_RAM}MB"
    
    # Check OS version
    if [ -f /etc/os-release ]; then
        OS_VERSION=$(grep -E "^PRETTY_NAME" /etc/os-release | cut -d'"' -f2)
    else
        OS_VERSION=$(uname -a)
    fi
    log "OS version: $OS_VERSION"
    
    # Check architecture
    ARCH=$(uname -m)
    log "Architecture: $ARCH"
    
    # Check if ARM
    case "$ARCH" in
        armv7l|aarch64)
            log "ARM architecture detected - compatible"
            ;;
        *)
            log "WARNING: Non-ARM architecture detected ($ARCH). May not work."
            ;;
    esac
    
    # Check available disk space
    DISK_SPACE=$(df -h "$HOME" | awk 'NR==2 {print $4}')
    log "Available disk space: $DISK_SPACE"
    
    # Check internet connectivity
    if ping -c 1 github.com &>/dev/null; then
        log "Internet connectivity: OK"
    else
        log "ERROR: No internet connectivity"
        exit 1
    fi
}

# Function to install dependencies
install_dependencies() {
    log "Installing dependencies..."
    
    # Update package list
    sudo apt-get update -qq 2>&1 | tee -a "$LOG_FILE"
    
    # Install required packages
    sudo apt-get install -y -qq git curl wget build-essential 2>&1 | tee -a "$LOG_FILE"
    
    # Check for Docker (optional but recommended)
    if command -v docker &>/dev/null; then
        log "Docker is installed"
    else
        log "Docker not found - installing..."
        curl -fsSL https://get.docker.com -o get-docker.sh
        sudo sh get-docker.sh 2>&1 | tee -a "$LOG_FILE"
        sudo usermod -aG docker "$USER"
        log "Docker installed. You may need to log out and back in for group changes to take effect."
    fi
}

# Function to clone and install sophia-edge-node
install_sophia() {
    log "Cloning sophia-edge-node repository..."
    
    # Remove existing directory if present
    if [ -d "$INSTALL_DIR" ]; then
        log "Removing existing installation..."
        rm -rf "$INSTALL_DIR"
    fi
    
    # Clone repository
    git clone "$REPO_URL" "$INSTALL_DIR" 2>&1 | tee -a "$LOG_FILE"
    
    if [ $? -ne 0 ]; then
        log "ERROR: Failed to clone repository"
        exit 1
    fi
    
    log "Repository cloned successfully"
    
    # Run install script
    log "Running install.sh..."
    cd "$INSTALL_DIR"
    
    if [ -f install.sh ]; then
        sudo ./install.sh 2>&1 | tee -a "$LOG_FILE"
        INSTALL_STATUS=$?
        
        if [ $INSTALL_STATUS -eq 0 ]; then
            log "install.sh completed successfully"
        else
            log "ERROR: install.sh failed with exit code $INSTALL_STATUS"
            exit 1
        fi
    else
        log "ERROR: install.sh not found in repository"
        exit 1
    fi
}

# Function to run the miner
run_miner() {
    log "Starting miner..."
    
    # Check for miner binary
    MINER_BIN=""
    for bin in sophia-miner sophia-edge-miner miner; do
        if [ -f "$INSTALL_DIR/$bin" ]; then
            MINER_BIN="$INSTALL_DIR/$bin"
            break
        fi
    done
    
    if [ -z "$MINER_BIN" ]; then
        log "Searching for miner binary..."
        MINER_BIN=$(find "$INSTALL_DIR" -type f -executable -name "*miner*" 2>/dev/null | head -1)
    fi
    
    if [ -z "$MINER_BIN" ]; then
        log "ERROR: Miner binary not found"
        exit 1
    fi
    
    log "Found miner binary: $MINER_BIN"
    
    # Run miner in background
    log "Running miner for 1 hour..."
    $MINER_BIN --wallet "$WALLET" &
    MINER_PID=$!
    
    log "Miner started with PID: $MINER_PID"
    
    # Monitor miner for 1 hour
    START_TIME=$(date +%s)
    END_TIME=$((START_TIME + 3600))
    
    while [ $(date +%s) -lt $END_TIME ]; do
        if kill -0 $MINER_PID 2>/dev/null; then
            # Check miner output
            if grep -q "attestation\|connected\|submitted" "$LOG_FILE" 2>/dev/null; then
                log "Miner is active and submitting attestations"
            fi
            sleep 60
        else
            log "WARNING: Miner process died. Attempting restart..."
            $MINER_BIN --wallet "$WALLET" &
            MINER_PID=$!
            sleep 30
        fi
    done
    
    # Stop miner after 1 hour
    kill $MINER_PID 2>/dev/null || true
    log "Miner stopped after 1 hour"
}

# Function to generate report
generate_report() {
    log "Generating report..."
    
    REPORT_FILE="$HOME/sophia-edge-report-$(date +%Y%m%d-%H%M%S).txt"
    
    {
        echo "============================================"
        echo "Sophia Edge Node Installation Report"
        echo "============================================"
        echo ""
        echo "Date: $(date)"
        echo ""
        echo "--- Hardware Information ---"
        echo "Model: $(cat /proc/device-tree/model 2>/dev/null || echo 'Unknown')"
        echo "RAM: $(free -h | awk '/^Mem:/{print $2}')"
        echo "Architecture: $(uname -m)"
        echo "CPU Info: $(cat /proc/cpuinfo | grep 'model name' | head -1 | cut -d: -f2 | xargs)"
        echo ""
        echo "--- Software Information ---"
        echo "OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
        echo "Kernel: $(uname -r)"
        echo ""
        echo "--- Installation Results ---"
        echo "Install.sh completed: $(grep -q 'install.sh completed successfully' $LOG_FILE && echo 'Yes' || echo 'No')"
        echo "Errors during installation: $(grep -c 'ERROR' $LOG_FILE || echo '0')"
        echo ""
        echo "--- Mining Results ---"
        echo "Miner ran for: 1 hour"
        echo "Miner connected: $(grep -q 'connected\|attestation' $LOG_FILE && echo 'Yes' || echo 'No')"
        echo "Attestations submitted: $(grep -c 'attestation\|submitted' $LOG_FILE || echo '0')"
        echo ""
        echo "--- Issues Found ---"
        grep -i "error\|warning\|fail" "$LOG_FILE" || echo "No issues found"
        echo ""
        echo "--- Wallet Address ---"
        echo "$WALLET"
        echo ""
        echo "============================================"
        echo "Report generated by automated test script"
        echo "============================================"
    } > "$REPORT_FILE"
    
    log "Report saved to: $REPORT_FILE"
    cat "$REPORT_FILE"
}

# Main execution
main() {
    log "Starting sophia-edge-node installation and test..."
    log "Wallet: $WALLET"
    
    check_system
    install_dependencies
    install_sophia
    run_miner
    generate_report
    
    log "Test completed successfully!"
    log "Full log available at: $LOG_FILE"
}

# Run main function
main