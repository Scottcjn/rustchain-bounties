#!/bin/bash
# SPDX-License-Identifier: MIT
# SHA256 Checksum Verifier
# Verifies integrity of RustChain Bounty artifacts

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
CHECKSUM_FILE="$SCRIPT_DIR/checksums.sha256"

echo "RustChain Artifact Verification"
echo "==============================="
echo ""

# Check if checksum file exists
if [ ! -f "$CHECKSUM_FILE" ]; then
    echo "ERROR: Checksum file not found: $CHECKSUM_FILE"
    echo "Run checksum.sh first to generate checksums"
    exit 1
fi

# Change to repo root
cd "$REPO_ROOT"

# Verify checksums
echo "Verifying checksums..."
echo ""

# Use sha256sum (Linux) or shasum (macOS)
if command -v sha256sum &> /dev/null; then
    CHECK_CMD="sha256sum --check"
else
    CHECK_CMD="shasum -a 256 --check"
fi

if $CHECK_CMD --status "$CHECKSUM_FILE" 2>/dev/null; then
    echo "✓ All checksums verified successfully!"
    echo ""
    echo "Summary:"
    echo "  File: $CHECKSUM_FILE"
    echo "  Status: VERIFIED"
    exit 0
else
    echo "✗ CHECKSUM MISMATCH DETECTED!"
    echo ""
    echo "The following files failed verification:"
    $CHECK_CMD "$CHECKSUM_FILE" 2>&1 | grep -v "OK$" || true
    echo ""
    echo "This may indicate:"
    echo "  - File tampering"
    echo "  - Missing files"
    echo "  - Repository modifications"
    exit 1
fi
