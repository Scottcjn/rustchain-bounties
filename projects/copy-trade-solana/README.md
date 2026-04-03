# Copy-Trade Bot (Solana) — MVP

Purpose: Internal test project to validate agent-driven delivery: end-to-end PoC for a copy-trade bot that listens to a source Solana address (or strategy), replicates trades to follower wallets with risk limits, and logs activity.

Scope (MVP):
- Connect to Solana testnet (RPC) and subscribe to a source account or program events
- Simulate/execute SPL token transfers/orders on testnet (no mainnet funds)
- Simple policy: copy market-sized trades, apply per-wallet risk caps
- CLI to run a dry-run and a live-run (requires keys)

Deliverables:
- README + TODO + PROOFS
- Basic TypeScript project with listener + executor + poster (for logging)
- Unit tests & demo script

