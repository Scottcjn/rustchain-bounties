# Track B — wRTC on Base (RIP-305)

Production ERC-20: **6 decimals**, **ERC20Burnable**, **ERC20Permit** (EIP-2612), **Pausable**, **AccessControl** (`DEFAULT_ADMIN_ROLE`, `MINTER_ROLE`, `PAUSER_ROLE`), **20,000 wRTC cumulative mint cap**.

## Features

| Feature | Purpose |
|---------|---------|
| **6 decimals** | Matches native RTC precision |
| **Mint cap (20k)** | Enforces RIP-305 Base allocation; `totalMinted` is cumulative (burns don't reduce it) |
| **AccessControl** | `DEFAULT_ADMIN_ROLE` (multisig), `MINTER_ROLE` (bridge), `PAUSER_ROLE` (ops) |
| **Pausable** | Emergency freeze — admin/pauser can halt all transfers, mints, burns |
| **ERC20Permit** | Gasless approvals via EIP-2612 signatures (critical for L2 UX) |
| **ERC20Burnable** | Users and bridge can burn tokens for cross-chain release |

## Quick Start

```bash
cd contracts
cp .env.example .env   # edit .env — never commit secrets
npm install
npx hardhat test       # 11 tests, all green
```

## Deploy

### 1. Environment

| Variable | Required | Purpose |
|----------|----------|---------|
| `DEPLOYER_PRIVATE_KEY` | Yes | EOA that pays gas (0x + 64 hex) |
| `ETHERSCAN_API_KEY` | For verify | [etherscan.io/myapikey](https://etherscan.io/myapikey) — V2 multichain key |
| `BRIDGE_MINTER_ADDRESS` | Recommended | Receives `MINTER_ROLE` |
| `MULTISIG_ADDRESS` | Recommended | Receives `DEFAULT_ADMIN_ROLE` + `PAUSER_ROLE`; deployer renounces |

### 2. Deploy + Auto-Verify

```bash
npx hardhat run scripts/deploy.ts --network baseSepolia
```

The script deploys, hands over roles (if env vars set), saves a JSON artifact to `deployments/`, and automatically verifies on BaseScan (waits 15s for indexing).

### 3. Verify (Sourcify — no API key needed)

Sourcify is enabled by default and verifies automatically during deploy. It also works standalone:

```bash
npx hardhat verify --network baseSepolia <CONTRACT_ADDRESS> "<DEPLOYER_EOA>"
```

BaseScan imports Sourcify verification automatically. For direct BaseScan verification, set `BASESCAN_API_KEY` in `.env` (create at [basescan.org/myapikey](https://basescan.org/myapikey)).

### 4. Role Handover (if not done at deploy)

```bash
# Set in .env: WRTC_ADDRESS, BRIDGE_MINTER_ADDRESS, MULTISIG_ADDRESS
npx hardhat run scripts/handover-roles.ts --network baseSepolia
```

End state:
- **Multisig** → `DEFAULT_ADMIN_ROLE` + `PAUSER_ROLE`
- **Bridge** → `MINTER_ROLE`
- **Deployer** → no roles

### 5. Mainnet

Same flow with `--network base`. Chain ID **8453**. Fund deployer on Base mainnet first.

## Technical Details

- **Solidity** 0.8.28 (Cancun EVM — required for OpenZeppelin 5.x)
- **OpenZeppelin** 5.x (ERC20, ERC20Burnable, ERC20Permit, Pausable, AccessControl)
- **Hardhat** 2.28+ with toolbox 6.x
- **Etherscan V2 API** — single string apiKey, auto-routes to Base via chainId

## Troubleshooting

| Error | Fix |
|-------|-----|
| `Invalid API Key … BASE1-` | Your `ETHERSCAN_API_KEY` is invalid. Create new key at [etherscan.io/myapikey](https://etherscan.io/myapikey) |
| `mcopy instruction` error | Set `evmVersion: "cancun"` in hardhat config (already done) |
| No deployer account | Set `DEPLOYER_PRIVATE_KEY` in `.env` with `0x` prefix |
| Verify fails repeatedly | Use [VERIFY-MANUAL.md](VERIFY-MANUAL.md) — paste Standard JSON Input on BaseScan |

## Security

- **Multisig** for `DEFAULT_ADMIN_ROLE` — never leave admin on a hot EOA in production
- **Vault/KMS** for relayer keys — never in repo
- **Pausable** gives incident response capability without needing to redeploy
- **ERC20Permit** — no separate approve tx needed, reduces phishing surface
