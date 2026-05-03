// package.json
{
  "name": "rustchain-dashboard",
  "displayName": "RustChain Dashboard",
  "description": "Wallet balance, miner status, and bounty board for RustChain",
  "version": "0.0.1",
  "publisher": "rustchain",
  "engines": {
    "vscode": "^1.60.0"
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
          "icon": "media/rustchain.svg"
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
          "default": "https://rpc.rustchain.network",
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
    "@types/node": "^16.11.7",
    "@types/vscode": "^1.60.0",
    "typescript": "^4.5.4",
    "eslint": "^8.6.0",
    "@typescript-eslint/eslint-plugin": "^5.9.1",
    "@typescript-eslint/parser": "^5.9.1"
  },
  "dependencies": {
    "axios": "^0.24.0",
    "ethers": "^5.5.3"
  }
}