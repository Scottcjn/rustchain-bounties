#!/bin/bash
set -euo pipefail

# Main agent loop: Scan -> (Optional) Claim -> PR instructions
REPO_DEFAULT="Scottcjn/rustchain-bounties"
REPO="${REPO:-$REPO_DEFAULT}"
PICK=1
ID=""
DO_CLAIM=false

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO="$2"; shift 2;;
    --pick)
      PICK="$2"; shift 2;;
    --id)
      ID="$2"; shift 2;;
    --claim)
      DO_CLAIM=true; shift;;
    *)
      echo "Unknown arg: $1"; exit 1;;
  esac
 done

if ! command -v gh &> /dev/null; then
  echo "Error: gh CLI is required. Install: https://cli.github.com/"
  exit 1
fi
if ! command -v jq &> /dev/null; then
  echo "Error: jq is required. Install: https://stedolan.github.io/jq/"
  exit 1
fi
if ! gh auth status &> /dev/null; then
  echo "Error: gh is not authenticated. Run: gh auth login"
  exit 1
fi

echo "🤖 OpenClaw Bounty Hunter v1.0"

if [[ -z "$ID" ]]; then
  echo "Scanning for targets in $REPO..."
  ./bounty_scanner.sh --repo "$REPO" > targets.txt
  if [[ ! -s targets.txt ]]; then
    echo "No bounties found."
    exit 0
  fi
  cat targets.txt
  TARGET=$(sed -n "${PICK}p" targets.txt || true)
  if [[ -z "$TARGET" ]]; then
    echo "No bounty at pick=$PICK."
    exit 1
  fi
  ID=$(echo "$TARGET" | awk -F'[][]' '{print $2}')
fi

echo "🎯 Targeting Bounty #$ID"

if [[ "$DO_CLAIM" == true ]]; then
  ./claim_bounty.sh --repo "$REPO" "$ID"
else
  echo "Claim skipped (use --claim to enable)."
fi

# Instructions for the agent (self-reflection)
echo "To complete this bounty:"
echo "1. Fork repo"
echo "2. Implement fix"
echo "3. gh pr create --repo $REPO --title \"Fix #$ID\" --body \"Completed autonomously.\""
