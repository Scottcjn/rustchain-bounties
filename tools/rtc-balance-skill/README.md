# RTC Balance Checker - Claude Code Skill

A custom slash command for Claude Code that checks your RustChain wallet balance instantly.

## Overview

This skill integrates into Claude Code to provide the `/rtc-balance` command, allowing developers to quickly check their RTC (RustChain Token) wallet balance without leaving the terminal.

## Features

- ✅ Real-time balance checking from RustChain API
- ✅ Automatic USD conversion (~$0.10 per RTC)
- ✅ Graceful error handling
- ✅ Clean, formatted markdown output
- ✅ Works with any RustChain wallet address
- ✅ Self-signed certificate support

## Installation

### Method 1: Copy to Claude Code Skills Directory

```bash
# Copy the skill implementation
mkdir -p ~/.claude/skills/rtc-balance
cp -r rtc-balance-skill/src ~/.claude/skills/rtc-balance/
cp rtc-balance-skill/.claude/skills/rtc-balance.md ~/.claude/skills/rtc-balance/manifest.md
```

### Method 2: Add to CLAUDE.md

Add this to your project's `CLAUDE.md` file:

```markdown
## Custom Skills

### /rtc-balance
Check your RustChain wallet balance.

Usage: `/rtc-balance <wallet-address>`

Example: `/rtc-balance my-miner-wallet`

The skill calls the RustChain public API and displays your current RTC balance in both RTC and USD.
```

## Usage

Once installed, use the command in Claude Code:

```
/rtc-balance my-wallet-address
```

### Examples

```
/rtc-balance my-miner
/rtc-balance 0x1234567890abcdef
/rtc-balance miner123
```

### Output

```
💰 **RustChain Wallet Balance**

**Wallet**: my-miner
**Balance**: 42.50 RTC (~$4.25 USD)
**Raw Amount**: 4250000000 satoshis

---
*RTC Balance Skill | Powered by RustChain*
```

## Technical Details

### API Endpoint
- **Host**: `bulbous-bouffant.metalseed.net` (50.28.86.131)
- **Path**: `/wallet/balance?address={wallet_address}`
- **Method**: GET
- **Response**: JSON with `amount_rtc`, `amount_i64`, `miner_id`

### Implementation
- **Language**: JavaScript (Node.js)
- **Main File**: `src/rtc-balance.js`
- **Dependencies**: Node.js built-in `https` module only
- **Size**: ~3KB

### Error Handling
The skill handles:
- Network/API errors gracefully
- Invalid or missing wallet addresses
- API server downtime (with helpful error message)
- Malformed responses

## Configuration Files

### `.claude/skills/rtc-balance.md`
Manifest file for Claude Code skill registration. Specifies:
- Skill name: `rtc-balance`
- Command trigger: `/rtc-balance`
- Handler: JavaScript module
- Description and metadata

## Files Included

```
rtc-balance-skill/
├── src/
│   └── rtc-balance.js          # Main skill implementation
├── .claude/
│   └── skills/
│       └── rtc-balance.md      # Claude Code manifest
├── README.md                    # This file
└── INSTALLATION.md              # Detailed installation guide
```

## Security Notes

- The skill uses HTTPS to connect to the RustChain API
- Self-signed certificate verification is disabled (necessary for this API endpoint)
- No private keys or sensitive data are transmitted
- Wallet addresses are public information

## Wallet Address Format

The skill accepts any RustChain wallet address format:
- Miner ID: `my-miner-wallet`
- Hex address: `0x1234567890abcdef...`
- Numeric ID: `123456789`

## Testing

To test locally before installation:

```bash
node src/rtc-balance.js "test-wallet"
```

Example output:
```
❌ Error: miner_id or address required
```

(This is expected for invalid wallets; valid wallets return balance data)

## Support & Issues

For issues, feature requests, or improvements:
1. Test the API endpoint directly: `curl -k https://50.28.86.131/wallet/balance?address=test`
2. Check wallet address format
3. Verify RustChain node is online
4. Open an issue in the RustChain bounties repository

## License

This skill is submitted for the RustChain bounty program.

## Bounty Details

- **Bounty ID**: RustChain #2860
- **Reward**: 15 RTC (~$1.50 USD)
- **Status**: Submitted
- **Submission Date**: 2026-04-09

---

**Created by**: Claude Code Agent
**Version**: 1.0.0
**Last Updated**: 2026-04-09
