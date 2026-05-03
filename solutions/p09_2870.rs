#!/usr/bin/env bash
# RustChain Miner Installer & Runner
# Wallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu

set -euo pipefail

# Configuration
WALLET="TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu"
MINER_DIR="$HOME/.rustchain"
MINER_LOG="$MINER_DIR/miner.log"
MINER_BIN="$MINER_DIR/rustchain-miner"
INSTALL_URL="https://rustchain.org/install.sh"

# Colors for output
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

# Check dependencies
check_dependencies() {
    local deps=("curl" "bash" "cat" "grep" "tail")
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            log_error "Missing dependency: $dep"
            exit 1
        fi
    done
}

# Install miner
install_miner() {
    log_info "Installing RustChain miner..."
    if curl -fsSL "$INSTALL_URL" | bash -s -- --wallet "$WALLET"; then
        log_info "Installation completed successfully"
    else
        log_error "Installation failed"
        exit 1
    fi
}

# Start mining
start_mining() {
    log_info "Starting RustChain miner..."
    if [ -f "$MINER_BIN" ]; then
        nohup "$MINER_BIN" --wallet "$WALLET" >> "$MINER_LOG" 2>&1 &
        MINER_PID=$!
        echo $MINER_PID > "$MINER_DIR/miner.pid"
        log_info "Miner started with PID: $MINER_PID"
    else
        log_error "Miner binary not found at $MINER_BIN"
        exit 1
    fi
}

# Check mining status
check_status() {
    if [ -f "$MINER_DIR/miner.pid" ]; then
        local pid=$(cat "$MINER_DIR/miner.pid")
        if kill -0 "$pid" 2>/dev/null; then
            log_info "Miner is running (PID: $pid)"
            return 0
        else
            log_warn "Miner is not running"
            return 1
        fi
    else
        log_warn "No miner PID file found"
        return 1
    fi
}

# Stop mining
stop_mining() {
    if [ -f "$MINER_DIR/miner.pid" ]; then
        local pid=$(cat "$MINER_DIR/miner.pid")
        kill "$pid" 2>/dev/null || true
        rm -f "$MINER_DIR/miner.pid"
        log_info "Miner stopped"
    fi
}

# Generate hardware report
generate_report() {
    log_info "Generating hardware report..."
    echo "=========================================="
    echo "RustChain Miner Hardware Report"
    echo "Wallet: $WALLET"
    echo "Timestamp: $(date)"
    echo "=========================================="
    echo ""
    
    # System information
    echo "--- System Information ---"
    uname -a
    echo ""
    
    # CPU information
    echo "--- CPU Information ---"
    if command -v lscpu &> /dev/null; then
        lscpu | grep "Model name\|CPU(s)\|Thread(s) per core\|Core(s) per socket\|Socket(s)"
    elif [ -f /proc/cpuinfo ]; then
        grep "model name\|processor\|cpu cores" /proc/cpuinfo | sort -u
    fi
    echo ""
    
    # Memory information
    echo "--- Memory Information ---"
    if command -v free &> /dev/null; then
        free -h
    elif [ -f /proc/meminfo ]; then
        grep "MemTotal\|MemFree\|MemAvailable" /proc/meminfo
    fi
    echo ""
    
    # Disk information
    echo "--- Disk Information ---"
    if command -v df &> /dev/null; then
        df -h "$MINER_DIR" | tail -1
    fi
    echo ""
    
    # Network information
    echo "--- Network Information ---"
    if command -v ip &> /dev/null; then
        ip addr show | grep "inet " | grep -v "127.0.0.1"
    elif command -v ifconfig &> /dev/null; then
        ifconfig | grep "inet " | grep -v "127.0.0.1"
    fi
    echo ""
    
    # Miner log analysis
    echo "--- Miner Log Analysis ---"
    if [ -f "$MINER_LOG" ]; then
        echo "Log file size: $(du -h "$MINER_LOG" | cut -f1)"
        echo ""
        echo "Recent device/attestation/fingerprint entries:"
        grep -i "device\|attestation\|fingerprint" "$MINER_LOG" | tail -20
        echo ""
        echo "Mining statistics:"
        grep -c "mined" "$MINER_LOG" 2>/dev/null && echo "blocks mined" || echo "No blocks mined yet"
        grep -c "hash" "$MINER_LOG" 2>/dev/null && echo "hash calculations" || echo "No hash calculations"
    else
        echo "No miner log found at $MINER_LOG"
    fi
    echo ""
    echo "=========================================="
}

# Main execution
main() {
    echo "=========================================="
    echo "RustChain Miner - 24 Hour Mining Script"
    echo "Wallet: $WALLET"
    echo "=========================================="
    echo ""
    
    check_dependencies
    
    # Check if miner is already installed
    if [ ! -f "$MINER_BIN" ]; then
        install_miner
    else
        log_info "Miner already installed"
    fi
    
    # Create log directory if needed
    mkdir -p "$MINER_DIR"
    
    # Start mining if not already running
    if ! check_status; then
        start_mining
    fi
    
    # Display initial status
    echo ""
    log_info "Miner is running. Let it run for 24 hours."
    log_info "To check status, run: $0 --status"
    log_info "To generate report, run: $0 --report"
    log_info "To stop miner, run: $0 --stop"
    echo ""
    
    # If --report flag, generate and display report
    if [ "${1:-}" = "--report" ]; then
        generate_report
    fi
    
    # If --status flag, just show status
    if [ "${1:-}" = "--status" ]; then
        check_status
    fi
    
    # If --stop flag, stop miner
    if [ "${1:-}" = "--stop" ]; then
        stop_mining
    fi
    
    # If --install flag, force reinstall
    if [ "${1:-}" = "--install" ]; then
        install_miner
    fi
}

# Run main with arguments
main "$@"