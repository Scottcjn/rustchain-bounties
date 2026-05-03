#!/usr/bin/env bash
# RustChain Miner - 24h Hardware Report Generator
# Wallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu

set -euo pipefail

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
WALLET="TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu"
MINER_DIR="$HOME/.rustchain"
MINER_LOG="$MINER_DIR/miner.log"
MINER_BIN="$MINER_DIR/rustchain-miner"
MINER_PID_FILE="$MINER_DIR/miner.pid"
REPORT_FILE="$MINER_DIR/hardware_report_$(date +%Y%m%d_%H%M%S).txt"
TARGET_RUNTIME_HOURS=24
CHECK_INTERVAL=60 # seconds

# Ensure miner directory exists
mkdir -p "$MINER_DIR"

# Function to print colored messages
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Function to check if miner is running
is_miner_running() {
    if [ -f "$MINER_PID_FILE" ]; then
        local pid=$(cat "$MINER_PID_FILE")
        if kill -0 "$pid" 2>/dev/null; then
            return 0
        fi
    fi
    return 1
}

# Function to start miner
start_miner() {
    print_info "Starting RustChain miner with wallet: $WALLET"
    
    # Check if miner binary exists
    if [ ! -f "$MINER_BIN" ]; then
        print_error "Miner binary not found at $MINER_BIN"
        print_info "Installing miner..."
        curl -fsSL https://rustchain.org/install.sh | bash -s -- --wallet "$WALLET"
    fi
    
    # Start miner in background
    nohup "$MINER_BIN" --wallet "$WALLET" --log-file "$MINER_LOG" > /dev/null 2>&1 &
    local pid=$!
    echo $pid > "$MINER_PID_FILE"
    
    print_success "Miner started with PID: $pid"
    print_info "Log file: $MINER_LOG"
}

# Function to stop miner
stop_miner() {
    if is_miner_running; then
        local pid=$(cat "$MINER_PID_FILE")
        print_info "Stopping miner (PID: $pid)..."
        kill "$pid" 2>/dev/null || true
        rm -f "$MINER_PID_FILE"
        print_success "Miner stopped"
    else
        print_warning "Miner is not running"
    fi
}

# Function to get runtime in seconds
get_runtime_seconds() {
    if [ -f "$MINER_LOG" ]; then
        local start_time=$(head -1 "$MINER_LOG" | grep -oP '\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}' || echo "")
        if [ -n "$start_time" ]; then
            local start_epoch=$(date -d "$start_time" +%s 2>/dev/null || echo "")
            if [ -n "$start_epoch" ]; then
                local now_epoch=$(date +%s)
                echo $((now_epoch - start_epoch))
                return
            fi
        fi
    fi
    echo 0
}

# Function to format runtime
format_runtime() {
    local seconds=$1
    local hours=$((seconds / 3600))
    local minutes=$(( (seconds % 3600) / 60 ))
    local secs=$((seconds % 60))
    printf "%02d:%02d:%02d" $hours $minutes $secs
}

# Function to generate hardware report
generate_report() {
    print_info "Generating hardware report..."
    
    # Create report header
    cat > "$REPORT_FILE" << EOF
========================================
 RustChain Miner Hardware Report
 Generated: $(date)
 Wallet: $WALLET
========================================

EOF
    
    # System Information
    echo "=== SYSTEM INFORMATION ===" >> "$REPORT_FILE"
    echo "Hostname: $(hostname)" >> "$REPORT_FILE"
    echo "Kernel: $(uname -r)" >> "$REPORT_FILE"
    echo "OS: $(uname -s)" >> "$REPORT_FILE"
    echo "Architecture: $(uname -m)" >> "$REPORT_FILE"
    echo "" >> "$REPORT_FILE"
    
    # CPU Information
    echo "=== CPU INFORMATION ===" >> "$REPORT_FILE"
    if command -v lscpu &> /dev/null; then
        lscpu >> "$REPORT_FILE"
    elif [ -f /proc/cpuinfo ]; then
        grep -E "model name|cpu cores|siblings|cache size" /proc/cpuinfo | sort -u >> "$REPORT_FILE"
    fi
    echo "" >> "$REPORT_FILE"
    
    # Memory Information
    echo "=== MEMORY INFORMATION ===" >> "$REPORT_FILE"
    if command -v free &> /dev/null; then
        free -h >> "$REPORT_FILE"
    elif [ -f /proc/meminfo ]; then
        grep -E "MemTotal|MemFree|MemAvailable|SwapTotal|SwapFree" /proc/meminfo >> "$REPORT_FILE"
    fi
    echo "" >> "$REPORT_FILE"
    
    # Disk Information
    echo "=== DISK INFORMATION ===" >> "$REPORT_FILE"
    if command -v df &> /dev/null; then
        df -h / >> "$REPORT_FILE"
    fi
    echo "" >> "$REPORT_FILE"
    
    # Network Information
    echo "=== NETWORK INFORMATION ===" >> "$REPORT_FILE"
    if command -v ip &> /dev/null; then
        ip addr show | grep -E "inet |inet6 " >> "$REPORT_FILE"
    elif command -v ifconfig &> /dev/null; then
        ifconfig | grep -E "inet |inet6 " >> "$REPORT_FILE"
    fi
    echo "" >> "$REPORT_FILE"
    
    # Miner Log Analysis
    echo "=== MINER LOG ANALYSIS ===" >> "$REPORT_FILE"
    if [ -f "$MINER_LOG" ]; then
        echo "Log file size: $(du -h "$MINER_LOG" | cut -f1)" >> "$REPORT_FILE"
        echo "Total lines: $(wc -l < "$MINER_LOG")" >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        
        # Extract device, attestation, and fingerprint info
        echo "Device/Attestation/Fingerprint entries:" >> "$REPORT_FILE"
        grep -i "device\|attestation\|fingerprint" "$MINER_LOG" | tail -20 >> "$REPORT_FILE"
        echo "" >> "$REPORT_FILE"
        
        # Mining statistics
        echo "Mining statistics:" >> "$REPORT_FILE"
        echo "  Total hashes: $(grep -c "hash" "$MINER_LOG" || echo 0)" >> "$REPORT_FILE"
        echo "  Shares found: $(grep -c "share" "$MINER_LOG" || echo 0)" >> "$REPORT_FILE"
        echo "  Errors: $(grep -ci "error\|fail" "$MINER_LOG" || echo 0)" >> "$REPORT_FILE"
    else
        echo "No miner log found at $MINER_LOG" >> "$REPORT_FILE"
    fi
    echo "" >> "$REPORT_FILE"
    
    # Runtime Information
    local runtime_seconds=$(get_runtime_seconds)
    echo "=== RUNTIME INFORMATION ===" >> "$REPORT_FILE"
    echo "Total runtime: $(format_runtime $runtime_seconds)" >> "$REPORT_FILE"
    echo "Target runtime: $TARGET_RUNTIME_HOURS hours" >> "$REPORT_FILE"
    echo "Status: $([ $runtime_seconds -ge $((TARGET_RUNTIME_HOURS * 3600)) ] && echo "COMPLETED" || echo "IN PROGRESS")" >> "$REPORT_FILE"
    
    print_success "Report generated: $REPORT_FILE"
}

