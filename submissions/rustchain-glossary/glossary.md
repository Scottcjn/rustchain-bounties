# RustChain Glossary

A comprehensive reference of all RustChain terminology, organized alphabetically.

---

## A

### API Node
A full node configured to expose RPC endpoints for external applications. API nodes serve blockchain data to wallets, explorers, and dApps.

### Address
A unique identifier on the RustChain network derived from a public key. RustChain addresses follow a specific encoding scheme and are used to send and receive RTC tokens.

### Block
A data structure containing a batch of validated transactions, a reference to the previous block, and consensus metadata. Blocks are the fundamental units of the RustChain blockchain.

### Block Explorer
A web application that allows users to browse blocks, transactions, addresses, and other blockchain data. RustChain's built-in explorer provides real-time visibility into network activity.

---

## B

### Beacon
The consensus coordination mechanism in RustChain. The Beacon module is responsible for proposing block producers, managing validator sets, and coordinating the transition between Epochs. It ensures that only authorized validators participate in block production during each Epoch.

### BCOS
**Blockchain Operating System** — the underlying framework that RustChain builds upon. BCOS provides modular blockchain infrastructure including consensus, storage, and networking layers. RustChain extends BCOS with Rust-based performance optimizations and additional protocol features.

### BoTTube
A decentralized video platform built on the RustChain ecosystem. BoTTube enables content creators to publish, share, and monetize video content without centralized intermediaries. Content is stored on distributed storage, and creator rewards are distributed via smart contracts on RustChain.

---

## C

### Consensus
The mechanism by which nodes in the RustChain network agree on the state of the blockchain. RustChain uses Proof of Authority (PoA) consensus, where a known set of validators take turns producing blocks.

### CLI (Command Line Interface)
The `rustchain-cli` tool for interacting with a RustChain node from the terminal. Supports wallet management, transaction signing, node configuration, and query operations.

---

## D

### dApp
Decentralized application — an application whose backend logic runs on smart contracts deployed on RustChain, rather than on centralized servers.

### Delegator
A token holder who stakes RTC tokens to support a validator. Delegators earn a share of block rewards proportional to their stake.

---

## E

### Epoch
A defined time period in RustChain's consensus mechanism during which a specific set of validators is authorized to produce blocks. Each Epoch has a fixed duration measured in blocks. At the end of an Epoch, the Beacon module re-evaluates the validator set and may rotate validators for the next Epoch.

### Epoch Explorer
A tool for visualizing and inspecting Epoch-related data, including validator assignments, block production statistics, and Epoch transitions.

### EVM Compatibility
RustChain's ability to execute Ethereum-compatible smart contracts. Developers can deploy Solidity contracts and use familiar Ethereum tooling (MetaMask, Hardhat, Remix) with minimal modifications.

---

## F

### Faucet
A service that distributes small amounts of RTC tokens to new users for testing and development purposes. Typically used on testnets.

### Finality
The point at which a block and its transactions are considered irreversible. Under PoA consensus, RustChain achieves fast finality once supermajority validators have confirmed a block.

---

## G

### Gas
A unit of computational effort used to price transaction execution on RustChain. Each operation in a smart contract consumes a specific amount of gas, paid in RTC.

### Gas Price
The amount of RTC a user is willing to pay per unit of gas. Higher gas prices incentivize faster transaction inclusion.

### Genesis Block
The first block in the RustChain blockchain. It contains the initial state, validator set, token distribution, and chain configuration parameters.

---

## H

### Hard Fork
A protocol upgrade that introduces changes incompatible with previous versions. All nodes must upgrade to continue participating in the network.

### Hash
A fixed-length cryptographic digest produced by applying a hash function (e.g., SHA-256, Keccak-256) to data. Hashes are used extensively for block linking, transaction identification, and Merkle tree construction.

---

## I

### Integration Test
End-to-end tests that verify the interaction between multiple RustChain components (consensus, networking, storage, RPC) in a realistic network environment.

---

## J

### JSON-RPC
The remote procedure call protocol used by RustChain nodes to expose blockchain data and transaction submission endpoints. All API interactions use JSON-RPC over HTTP or WebSocket.

---

## K

### Keystore
An encrypted file containing a user's private key, protected by a password. RustChain wallets use keystore files for secure key management.

---

## L

### Light Client
A node that downloads only block headers and verifies proofs, rather than the full blockchain state. Useful for resource-constrained devices.

### Liquidity Pool
A smart contract that holds reserves of two or more tokens and enables automated trading. RustChain supports liquidity pools through its EVM-compatible smart contracts.

---

## M

### Mainnet
The primary RustChain production network where RTC tokens have real economic value. Contrast with Testnet.

### Merkle Tree
A tree data structure where each leaf is a hash of a data block, and each parent node is a hash of its children. Used in RustChain for efficient transaction and state verification.

