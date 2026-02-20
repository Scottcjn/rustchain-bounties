#!/bin/bash
# SPDX-License-Identifier: MIT
# SHA256 Checksum Generator for RustChain Bounty Artifacts

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_FILE="${1:-$SCRIPT_DIR/checksums.sha256}"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

echo "Generating SHA256 checksums..."
echo "Output: $OUTPUT_FILE"
echo ""

# Change to repo root
cd "$REPO_ROOT"

# Generate checksums for important files
{
    # Scripts
    find scripts -type f -name "*.py" 2>/dev/null | sort
    
    # Tests
    find tests -type f -name "*.py" 2>/dev/null | sort
    
    # Config files
    find . -maxdepth 2 -type f \( -name "*.yml" -o -name "*.yaml" -o -name "*.json" \) 2>/dev/null | grep -v node_modules | grep -v ".git" | sort
    
    # Requirements
    ls requirements*.txt pyproject.toml 2>/dev/null || true
} | while read -r file; do
    if [ -f "$file" ]; then
        # Use sha256sum (Linux) or shasum (macOS)
        if command -v sha256sum &> /dev/null; then
            sha256sum "$file"
        else
            shasum -a 256 "$file"
        fi
    fi
done > "$OUTPUT_FILE"

echo "Generated $(wc -l < "$OUTPUT_FILE") checksums"
echo ""
echo "Checksums written to: $OUTPUT_FILE"
echo ""
echo "To verify:"
echo "  ./reproducible/verify.sh"
echo ""
echo "Or manually:"
echo "  shasum -a 256 -c $OUTPUT_FILE"
