#!/bin/bash

# wRTC Quick Start Script
# This script helps users get started with wRTC on Solana

echo "=========================================="
echo "  wRTC (Wrapped RustChain Credit)"
echo "  Quick Start Guide"
echo "=========================================="
echo ""

# Color codes
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Token information
WRTC_MINT="12TAdKXxcGf6oCv4rqDz2NkgxjyHq6HQKoxKZYGf5i4X"
RAYDIUM_POOL="8CF2Q8nSCxRacDShbtF86XTSrYjueBMKmfdR3MLdnYzb"
RAYDIUM_SWAP="https://raydium.io/swap/?inputMint=sol&outputMint=$WRTC_MINT"

echo -e "${BLUE}Token Information:${NC}"
echo "  Name: Wrapped RustChain Credit"
echo "  Symbol: wRTC"
echo "  Network: Solana"
echo -e "  Mint Address: ${GREEN}$WRTC_MINT${NC}"
echo ""

echo -e "${BLUE}Trading Information:${NC}"
echo -e "  Raydium Pool: ${GREEN}$RAYDIUM_POOL${NC}"
echo -e "  Swap Link: ${GREEN}$RAYDIUM_SWAP${NC}"
echo ""

echo -e "${YELLOW}Quick Steps to Get Started:${NC}"
echo ""
echo "1. Install a Solana wallet (recommended: Phantom)"
echo "   https://phantom.app/"
echo ""
echo "2. Add SOL to your wallet for gas fees (~0.01 SOL)"
echo ""
echo "3. Add wRTC to your wallet:"
echo "   a. Open Phantom wallet"
echo "   b. Click on the wallet icon"
echo "   c. Click 'Add Token'"
echo "   d. Paste this address: $WRTC_MINT"
echo ""
echo "4. Get wRTC:"
echo "   Option A - Buy on Raydium:"
echo "     $RAYDIUM_SWAP"
echo ""
echo "   Option B - Bridge from RTC:"
echo "     https://bottube.ai/bridge/wrtc"
echo ""
echo "   Option C - Mine RTC:"
echo "     https://github.com/Scottcjn/rustchain-bounties"
echo ""

echo -e "${BLUE}Useful Links:${NC}"
echo "  Official Bridge: https://bottube.ai/bridge/wrtc"
echo "  Twitter/X: https://x.com/RustchainPOA"
echo "  GitHub: https://github.com/Scottcjn/rustchain-bounties"
echo ""

echo -e "${GREEN}For detailed documentation, see README.md${NC}"
echo ""
echo "=========================================="
echo "  Welcome to the wRTC ecosystem!"
echo "=========================================="

# Check if user wants to open the swap link
read -p "Would you like to open the Raydium swap page? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    if command -v xdg-open &> /dev/null; then
        xdg-open "$RAYDIUM_SWAP"
    elif command -v open &> /dev/null; then
        open "$RAYDIUM_SWAP"
    else
        echo "Please open this link in your browser:"
        echo "$RAYDIUM_SWAP"
    fi
fi

echo ""
echo "Need help? Check the README.md or contact:"
echo "  - Twitter: https://x.com/RustchainPOA"
echo "  - GitHub: https://github.com/Scottcjn/rustchain-bounties/issues"
