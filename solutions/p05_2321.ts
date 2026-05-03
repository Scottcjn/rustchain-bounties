#!/bin/bash

# sophia-edge-node installation and verification script
# For ARM Linux devices (RPi 4, RPi 5, or other SBC)

set -e

echo "=== Sophia Edge Node Installation & Verification ==="
echo "Hardware Detection:"
echo "Model: $(cat /proc/device-tree/model 2>/dev/null || uname -m)"
echo "RAM: $(free -h | awk '/^Mem:/ {print $2}')"
echo "OS: $(lsb_release -ds 2>/dev/null || cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d= -f2 | tr -d '\"')"
echo "Kernel: $(uname -r)"
echo ""

# Step 1: Clone repository
echo "=== Cloning sophia-edge-node ==="
if [ -d "sophia-edge-node" ]; then
    echo "Directory exists, updating..."
    cd sophia-edge-node
    git pull
else
    git clone https://github.com/Scottcjn/sophia-edge-node
    cd sophia-edge-node
fi

# Step 2: Run install script
echo "=== Running install.sh ==="
if sudo ./install.sh; then
    echo "install.sh completed successfully"
    INSTALL_STATUS="SUCCESS"
else
    echo "install.sh failed with exit code $?"
    INSTALL_STATUS="FAILED"
    exit 1
fi

# Step 3: Start miner and run for 1 hour
echo "=== Starting miner ==="
# Assuming miner binary is named 'sophia-miner' after installation
MINER_BIN="./sophia-miner"
if [ ! -f "$MINER_BIN" ]; then
    # Try to find it
    MINER_BIN=$(find /usr/local/bin /opt -name "sophia-miner" 2>/dev/null | head -1)
fi

if [ -z "$MINER_BIN" ]; then
    echo "Miner binary not found. Checking installed files..."
    ls -la
    echo "Please check the installation directory"
    exit 1
fi

echo "Starting miner: $MINER_BIN"
# Run miner in background with timeout of 1 hour
timeout 3600 $MINER_BIN &
MINER_PID=$!
echo "Miner PID: $MINER_PID"

# Wait for miner to initialize
sleep 10

# Check if miner is running
if kill -0 $MINER_PID 2>/dev/null; then
    echo "Miner is running successfully"
    MINER_STATUS="RUNNING"
else
    echo "Miner failed to start"
    MINER_STATUS="FAILED"
    exit 1
fi

# Monitor miner for 1 hour
echo "Monitoring miner for 1 hour..."
for i in {1..60}; do
    sleep 60
    if ! kill -0 $MINER_PID 2>/dev/null; then
        echo "Miner stopped unexpectedly at minute $i"
        MINER_STATUS="STOPPED"
        break
    fi
    echo "Miner running for $i minutes..."
done

# Check if miner completed full hour
if kill -0 $MINER_PID 2>/dev/null; then
    echo "Miner ran for full hour"
    MINER_STATUS="COMPLETED"
    kill $MINER_PID 2>/dev/null || true
fi

# Step 4: Check logs for attestation
echo "=== Checking miner logs ==="
LOG_FILE="miner.log"
if [ -f "$LOG_FILE" ]; then
    if grep -q "attestation" "$LOG_FILE"; then
        echo "Attestation found in logs"
        ATTESTATION_STATUS="SUCCESS"
        grep "attestation" "$LOG_FILE" | tail -5
    else
        echo "No attestation found in logs"
        ATTESTATION_STATUS="NOT_FOUND"
    fi
else
    echo "No log file found"
    ATTESTATION_STATUS="UNKNOWN"
fi

# Step 5: Generate report
echo ""
echo "=========================================="
echo "         VERIFICATION REPORT              "
echo "=========================================="
echo "Hardware: $(cat /proc/device-tree/model 2>/dev/null || echo "Unknown ARM device")"
echo "RAM: $(free -h | awk '/^Mem:/ {print $2}')"
echo "OS: $(lsb_release -ds 2>/dev/null || cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d= -f2 | tr -d '\"')"
echo "Install Status: $INSTALL_STATUS"
echo "Miner Status: $MINER_STATUS"
echo "Attestation Status: $ATTESTATION_STATUS"
echo ""
echo "Wallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu"
echo "=========================================="

# Save report to file
cat > verification_report.txt << EOF
Sophia Edge Node Verification Report
====================================
Date: $(date)
Hardware: $(cat /proc/device-tree/model 2>/dev/null || echo "Unknown ARM device")
RAM: $(free -h | awk '/^Mem:/ {print $2}')
OS: $(lsb_release -ds 2>/dev/null || cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d= -f2 | tr -d '\"')
Kernel: $(uname -r)

Install Status: $INSTALL_STATUS
Miner Status: $MINER_STATUS
Attestation Status: $ATTESTATION_STATUS

Wallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu
EOF

echo "Report saved to verification_report.txt"