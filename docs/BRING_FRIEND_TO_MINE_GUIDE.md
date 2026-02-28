# Bring a Friend to Mine - RustChain Bounty Guide

## Overview
This guide explains how to bring friends to participate in RustChain mining and earn rewards through the bounty program.

## How It Works

### 1. Share RustChain with Friends
- Introduce RustChain to your friends, colleagues, or community
- Share the official documentation and mining instructions
- Help them understand the benefits of participating

### 2. Friend Setup Process
Your friend needs to:

1. **Get a Wallet ID**: Any string works as a wallet ID on testnet (e.g., `friend-name`)
2. **Set up a Miner**: Run the universal miner script
3. **Start Mining**: Begin earning RTC while contributing to the network

### 3. Mining Setup Instructions

```bash
# Clone the miner
git clone https://github.com/Scottcjn/rustchain-bounties.git

# Or get the miner script directly from the node:
curl -sk https://50.28.86.131/miner/download -o rustchain_miner.py

# Run it (replace FRIEND_WALLET_ID with their chosen name)
python3 rustchain_miner.py --wallet FRIEND_WALLET_ID --node https://50.28.86.131
```

### 4. Verification
- Friends can check their balance at any time:
```bash
curl -sk "https://50.28.86.131/wallet/balance?miner_id=FRIEND_WALLET_ID"
```

## Bounty Claim Process

### For Referrers (You)
When your friend successfully starts mining:

1. **Document the referral** in Issue #167
2. **Include your wallet ID** for payout
3. **Provide proof** of successful referral (friend's wallet ID, mining confirmation)

### Claim Template
```
**Claim**
- Wallet: your-wallet-id
- Agent/Handle: your-name
- Approach: Successfully referred [friend-name] to RustChain mining
- Friend's Wallet: friend-wallet-id
- Proof: [Screenshot or link showing friend's mining activity]
```

## Benefits

### For You (Referrer)
- **10 RTC per successful referral**
- **Community building contribution**
- **XP points** for outreach activities (+30 XP)

### For Your Friend
- **Free RTC earnings** from mining
- **No gas fees** - RTC transfers are free on the RustChain ledger
- **No bridges** - Direct transfer, no EVM/L2 complexity
- **Passive income** while contributing to network security

## Best Practices

### Effective Referral Tips
1. **Target interested audiences**: Developers, crypto enthusiasts, AI agents
2. **Provide clear instructions**: Use this guide to help friends get started
3. **Offer support**: Help troubleshoot initial setup issues
4. **Verify success**: Ensure your friend is actually mining before claiming

### Quality Requirements
- **Genuine referrals only**: No fake or duplicate accounts
- **Active mining required**: Friend must be actively mining, not just setting up
- **Valid wallet format**: Must follow RTC wallet ID requirements

## Technical Details

### Supported Hardware
Any real (non-VM) hardware can mine. Vintage hardware gets bonuses:

| Architecture | Multiplier |
|-------------|-----------|
| PowerPC G4 | 2.5x |
| PowerPC G5 | 2.0x |
| PowerPC G3 | 1.8x |
| Pentium 4 | 1.5x |
| Retro x86 | 1.4x |
| Apple Silicon | 1.2x |
| Modern x86_64 | 1.0x |

### Network Information
- **Primary Node**: https://50.28.86.131
- **Health Check**: https://50.28.86.131/health
- **Block Explorer**: https://50.28.86.131/explorer
- **Active Miners**: https://50.28.86.131/api/miners

## Troubleshooting

### Common Issues
1. **Miner not connecting**: Check firewall settings and internet connection
2. **Wallet ID rejected**: Ensure wallet ID follows format requirements
3. **No earnings**: Verify hardware is real (not VM) and properly configured

### Support Resources
- **GitHub Issues**: Report problems in the rustchain-bounties repository
- **Community**: Join Discord for real-time support
- **Documentation**: Refer to official RustChain documentation

## Related Bounties

- **Issue #165**: Share Why You Starred RustChain (3 RTC)
- **Issue #179**: Test Windows Miner Bundle (10 RTC)
- **Issue #166**: Mine for 7 Days — Sustained Mining (15 RTC)

## License
MIT

## Author
This guide was created as part of the RustChain bounty program to help grow the mining community.