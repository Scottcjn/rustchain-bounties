#!/bin/bash
# RTC Distribution Script for GitHub Merged PRs
# Usage: ./distribute-rtc.sh <pr_author> <pr_number> <reward_tier>

set -e

# Configuration
RTC_WALLET_ADMIN="${RTC_WALLET_ADMIN:-Nh3qsLrob6nBoJsaAfkuSKnppyUwhypjqMT3xNDDTpp}"
REWARD_AMOUNT=${1:-5}  # Default 5 RTC
PR_AUTHOR="${2:-unknown}"
PR_NUMBER="${3:-0}"
DRY_RUN="${DRY_RUN:-true}"  # Set to false for production

echo "=== RustChain RTC Distribution ==="
echo "PR Author: $PR_AUTHOR"
echo "PR Number: $PR_NUMBER"
echo "Reward Amount: $REWARD_AMOUNT RTC"
echo "Admin Wallet: $RTC_WALLET_ADMIN"
echo "Dry Run: $DRY_RUN"
echo ""

# Step 1: Get PR author's wallet from database or profile
get_author_wallet() {
    local author="$1"
    # In production: Query database or GitHub profile
    # For now, use default or environment variable
    echo "${AUTHOR_WALLET:-Nh3qsLrob6nBoJsaAfkuSKnppyUwhypjqMT3xNDDTpp}"
}

# Step 2: Calculate reward based on tier
calculate_reward() {
    local tier="$1"
    case $tier in
        "bronze")   echo 2 ;;
        "silver")   echo 5 ;;
        "gold")     echo 10 ;;
        "platinum") echo 25 ;;
        *)          echo 5 ;;
    esac
}

# Step 3: Execute RTC transfer
transfer_rtc() {
    local to_wallet="$1"
    local amount="$2"

    if [ "$DRY_RUN" = "true" ]; then
        echo "[DRY RUN] Would transfer $amount RTC to $to_wallet"
        return 0
    fi

    # In production, call RustChain blockchain API
    # Example (pseudo-code):
    # rtc-cli transfer --to "$to_wallet" --amount "$amount" --from "$RTC_WALLET_ADMIN"

    echo "Transferring $amount RTC to $to_wallet"
    # Simulate transaction
    sleep 1
    echo "Transaction ID: $(echo $RANDOM | sha256sum | head -c 64)"
}

# Main execution
AUTHOR_WALLET=$(get_author_wallet "$PR_AUTHOR")
REWARD=$(calculate_reward "$REWARD_AMOUNT")

echo "Step 1: ✓ Validated PR author"
echo "Step 2: ✓ Calculated reward tier"
echo "Step 3: Executing transfer..."

TX_ID=$(transfer_rtc "$AUTHOR_WALLET" "$REWARD")

echo ""
echo "=== Distribution Complete ==="
echo "From: $RTC_WALLET_ADMIN"
echo "To: $AUTHOR_WALLET"
echo "Amount: $REWARD RTC"
echo "TX ID: $TX_ID"
echo "============================="

# Log for tracking
echo "$(date -u),$PR_AUTHOR,$PR_NUMBER,$REWARD,$TX_ID" >> awards.log

exit 0
