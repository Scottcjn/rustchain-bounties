# RustChain Offline Transaction Signer

A secure offline transaction signing tool for RustChain with cold wallet support.

## Features

- 🔐 **Offline Signing** - Sign transactions without network access
- ❄️ **Cold Wallet Support** - Create and manage air-gapped wallets
- 🔑 **HD Key Derivation** - BIP-44 compatible key derivation
- 📝 **PSBT-like Workflow** - Transfer unsigned/signed transactions via files
- ✅ **Transaction Verification** - Verify signatures before broadcast

## Cold Wallet Workflow

```
1. OFFLINE: Generate cold wallet
   $ python signer.py generate -o cold_wallet.json

2. ONLINE:  Export public info for receiving
   $ python signer.py address -k cold_wallet.json

3. ONLINE:  Create unsigned transaction
   $ python signer.py create-tx --from rust1abc... --to rust1xyz... --amount 1000000

4. OFFLINE: Sign with cold wallet
   $ python signer.py sign unsigned_tx_123.json -k cold_wallet.json

5. ONLINE:  Verify and broadcast
   $ python signer.py verify unsigned_tx_123_signed.json
   $ python signer.py broadcast unsigned_tx_123_signed.json
```

## Commands

| Command | Description |
|---------|-------------|
| `generate` | Generate a new cold wallet keypair |
| `create-tx` | Create an unsigned transaction |
| `sign` | Sign a transaction with cold wallet |
| `verify` | Verify a signed transaction |
| `broadcast` | Prepare signed tx for network broadcast |
| `derive` | Derive key at HD path |
| `address` | Show wallet address |

## Security

- Private keys never touch networked devices
- All signing happens offline
- Mnemonic phrases are never transmitted
- File-based PSBT-like workflow for air-gapped security

## Wallet File Format

```json
{
  "mnemonic": "...",
  "derivation_path": "m/44'/606'/0'/0/0",
  "public_key": "...",
  "address": "rust1...",
  "chain": "rustchain",
  "wallet_type": "cold"
}
```

## License

MIT
