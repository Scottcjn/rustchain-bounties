# RTC Reward Action — Usage Guide

## Overview

**rtc-reward-action** (https://github.com/liuyuzhe530/rtc-reward-action) automatically awards RTC tokens when PRs are merged.

## Quick Start

1. Add to your repo: \`.github/workflows/rtc-reward.yml\`
2. Configure secrets: \`RTC_NODE_URL\`, \`RTC_ADMIN_KEY\`
3. Contributors add their wallet to PR body

## Input Options

| Input | Required | Default | Description |
|-------|----------|---------|-------------|
| \`amount\` | Yes | — | RTC tokens per merged PR |
| \`node-url\` | Yes | — | RustChain node URL |
| \`admin-key\` | Yes | — | Admin key for transfers |
| \`dry-run\` | No | \`false\` | Simulate without transfer |

## Wallet Detection

Looks for:
1. PR body: \`RTC[a-zA-Z0-9]{40}\` pattern
2. \`.rtc-wallet\` file in repo root

## Published

✅ GitHub Marketplace: [liuyuzhe530/rtc-reward-action](https://github.com/marketplace/rtc-reward-action)
