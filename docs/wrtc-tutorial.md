# wRTC Onboarding Tutorial

## Overview
This tutorial guides users through the complete wRTC (Wrapped RTC) onboarding process.

## Prerequisites
- RustChain wallet installed
- Basic understanding of blockchain
- Access to a web browser

## Step 1: Bridge to wRTC

### Connect Your Wallet
```bash
rustchain-cli connect --network mainnet
rustchain-cli status
```

### Initiate Bridge
```bash
rustchain-cli bridge --from RTC --to wRTC --amount 100
rustchain-cli bridge-status --tx-id <transaction-id>
```

## Step 2: Raydium Swap

1. Visit https://raydium.io
2. Connect your RustChain wallet
3. Select wRTC trading pair

## Step 3: Staking

Choose from available pools:
- **Conservative**: 5% APY
- **Balanced**: 12% APY
- **Aggressive**: 25% APY

## Security Notes

- Always verify contract addresses
- Start with small amounts
- Keep private keys secure
- Use hardware wallets for large amounts

---
*Created for RustChain Bounty #123*
