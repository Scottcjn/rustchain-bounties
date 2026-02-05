#!/bin/bash
set -euo pipefail

# Scan for open bounties on RustChain
REPO_DEFAULT="Scottcjn/rustchain-bounties"
REPO="${REPO:-$REPO_DEFAULT}"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)
      REPO="$2"; shift 2;;
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

gh search issues --repo "$REPO" --label bounty --state open \
  --json number,title,url --limit 20 | jq -r '.[] | "[\(.number)] \(.title) - \(.url)"'
