# 🔐 RustChain Wallet Recovery Tool

Recover cryptocurrency wallet addresses from mnemonic seed phrases. Supports multi-coin address derivation with BIP32/BIP44 standard paths.

## Features

- **Multi-coin support**: RTC, BTC, ETH, SOL, ATOM
- **BIP39 mnemonic**: 12/15/18/21/24 word phrases
- **BIP32/BIP44 derivation**: Standard HD wallet paths
- **Multiple addresses**: Derive multiple addresses per coin
- **Export**: Save recovered addresses to file
- **Interactive mode**: Step-by-step guided recovery
- **File input**: Read mnemonic from file

## Quick Start

```bash
# From mnemonic phrase
python recover.py "word1 word2 word3 ... word12"

# Interactive mode
python recover.py --interactive

# From file, specific coins
python recover.py --file mnemonic.txt --coins rtc,btc,eth

# Export results
python recover.py "mnemonic words..." --export wallet.txt

# Multiple addresses
python recover.py "mnemonic words..." --count 10
```

## Supported Coins

| Symbol | Coin       | Derivation Path          |
|--------|------------|--------------------------|
| RTC    | RustChain  | m/44'/8888'/0'/0/index   |
| BTC    | Bitcoin    | m/44'/0'/0'/0/index      |
| ETH    | Ethereum   | m/44'/60'/0'/0/index     |
| SOL    | Solana     | m/44'/501'/index'/0'     |
| ATOM   | Cosmos     | m/44'/118'/0'/0/index    |

## Usage Examples

### Basic Recovery
```bash
python recover.py "abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon abandon about"
```

### Specific Coins
```bash
python recover.py "your mnemonic words here" --coins rtc,btc,eth --count 5
```

### Interactive Mode
```bash
python recover.py -i
```
Follow the prompts to enter your mnemonic, passphrase, and coin selection.

### With Passphrase
```bash
python recover.py "mnemonic words" --passphrase "my secret passphrase"
```

## Security Notes

⚠️ **IMPORTANT**: 
- **Never share your mnemonic phrase** with anyone
- **Never enter your mnemonic** on untrusted devices or websites
- This tool runs **locally** and does **not transmit** your mnemonic anywhere
- The mnemonic is processed entirely in memory and is not stored unless you explicitly export

## How It Works

1. **Input**: Mnemonic phrase (12-24 words)
2. **Seed Generation**: PBKDF2-SHA512 with 2048 iterations
3. **Key Derivation**: BIP32 hierarchical deterministic derivation
4. **Address Generation**: Coin-specific address encoding (Base58, Bech32, Hex)

## Dependencies

- Python 3.7+
- No external dependencies (uses only Python standard library)

For production use with full secp256k1 curve support, consider installing:
```bash
pip install coincurve ecdsa
```

## License

MIT License - Part of the RustChain Ecosystem
