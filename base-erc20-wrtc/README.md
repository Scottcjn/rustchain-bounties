# Base ERC-20 wRTC (Track B)

## Bounty

- **Reward:** 75 RTC (Track B)
- **Issue:** [#1149](https://github.com/Scottcjn/rustchain-bounties/issues/1149)

## Overview

This implements **Track B: Base ERC-20 Token** for the RIP-305 Cross-Chain Airdrop.

## Specification

- **Token Name:** Wrapped RTC
- **Token Symbol:** wRTC
- **Decimals:** 6 (matches native RTC)
- **Network:** Base (testnet first, then mainnet)
- **Initial Supply:** 0 (minted via bridge)

## Features

### Core Features
- ERC-20 standard with OpenZeppelin
- Mint/burn functions controlled by bridge admin
- Ownable (transferable to multisig)

### Anti-Sybil Requirements
- Minimum ETH balance check (0.01 ETH) for bridge burns
- Prevents empty wallet farms

### Bridge Integration
- `bridgeMint()` - Called when locking RTC on source chain
- `bridgeBurn()` - Called when unlocking wRTC on Base

## Deployment

### 1. Install Dependencies
```bash
cd base-erc20-wrtc
npm install
```

### 2. Set Environment
```bash
export DEPLOYER_PRIVATE_KEY=your_private_key
export BASESCAN_API_KEY=your_basescan_api_key
```

### 3. Compile Contract
```bash
npx hardhat compile
```

### 4. Deploy to Testnet
```bash
npx hardhat run scripts/deploy.js --network base-sepolia
```

### 5. Deploy to Mainnet
```bash
npx hardhat run scripts/deploy.js --network base-mainnet
```

## Contract Address

| Network | Address |
|---------|---------|
| Base Sepolia (Testnet) | `TBD` |
| Base Mainnet | `TBD` |

## API Reference

### Bridge Functions

```solidity
// Mint tokens when RTC is locked on source chain
function bridgeMint(address to, uint256 amount, bytes32 lockTxHash) external;

// Burn tokens to unlock on source chain
function bridgeBurn(uint256 amount, string calldata recipient) external;
```

### Admin Functions

```solidity
// Pause/unpause bridge
function setBridgePaused(bool paused) external;

// Update bridge admin
function setBridgeAdmin(address newAdmin) external;
```

## Integration with Bridge API

The Bridge API (Track C) will call:
1. `/bridge/lock` → triggers `bridgeMint()` on Base
2. `/bridge/release` → triggers `bridgeBurn()` on Base

## Verification

After deployment, verify on Basescan:
1. Go to https://sepolia.basescan.org/verify-contracts
2. Enter contract address
3. Select "Solidity (Single File)"
4. Compiler: ^0.8.20
5. EVM Version: london
6. Upload `contracts/WrappedRTC.sol`

## Related Tracks

- **Track A (Solana):** SPL Token on Solana
- **Track C (Bridge API):** /bridge/lock and /bridge/release endpoints
- **Track D (Claim Page):** Frontend for claiming airdrop

## License

MIT
