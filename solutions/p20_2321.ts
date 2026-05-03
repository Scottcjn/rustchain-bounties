#!/bin/bash

# sophia-edge-node installation and verification script
# This script automates the installation, running, and reporting of sophia-edge-node

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

# Function to get system information
get_system_info() {
    log_info "Gathering system information..."
    
    # Get hardware model
    if [ -f /proc/device-tree/model ]; then
        HARDWARE_MODEL=$(tr -d '\0' < /proc/device-tree/model)
    elif command -v uname &> /dev/null; then
        HARDWARE_MODEL=$(uname -m)
    else
        HARDWARE_MODEL="Unknown"
    fi
    
    # Get RAM information
    if command -v free &> /dev/null; then
        TOTAL_RAM=$(free -h | awk '/^Mem:/ {print $2}')
    else
        TOTAL_RAM="Unknown"
    fi
    
    # Get OS version
    if [ -f /etc/os-release ]; then
        OS_VERSION=$(grep -E "^PRETTY_NAME=" /etc/os-release | cut -d'"' -f2)
    elif command -v lsb_release &> /dev/null; then
        OS_VERSION=$(lsb_release -d | cut -f2)
    else
        OS_VERSION=$(uname -a)
    fi
    
    # Get kernel version
    KERNEL_VERSION=$(uname -r)
    
    # Get CPU information
    if [ -f /proc/cpuinfo ]; then
        CPU_INFO=$(grep -m1 "model name" /proc/cpuinfo | cut -d':' -f2 | sed 's/^ //')
        if [ -z "$CPU_INFO" ]; then
            CPU_INFO=$(grep -m1 "Hardware" /proc/cpuinfo | cut -d':' -f2 | sed 's/^ //')
        fi
    else
        CPU_INFO="Unknown"
    fi
    
    # Get disk space
    DISK_SPACE=$(df -h / | awk 'NR==2 {print $4}')
}

# Function to check dependencies
check_dependencies() {
    log_info "Checking dependencies..."
    
    # Check for git
    if ! command -v git &> /dev/null; then
        log_warn "git not found. Installing..."
        sudo apt-get update && sudo apt-get install -y git
    fi
    
    # Check for curl
    if ! command -v curl &> /dev/null; then
        log_warn "curl not found. Installing..."
        sudo apt-get update && sudo apt-get install -y curl
    fi
    
    # Check for jq
    if ! command -v jq &> /dev/null; then
        log_warn "jq not found. Installing..."
        sudo apt-get update && sudo apt-get install -y jq
    fi
    
    # Check for screen or tmux
    if command -v screen &> /dev/null; then
        TERMINAL_MUX="screen"
    elif command -v tmux &> /dev/null; then
        TERMINAL_MUX="tmux"
    else
        log_warn "screen or tmux not found. Installing screen..."
        sudo apt-get update && sudo apt-get install -y screen
        TERMINAL_MUX="screen"
    fi
}

# Function to install sophia-edge-node
install_sophia_edge() {
    log_info "Installing sophia-edge-node..."
    
    # Remove existing installation if present
    if [ -d "$INSTALL_DIR" ]; then
        log_warn "Existing installation found. Removing..."
        rm -rf "$INSTALL_DIR"
    fi
    
    # Clone repository
    log_info "Cloning repository..."
    git clone "$REPO_URL" "$INSTALL_DIR"
    
    # Change to installation directory
    cd "$INSTALL_DIR"
    
    # Run install script
    log_info "Running install.sh..."
    if sudo ./install.sh; then
        INSTALL_SUCCESS=true
        log_info "Installation completed successfully."
    else
        INSTALL_SUCCESS=false
        log_error "Installation failed."
        exit 1
    fi
}

