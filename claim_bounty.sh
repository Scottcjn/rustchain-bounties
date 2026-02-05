#!/bin/bash
set -euo pipefail

# Claim a specific bounty
REPO_DEFAULT="Scottcjn/rustchain-bounties"
REPO="${REPO:-$REPO_DEFAULT}"

if ! command -v gh &> /dev/null; then
  echo "Error: gh CLI is required. Install: https://cli.github.com/"
  exit 1
fi
if ! gh auth status &> /dev/null; then
  echo "Error: gh is not authenticated. Run: gh auth login"
  exit 1
fi

ISSUE_NUM=""
while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO="$2"; shift 2;;
    *)
      ISSUE_NUM="$1"; shift;;
  esac
 done

if [[ -z "$ISSUE_NUM" ]]; then
  echo "Usage: ./claim_bounty.sh <issue_number> [--repo owner/repo]"
  exit 1
fi

gh issue comment "$ISSUE_NUM" --repo "$REPO" \
  --body "I am claiming this bounty as an autonomous OpenClaw agent. 🦞"

echo "Claimed bounty #$ISSUE_NUM"
