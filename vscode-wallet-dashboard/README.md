# RustChain Wallet Dashboard Extension

This Visual Studio Code extension provides a simple dashboard for monitoring your RustChain wallet and miner status directly from the editor.

## Features

- **Status Bar Balance:** Displays your RTC balance in the status bar.
- **Miner Status Indicator:** Shows whether your miner is online (green) or offline (red).
- **Epoch Countdown:** Shows a countdown timer to the next epoch settlement on the RustChain network.
- **Open Bounties Browser:** Lists currently open bounty issues from the [rustchain-bounties](https://github.com/Scottcjn/rustchain-bounties) repository.
- **Dashboard Command:** Run the command `RustChain Wallet: Show Dashboard` to open a full dashboard view (placeholder for future UI).

## Configuration

The extension defines the following settings under `rustchainWallet`:

- `rustchainWallet.nodeUrl` – URL of the RustChain node API (default: `https://api.rustchain.org`).
- `rustchainWallet.walletId` – Your wallet identifier used to fetch balance and miner status.

You can configure these settings in *Settings → Extensions → RustChain Wallet Dashboard*.

## Development

This extension is written in TypeScript and uses the VS Code extension API.

### Build

Run the following commands from the `vscode-wallet-dashboard` directory to compile the extension:

```bash
npm install
npm run compile
```

The compiled extension will be output to the `dist` folder.

### Run and Test

To run and test the extension in VS Code:

1. Open this folder in VS Code.
2. Run the `Launch Extension` debug configuration from the Run & Debug panel.

### Package

To package the extension for distribution, ensure `vsce` is installed (`npm install -g vsce`) and run:

```bash
vsce package
```

This will create a `.vsix` file that you can install locally or publish to the marketplace.

---

This extension is a work in progress. Contributions are welcome!
