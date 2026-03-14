# IBM 650 Miner - Quick Start Guide

## 🚀 5-Minute Setup

### Prerequisites

- Python 3.7 or later
- No external dependencies required!

### Installation

```bash
# Clone or download the ibm650-miner folder
cd ibm650-miner

# That's it! No pip install needed.
```

## ⚡ Quick Start

### 1. Run Your First Mining Cycle

```bash
python ibm650_miner_sim.py --wallet YOUR_WALLET_ADDRESS --cycles 5
```

Example output:
```
============================================================
  RUSTCHAIN IBM 650 MINER SIMULATOR (1953)
  LEGENDARY Tier Bounty #345 - 200 RTC
  Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
============================================================

Starting 5 mining cycle(s)...

--- Cycle 1 ---
[MINING] Starting IBM 650 Mining Cycle...
  Entropy: 1773425093
  Proof Hash: 0146768821
  Proof Card: 4325952659260314020401467688211773425093...
[OK] Proof verified!
[SAVE] Saved to proof_card_1.txt
```

### 2. Verify a Proof Card

```bash
python ibm650_miner_sim.py --verify proof_card_1.txt
```

Output:
```
Verifying proof card: proof_card_1.txt
[VERIFIED] Proof VERIFIED!
```

### 3. Run Tests

```bash
python test_miner.py
```

Expected output:
```
============================================================
IBM 650 MINER TEST SUITE
============================================================
RESULTS: 7 passed, 0 failed
============================================================
```

## 📖 Command Line Options

```
--wallet ADDRESS    Your RustChain wallet address (default: bounty wallet)
--cycles N          Number of mining cycles to run (default: 1)
--load FILE         Load SOAP assembly program
--run               Run loaded program
--verify FILE       Verify a proof card file
--drum-size SIZE    Drum memory: 1000, 2000, or 4000 (default: 2000)
```

## 🎯 Examples

### Generate 100 Proofs

```bash
python ibm650_miner_sim.py --wallet RTC4325af95d26d59c3ef025963656d22af638bb96b --cycles 100
```

### Run SOAP Program

```bash
python ibm650_miner_sim.py --load miner.soap --run
```

### Use 4K Drum Memory

```bash
python ibm650_miner_sim.py --drum-size 4000 --cycles 10
```

## 📁 Project Structure

```
ibm650-miner/
├── README.md              # Project overview
├── ARCHITECTURE.md        # Technical documentation
├── QUICK_START.md         # This file
├── PR_SUBMISSION.md       # PR submission template
├── ibm650_miner_sim.py    # Python simulator (main)
├── test_miner.py          # Test suite
├── miner.soap             # SOAP assembly source
└── sample_cards.txt       # Example proof cards
```

## 🔍 Understanding the Output

### Proof Card Format

Each proof card is 80 digits:

```
43259526592603140204014676882117734250930000000115000000000000000000000000000000
│          │          │          │          │
│          │          │          └─ Checksum (10 digits)
│          │          └─ Proof Hash (20 digits)
│          └─ Timestamp (10 digits, YYMMDDHHMM)
└─ Wallet ID (10 digits)
```

### Verification

Checksum = sum of all digits in wallet + timestamp + hash, modulo 10^10

## 🛠️ Troubleshooting

### "UnicodeEncodeError" on Windows

The simulator uses ASCII-only output for Windows compatibility. If you see encoding errors:

```bash
# Set console encoding
chcp 65001
python ibm650_miner_sim.py ...
```

### "Module not found"

Make sure you're in the correct directory:

```bash
cd ibm650-miner
python ibm650_miner_sim.py
```

### Tests failing

Check Python version:

```bash
python --version  # Should be 3.7+
```

## 📚 Learn More

- **README.md** - Project overview and history
- **ARCHITECTURE.md** - Deep technical dive
- **sample_cards.txt** - Example proof cards with annotations
- **miner.soap** - SOAP assembly source code

## 🎓 Historical Note

The IBM 650 was programmed using **punched cards** and **SOAP** (Symbolic Optimal Assembly Program). Programs were:

1. Written on coding sheets
2. Punched into cards
3. Loaded into card reader
4. Assembled by SOAP (itself on cards!)
5. Executed from drum memory

Our simulator replicates this workflow in Python!

## 🏆 Bounty Claim

This implementation targets **Bounty #345**:
- **Platform**: IBM 650 (1953)
- **Tier**: LEGENDARY
- **Reward**: 200 RTC ($20)
- **Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

## 💡 Tips

1. **Batch mining**: Run multiple cycles at once (`--cycles 100`)
2. **Save proofs**: Each cycle saves to `proof_card_N.txt`
3. **Verify often**: Use `--verify` to check proofs before submission
4. **Read ARCHITECTURE.md**: Understand the decimal hash design
5. **Try SOAP**: Load `miner.soap` to see assembly version

## 🤝 Contributing

Found a bug? Want to improve the simulator?

1. Fork the repository
2. Make your changes
3. Run tests: `python test_miner.py`
4. Submit PR

## 📄 License

MIT License - See project root for details

---

**Happy Mining on the First Mass-Produced Computer! 🖥️**