# Function to display miner status
show_status() {
    echo ""
    echo "========================================"
    echo " RustChain Miner Status"
    echo "========================================"
    
    if is_miner_running; then
        echo -e " Status: ${GREEN}RUNNING${NC}"
        local pid=$(cat "$MINER_PID_FILE")
        echo " PID: $pid"
        
        local runtime_seconds=$(get_runtime_seconds)
        local runtime_formatted=$(format_runtime $runtime_seconds)
        local target_seconds=$((TARGET_RUNTIME_HOURS * 3600))
        local progress=$((runtime_seconds * 100 / target_seconds))
        
        echo " Runtime: $runtime_formatted / $TARGET_RUNTIME_HOURS hours"
        echo " Progress: $progress%"
        
        # Show recent log entries
        if [ -f "$MINER_LOG" ]; then
            echo ""
            echo " Recent log entries (device/attestation/fingerprint):"
            grep -i "device\|attestation\|fingerprint" "$MINER_LOG" | tail -5
        fi
    else
        echo -e " Status: ${RED}STOPPED${NC}"
    fi
    echo "========================================"
    echo ""
}

# Function to cleanup on exit
cleanup() {
    print_info "Cleaning up..."
    stop_miner
    print_info "Goodbye!"
}

# Set trap for cleanup
trap cleanup EXIT INT TERM

# Main execution
main() {
    echo ""
    echo "========================================"
    echo " RustChain Miner - 24h Hardware Report"
    echo "========================================"
    echo " Wallet: $WALLET"
    echo " Target runtime: $TARGET_RUNTIME_HOURS hours"
    echo "========================================"
    echo ""
    
    # Start miner if not running
    if ! is_miner_running; then
        start_miner
    else
        print_info "Miner is already running"
    fi
    
    # Main monitoring loop
    local start_time=$(date +%s)
    local target_end=$((start_time + TARGET_RUNTIME_HOURS * 3600))
    
    while true; do
        local current_time=$(date +%s)
        local elapsed=$((current_time - start_time))
        local remaining=$((target_end - current_time))
        
        # Clear screen and show status
        clear
        show_status
        
        # Check if target runtime reached
        if [ $elapsed -ge $((TARGET_RUNTIME_HOURS * 3600)) ]; then
            print_success "Target runtime of $TARGET_RUNTIME_HOURS hours reached!"
            generate_report
            print_success "Hardware report generated!"
            print_info "Report file: $REPORT_FILE"
            print_info "To view the report, run: cat $REPORT_FILE"
            print_info "To share your results, run:"
            echo "  cat ~/.rustchain/miner.log | grep \"device\\|attestation\\|fingerprint\" | tail -20"
            break
        fi
        
        # Check if miner is still running
        if ! is_miner_running; then
            print_warning "Miner has stopped unexpectedly. Restarting..."
            start_miner
        fi
        
        # Sleep before next check
        sleep $CHECK_INTERVAL
    done
    
    # Keep miner running for the full 24 hours if user wants to continue
    print_info "Miner will continue running. Press Ctrl+C to stop."
    while true; do
        sleep 60
        if ! is_miner_running; then
            print_warning "Miner stopped. Exiting."
            break
        fi
    done
}

# Run main function
main