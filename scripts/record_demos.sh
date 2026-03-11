#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
#
# record_demos.sh — Re-record asciinema demos for RustChain miner install docs.
#
# Prerequisites:
#   - asciinema installed (https://asciinema.org/docs/installation)
#   - Python 3.8+ available
#   - Access to the RustChain node (https://50.28.86.131)
#
# Usage:
#   ./scripts/record_demos.sh              # Record both demos interactively
#   ./scripts/record_demos.sh install      # Record install demo only
#   ./scripts/record_demos.sh attestation  # Record attestation demo only
#   ./scripts/record_demos.sh --help       # Show this help
#
# The recordings are saved as asciinema v2 .cast files in assets/demos/.
# To convert to GIF, use agg (https://github.com/asciinema/agg):
#   agg assets/demos/miner-install.cast assets/demos/miner-install.gif
#   agg assets/demos/first-attestation.cast assets/demos/first-attestation.gif

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
DEMOS_DIR="$REPO_ROOT/assets/demos"

usage() {
    sed -n '/^# Usage:/,/^$/p' "$0" | sed 's/^# //'
    echo ""
    echo "Tip: Play back a recording with:  asciinema play assets/demos/miner-install.cast"
    echo "Tip: Convert to GIF with agg:     agg assets/demos/miner-install.cast miner-install.gif"
}

check_deps() {
    if ! command -v asciinema >/dev/null 2>&1; then
        echo "Error: asciinema is not installed."
        echo "Install it: https://asciinema.org/docs/installation"
        echo "  - pip install asciinema"
        echo "  - brew install asciinema"
        echo "  - apt install asciinema"
        exit 1
    fi
}

record_install() {
    local outfile="$DEMOS_DIR/miner-install.cast"
    echo "==> Recording miner install demo to $outfile"
    echo "    Follow these steps during the recording:"
    echo ""
    echo "    1. git clone https://github.com/Scottcjn/Rustchain.git"
    echo "    2. cd Rustchain"
    echo "    3. python3 --version"
    echo "    4. ls miners/"
    echo "    5. ls miners/linux/"
    echo "    6. python3 miners/linux/rustchain_linux_miner.py --wallet demo-miner"
    echo "    7. Wait for first attestation, then Ctrl-C"
    echo ""
    echo "Press Enter to start recording (Ctrl-D or 'exit' to stop)..."
    read -r
    asciinema rec "$outfile" \
        --title "RustChain Miner Install" \
        --cols 100 \
        --rows 30 \
        --overwrite
    echo "==> Saved: $outfile"
}

record_attestation() {
    local outfile="$DEMOS_DIR/first-attestation.cast"
    echo "==> Recording first attestation demo to $outfile"
    echo "    Follow these steps during the recording:"
    echo ""
    echo "    1. curl -sk https://50.28.86.131/health"
    echo "    2. curl -sk https://50.28.86.131/api/miners | python3 -m json.tool"
    echo "    3. curl -sk \"https://50.28.86.131/wallet/balance?miner_id=demo-miner\""
    echo "    4. curl -sk https://50.28.86.131/epoch"
    echo ""
    echo "Press Enter to start recording (Ctrl-D or 'exit' to stop)..."
    read -r
    asciinema rec "$outfile" \
        --title "RustChain First Attestation + Balance Check" \
        --cols 100 \
        --rows 30 \
        --overwrite
    echo "==> Saved: $outfile"
}

# --- main ---

mkdir -p "$DEMOS_DIR"

case "${1:-all}" in
    install)
        check_deps
        record_install
        ;;
    attestation)
        check_deps
        record_attestation
        ;;
    all)
        check_deps
        record_install
        record_attestation
        ;;
    -h|--help)
        usage
        exit 0
        ;;
    *)
        echo "Unknown option: $1"
        usage
        exit 1
        ;;
esac

echo ""
echo "Done! Play recordings with:"
echo "  asciinema play assets/demos/miner-install.cast"
echo "  asciinema play assets/demos/first-attestation.cast"
echo ""
echo "Convert to GIF (requires agg — https://github.com/asciinema/agg):"
echo "  agg assets/demos/miner-install.cast assets/demos/miner-install.gif"
echo "  agg assets/demos/first-attestation.cast assets/demos/first-attestation.gif"
