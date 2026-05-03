#!/bin/bash

# sophia-edge-node installation and test script for ARM Linux devices
# This script automates the installation, mining, and reporting process

set -e

# Configuration
REPO_URL="https://github.com/Scottcjn/sophia-edge-node"
INSTALL_DIR="$HOME/sophia-edge-node"
REPORT_FILE="$HOME/sophia-edge-report.txt"
MINER_DURATION=3600  # 1 hour in seconds
WALLET="TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    log_error "Please run as root (use sudo)"
    exit 1
fi

# Detect hardware
detect_hardware() {
    log_info "Detecting hardware..."
    
    # Get model
    if [ -f /proc/device-tree/model ]; then
        MODEL=$(tr -d '\0' < /proc/device-tree/model)
    else
        MODEL=$(uname -m)
    fi
    
    # Get RAM
    TOTAL_RAM=$(free -m | awk '/^Mem:/{print $2}')
    
    # Get OS version
    if [ -f /etc/os-release ]; then
        OS_VERSION=$(grep -w "PRETTY_NAME" /etc/os-release | cut -d= -f2 | tr -d '"')
    else
        OS_VERSION=$(uname -a)
    fi
    
    # Get CPU info
    CPU_INFO=$(cat /proc/cpuinfo | grep "model name" | head -1 | cut -d: -f2 | xargs)
    if [ -z "$CPU_INFO" ]; then
        CPU_INFO=$(uname -m)
    fi
    
    echo "Hardware: $MODEL"
    echo "RAM: ${TOTAL_RAM}MB"
    echo "OS: $OS_VERSION"
    echo "CPU: $CPU_INFO"
}

# Install dependencies
install_dependencies() {
    log_info "Installing dependencies..."
    
    apt-get update
    apt-get install -y git curl wget build-essential python3 python3-pip jq
    
    # Install Node.js if not present
    if ! command -v node &> /dev/null; then
        log_info "Installing Node.js..."
        curl -fsSL https://deb.nodesource.com/setup_18.x | bash -
        apt-get install -y nodejs
    fi
    
    # Install npm packages
    npm install -g pm2 yarn
}

# Clone and install sophia-edge-node
install_sophia_edge() {
    log_info "Cloning sophia-edge-node repository..."
    
    if [ -d "$INSTALL_DIR" ]; then
        log_warn "Directory $INSTALL_DIR already exists. Removing..."
        rm -rf "$INSTALL_DIR"
    fi
    
    git clone "$REPO_URL" "$INSTALL_DIR"
    cd "$INSTALL_DIR"
    
    log_info "Running install.sh..."
    if sudo ./install.sh; then
        INSTALL_STATUS="SUCCESS"
        log_info "Installation completed successfully"
    else
        INSTALL_STATUS="FAILED"
        log_error "Installation failed"
        return 1
    fi
}

# Configure wallet
configure_wallet() {
    log_info "Configuring wallet..."
    
    # Check if config file exists
    CONFIG_FILE="$INSTALL_DIR/config.json"
    if [ -f "$CONFIG_FILE" ]; then
        # Update wallet address
        jq --arg wallet "$WALLET" '.wallet = $wallet' "$CONFIG_FILE" > "${CONFIG_FILE}.tmp" && mv "${CONFIG_FILE}.tmp" "$CONFIG_FILE"
        log_info "Wallet configured: $WALLET"
    else
        log_warn "Config file not found, creating default config"
        echo "{\"wallet\": \"$WALLET\"}" > "$CONFIG_FILE"
    fi
}

# Run miner
run_miner() {
    log_info "Starting miner for $MINER_DURATION seconds..."
    
    cd "$INSTALL_DIR"
    
    # Start miner in background
    if command -v pm2 &> /dev/null; then
        pm2 start miner.js --name sophia-miner
        MINER_PID=$(pm2 pid sophia-miner)
    else
        node miner.js &
        MINER_PID=$!
    fi
    
    log_info "Miner started with PID: $MINER_PID"
    
    # Monitor miner for specified duration
    START_TIME=$(date +%s)
    CONNECTION_STATUS="NOT_CONNECTED"
    ATTESTATION_STATUS="NO_ATTESTATION"
    
    while [ $(($(date +%s) - START_TIME)) -lt $MINER_DURATION ]; do
        sleep 10
        
        # Check if miner is still running
        if ! kill -0 $MINER_PID 2>/dev/null; then
            log_error "Miner process died"
            break
        fi
        
        # Check connection status
        if grep -q "connected" "$INSTALL_DIR/logs/miner.log" 2>/dev/null; then
            CONNECTION_STATUS="CONNECTED"
        fi
        
        # Check for attestation
        if grep -q "attestation" "$INSTALL_DIR/logs/miner.log" 2>/dev/null; then
            ATTESTATION_STATUS="ATTESTATION_SUBMITTED"
        fi
        
        # Progress indicator
        ELAPSED=$(( $(date +%s) - START_TIME ))
        REMAINING=$(( MINER_DURATION - ELAPSED ))
        log_info "Running... ${ELAPSED}s elapsed, ${REMAINING}s remaining"
    done
    
    # Stop miner
    log_info "Stopping miner..."
    if command -v pm2 &> /dev/null; then
        pm2 stop sophia-miner
        pm2 delete sophia-miner
    else
        kill $MINER_PID 2>/dev/null || true
    fi
    
    echo "Connection Status: $CONNECTION_STATUS"
    echo "Attestation Status: $ATTESTATION_STATUS"
}

# Generate report
generate_report() {
    log_info "Generating report..."
    
    {
        echo "========================================="
        echo "  sophia-edge-node Installation Report"
        echo "========================================="
        echo ""
        echo "Report Generated: $(date)"
        echo ""
        echo "--- Hardware Information ---"
        echo "Device Model: $MODEL"
        echo "Total RAM: ${TOTAL_RAM}MB"
        echo "OS Version: $OS_VERSION"
        echo "CPU: $CPU_INFO"
        echo ""
        echo "--- Installation Status ---"
        echo "Install Script: $INSTALL_STATUS"
        echo ""
        echo "--- Mining Results ---"
        echo "Mining Duration: ${MINER_DURATION}s"
        echo "Connection Status: $CONNECTION_STATUS"
        echo "Attestation Status: $ATTESTATION_STATUS"
        echo ""
        echo "--- Wallet ---"
        echo "Wallet Address: $WALLET"
        echo ""
        echo "--- Logs ---"
        if [ -f "$INSTALL_DIR/logs/miner.log" ]; then
            echo "Last 20 lines of miner.log:"
            tail -20 "$INSTALL_DIR/logs/miner.log"
        else
            echo "No miner.log found"
        fi
        echo ""
        echo "========================================="
        echo "  Report End"
        echo "========================================="
    } > "$REPORT_FILE"
    
    log_info "Report saved to: $REPORT_FILE"
    cat "$REPORT_FILE"
}

# Main execution
main() {
    echo "========================================="
    echo "  sophia-edge-node Installation & Test"
    echo "========================================="
    echo ""
    
    # Step 1: Detect hardware
    detect_hardware
    
    # Step 2: Install dependencies
    install_dependencies
    
    # Step 3: Install sophia-edge-node
    install_sophia_edge
    
    # Step 4: Configure wallet
    configure_wallet
    
    # Step 5: Run miner
    run_miner
    
    # Step 6: Generate report
    generate_report
    
    echo ""
    log_info "Installation and testing complete!"
    log_info "Report saved to: $REPORT_FILE"
}

# Run main function
main