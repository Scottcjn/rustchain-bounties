#!/usr/bin/env bash
# RustChain Miner - Hardware Report Generator
# Wallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu

set -euo pipefail

# Configuration
MINER_DIR="${HOME}/.rustchain"
MINER_LOG="${MINER_DIR}/miner.log"
WALLET="TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu"
MINER_BIN="${MINER_DIR}/rustchain-miner"
INSTALL_URL="https://rustchain.org/install.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to check if miner is running
is_miner_running() {
    pgrep -f "rustchain-miner" > /dev/null 2>&1
}

# Function to get miner uptime
get_uptime() {
    if is_miner_running; then
        local pid=$(pgrep -f "rustchain-miner" | head -1)
        if [ -n "$pid" ] && [ -f "/proc/${pid}/stat" ]; then
            local start_time=$(awk '{print $22}' "/proc/${pid}/stat")
            local uptime_seconds=$(awk '{print int($1)}' /proc/uptime)
            local uptime=$((uptime_seconds - start_time / 100))
            echo $uptime
        else
            echo 0
        fi
    else
        echo 0
    fi
}

# Function to format uptime
format_uptime() {
    local seconds=$1
    local hours=$((seconds / 3600))
    local minutes=$(( (seconds % 3600) / 60 ))
    local secs=$((seconds % 60))
    printf "%02d:%02d:%02d" $hours $minutes $secs
}

# Function to check installation
check_installation() {
    if [ ! -f "$MINER_BIN" ]; then
        print_warn "Miner not found. Installing..."
        install_miner
    fi
    
    if [ ! -f "$MINER_LOG" ]; then
        print_warn "Log file not found. Creating..."
        mkdir -p "$MINER_DIR"
        touch "$MINER_LOG"
    fi
}

# Function to install miner
install_miner() {
    print_info "Installing RustChain miner..."
    curl -fsSL "$INSTALL_URL" | bash -s -- --wallet "$WALLET"
    
    if [ $? -ne 0 ]; then
        print_error "Installation failed"
        exit 1
    fi
    
    print_info "Installation completed successfully"
}

# Function to start miner
start_miner() {
    if is_miner_running; then
        print_warn "Miner is already running"
        return
    fi
    
    print_info "Starting RustChain miner..."
    nohup "$MINER_BIN" --wallet "$WALLET" >> "$MINER_LOG" 2>&1 &
    MINER_PID=$!
    
    sleep 2
    
    if is_miner_running; then
        print_info "Miner started successfully (PID: $MINER_PID)"
    else
        print_error "Failed to start miner"
        exit 1
    fi
}

# Function to stop miner
stop_miner() {
    if is_miner_running; then
        print_info "Stopping miner..."
        pkill -f "rustchain-miner" || true
        sleep 2
        if is_miner_running; then
            print_warn "Force stopping miner..."
            pkill -9 -f "rustchain-miner" || true
        fi
        print_info "Miner stopped"
    else
        print_warn "Miner is not running"
    fi
}

