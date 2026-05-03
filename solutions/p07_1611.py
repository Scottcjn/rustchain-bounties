#!/bin/bash

# GitHub Issue Emoji Reactor Script
# Reacts with thumbs-up, rocket, and heart to 3+ open issues
# Wallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu

# Configuration
GITHUB_TOKEN="${GITHUB_TOKEN:-}"
REPO="${REPO:-}"
ISSUE_IDS=("1" "2" "3")  # Replace with actual issue numbers
EMOJIS=("+1" "rocket" "heart")

# Function to react to an issue
react_to_issue() {
    local issue_id=$1
    local emoji=$2
    
    curl -s -X POST \
        -H "Authorization: token $GITHUB_TOKEN" \
        -H "Accept: application/vnd.github.squirrel-girl-preview+json" \
        "https://api.github.com/repos/$REPO/issues/$issue_id/reactions" \
        -d "{\"content\":\"$emoji\"}"
}

# Main execution
echo "Reacting to issues with emojis..."
echo "Wallet: TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu"

for issue_id in "${ISSUE_IDS[@]}"; do
    for emoji in "${EMOJIS[@]}"; do
        echo "Reacting to issue #$issue_id with :$emoji:"
        react_to_issue "$issue_id" "$emoji"
        sleep 1  # Rate limiting
    done
done

echo "Reactions complete!"
echo "Commented links:"
for issue_id in "${ISSUE_IDS[@]}"; do
    echo "https://github.com/$REPO/issues/$issue_id"
done