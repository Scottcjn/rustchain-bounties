# RustChain CLI Block Explorer

Query and explore the RustChain blockchain from the command line.

## Features

- 📦 **Block Viewer** — Inspect blocks by height, list recent blocks
- 💸 **Transaction Lookup** — View tx details, events, gas usage
- 👤 **Address Explorer** — Balance, account info, recent transactions
- 🏛️ **Validator Info** — Validator set, staking info, commission rates
- 🌐 **Network Peers** — Connected peers and node info
- 📋 **Governance** — Proposals and voting status
- 🔍 **Search** — Flexible transaction search with TM event syntax
- 🎨 **Colored Output** — Readable terminal output with colors

## Quick Start

```bash
python explorer.py status                          # Chain status
python explorer.py block latest                    # Latest block
python explorer.py block 1000                      # Block #1000
python explorer.py blocks --count 5                # Recent 5 blocks
python explorer.py tx ABC123DEF456...              # Transaction details
python explorer.py address rust1abc...             # Address info
python explorer.py validators                      # Validator list
python explorer.py peers                           # Network peers
python explorer.py proposals                       # Governance
python explorer.py supply                          # Token supply
python explorer.py search "transfer.sender='rust1...'"
```

## Configuration

```bash
# Custom RPC endpoint
python explorer.py --rpc https://my-rpc-node:26657 status

# Disable colors
python explorer.py --no-color status
```

## Commands

| Command | Description |
|---------|-------------|
| `status` | Blockchain status and sync info |
| `block` | Block details by height |
| `blocks` | List recent blocks |
| `tx` | Transaction details by hash |
| `address` | Address balance and info |
| `validators` | Validator set and staking |
| `peers` | Network peer connections |
| `proposals` | Governance proposals |
| `supply` | Token supply info |
| `search` | Search transactions |

## No Dependencies

Uses only Python standard library — no external packages required.

## License

MIT