### Miner
In RustChain's PoA context, an authorized validator who produces blocks. Unlike PoW mining, PoA miners are pre-approved and do not compete using computational power.

### Mining Monitor
A dashboard tool for tracking validator performance, block production rates, and node health in real-time.

---

## N

### Node
A computer running the RustChain client software connected to the network. Nodes can be validators (producing blocks), API nodes (serving data), or full nodes (syncing and verifying the chain).

### Nonce
A sequential number associated with each address representing the number of transactions sent from that address. Used to prevent replay attacks and ensure transaction ordering.

---

## O

### Oracle
A service that provides external (off-chain) data to smart contracts on RustChain. Oracles enable dApps to interact with real-world data such as price feeds, weather, or event outcomes.

---

## P

### Peer-to-Peer (P2P)
The networking model used by RustChain, where nodes communicate directly with each other without a central server.

### PoA (Proof of Authority)
RustChain's consensus algorithm. In PoA, a set of trusted validators take turns producing blocks. Validators are identified by their staked identity and reputation. Key properties:
- **Fast finality** — blocks are confirmed quickly
- **Energy efficient** — no computational mining
- **Permissioned validation** — validators are known entities
- **Deterministic block production** — validators follow a fixed schedule

### Private Key
A secret cryptographic key used to sign transactions and prove ownership of an address. Must never be shared.

### Public Key
Derived from the private key, the public key is used to generate addresses and verify transaction signatures.

---

## Q

### QR Wallet
A RustChain wallet feature that generates QR codes for address sharing and payment requests, enabling easy mobile transfers.

---

## R

### RPC (Remote Procedure Call)
The API interface exposed by RustChain nodes for programmatic interaction. Includes methods for querying chain state, sending transactions, and managing subscriptions.

### RTC
The native cryptocurrency of the RustChain network. RTC is used for:
- Transaction gas fees
- Staking as a validator or delegator
- Smart contract deployment
- Governance participation
- Rewards for block production

### RustChain
A high-performance, EVM-compatible blockchain built with Rust and based on the BCOS framework. RustChain combines the safety and speed of Rust with proven blockchain architecture to deliver fast, reliable, and developer-friendly infrastructure.

---

## S

### SDK (Software Development Kit)
Libraries and tools provided for developers to build applications on RustChain. Available in multiple languages including Python, JavaScript, and Rust.

### Smart Contract
Self-executing code deployed on the RustChain blockchain. Smart contracts automatically enforce their terms when conditions are met. RustChain supports Solidity-based contracts through its EVM compatibility layer.

### Staking
The process of locking RTC tokens as collateral to become a validator or to delegate to one. Staking secures the network and earns rewards.

### State
The current snapshot of all account balances, contract storage, and other on-chain data at a given block height.

### Sync
The process by which a node downloads and validates the blockchain from the genesis block to the current head, establishing an up-to-date state.

---

## T

### Testnet
A parallel RustChain network used for development and testing. Testnet RTC has no real value and is available through faucets.

### Token
A digital asset on the RustChain blockchain. RTC is the native token; additional tokens can be created via smart contracts (e.g., ERC-20 compatible tokens).

### Transaction
A signed data structure that represents a state change on RustChain. Types include value transfers, contract calls, contract deployments, and staking operations.

### Transaction Explorer
A tool for searching and inspecting individual transactions, showing sender, receiver, value, gas used, and execution logs.

---

## U

### Upgrade
A planned modification to the RustChain protocol or node software. Upgrades may include hard forks, soft forks, or simple client updates.

---

## V

### Validator
An authorized participant in RustChain's PoA consensus. Validators produce blocks, validate transactions, and earn RTC rewards. Validators must stake tokens and maintain high availability and reliability.

### Validator Set
The current group of validators authorized to produce blocks during an Epoch. The validator set is determined by the Beacon module and may change between Epochs.

---

## W

### Wallet
Software for managing RTC tokens, signing transactions, and interacting with RustChain dApps. RustChain supports browser-based wallets (MetaMask compatible), CLI wallets, and mobile wallets with QR functionality.

### WebSocket
A persistent connection protocol used for real-time blockchain event subscriptions. RustChain nodes support WebSocket connections for live event streaming, new block notifications, and pending transaction monitoring.

---

## X

### xRTC
A wrapped or bridged version of RTC used in cross-chain operations. xRTC enables RTC to be used on other blockchain networks through bridge protocols.

---

## Y

### Yield
The annualized return earned by staking RTC tokens, expressed as a percentage of the staked amount. Yield comes from block rewards and transaction fees distributed to validators and delegators.

---

## Z

### Zero-Knowledge Proof (ZKP)
A cryptographic method by which one party can prove knowledge of a fact without revealing the fact itself. RustChain's roadmap includes ZKP support for privacy-enhanced transactions and scalable verification.

---

*Last updated: 2025-05*