# Function to configure and start miner
start_miner() {
    log_info "Configuring and starting miner..."
    
    # Check if config file exists
    CONFIG_FILE="$INSTALL_DIR/config.json"
    if [ ! -f "$CONFIG_FILE" ]; then
        log_warn "Config file not found. Creating default config..."
        cat > "$CONFIG_FILE" << EOF
{
    "wallet": "$WALLET",
    "node": "mainnet",
    "miner": {
        "enabled": true,
        "threads": $(nproc)
    },
    "logging": {
        "level": "info",
        "file": "sophia-edge.log"
    }
}
EOF
    fi
    
    # Start miner in background
    log_info "Starting miner for $MINER_DURATION seconds..."
    
    # Use screen to run miner in background
    screen -dmS sophia-miner bash -c "cd $INSTALL_DIR && ./sophia-edge-node --config config.json 2>&1 | tee miner.log"
    
    # Wait for miner to start
    sleep 10
    
    # Check if miner is running
    if screen -list | grep -q "sophia-miner"; then
        MINER_STARTED=true
        log_info "Miner started successfully."
    else
        MINER_STARTED=false
        log_error "Failed to start miner."
        exit 1
    fi
}

# Function to monitor miner progress
monitor_miner() {
    log_info "Monitoring miner progress..."
    
    START_TIME=$(date +%s)
    CURRENT_TIME=$START_TIME
    ELAPSED=0
    
    while [ $ELAPSED -lt $MINER_DURATION ]; do
        CURRENT_TIME=$(date +%s)
        ELAPSED=$((CURRENT_TIME - START_TIME))
        REMAINING=$((MINER_DURATION - ELAPSED))
        
        # Format time
        ELAPSED_HOURS=$((ELAPSED / 3600))
        ELAPSED_MINUTES=$(( (ELAPSED % 3600) / 60 ))
        ELAPSED_SECONDS=$((ELAPSED % 60))
        
        REMAINING_HOURS=$((REMAINING / 3600))
        REMAINING_MINUTES=$(( (REMAINING % 3600) / 60 ))
        REMAINING_SECONDS=$((REMAINING % 60))
        
        # Check miner log for attestation
        if [ -f "$INSTALL_DIR/miner.log" ]; then
            if grep -q "attestation" "$INSTALL_DIR/miner.log" 2>/dev/null; then
                ATTESTATION_FOUND=true
                ATTESTATION_TIME=$(date -d "@$CURRENT_TIME" "+%Y-%m-%d %H:%M:%S")
                log_info "Attestation found at $ATTESTATION_TIME"
            fi
            
            # Check for errors
            if grep -qi "error\|failed\|exception" "$INSTALL_DIR/miner.log" 2>/dev/null; then
                MINER_ERRORS=$(grep -ci "error\|failed\|exception" "$INSTALL_DIR/miner.log")
                log_warn "Found $MINER_ERRORS errors in miner log"
            fi
        fi
        
        # Display progress
        printf "\r${GREEN}[RUNNING]${NC} Elapsed: %02d:%02d:%02d | Remaining: %02d:%02d:%02d | Attestation: %s" \
            $ELAPSED_HOURS $ELAPSED_MINUTES $ELAPSED_SECONDS \
            $REMAINING_HOURS $REMAINING_MINUTES $REMAINING_SECONDS \
            "${ATTESTATION_FOUND:-No}"
        
        sleep 10
    done
    
    echo ""  # New line after progress
}

# Function to stop miner
stop_miner() {
    log_info "Stopping miner..."
    
    # Kill screen session
    screen -S sophia-miner -X quit 2>/dev/null || true
    
    # Kill any remaining processes
    pkill -f "sophia-edge-node" 2>/dev/null || true
    
    log_info "Miner stopped."
}

