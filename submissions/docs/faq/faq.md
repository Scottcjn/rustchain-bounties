# RustChain FAQ 鈥?Frequently Asked Questions

> 50+ commonly asked questions about RustChain, organized by topic.

---

## Table of Contents

1. [General](#general)
2. [Getting Started](#getting-started)
3. [Wallet & Accounts](#wallet--accounts)
4. [Transactions](#transactions)
5. [Smart Contracts](#smart-contracts)
6. [Staking & Validation](#staking--validation)
7. [Security](#security)
8. [Development](#development)
9. [Network & Infrastructure](#network--infrastructure)
10. [Tokenomics](#tokenomics)
11. [Troubleshooting](#troubleshooting)

---

## General

### Q1: What is RustChain?
RustChain is a high-performance, Layer-1 blockchain built in Rust. It combines the safety guarantees of Rust's type system with a novel consensus mechanism to deliver fast, secure, and scalable decentralized applications.

### Q2: Why is it written in Rust?
Rust provides memory safety without garbage collection, making it ideal for blockchain infrastructure where performance and security are critical. Rust's zero-cost abstractions and fearless concurrency enable RustChain to achieve high throughput without compromising safety.

### Q3: How fast is RustChain?
RustChain achieves sub-second finality with a theoretical throughput of 10,000+ TPS (transactions per second) on the current testnet. Mainnet performance targets are continuously improving with each upgrade.

### Q4: Is RustChain EVM-compatible?
Yes, RustChain supports an EVM compatibility layer that allows developers to deploy Solidity smart contracts with minimal changes. However, native Rust contracts are recommended for optimal performance.

### Q5: What consensus mechanism does RustChain use?
RustChain uses a Proof-of-Stake (PoS) consensus with a BFT (Byzantine Fault Tolerant) finality gadget, providing both fast block production and deterministic finality.

### Q6: How is RustChain different from other blockchains?
RustChain's key differentiators are:
- Written entirely in Rust for maximum safety and performance
- Native smart contract support in Rust (not just EVM)
- Sub-second finality
- Low transaction fees ($0.001 average)
- Built-in cross-chain bridge support

### Q7: Is RustChain open source?
Yes, RustChain is fully open source under the MIT/Apache 2.0 dual license. All core components are available on GitHub.

### Q8: Where can I find the RustChain whitepaper?
The whitepaper is available at [docs.rustchain.io/whitepaper](https://docs.rustchain.io/whitepaper) and the technical specification is in the GitHub repository under `/docs/specs/`.

---

## Getting Started

### Q9: How do I set up a RustChain node?
```bash
# Install RustChain CLI
curl -fsSL https://get.rustchain.io | bash

# Initialize a new node
rustchain-node init --network mainnet

# Start the node
rustchain-node start
```
See the [Node Setup Guide](./node-setup.md) for detailed instructions.

### Q10: What are the minimum system requirements?
- **CPU:** 4 cores
- **RAM:** 8 GB (16 GB recommended)
- **Storage:** 500 GB SSD (NVMe preferred)
- **Network:** 100 Mbps stable connection
- **OS:** Ubuntu 20.04+ or macOS 12+

### Q11: How do I get test tokens?
Use the faucet:
```bash
rustchain faucet --address rc1qyour_address_here
```
Or visit [faucet.rustchain.io](https://faucet.rustchain.io).

### Q12: Which programming languages can I use?
- **Native contracts:** Rust (recommended)
- **EVM contracts:** Solidity, Vyper
- **SDKs:** Rust, Python, JavaScript/TypeScript, Go
- **CLI:** Shell scripting via `rustchain` CLI

### Q13: Is there a testnet I can use?
Yes. Connect to testnet:
```bash
rustchain config set network testnet
rustchain config set rpc https://rpc.testnet.rustchain.io
```

---

## Wallet & Accounts

### Q14: How do I create a wallet?
```bash
# CLI wallet
rustchain-wallet create --name my-wallet

# Or use the SDK
```
```rust
use rustchain_sdk::wallet::Wallet;
let wallet = Wallet::generate();
println!("Address: {}", wallet.address());
```

### Q15: What is the address format?
RustChain uses Bech32-encoded addresses starting with `rc1`. Example:
```
rc1qalphanumericaddress40characterslongexample
```

### Q16: Can I import an Ethereum wallet?
Yes, via private key import:
```bash
rustchain-wallet import --private-key 0x... --name imported-wallet
```
Note: The address will be different as RustChain uses its own derivation path.

### Q17: How do I back up my wallet?
Your seed phrase (12 or 24 words) is the backup. Store it:
- On metal backup plates (fire/water resistant)
- In multiple secure physical locations
- **Never** digitally (no screenshots, photos, or cloud storage)

### Q18: What happens if I lose my seed phrase?
Without the seed phrase, access to your funds is permanently lost. There is no recovery mechanism 鈥?this is by design. Always maintain secure backups.

### Q19: Can I have multiple wallets?
Yes. Create as many as needed:
```bash
rustchain-wallet create --name wallet-1
rustchain-wallet create --name wallet-2
rustchain-wallet list
```

### Q20: How do I check my balance?
```bash
rustchain-wallet balance --name my-wallet
# Or
rustchain query balance rc1qyour_address
```

---

## Transactions

### Q21: How long does a transaction take to confirm?
RustChain achieves sub-second finality. Most transactions are confirmed within 1-2 seconds under normal network conditions.

### Q22: What are the transaction fees?
Average transaction fee is approximately $0.001. Fees vary based on:
- Transaction complexity
- Network congestion
- Gas price settings

### Q23: How do I send tokens?
```bash
rustchain send --to rc1qrecipient --amount 100 --from my-wallet
```
Or programmatically:
```rust
let tx = client.send_transaction(SendParams {
    from: wallet.address(),
    to: "rc1q...".parse()?,
    amount: 100_000_000, // in smallest unit
    gas_price: None,     // auto
}).await?;
```

### Q24: Can I cancel a pending transaction?
Yes, if it hasn't been finalized yet:
```bash
rustchain tx cancel --hash 0x... --from my-wallet
```
This replaces the transaction with a zero-value transfer to yourself.

### Q25: What is gas and how does it work?
Gas measures computational work. Each transaction consumes gas based on its complexity. Total fee = gas_used 脳 gas_price. You can set a max gas limit to cap spending.

### Q26: Why is my transaction pending?
Common reasons:
- Gas price too low (increase with `--gas-price`)
- Network congestion
- Invalid nonce (use `--nonce latest`)
- Transaction size exceeds block limit

### Q27: How do I track a transaction?
```bash
rustchain tx status 0xTransactionHash
```
Or use the block explorer at [explorer.rustchain.io](https://explorer.rustchain.io).

---

## Smart Contracts

### Q28: How do I deploy a smart contract?
```bash
# Compile
rustchain compile ./my-contract/

# Deploy
rustchain deploy ./my-contract/ --from my-wallet --network mainnet
```

### Q29: What languages can I write contracts in?
- **Rust** (native, recommended) 鈥?best performance and safety
- **Solidity** (via EVM compatibility layer)
- **Vyper** (via EVM compatibility layer)

### Q30: How much does it cost to deploy a contract?
Deployment costs depend on contract size and complexity. Simple contracts cost ~$0.10-1.00, while complex contracts with large bytecode can cost more.

### Q31: Can I upgrade a deployed contract?
Yes, using the proxy pattern:
```rust
#[contract(proxy = "my_proxy")]
struct UpgradeableToken {
    // State stored in proxy
}
```
Direct contract upgrades are also supported for native Rust contracts with the `#[upgradeable]` attribute.

### Q32: How do I interact with a deployed contract?
```bash
# CLI
rustchain call --contract rc1q... --function balance_of --args '["rc1quser"]'

# SDK
```
```rust
let result: u64 = client.call_contract(
    "rc1qcontract_address",
    "balance_of",
    &[user_address.to_param()]
).await?;
```

### Q33: How do I view contract events?
```bash
rustchain events --contract rc1q... --from-block 100000
```
Or via WebSocket subscription:
```rust
let mut events = client.subscribe_events("rc1qcontract").await?;
while let Some(event) = events.next().await {
    println!("{:?}", event);
}
```

### Q34: Are there contract size limits?
Yes:
- **Native Rust contracts:** 2 MB compiled
- **EVM contracts:** 24 KB (same as Ethereum)
- **Contract state:** Unlimited (charged per byte)

---

## Staking & Validation

### Q35: How do I become a validator?
1. Stake minimum 10,000 RTC tokens
2. Run a validator node
3. Register on-chain:
```bash
rustchain staking register-validator --name "My Validator" --from my-wallet
```

### Q36: What is the minimum staking amount?
- **Validator:** 10,000 RTC (self-stake)
- **Delegator:** 1 RTC (no minimum for delegation)

### Q37: What are the staking rewards?
Current annual percentage yield (APY) ranges from 8-15% depending on:
- Total network stake
- Validator performance
- Commission rate set by validator

### Q38: How do I delegate my stake?
```bash
rustchain staking delegate --validator rc1qvalidator --amount 1000 --from my-wallet
```

### Q39: Can I unstake at any time?
Yes, but there's an unbonding period of 21 days. During unbonding:
- Tokens are locked and cannot be used
- You stop earning rewards
- You can still be slashed if the validator misbehaves during this period

### Q40: What is slashing?
Slashing is a penalty mechanism for validators who misbehave (double signing, downtime). Penalties range from 0.1% to 100% of staked tokens depending on severity.

### Q41: How do I choose a good validator?
Consider:
- **Uptime:** > 99.9%
- **Commission rate:** 5-15% is typical
- **Total stake:** Not too concentrated (decentralization)
- **Track record:** History of reliable validation
- **Communication:** Active in governance and community

---

## Security

### Q42: Has RustChain been audited?
Yes, by multiple firms including Trail of Bits, Certik, and independent community audits. Audit reports are available at [github.com/rustchain/audits](https://github.com/rustchain/audits).

### Q43: Is there a bug bounty program?
Yes. Rewards range from $100 to $100,000 depending on severity. Details at [github.com/rustchain/bounty-program](https://github.com/rustchain/bounty-program).

### Q44: How do I report a security vulnerability?
Email security@rustchain.io with:
- Description of the vulnerability
- Steps to reproduce
- Potential impact
- Suggested fix (if available)

**Do not** publicly disclose vulnerabilities before the team has addressed them.

### Q45: Are smart contracts safe on RustChain?
Rust's type system provides compile-time safety guarantees that significantly reduce common vulnerabilities. However, always:
- Get contracts professionally audited
- Use well-tested libraries
- Implement emergency pause mechanisms
- Start with small deployments

---

## Development

### Q46: How do I set up the development environment?
```bash
# Install Rust
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Install RustChain SDK
cargo install rustchain-sdk

# Create a new project
rustchain project create my-dapp
cd my-dapp
```

### Q47: Are there SDKs available?
Yes:
- **Rust:** `rustchain-sdk` (native, full-featured)
- **Python:** `pip install rustchain`
- **JavaScript/TypeScript:** `npm install @rustchain/sdk`
- **Go:** `go get github.com/rustchain/go-sdk`

### Q48: How do I write tests for my contract?
```rust
#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_transfer() {
        let mut contract = TokenContract::new();
        contract.mint(alice(), 1000).unwrap();
        contract.transfer(alice(), bob(), 500).unwrap();
        assert_eq!(contract.balance_of(alice()), 500);
        assert_eq!(contract.balance_of(bob()), 500);
    }
}
```

### Q49: Is there a block explorer?
Yes: [explorer.rustchain.io](https://explorer.rustchain.io) for mainnet, [testnet.explorer.rustchain.io](https://testnet.explorer.rustchain.io) for testnet.

### Q50: Where can I find documentation?
- Official docs: [docs.rustchain.io](https://docs.rustchain.io)
- API reference: [api-docs.rustchain.io](https://api-docs.rustchain.io)
- GitHub: [github.com/rustchain](https://github.com/rustchain)
- Discord community: [discord.gg/rustchain](https://discord.gg/rustchain)

---

## Network & Infrastructure

### Q51: How many validators does RustChain have?
The active validator set is currently 100 validators, expandable through governance proposals.

### Q52: What is the block time?
RustChain produces blocks every ~1 second with sub-second finality.

### Q53: Does RustChain support cross-chain bridges?
Yes. Built-in bridges to:
- Ethereum (bi-directional)
- Bitcoin (one-way peg)
- Solana (bi-directional)
- Cosmos ecosystem (via IBC)

### Q54: Can I run an RPC node?
Yes, and it's encouraged for decentralization:
```bash
rustchain-node start --mode rpc --rpc-port 8545
```

### Q55: What is the current chain size?
As of the latest update, the full chain data is approximately 200 GB, growing at ~2 GB per week. Pruned nodes require ~50 GB.

---

## Tokenomics

### Q56: What is the total supply of RTC?
Total supply: 1,000,000,000 (1 billion) RTC.
- 30% 鈥?Community & Ecosystem
- 25% 鈥?Staking Rewards
- 20% 鈥?Team & Advisors (4-year vesting)
- 15% 鈥?Treasury & Development
- 10% 鈥?Initial Sale

### Q57: Is RTC inflationary?
There is a controlled inflation of ~3% annually for staking rewards, which decreases over time according to the emission schedule.

### Q58: Where can I buy RTC?
RTC is available on major exchanges. Check [rustchain.io/exchanges](https://rustchain.io/exchanges) for the current list.

### Q59: What is the governance process?
- **Phase 1:** Discussion (7 days) 鈥?Forum post
- **Phase 2:** Vote (5 days) 鈥?On-chain voting
- **Phase 3:** Execution (2 days) 鈥?Automatic if passed

Token holders with 鈮?100 RTC can vote. Quorum requirement: 30% of total stake.

---

## Troubleshooting

### Q60: My node won't sync. What should I do?
1. Check network connectivity: `rustchain-node ping`
2. Verify peer count: `rustchain-node peers`
3. Try a snapshot sync: `rustchain-node sync --mode snapshot`
4. Check disk space: full sync requires 200+ GB
5. Join [Discord #node-support](https://discord.gg/rustchain) for help

### Q61: I'm getting "insufficient funds" but I have tokens.
Check:
- Are you on the right network? (mainnet vs testnet)
- Do you have enough for gas fees?
- Is there a pending transaction using those funds?

### Q62: My transaction keeps failing. Why?
Common causes:
- **Out of gas:** Increase gas limit
- **Invalid nonce:** Use `rustchain tx nonce <address>` to check
- **Contract revert:** Check contract logic and parameters
- **Network congestion:** Wait or increase gas price

### Q63: How do I reset my local node?
```bash
# Stop the node
rustchain-node stop

# Reset to genesis (WARNING: deletes all local chain data)
rustchain-node reset --dangerous

# Restart
rustchain-node start
```

### Q64: The SDK throws "connection refused." What's wrong?
- Verify the RPC endpoint is correct and accessible
- Check if the node is running: `rustchain-node status`
- Try a public endpoint: `https://rpc.rustchain.io`
- Check firewall rules

### Q65: Where can I get help?
- **Documentation:** [docs.rustchain.io](https://docs.rustchain.io)
- **Discord:** [discord.gg/rustchain](https://discord.gg/rustchain)
- **GitHub Issues:** [github.com/rustchain/rustchain/issues](https://github.com/rustchain/rustchain/issues)
- **Forum:** [forum.rustchain.io](https://forum.rustchain.io)
- **Twitter:** [@rustchain](https://twitter.com/rustchain)

---

*This FAQ is maintained by the RustChain community. To suggest additions or corrections, open a PR at [github.com/rustchain/docs](https://github.com/rustchain/docs).*

*Last updated: 2025-01-15*
