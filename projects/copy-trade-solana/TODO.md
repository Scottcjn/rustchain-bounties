TODO — Copy-Trade Bot (MVP)

[x] 1) Research Solana RPC + program events for trades
[x] 2) Design copy policy (min trade size, slippage, risk limits)
[x] 3) Implement listener (testnet)
[x] 4) Implement executor (wallet signing + transaction submit)
[x] 5) Add dry-run mode and demo script
[ ] 6) Add logging/poster to Dashboard/Discord
[x] 7) Tests + PROOFS + PR

Sprint-2 additions:
[x] 8) Implement policy.ts (minTradeLamports, maxPerWalletLamports, slippagePct, shouldCopy)
[x] 9) Update executor.ts — devnet airdrop funding, ephemeral keypairs, policy integration
[x] 10) Create demo-run.ts — 3 follower keypairs, 3 mirrored trades, PROOFS.md output
[x] 11) Policy unit tests (6 test cases)
[x] 12) End-to-end devnet demo (dry-run fallback confirmed)
