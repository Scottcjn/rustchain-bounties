#!/usr/bin/env bash
# Harvard Mark II Miner - Quick Start Script
# 
# Usage:
#   ./run.sh              # Run simulator with default settings
#   ./run.sh test         # Run quick test
#   ./run.sh demo         # Run full demo
#   ./run.sh encode       # Generate sample paper tape
#   ./run.sh help         # Show help

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

case "${1:-run}" in
    run)
        echo "Running Harvard Mark II Miner Simulator..."
        python3 simulation/mark2_miner.py 2
        ;;
    
    test)
        echo "Running quick test..."
        python3 simulation/mark2_miner.py 1
        ;;
    
    demo)
        echo "Running full demo (3 epochs)..."
        python3 simulation/mark2_miner.py 3
        ;;
    
    encode)
        echo "Generating sample paper tape..."
        python3 simulation/paper_tape_encoder.py --miner sample_miner.pt
        python3 simulation/paper_tape_decoder.py sample_miner.pt
        ;;
    
    decode)
        if [ -z "$2" ]; then
            echo "Usage: $0 decode <file.pt>"
            exit 1
        fi
        python3 simulation/paper_tape_decoder.py "$2" --verbose
        ;;
    
    help|--help|-h)
        echo "Harvard Mark II Miner - Quick Start"
        echo ""
        echo "Usage: $0 [command]"
        echo ""
        echo "Commands:"
        echo "  run       Run simulator (default, 2 epochs)"
        echo "  test      Quick test (1 epoch)"
        echo "  demo      Full demo (3 epochs)"
        echo "  encode    Generate sample paper tape"
        echo "  decode    Decode a paper tape file"
        echo "  help      Show this help message"
        echo ""
        echo "Examples:"
        echo "  $0              # Run simulator"
        echo "  $0 test         # Quick test"
        echo "  $0 decode output.pt"
        echo ""
        echo "Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b"
        echo "Issue:  #393 - LEGENDARY Tier (200 RTC)"
        ;;
    
    *)
        echo "Unknown command: $1"
        echo "Run '$0 help' for usage information."
        exit 1
        ;;
esac

echo ""
echo "Done!"
