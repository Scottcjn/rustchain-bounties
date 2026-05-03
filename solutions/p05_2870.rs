#!/usr/bin/env bash
# RustChain Miner - 24-hour hardware report generator
# Wallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu

set -euo pipefail

# Configuration
WALLET="TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu"
MINER_DIR="$HOME/.rustchain"
MINER_LOG="$MINER_DIR/miner.log"
MINER_BIN="$MINER_DIR/rustchain-miner"
INSTALL_URL="https://rustchain.org/install.sh"
TARGET_HOURS=24
CHECK_INTERVAL=60  # seconds between status checks

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

# Check if running as root (not recommended)
if [[ $EUID -eq 0 ]]; then
    log_warn "Running as root is not recommended. Consider using a regular user."
fi

# Create miner directory
mkdir -p "$MINER_DIR"

# Install miner if not present
install_miner() {
    if [[ ! -f "$MINER_BIN" ]]; then
        log_info "Installing RustChain miner..."
        curl -fsSL "$INSTALL_URL" | bash -s -- --wallet "$WALLET"
        if [[ $? -ne 0 ]]; then
            log_error "Installation failed. Check network or permissions."
            exit 1
        fi
        log_info "Miner installed successfully."
    else
        log_info "Miner already installed."
    fi
}

# Start mining process
start_mining() {
    log_info "Starting RustChain miner for wallet: $WALLET"
    nohup "$MINER_BIN" --wallet "$WALLET" >> "$MINER_LOG" 2>&1 &
    MINER_PID=$!
    echo $MINER_PID > "$MINER_DIR/miner.pid"
    log_info "Miner started with PID: $MINER_PID"
}

# Stop mining process
stop_mining() {
    if [[ -f "$MINER_DIR/miner.pid" ]]; then
        local pid=$(cat "$MINER_DIR/miner.pid")
        if kill -0 "$pid" 2>/dev/null; then
            kill "$pid" 2>/dev/null || true
            log_info "Miner stopped (PID: $pid)"
        fi
        rm -f "$MINER_DIR/miner.pid"
    fi
}

# Check miner status
check_miner() {
    if [[ -f "$MINER_DIR/miner.pid" ]]; then
        local pid=$(cat "$MINER_DIR/miner.pid")
        if kill -0 "$pid" 2>/dev/null; then
            return 0
        fi
    fi
    return 1
}

# Get elapsed mining time in seconds
get_elapsed_time() {
    if [[ -f "$MINER_DIR/miner.pid" ]]; then
        local pid=$(cat "$MINER_DIR/miner.pid")
        if kill -0 "$pid" 2>/dev/null; then
            local start_time=$(stat -c %Y /proc/$pid 2>/dev/null || echo $(date +%s))
            local now=$(date +%s)
            echo $((now - start_time))
            return
        fi
    fi
    echo 0
}

# Format seconds to human readable
format_time() {
    local seconds=$1
    local hours=$((seconds / 3600))
    local minutes=$(( (seconds % 3600) / 60 ))
    local secs=$((seconds % 60))
    printf "%02d:%02d:%02d" $hours $minutes $secs
}

# Generate hardware fingerprint report
generate_report() {
    log_info "Generating hardware fingerprint report..."
    
    echo "=========================================="
    echo "  RustChain Miner - Hardware Report"
    echo "  Wallet: $WALLET"
    echo "  Generated: $(date)"
    echo "=========================================="
    echo ""
    
    # CPU Information
    echo "--- CPU ---"
    if command -v lscpu &>/dev/null; then
        lscpu | grep -E "Model name|Architecture|CPU\(s\)|Thread|Core|Socket|MHz" | head -10
    elif [[ -f /proc/cpuinfo ]]; then
        grep -E "model name|cpu cores|siblings|processor|MHz" /proc/cpuinfo | head -10
    fi
    echo ""
    
    # Memory Information
    echo "--- Memory ---"
    if command -v free &>/dev/null; then
        free -h | head -3
    elif [[ -f /proc/meminfo ]]; then
        grep -E "MemTotal|MemFree|MemAvailable" /proc/meminfo
    fi
    echo ""
    
    # Disk Information
    echo "--- Disk ---"
    if command -v df &>/dev/null; then
        df -h / | tail -1
    fi
    echo ""
    
    # Network Information
    echo "--- Network ---"
    if command -v ip &>/dev/null; then
        ip addr show | grep -E "inet |inet6" | head -5
    elif command -v ifconfig &>/dev/null; then
        ifconfig | grep -E "inet |inet6" | head -5
    fi
    echo ""
    
    # OS Information
    echo "--- OS ---"
    if command -v uname &>/dev/null; then
        uname -a
    fi
    if [[ -f /etc/os-release ]]; then
        grep -E "^NAME|^VERSION" /etc/os-release
    fi
    echo ""
    
    # Miner specific logs
    echo "--- Miner Logs (last 20 lines with device/attestation/fingerprint) ---"
    if [[ -f "$MINER_LOG" ]]; then
        grep -i "device\|attestation\|fingerprint" "$MINER_LOG" | tail -20
    else
        echo "No miner log found at $MINER_LOG"
    fi
    echo ""
    
    # Mining statistics
    echo "--- Mining Statistics ---"
    local elapsed=$(get_elapsed_time)
    echo "Mining duration: $(format_time $elapsed)"
    if [[ -f "$MINER_LOG" ]]; then
        local hashes=$(grep -c "hash" "$MINER_LOG" 2>/dev/null || echo 0)
        echo "Total hashes computed: $hashes"
        if [[ $elapsed -gt 0 ]]; then
            local hash_rate=$((hashes * 1000 / elapsed))
            echo "Average hash rate: ${hash_rate} H/s"
        fi
    fi
    echo ""
    
    echo "=========================================="
    echo "  Report Complete"
    echo "=========================================="
}

# Main execution
main() {
    log_info "RustChain 24-Hour Miner - Wallet: $WALLET"
    
    # Install miner
    install_miner
    
    # Cleanup on exit
    trap stop_mining EXIT
    
    # Start mining
    start_mining
    
    # Monitor for 24 hours
    local target_seconds=$((TARGET_HOURS * 3600))
    local start_time=$(date +%s)
    
    log_info "Mining started. Target: $TARGET_HOURS hours"
    log_info "Log file: $MINER_LOG"
    
    while true; do
        local elapsed=$(get_elapsed_time)
        local remaining=$((target_seconds - elapsed))
        
        if [[ $remaining -le 0 ]]; then
            log_info "Target time reached! ($TARGET_HOURS hours)"
            break
        fi
        
        if ! check_miner; then
            log_error "Miner process died! Restarting..."
            start_mining
        fi
        
        local elapsed_formatted=$(format_time $elapsed)
        local remaining_formatted=$(format_time $remaining)
        log_info "Mining: $elapsed_formatted / $TARGET_HOURS:00:00 (Remaining: $remaining_formatted)"
        
        sleep $CHECK_INTERVAL
    done
    
    # Generate final report
    generate_report
    
    log_info "Mining complete! Share the report above."
    log_info "Reward claim: 1 RTC for first 50 participants"
}

# Run main
main "$@"