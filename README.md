# RustChain Protocol Documentation

> Complete technical documentation for the RustChain Proof-of-Antiquity blockchain.
> Earn RTC by contributing: https://github.com/Scottcjn/rustchain-bounties

## 📚 Documentation Index

| Document | Description |
|----------|-------------|
| [01_PROTOCOL_OVERVIEW.md](./docs/01_PROTOCOL_OVERVIEW.md) | Full protocol spec — RIP-200 consensus, hardware checks, token economics, architecture |
| [API_REFERENCE.md](./docs/API_REFERENCE.md) | Complete API reference with curl examples for all public endpoints |
| [GLOSSARY.md](./docs/GLOSSARY.md) | All terms and definitions |

## 🔑 Quick Facts

| Property | Value |
|----------|-------|
| Token | RTC (RustChain Token) |
| Consensus | RIP-200 Proof-of-Antiquity |
| Chain | RustChain + Ergo anchoring |
| Node | https://50.28.86.131 |
| Explorer | https://50.28.86.131/explorer |
| Version | 2.2.1-rip200 |
| GitHub Bounties | [rustchain-bounties](https://github.com/Scottcjn/rustchain-bounties) |

## ⚡ Quick Start

```bash
# Check node health
curl -sk https://50.28.86.131/health

# List active miners
curl -sk https://50.28.86.131/api/miners | python3 -m json.tool

# See live network stats
curl -sk https://50.28.86.131/api/miners | \
  python3 -c "import json,sys; data=json.load(sys.stdin); \
  print(f'Active miners: {len(data[\"miners\"])}')"
```

## 📂 For Developers

### Clone the docs repo
```bash
git clone https://github.com/Scottcjn/rustchain-bounties.git
```

### Run the API examples
```bash
# Get node health
curl -sk https://50.28.86.131/health

# Get miner list sorted by antiquity
curl -sk https://50.28.86.131/api/miners
```

## 🤝 Contributing

Found an error or want to improve these docs?
→ Open an issue at https://github.com/Scottcjn/rustchain-bounties/issues
→ Or submit a PR directly to this repo

## 📊 Live Network

```
Current miners:  13
Attestation nodes: 3
Protocol version: 2.2.1-rip200
```

*Data fetched live from the RustChain node on 2026-04-09.*
