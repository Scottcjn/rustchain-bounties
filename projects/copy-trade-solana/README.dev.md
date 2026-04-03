# Developer Notes — Copy-Trade Bot (Solana)

## Quick start

```bash
npm install
npm run demo          # dry-run, no keys needed
npm test              # run unit tests
```

## Environment variables (.env)

Create a `.env` file in the project root for live mode:

```env
# Solana JSON-RPC endpoint (devnet recommended for testing)
RPC_URL=https://api.devnet.solana.com

# Public key of the wallet to copy trades from
SOURCE_PUBKEY=<base58 pubkey>

# Path to the follower wallet keypair JSON (solana-keygen output)
KEYPAIR_PATH=./my-wallet.json
```

### Generating a devnet keypair

```bash
solana-keygen new --outfile ./my-wallet.json --no-bip39-passphrase
solana airdrop 2 $(solana-keygen pubkey ./my-wallet.json) --url devnet
```

## Commands

| Command | Description |
|---------|-------------|
| `npm run demo` | Simulates a trade and runs executor in dry-run mode |
| `npm start` | Starts live listener + executor (requires .env) |
| `npm test` | Runs Jest unit tests |

## Architecture (sprint-1)

```
src/
  types.ts       — Trade and BotConfig interfaces
  listener.ts    — TradeListener: subscribes to source wallet via RPC
  executor.ts    — Executor: signs and submits mirrored transactions
  index.ts       — CLI entry point (demo / start)
  __tests__/     — Jest unit tests with mock RPC data
```

## What's NOT implemented yet (sprint-2+)

- SPL token copy-trades (only native SOL for now)
- Risk limits / per-wallet caps
- Slippage protection / priority fees
- Discord / dashboard logging
- Mainnet support (currently devnet only)
