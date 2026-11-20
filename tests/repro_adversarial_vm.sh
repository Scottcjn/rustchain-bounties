#!/bin/bash
# Script to reproduce VM detection for RIP-PoA validation
# Target: clawrtc miner

echo "Setting up adversarial QEMU environment..."

# Check if QEMU is installed
if ! command -v qemu-system-x86_64 &> /dev/null; then
    echo "QEMU not found. Please install it to run this test."
    exit 1
fi

echo "Running miner with hypervisor masking..."

# We simulate the execution environment that triggers the detection
# In a real scenario, the user would run the binary inside the VM.
# This script logs the expected adversarial flags for documentation.

qemu-system-x86_64 \
    -m 2G \
    -cpu host,kvm=off,hv_relaxed,hv_spinlocks=0x1fff,hv_vapic,hv_time \
    -display none \
    -append "console=ttyS0" \
    -kernel ./vmlinuz \
    -initrd ./initrd.img \
    -drive file=./clawrtc_disk.img,format=raw | grep -E "Anti-Emulation|vm_indicators|weight"

echo "Test complete. Check output for 0.000000001x weight adjustment."
