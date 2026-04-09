# RustChain Dashboard VS Code Extension

> Wallet balance, miner status, and bounty browser in your editor

## Features

- 💰 **Wallet Balance** - View your RTC balance in the sidebar
- ⛏️ **Miner Status** - See if your miner is active or inactive
- 📅 **Epoch Timer** - Countdown to next epoch settlement
- 🔄 **Refresh** - Manual refresh button

## Installation

1. Clone this repository
2. Run `npm install`
3. Run `npm run compile`
4. Open in VS Code and press `F5` to debug
5. Or publish to VS Code Marketplace

## Configuration

In VS Code settings:

```json
{
  "rustchain.walletName": "your_wallet_name",
  "rustchain.nodeUrl": "https://50.28.86.131"
}
```

## Development

```bash
npm install
npm run compile
code .
# Press F5 to debug
```

## Publishing

```bash
npm install -g vsce
vsce package
vsce publish
```

## License

MIT
