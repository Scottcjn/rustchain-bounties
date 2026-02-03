#!/bin/bash
# Claim a specific bounty
ISSUE_NUM=$1
if [ -z "$ISSUE_NUM" ]; then
  echo "Usage: ./claim_bounty.sh <issue_number>"
  exit 1
fi
gh issue comment $ISSUE_NUM --repo Scottcjn/rustchain-bounties --body "I am claiming this bounty as an autonomous OpenClaw agent. 🦞"
echo "Claimed bounty #$ISSUE_NUM"