# Function to generate hardware report
generate_report() {
    print_info "Generating hardware report..."
    
    echo "========================================="
    echo "  RustChain Miner Hardware Report"
    echo "  Wallet: $WALLET"
    echo "========================================="
    echo ""
    
    # System Information
    echo "--- System Information ---"
    echo "Hostname: $(hostname)"
    echo "OS: $(uname -s -r -m)"
    echo "Kernel: $(uname -r)"
    echo ""
    
    # CPU Information
    echo "--- CPU Information ---"
    if command -v lscpu &> /dev/null; then
        lscpu | grep -E "Model name|CPU\(s\)|Thread|Core|Socket|MHz|Cache" | head -10
    elif [ -f /proc/cpuinfo ]; then
        grep -E "model name|cpu cores|siblings|cache size" /proc/cpuinfo | sort -u | head -10
    fi
    echo ""
    
    # Memory Information
    echo "--- Memory Information ---"
    if command -v free &> /dev/null; then
        free -h | head -3
    elif [ -f /proc/meminfo ]; then
        grep -E "MemTotal|MemFree|MemAvailable|SwapTotal|SwapFree" /proc/meminfo
    fi
    echo ""
    
    # Disk Information
    echo "--- Disk Information ---"
    if command -v df &> /dev/null; then
        df -h / | tail -1
    fi
    echo ""
    
    # Network Information
    echo "--- Network Information ---"
    if command -v ip &> /dev/null; then
        ip addr show | grep -E "inet |inet6" | head -5
    elif command -v ifconfig &> /dev/null; then
        ifconfig | grep -E "inet |inet6" | head -5
    fi
    echo ""
    
    # Miner Status
    echo "--- Miner Status ---"
    if is_miner_running; then
        local uptime_seconds=$(get_uptime)
        echo "Status: RUNNING"
        echo "Uptime: $(format_uptime $uptime_seconds)"
        echo "PID: $(pgrep -f "rustchain-miner" | head -1)"
    else
        echo "Status: STOPPED"
    fi
    echo ""
    
    # Recent Log Entries
    echo "--- Recent Miner Logs ---"
    if [ -f "$MINER_LOG" ]; then
        grep -E "device|attestation|fingerprint" "$MINER_LOG" | tail -20
    else
        echo "No log file found"
    fi
    echo ""
    
    # Hardware Fingerprint
    echo "--- Hardware Fingerprint ---"
    local fingerprint=$(cat /etc/machine-id 2>/dev/null || cat /var/lib/dbus/machine-id 2>/dev/null || echo "N/A")
    echo "Machine ID: $fingerprint"
    echo "CPU Fingerprint: $(grep -m1 "model name" /proc/cpuinfo 2>/dev/null | cut -d: -f2 | xargs)"
    echo "MAC Address: $(ip link show 2>/dev/null | grep -E "link/ether" | head -1 | awk '{print $2}' || echo "N/A")"
    echo ""
    
    echo "========================================="
    echo "  Report Generated: $(date)"
    echo "========================================="
}

# Function to run 24-hour mining session
run_24h_session() {
    print_info "Starting 24-hour mining session..."
    
    # Check and install if needed
    check_installation
    
    # Start miner
    start_miner
    
    # Monitor for 24 hours
    local target_seconds=$((24 * 3600))
    local start_time=$(date +%s)
    
    while true; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        local remaining=$((target_seconds - elapsed))
        
        if [ $remaining -le 0 ]; then
            print_info "24-hour mining session completed!"
            break
        fi
        
        local hours=$((remaining / 3600))
        local minutes=$(( (remaining % 3600) / 60 ))
        local seconds=$((remaining % 60))
        
        echo -ne "\r${GREEN}[MINING]${NC} Time remaining: ${hours}h ${minutes}m ${seconds}s"
        
        # Check if miner is still running
        if ! is_miner_running; then
            print_warn "Miner stopped unexpectedly. Restarting..."
            start_miner
        fi
        
        sleep 10
    done
    
    echo ""
    
    # Generate final report
    generate_report
    
    # Stop miner
    stop_miner
    
    print_info "Session complete! Share your report from: ~/.rustchain/miner.log"
}

# Main execution
main() {
    case "${1:-}" in
        start)
            check_installation
            start_miner
            ;;
        stop)
            stop_miner
            ;;
        status)
            if is_miner_running; then
                local uptime_seconds=$(get_uptime)
                print_info "Miner is running (Uptime: $(format_uptime $uptime_seconds))"
            else
                print_info "Miner is not running"
            fi
            ;;
        report)
            generate_report
            ;;
        run)
            run_24h_session
            ;;
        install)
            install_miner
            ;;
        *)
            echo "Usage: $0 {start|stop|status|report|run|install}"
            echo ""
            echo "Commands:"
            echo "  start    - Start the miner"
            echo "  stop     - Stop the miner"
            echo "  status   - Check miner status"
            echo "  report   - Generate hardware report"
            echo "  run      - Run 24-hour mining session"
            echo "  install  - Install/update miner"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"