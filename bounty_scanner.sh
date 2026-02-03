#!/bin/bash
# Scan for open bounties on RustChain
if ! command -v jq &> /dev/null; then
    echo "Error: jq is required"
    exit 1
fi
gh search issues --repo Scottcjn/rustchain-bounties --label bounty --state open --json number,title,url --limit 20 | jq -r '.[] | "[\(.number)] \(.title) - \(.url)"'
