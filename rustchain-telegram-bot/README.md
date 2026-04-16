# RustChain Telegram Bot (@RustChainBot)

Check RTC balance, miner status, epoch info, and price via Telegram.

## Commands

| Command | Description |
|---------|-------------|
| \`/balance <wallet>\` | Check RTC balance |
| \`/miners\` | List active miners |
| \`/epoch\` | Current epoch info |
| \`/price\` | Show RTC reference rate (\/bin/zsh.10) |
| \`/help\` | Show commands |

## Quick Start

```bash
pip install -r requirements.txt
export TELEGRAM_BOT_TOKEN="your-bot-token"
export RUSTCHAIN_NODE_URL="https://50.28.86.131"
python rustchain_bot.py
```

## Features

- ✅ Rate limiting (1 request per 5 seconds per user)
- ✅ Error handling for offline node
- ✅ Markdown formatted responses
- ✅ Deploy on Railway, Fly.io, or systemd

## Bounty

- **Issue**: [#2869](https://github.com/Scottcjn/rustchain-bounties/issues/2869)
- **Reward**: 10 RTC (~\.00 USD)
- **Author**: 大鹏 (YPC0813)
