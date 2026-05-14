# RustChain Multi-Signature Wallet

Create and manage M-of-N multi-signature wallets for RustChain.

## Features

- 🔐 **M-of-N Threshold** - Flexible signature requirements
- 👥 **Multi-participant** - Support for any number of signers
- 📝 **Proposal Workflow** - Propose → Sign → Execute
- 💾 **Persistent State** - Wallet and proposals saved to JSON files
- 🔑 **Key Management** - Generate and manage participant key files

## Quick Start

```bash
# 1. Generate participant keys
python multisig.py keygen --label alice --output alice.json
python multisig.py keygen --label bob --output bob.json
python multisig.py keygen --label carol --output carol.json

# 2. Create 2-of-3 multisig wallet
python multisig.py create --name treasury --threshold 2 -p alice.json bob.json carol.json

# 3. Propose a transaction
python multisig.py propose --wallet treasury_multisig.json --to rust1xyz... --amount 1000000

# 4. Sign (need 2 of 3)
python multisig.py sign --proposal <id> --keyfile alice.json --wallet treasury_multisig.json
python multisig.py sign --proposal <id> --keyfile bob.json --wallet treasury_multisig.json

# 5. Execute when threshold met
python multisig.py execute --proposal <id> --wallet treasury_multisig.json
```

## Commands

| Command | Description |
|---------|-------------|
| `keygen` | Generate a participant key file |
| `create` | Create a multisig wallet |
| `propose` | Propose a transaction |
| `sign` | Sign a proposal |
| `execute` | Execute approved proposal |
| `list` | List all proposals |
| `status` | Show proposal details |
| `info` | Show wallet info |

## Workflow

```
Create Wallet → Propose TX → Participants Sign → Threshold Met → Execute
```

## License

MIT
