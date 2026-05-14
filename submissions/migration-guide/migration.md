# Migrating from Ethereum / Ethereum Classic to RustChain

A practical guide for developers and operators transitioning dApps, smart contracts, and infrastructure from Ethereum or ETC to RustChain.

---

## Table of Contents

1. [Overview](#overview)
2. [Key Differences](#key-differences)
3. [Smart Contract Migration](#smart-contract-migration)
4. [Tooling Comparison](#tooling-comparison)
5. [Wallet & Account Migration](#wallet--account-migration)
6. [Node Operation Migration](#node-operation-migration)
7. [Network Configuration](#network-configuration)
8. [Common Pitfalls](#common-pitfalls)
9. [FAQ](#faq)

---

## Overview

RustChain is an EVM-compatible blockchain built on the BCOS framework with a Rust-based implementation. This means most Ethereum smart contracts and tools work on RustChain with minimal changes. The primary differences are in **consensus (PoA vs PoW)**, **chain ID**, and **block timing**.

### Why Migrate?

| Feature | Ethereum | Ethereum Classic | RustChain |
|---|---|---|---|
| Consensus | PoS | PoW | PoA |
| Block Time | ~12s | ~15s | ~2-3s |
| Finality | Minutes | Minutes | Seconds |
| Gas Cost | High | Medium | Low |
| EVM Compatible | ✅ | ✅ | ✅ |
| Language | Go | Go | Rust |

---

## Key Differences

### 1. Chain ID
- Ethereum Mainnet: `1`
- Ethereum Classic: `61`
- RustChain Mainnet: Check `rustchain-cli chain-id`
- RustChain Testnet: Check testnet documentation

Update your deployment scripts and wallet configurations with the correct Chain ID.

### 2. Consensus Model
RustChain uses **Proof of Authority (PoA)** instead of Proof of Stake (PoS) or Proof of Work (PoW). This means:
- No staking required for basic users (validators are pre-approved)
- Faster block times and finality
- Different block reward distribution
- No uncle/ommer blocks

### 3. Gas Economics
RustChain gas prices are significantly lower. Recommended starting point:
```
Gas Price: 1 Gwei (vs 20+ Gwei on Ethereum)
Gas Limit: Same calculation methods apply
```

### 4. Block Structure
- Blocks are produced by a rotating set of validators
- Block headers include PoA-specific fields (validator signature, epoch info)
- No difficulty field in the traditional PoW sense

---

## Smart Contract Migration

### Step 1: Audit Your Contracts

Review your Solidity contracts for Ethereum-specific assumptions:

```solidity
// ❌ May cause issues - relies on specific block.difficulty
uint256 randomness = uint256(block.difficulty);

// ✅ RustChain alternative - use block timestamp + proposer
uint256 randomness = uint256(keccak256(abi.encodePacked(block.timestamp, block.coinbase)));
```

### Step 2: Update Hardhat Configuration

```javascript
// hardhat.config.js
module.exports = {
  solidity: "0.8.x",
  networks: {
    rustchain: {
      url: "https://rpc.rustchain.io",
      accounts: [process.env.PRIVATE_KEY],
      chainId: <RUSTCHAIN_CHAIN_ID>,
      gasPrice: 1000000000, // 1 Gwei
    },
    rustchainTestnet: {
      url: "https://rpc.testnet.rustchain.io",
      accounts: [process.env.PRIVATE_KEY],
      chainId: <TESTNET_CHAIN_ID>,
      gasPrice: 1000000000,
    },
  },
};
```

### Step 3: Update Foundry Configuration

```toml
# foundry.toml
[rpc_endpoints]
rustchain = "https://rpc.rustchain.io"
rustchain_testnet = "https://rpc.testnet.rustchain.io"

[profile.rustchain]
chain_id = <RUSTCHAIN_CHAIN_ID>
rpc_url = "https://rpc.rustchain.io"
```

### Step 4: Update Truffle Configuration

```javascript
// truffle-config.js
module.exports = {
  networks: {
    rustchain: {
      provider: () => new HDWalletProvider(mnemonic, "https://rpc.rustchain.io"),
      network_id: "<RUSTCHAIN_CHAIN_ID>",
      gasPrice: 1000000000,
      confirmations: 2,
      timeoutBlocks: 200,
    },
  },
};
```

### Step 5: Redeploy Contracts

1. Compile contracts with the same Solidity version
2. Deploy to RustChain testnet first
3. Verify all functions work correctly
4. Run integration tests against the testnet
5. Deploy to RustChain mainnet

### Contract Compatibility Checklist

| Feature | Compatible? | Notes |
|---|---|---|
| Solidity 0.6.x | ✅ | Fully supported |
| Solidity 0.7.x | ✅ | Fully supported |
| Solidity 0.8.x | ✅ | Fully supported |
| ERC-20 tokens | ✅ | Deploy as-is |
| ERC-721 (NFTs) | ✅ | Deploy as-is |
| ERC-1155 | ✅ | Deploy as-is |
| block.difficulty | ⚠️ | Returns 0 or fixed value in PoA |
| block.basefee | ⚠️ | May behave differently |
| SELFDESTRUCT | ⚠️ | Avoid; being deprecated across EVM chains |
| Precompiles | ✅ | Standard EVM precompiles supported |

---

## Tooling Comparison

### Development Frameworks

| Tool | Ethereum | RustChain | Migration Effort |
|---|---|---|---|
| Hardhat | ✅ | ✅ | Change RPC URL & chain ID |
| Foundry | ✅ | ✅ | Change RPC URL & chain ID |
| Truffle | ✅ | ✅ | Change RPC URL & chain ID |
| Remix | ✅ | ✅ | Change provider in Remix |
| Brownie | ✅ | ✅ | Add network config |

### Wallets

| Wallet | Ethereum | RustChain | Notes |
|---|---|---|---|
| MetaMask | ✅ | ✅ | Add custom network |
| WalletConnect | ✅ | ✅ | Configure RPC URL |
| Hardware Wallets | ✅ | ✅ | Same derivation path |
| rustchain-cli | — | ✅ | Native CLI wallet |

### Monitoring & Analytics

| Tool | Purpose | RustChain Alternative |
|---|---|---|
| Etherscan | Block explorer | RustChain Block Explorer |
| The Graph | Indexing | Custom subgraph or RustChain indexer |
| Tenderly | Monitoring | Custom alerting via RPC |
| Alchemy/Infura | RPC provider | Self-hosted or official RPC |

### Setting Up MetaMask for RustChain

1. Open MetaMask → Settings → Networks → Add Network
2. Enter:
   - **Network Name:** RustChain Mainnet
   - **RPC URL:** `https://rpc.rustchain.io`
   - **Chain ID:** `<RUSTCHAIN_CHAIN_ID>`
   - **Currency Symbol:** RTC
   - **Block Explorer:** `https://explorer.rustchain.io`

---

## Wallet & Account Migration

### Same Address, New Chain

RustChain uses the same account format as Ethereum (secp256k1). Your Ethereum private keys and addresses work on RustChain.

⚠️ **Important:** Never reuse the same private key across chains without understanding the risks. Best practice is to generate a fresh key for RustChain.

### Migration Steps

1. **Generate a new RustChain address** (or import existing):
   ```bash
   rustchain-cli account new
   # or import:
   rustchain-cli account import --private-key <KEY>
   ```

2. **Fund the address** with RTC from an exchange or faucet (testnet)

3. **Update your dApp frontend** to connect to RustChain RPC

4. **Migrate token balances** by bridging or redeploying tokens

---

## Node Operation Migration

### From Geth/Parity to RustChain Node

```bash
# Install RustChain node
git clone https://github.com/rustchain/rustchain-node
cd rustchain-node
cargo build --release

# Initialize with genesis
./target/release/rustchain-node init --genesis genesis.json

# Start syncing
./target/release/rustchain-node start --network mainnet
```

### Configuration Differences

| Setting | Geth | RustChain |
|---|---|---|
| Data Directory | `~/.ethereum` | `~/.rustchain` |
| RPC Port | 8545 | 8545 (configurable) |
| WebSocket Port | 8546 | 8546 (configurable) |
| P2P Port | 30303 | 30303 (configurable) |
| Sync Mode | Full/Fast/Snap | Full |

### Running an API Node

```bash
./target/release/rustchain-node start \
  --network mainnet \
  --rpc \
  --rpc-addr 0.0.0.0 \
  --rpc-port 8545 \
  --ws \
  --ws-addr 0.0.0.0 \
  --ws-port 8546
```

---

## Network Configuration

### Endpoints

| Network | RPC URL | WebSocket | Explorer |
|---|---|---|---|
| Mainnet | `https://rpc.rustchain.io` | `wss://ws.rustchain.io` | `https://explorer.rustchain.io` |
| Testnet | `https://rpc.testnet.rustchain.io` | `wss://ws.testnet.rustchain.io` | `https://explorer.testnet.rustchain.io` |

### Python SDK Configuration

```python
from rustchain_sdk import RustChainClient

client = RustChainClient(
    rpc_url="https://rpc.rustchain.io",
    chain_id=<RUSTCHAIN_CHAIN_ID>,
)
```

### JavaScript/ethers.js Configuration

```javascript
const { ethers } = require("ethers");

const provider = new ethers.JsonRpcProvider("https://rpc.rustchain.io");
const signer = new ethers.Wallet(privateKey, provider);
```

### Web3.js Configuration

```javascript
const Web3 = require("web3");
const web3 = new Web3("https://rpc.rustchain.io");
```

---

## Common Pitfalls

### 1. Incorrect Chain ID
**Problem:** Transactions fail with "invalid chain id"  
**Fix:** Double-check the chain ID in all configurations (Hardhat, MetaMask, scripts)

### 2. Gas Price Too High
**Problem:** Overpaying for transactions  
**Fix:** RustChain gas prices are ~1 Gwei. Don't copy Ethereum gas price settings.

### 3. Block Difficulty Assumptions
**Problem:** Contracts using `block.difficulty` for randomness break  
**Fix:** Use Chainlink VRF or commit-reveal schemes for randomness

### 4. Uncle Blocks
**Problem:** Code expects uncle block data  
**Fix:** PoA chains don't produce uncle blocks. Remove related logic.

### 5. Pending Transaction Queue
**Problem:** Different transaction pool behavior  
**Fix:** Test transaction submission patterns on testnet first

### 6. Contract Verification
**Problem:** Can't verify contracts on explorer  
**Fix:** Use the RustChain explorer's verification tool with correct compiler settings

---

## FAQ

### Q: Can I use the same Solidity contracts?
**A:** Yes, with minor exceptions. Review the compatibility checklist above. Most contracts deploy without changes.

### Q: Do I need to learn Rust?
**A:** Only if you're modifying the node software or building native modules. For dApp and smart contract development, Solidity works perfectly.

### Q: How do I bridge assets from Ethereum?
**A:** Use the official RustChain bridge or a supported third-party bridge. Check the official documentation for current bridge endpoints.

### Q: Are OpenZeppelin contracts supported?
**A:** Yes. All OpenZeppelin contracts work on RustChain since it's EVM-compatible.

### Q: What about oracles?
**A:** Deploy your own oracle contracts or use compatible oracle services. The integration pattern is identical to Ethereum.

### Q: Can I use The Graph?
**A:** You'll need to set up a custom Graph node pointing to RustChain's RPC. The subgraph definition process is the same.

### Q: How are validator rewards different?
**A:** In PoA, rewards go to authorized validators. There's no mining reward. Delegators earn by staking to validators.

### Q: Is there a testnet faucet?
**A:** Yes, the testnet faucet provides RTC for development. Check the official Discord or documentation for the faucet URL.

---

*Last updated: 2025-05*
