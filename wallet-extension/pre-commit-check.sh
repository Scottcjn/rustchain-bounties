#!/bin/bash
# Wallet Extension - Pre-commit Check
# Bounty #730 - 40-100 RTC

set -e

echo "========================================"
echo "Wallet Extension - Pre-commit Check"
echo "========================================"
echo ""

# 1. Check manifest
echo "✓ Checking manifest.json..."
if [ ! -f "manifest.json" ]; then
    echo "❌ manifest.json not found!"
    exit 1
fi
echo "  ✅ manifest.json exists"

# Check manifest version
MANIFEST_VERSION=$(cat manifest.json | grep -o '"manifest_version": 3')
if [ -z "$MANIFEST_VERSION" ]; then
    echo "❌ manifest_version should be 3!"
    exit 1
fi
echo "  ✅ Manifest version 3"

# 2. Check popup
echo ""
echo "✓ Checking popup.html..."
if [ ! -f "popup.html" ]; then
    echo "❌ popup.html not found!"
    exit 1
fi
echo "  ✅ popup.html exists"

# Check for required elements
if ! grep -q "balance" popup.html; then
    echo "❌ Missing balance display!"
    exit 1
fi
echo "  ✅ Balance display present"

if ! grep -q "MetaMask Snap" popup.html; then
    echo "❌ Missing Snap integration!"
    exit 1
fi
echo "  ✅ Snap integration present"

# 3. Check background service
echo ""
echo "✓ Checking background.js..."
if [ ! -f "background.js" ]; then
    echo "❌ background.js not found!"
    exit 1
fi
echo "  ✅ background.js exists"

if ! grep -q "walletState" background.js; then
    echo "❌ Missing wallet state management!"
    exit 1
fi
echo "  ✅ Wallet state management present"

if ! grep -q "wallet_invokeSnap" background.js; then
    echo "❌ Missing Snap invocation!"
    exit 1
fi
echo "  ✅ Snap invocation present"

# 4. Run tests
echo ""
echo "✓ Running tests..."
node test_wallet.js > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "❌ Tests failed!"
    exit 1
fi
echo "  ✅ All tests passed"

# 5. Check code quality
echo ""
echo "✓ Checking code quality..."
BG_LINES=$(wc -l < background.js)
if [ $BG_LINES -lt 50 ]; then
    echo "❌ background.js too short ($BG_LINES lines)!"
    exit 1
fi
echo "  ✅ background.js: $BG_LINES lines"

POPUP_LINES=$(wc -l < popup.html)
if [ $POPUP_LINES -lt 50 ]; then
    echo "❌ popup.html too short ($POPUP_LINES lines)!"
    exit 1
fi
echo "  ✅ popup.html: $POPUP_LINES lines"

echo ""
echo "========================================"
echo "✅ Pre-commit check PASSED!"
echo "========================================"
echo ""
echo "Ready to commit and push!"