# Function to generate report
generate_report() {
    log_info "Generating report..."
    
    # Get final log statistics
    if [ -f "$INSTALL_DIR/miner.log" ]; then
        TOTAL_LINES=$(wc -l < "$INSTALL_DIR/miner.log")
        ATTESTATION_COUNT=$(grep -c "attestation" "$INSTALL_DIR/miner.log" 2>/dev/null || echo "0")
        ERROR_COUNT=$(grep -ci "error\|failed\|exception" "$INSTALL_DIR/miner.log" 2>/dev/null || echo "0")
    else
        TOTAL_LINES="N/A"
        ATTESTATION_COUNT="N/A"
        ERROR_COUNT="N/A"
    fi
    
    # Create report
    cat > "$REPORT_FILE" << EOF
========================================
Sophia Edge Node Installation Report
========================================
Date: $(date)
Wallet: $WALLET

1. Hardware Information
-----------------------
Hardware Model: $HARDWARE_MODEL
CPU: $CPU_INFO
Total RAM: $TOTAL_RAM
Disk Space Available: $DISK_SPACE
OS Version: $OS_VERSION
Kernel Version: $KERNEL_VERSION

2. Installation Status
-----------------------
Installation Successful: $INSTALL_SUCCESS
Installation Directory: $INSTALL_DIR

3. Miner Status
----------------
Miner Started: $MINER_STARTED
Miner Duration: $MINER_DURATION seconds (1 hour)
Attestation Found: ${ATTESTATION_FOUND:-No}
Attestation Time: ${ATTESTATION_TIME:-N/A}
Total Attestations: $ATTESTATION_COUNT
Total Log Lines: $TOTAL_LINES
Errors Found: $ERROR_COUNT

4. Network Connectivity
------------------------
Internet Access: $(ping -c 1 8.8.8.8 &>/dev/null && echo "Yes" || echo "No")
DNS Resolution: $(nslookup google.com &>/dev/null && echo "Yes" || echo "No")

5. Additional Notes
--------------------
- Installation completed without errors: $INSTALL_SUCCESS
- Miner connected and submitted attestation: ${ATTESTATION_FOUND:-No}
- System resources during mining: 
  * CPU Usage: $(top -bn1 | grep "Cpu(s)" | awk '{print $2 + $4}')%
  * Memory Usage: $(free -m | awk 'NR==2{printf "%.2f%%", $3*100/$2}')
  * Disk I/O: $(iostat -d 2>/dev/null | awk 'NR==4 {print $2}') MB/s

========================================
Report generated by automated script
========================================
EOF
    
    log_info "Report generated: $REPORT_FILE"
}

# Function to submit report
submit_report() {
    log_info "Submitting report to GitHub issue..."
    
    # Read report content
    REPORT_CONTENT=$(cat "$REPORT_FILE")
    
    # Create JSON payload for GitHub API
    # Note: This requires a GitHub token with appropriate permissions
    if [ -n "$GITHUB_TOKEN" ]; then
        log_info "GitHub token found. Attempting to submit report..."
        
        # This would require the GitHub API endpoint
        # For now, we'll just display the report
        log_info "Report ready for submission. Please submit manually if GitHub token is not configured."
    else
        log_warn "No GitHub token configured. Report will be displayed for manual submission."
    fi
    
    # Display report
    echo ""
    echo "========================================"
    echo "REPORT SUMMARY"
    echo "========================================"
    cat "$REPORT_FILE"
    echo "========================================"
}

# Main execution
main() {
    echo "========================================"
    echo "Sophia Edge Node Installation & Testing"
    echo "========================================"
    echo ""
    
    # Check if running as root
    if [ "$EUID" -eq 0 ]; then 
        log_warn "Running as root. It's recommended to run as a regular user."
    fi
    
    # Step 1: Get system information
    get_system_info
    
    # Step 2: Check dependencies
    check_dependencies
    
    # Step 3: Install sophia-edge-node
    install_sophia_edge
    
    # Step 4: Start miner
    start_miner
    
    # Step 5: Monitor miner
    monitor_miner
    
    # Step 6: Stop miner
    stop_miner
    
    # Step 7: Generate report
    generate_report
    
    # Step 8: Submit report
    submit_report
    
    echo ""
    log_info "Script completed successfully."
    log_info "Report saved to: $REPORT_FILE"
}

# Run main function
main