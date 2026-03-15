# RustChain Discord Bot

Discord bot for querying RustChain blockchain data.

## Features

- `!balance <address>` - Query RTC balance
- `!block` - Get latest block number
- `!tx <hash>` - Get transaction details
- `!stats` - Get network statistics

## Setup

1. Create a Discord bot at https://discord.com/developers/applications
2. Get your bot token
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set environment variable:
   ```bash
   export DISCORD_TOKEN="your-bot-token"
   export RUSTCHAIN_RPC_URL="https://rpc.rustchain.com"
   ```
5. Run the bot:
   ```bash
   python bot.py
   ```

## Usage

```
!balance RTC1234567890abcdef
!block
!tx 0xabc123...
!stats
```

## Permissions

The bot needs these Discord permissions:
- Send Messages
- Embed Links

---

Fixes #1596
