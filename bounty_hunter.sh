#!/bin/bash
# Main agent loop: Scan -> Claim -> Execute (Mock) -> PR
set -e

echo "🤖 OpenClaw Bounty Hunter v1.0"
echo "Scanning for targets..."
./bounty_scanner.sh > targets.txt
cat targets.txt

# Pick the first one for demo/proof (in real life, use LLM to pick)
TARGET=$(head -n 1 targets.txt)
if [ -z "$TARGET" ]; then
  echo "No bounties found."
  exit 0
fi

ID=$(echo "$TARGET" | awk -F'[][]' '{print $2}')
echo "🎯 Targeting Bounty #$ID"

# Claim
# ./claim_bounty.sh $ID # Commented out to avoid spamming while testing the framework itself

# Instructions for the agent (self-reflection)
echo "To complete this bounty:"
echo "1. Fork repo"
echo "2. Implement fix"
echo "3. gh pr create --repo Scottcjn/rustchain-bounties --title \"Fix #$ID\" --body \"Completed autonomously.\""
