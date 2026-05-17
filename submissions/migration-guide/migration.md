# Migrating from Ethereum / Ethereum Classic to RustChain

A practical guide for developers and operators transitioning dApps, smart contracts, and infrastructure from Ethereum or ETC to RustChain.

---

## Table of Contents

1. [Overview](#overview)
2. [Key Differences](#key-differences)
3. [Smart Contract Migration](#smart-contract-migration)
4. [Tooling Comparison](#tooling-comparison)
5. [Wallet & Account Migration](#wallet--account-migration)
6. [Node & Miner Operation](#node--miner-operation)
7. [Network Configuration](#network-configuration)
8. [Common Pitfalls](#common-pitfalls)
9. [FAQ](#faq)

---

## Overview

RustChain is a lightweight blockchain ecosystem written in Rust with a fundamentally different philosophy from Ethereum. Rather than competing on computational power, RustChain uses **RIP-200 Proof-of-Antiquity (PoAn)** consensus, where vintage and low-power hardware earns higher mining rewards. The core motto: *"Your 2005 laptop isn't e-waste. It's a mining rig."*

### Why Migrate?

| Feature | Ethereum | Ethereum Classic | RustChain |
|---|---|---|---|
| Consensus | PoS | PoW | Proof-of-Antiquity (RIP-200) |
| Block Time | ~12s | ~15s | Epoch-based |
| Hardware Requirements | High (validators) | High (ASICs/GPUs) | Ultra-low (32MB RAM minimum) |
| Mining | Staking 32 ETH | ASIC/GPU mining | Hardware attestation on any device |
| Language | Go | Go | Rust |
| Philosophy | Institutional DeFi | Code is Law | Anti-e-waste, absolute decentralization |

### Key Philosophical Difference

Unlike Ethereum's Proof-of-Stake or ETC's Proof-of-Work, RustChain's **Reverse-Proof-of-Work (RPoW)** actively rewards miners who use older, less powerful hardware. The protocol scales to run on devices as humble as a Pentium III or a Nintendo 64. This means:

- No expensive hardware required
- No energy arms race
- Real hardware attestation (not simulated)
- 1.5 RTC per epoch distributed among active miners

---

## Key Differences

### 1. Consensus: Proof-of-Antiquity (RIP-200)

RustChain uses hardware attestation rather than hash power or stake:

- Miners run attestation scripts that prove they are running on real hardware
- VMs may attest but rewards can be penalized or denied
- Older and more exotic hardware earns higher rewards
- **1.5 RTC per epoch** distributed among all active miners

### 2. No Traditional Gas Market

Unlike Ethereum's complex gas auction, RustChain has minimal transaction costs:

- Gas prices are negligible compared to Ethereum
- No MEV extraction concerns
- No priority fee auction

### 3. Hardware-First Architecture

RustChain is designed for real hardware, not cloud infrastructure:

- Ultra-low overhead miner (< 32MB RAM)
- Python-based miner scripts for Linux, macOS, and Windows
- No special hardware required (no ASICs, no GPUs)
- Exotic hardware bounties reward ports to unusual platforms

### 4. Block Structure

- Epoch-based rather than traditional block-by-block
- Miner attestations form the basis of consensus
- No difficulty adjustment algorithm (not hash-based)
- No uncle/ommer blocks

---

## Smart Contract Migration

### Step 1: Understand EVM Compatibility

RustChain is a Rust-based blockchain with its own runtime. Smart contract compatibility depends on the specific integration layer. Check the current documentation for the latest on EVM compatibility support.

### Step 2: Identify Ethereum-Specific Code

Review your Solidity contracts for Ethereum-specific assumptions:

```solidity
// May not translate - relies on PoW-specific block.difficulty
uint256 randomness = uint256(block.difficulty);

// Use alternative randomness sources
uint256 randomness = uint256(keccak256(abi.encodePacked(block.timestamp, block.coinbase)));
```

### Step 3: Adapt Development Tooling

If EVM compatibility is available, update your tool configurations:

```javascript
// hardhat.config.js - update RPC endpoint and chain ID
module.exports = {
  solidity: "0.8.x",
  networks: {
    rustchain: {
      url: process.env.RUSTCHAIN_RPC_URL || "http://localhost:8545",
      accounts: [process.env.PRIVATE_KEY],
      chainId: parseInt(process.env.RUSTCHAIN_CHAIN_ID || "0"),
    },
  },
};
```

```toml
# foundry.toml
[rpc_endpoints]
rustchain = "${RUSTCHAIN_RPC_URL}"

[profile.rustchain]
chain_id = "${RUSTCHAIN_CHAIN_ID}"
rpc_url = "${RUSTCHAIN_RPC_URL}"
```

### Step 4: Test and Deploy

1. Set up a local RustChain node for testing
2. Compile contracts and verify compatibility
3. Deploy to a test environment
4. Run integration tests
5. Deploy to the RustChain network

### Contract Compatibility Checklist

| Feature | Notes |
|---|---|
| Solidity 0.8.x | Check current EVM support status |
| ERC-20 tokens | May require adapter layer |
| ERC-721 (NFTs) | May require adapter layer |
| block.difficulty | Not applicable in PoAn consensus |
| block.basefee | May behave differently |
| SELFDESTRUCT | Avoid; being deprecated across chains |
| Precompiles | Check RustChain documentation |

---

## Tooling Comparison

### Development Frameworks

| Tool | Ethereum | RustChain | Migration Effort |
|---|---|---|---|
| Hardhat | ✅ | Check docs | Update RPC URL & chain ID |
| Foundry | ✅ | Check docs | Update RPC URL & chain ID |
| Truffle | ✅ | Check docs | Update RPC URL & chain ID |
| Remix | ✅ | Check docs | Update provider |
| rustchain-cli | — | ✅ | Native CLI tool |

### Wallets

| Wallet | Ethereum | RustChain | Notes |
|---|---|---|---|
| MetaMask | ✅ | If EVM-compatible | Add custom network |
| rustchain-cli | — | ✅ | Native CLI wallet |
| Hardware Wallets | ✅ | Check docs | Same secp256k1 keys |

### Mining & Monitoring

| Tool | Ethereum | RustChain |
|---|---|---|
| Mining | ASICs/GPUs/staking | Python miner scripts |
| Block Explorer | Etherscan | RustChain dashboard widgets |
| Monitoring | Tenderly/Alchemy | Custom Prometheus metrics |
| Node Software | Geth/Besu/Nethermind | RustChain node (Rust) |

---

## Wallet & Account Migration

### Same Cryptography, Different Chain

RustChain uses secp256k1 for account keys, the same curve as Ethereum. Your Ethereum addresses and keys are mathematically compatible.

**Important:** Best practice is to generate a fresh key for RustChain rather than reusing Ethereum private keys.

### Migration Steps

1. **Set up a miner identity** (your wallet/miner ID):

   ```bash
   # Clone the RustChain repo
   git clone https://github.com/Scottcjn/Rustchain.git
   cd Rustchain
   ```

2. **Start mining to earn RTC** (see Node & Miner Operation below)

3. **Check your balance**:

   ```bash
   curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_MINER_ID"
   ```

4. **If EVM-compatible layer exists**, configure your dApp frontend to connect to the RustChain RPC endpoint

---

## Node & Miner Operation

### From Geth/Parity to RustChain Miner

Unlike Ethereum's heavy node requirements, RustChain mining is lightweight:

```bash
# Linux miner
python3 miners/linux/rustchain_linux_miner.py --wallet YOUR_MINER_ID

# macOS miner
python3 miners/macos/rustchain_mac_miner_v2.4.py --wallet YOUR_MINER_ID --node https://50.28.86.131

# Windows miner (GUI)
python miners\windows\rustchain_windows_miner.py
```

### Key Differences from Ethereum Node Operation

| Setting | Geth/Parity | RustChain Miner |
|---|---|---|
| Hardware | Server-grade | Any real hardware |
| RAM | 8GB+ | < 32MB |
| Storage | 1TB+ SSD | Minimal |
| Network | High bandwidth | Low bandwidth |
| Setup Complexity | High | Low (Python script) |
| Consensus Participation | Stake 32 ETH or buy ASICs | Run miner on any device |

### Autostart Your Miner (Linux)

```bash
sudo tee /etc/systemd/system/rustchain-miner.service >/dev/null <<'UNIT'
[Unit]
Description=RustChain Miner
After=network.target

[Service]
Type=simple
User=YOUR_USERNAME
WorkingDirectory=/home/YOUR_USERNAME/Rustchain
ExecStart=/usr/bin/python3 miners/linux/rustchain_linux_miner.py --wallet YOUR_MINER_ID
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
UNIT

sudo systemctl enable rustchain-miner
sudo systemctl start rustchain-miner
```

### Verify Your Miner Is Working

```bash
# Download miner data
curl -sk https://50.28.86.131/api/miners > miners_data.json

# Check active miners
python3 -c "
import json
with open('miners_data.json', 'r') as f:
    miners = json.load(f)
print('active_miners:', len(miners))
"
```

---

## Network Configuration

### Current Node Endpoints

The RustChain network uses direct node endpoints. Check the official repository and documentation for current RPC URLs:

| Resource | URL |
|---|---|
| Main Repository | https://github.com/Scottcjn/Rustchain |
| Bounty Repository | https://github.com/Scottcjn/rustchain-bounties |
| Default Node | https://50.28.86.131 |

**Note:** Endpoint URLs may change. Always refer to the official RustChain repository for the latest configuration.

### Python SDK Configuration

```python
from rustchain_sdk import RustChainClient

client = RustChainClient(
    node_url="https://50.28.86.131",
)
```

### API Endpoints

```bash
# Check miner status
curl -sk https://50.28.86.131/api/miners

# Check wallet balance
curl -sk "https://50.28.86.131/wallet/balance?miner_id=YOUR_MINER_ID"
```

---

## Common Pitfalls

### 1. Assuming EVM Compatibility
**Problem:** Expecting all Ethereum tooling to work out of the box
**Fix:** RustChain has its own runtime. Check current documentation for EVM compatibility status before migrating contracts.

### 2. Using Hash-Power Mental Models
**Problem:** Thinking in terms of hash rate, difficulty, and mining pools
**Fix:** RustChain uses hardware attestation (Proof-of-Antiquity). Older hardware earns more, not less. There are no mining pools in the traditional sense.

### 3. Running Miners in VMs
**Problem:** VM-based miners may get penalized or denied rewards
**Fix:** Run the miner on real hardware. That is the entire point of RustChain.

### 4. Expecting Instant Finality Like PoA
**Problem:** Confusing Proof-of-Antiquity with traditional Proof-of-Authority
**Fix:** PoAn is hardware-attestation-based, not validator-approval-based. There are no pre-approved validators. Anyone with real hardware can participate.

### 5. Ignoring the E-Waste Mission
**Problem:** Building infrastructure that requires new, powerful hardware
**Fix:** Embrace the vintage hardware philosophy. RustChain rewards running on older, low-power devices.

### 6. Using Stale RPC Endpoints
**Problem:** Hardcoded RPC URLs that stop working
**Fix:** Use environment variables for all endpoint configuration and check the official repository for current URLs.

---

## FAQ

### Q: Can I use the same Solidity contracts?
**A:** Check the current RustChain documentation for EVM compatibility status. The chain is primarily Rust-based with its own runtime. Smart contract support may require adapter layers.

### Q: Do I need to learn Rust?
**A:** For dApp development, not necessarily. For contributing to the core protocol or building native modules, yes. The miner scripts are Python-based.

### Q: How do I earn RTC?
**A:** Run a RustChain miner on real hardware. Miners earn RTC through hardware attestation. The base reward is 1.5 RTC per epoch, distributed among active miners.

### Q: What hardware do I need to mine?
**A:** Any real hardware. Older and more exotic hardware earns higher rewards. A 2005 ThinkPad, a Pentium III, or even a Nintendo 64 can mine RTC.

### Q: How are rewards different from Ethereum?
**A:** Ethereum uses staking rewards (32 ETH to participate) or PoW mining (expensive hardware). RustChain rewards anyone with real hardware. There are no minimum stake requirements and no hardware arms race.

### Q: Is there a testnet?
**A:** Check the official RustChain repository and Discord for current testnet availability and faucet information.

### Q: Can I run multiple miners?
**A:** Each miner requires unique real hardware. Running multiple instances on the same machine does not increase rewards proportionally, as the attestation is hardware-based.

### Q: Where can I get help?
**A:** Join the RustChain community on Discord, star the repositories on GitHub, and check the documentation in the rustchain-bounties repository.

---

*Last updated: 2026-05*
