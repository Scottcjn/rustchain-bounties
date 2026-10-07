# Architecture

## Overview

Rustchain follows a layered architecture:

1. **Consensus Layer** — Tendermint-like BFT consensus
2. **State Layer** — Merkle Patricia Trie state root
3. **Network Layer** — Libp2p-based P2P networking
4. **VM Layer** — EVM-compatible execution engine

## Module Diagram

```
┌─────────────────────┐
│     Application     │
├─────────────────────┤
│        VM           │
├─────────────────────┤
│      State          │
├─────────────────────┤
│    Consensus        │
├─────────────────────┤
│     Network         │
└─────────────────────┘
```

## Related Docs

- [Mining Guide](./mining.md)
- [Tokenomics](./tokenomics.md)
