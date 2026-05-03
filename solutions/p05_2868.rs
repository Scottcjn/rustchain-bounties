// package.json
{
  "name": "rustchain-dashboard",
  "displayName": "RustChain Dashboard",
  "description": "Wallet, miner status, and bounty board for RustChain",
  "version": "0.1.0",
  "publisher": "rustchain",
  "engines": {
    "vscode": "^1.85.0"
  },
  "categories": [
    "Other"
  ],
  "activationEvents": [
    "onStartupFinished"
  ],
  "main": "./out/extension.js",
  "contributes": {
    "commands": [
      {
        "command": "rustchain.refresh",
        "title": "RustChain: Refresh Dashboard"
      },
      {
        "command": "rustchain.claimBounty",
        "title": "RustChain: Claim Bounty"
      },
      {
        "command": "rustchain.startMiner",
        "title": "RustChain: Start Miner"
      },
      {
        "command": "rustchain.stopMiner",
        "title": "RustChain: Stop Miner"
      }
    ],
    "viewsContainers": {
      "activitybar": [
        {
          "id": "rustchain-sidebar",
          "title": "RustChain",
          "icon": "media/icon.svg"
        }
      ]
    },
    "views": {
      "rustchain-sidebar": [
        {
          "type": "webview",
          "id": "rustchain.dashboard",
          "name": "Dashboard"
        }
      ]
    },
    "configuration": {
      "title": "RustChain",
      "properties": {
        "rustchain.walletAddress": {
          "type": "string",
          "default": "TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu",
          "description": "Your RustChain wallet address"
        },
        "rustchain.rpcUrl": {
          "type": "string",
          "default": "https://rpc.rustchain.io",
          "description": "RustChain RPC endpoint"
        },
        "rustchain.minerEnabled": {
          "type": "boolean",
          "default": false,
          "description": "Enable local miner"
        }
      }
    }
  },
  "scripts": {
    "vscode:prepublish": "npm run compile",
    "compile": "tsc -p ./",
    "watch": "tsc -watch -p ./",
    "lint": "eslint src --ext ts"
  },
  "devDependencies": {
    "@types/node": "^20.11.0",
    "@types/vscode": "^1.85.0",
    "typescript": "^5.3.3",
    "eslint": "^8.56.0"
  },
  "dependencies": {
    "node-fetch": "^2.7.0"
  }
}