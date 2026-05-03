#!/bin/bash

# sophia-edge-node installation and test script for ARM Linux devices
# This script automates the process described in the GitHub issue

set -e

echo "=========================================="
echo "Sophia Edge Node Installation & Test Script"
echo "=========================================="

# Step 1: System Information Collection
echo "Collecting system information..."
HARDWARE_INFO=$(cat /proc/cpuinfo | grep "Model" | head -1 || echo "Unknown")
RAM_INFO=$(free -h | grep "Mem:" | awk '{print $2}')
OS_VERSION=$(cat /etc/os-release | grep "PRETTY_NAME" | cut -d'"' -f2 || echo "Unknown")

echo "Hardware: $HARDWARE_INFO"
echo "RAM: $RAM_INFO"
echo "OS: $OS_VERSION"

# Step 2: Clone and Install
echo "Cloning sophia-edge-node repository..."
if [ -d "sophia-edge-node" ]; then
    echo "Directory exists, removing..."
    rm -rf sophia-edge-node
fi

git clone https://github.com/Scottcjn/sophia-edge-node
cd sophia-edge-node

echo "Running install.sh..."
INSTALL_RESULT=""
if sudo ./install.sh; then
    INSTALL_RESULT="SUCCESS"
    echo "Installation completed successfully."
else
    INSTALL_RESULT="FAILED"
    echo "Installation failed."
    exit 1
fi

# Step 3: Run the miner for 1 hour
echo "Starting miner for 1 hour..."
MINER_LOG="/tmp/sophia_miner_$(date +%Y%m%d_%H%M%S).log"
MINER_CONNECTED=false
MINER_ATTESTATION=false

# Run miner in background
nohup ./sophia-miner --wallet TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu > "$MINER_LOG" 2>&1 &
MINER_PID=$!
echo "Miner started with PID: $MINER_PID"

# Monitor for 1 hour (3600 seconds)
END_TIME=$((SECONDS + 3600))
while [ $SECONDS -lt $END_TIME ]; do
    sleep 60
    
    # Check if miner is still running
    if ! kill -0 $MINER_PID 2>/dev/null; then
        echo "Miner process died unexpectedly"
        break
    fi
    
    # Check connection status
    if grep -q "Connected" "$MINER_LOG" 2>/dev/null; then
        MINER_CONNECTED=true
    fi
    
    # Check attestation
    if grep -q "Attestation submitted" "$MINER_LOG" 2>/dev/null; then
        MINER_ATTESTATION=true
    fi
    
    echo "Miner running... ($((SECONDS / 60)) minutes elapsed)"
done

# Stop miner
kill $MINER_PID 2>/dev/null || true
wait $MINER_PID 2>/dev/null || true

# Step 4: Generate Report
echo ""
echo "=========================================="
echo "SOPHIA EDGE NODE TEST REPORT"
echo "=========================================="
echo "Date: $(date)"
echo ""
echo "Hardware Information:"
echo "  Model: $HARDWARE_INFO"
echo "  RAM: $RAM_INFO"
echo "  OS: $OS_VERSION"
echo ""
echo "Installation:"
echo "  install.sh completed: $INSTALL_RESULT"
echo ""
echo "Miner Performance:"
echo "  Connected to network: $MINER_CONNECTED"
echo "  Attestation submitted: $MINER_ATTESTATION"
echo "  Runtime: 1 hour"
echo ""
echo "Miner Log (last 20 lines):"
tail -20 "$MINER_LOG"
echo ""
echo "=========================================="
echo "Wallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu"
echo "=========================================="

# Save report to file
REPORT_FILE="sophia_test_report_$(date +%Y%m%d_%H%M%S).txt"
cat > "$REPORT_FILE" << EOF
SOPHIA EDGE NODE TEST REPORT
============================
Date: $(date)

Hardware Information:
  Model: $HARDWARE_INFO
  RAM: $RAM_INFO
  OS: $OS_VERSION

Installation:
  install.sh completed: $INSTALL_RESULT

Miner Performance:
  Connected to network: $MINER_CONNECTED
  Attestation submitted: $MINER_ATTESTATION
  Runtime: 1 hour

Wallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu
EOF

echo "Report saved to: $REPORT_FILE"
echo "Test completed."