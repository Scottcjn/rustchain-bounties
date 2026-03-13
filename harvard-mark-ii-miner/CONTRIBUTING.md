# Contributing to Harvard Mark II Miner

Thank you for your interest in the Harvard Mark II Miner project! This is a **conceptual demonstration** and educational project for the RustChain Proof-of-Antiquity bounty program.

---

## About This Project

This project implements a **symbolic** RustChain miner for the Harvard Mark II (1947), an electromechanical relay computer. While real cryptocurrency mining is physically impossible on this hardware, the project demonstrates:

- Historical accuracy in representing the Mark II's capabilities
- The conceptual framework of Proof-of-Antiquity
- Educational value about early computing
- Paper tape programming techniques
- Relay logic design

---

## Bounty Information

**Issue**: #393 - Port Miner to ASCC Harvard Mark II  
**Tier**: LEGENDARY  
**Reward**: 200 RTC ($20 USD)  
**Claim Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`

---

## Quick Start

### Prerequisites

- Python 3.7 or higher
- No external dependencies required!

### Running the Simulator

**Windows:**
```batch
run.bat test
```

**Mac/Linux:**
```bash
./run.sh test
```

**Manual:**
```bash
python simulation/mark2_miner.py
```

### Generating Paper Tape

```bash
python simulation/paper_tape_encoder.py --miner output.pt
python simulation/paper_tape_decoder.py output.pt --verbose
```

---

## Project Structure

```
harvard-mark-ii-miner/
├── README.md                    # Main documentation
├── ARCHITECTURE.md              # Technical specification
├── PAPER_TAPE_FORMAT.md         # Paper tape encoding
├── RELAY_LOGIC.md               # Relay circuit diagrams
├── LICENSE                      # MIT License
├── requirements.txt             # Python dependencies (none!)
├── run.sh                       # Unix/Mac run script
├── run.bat                      # Windows run script
├── simulation/
│   ├── mark2_miner.py           # Main simulator
│   ├── paper_tape_encoder.py    # Tape encoder
│   └── paper_tape_decoder.py    # Tape decoder
└── docs/
    ├── bounty_claim.md          # Bounty claim documentation
    └── harvard_mark_ii_history.md # Historical background
```

---

## How to Contribute

### 1. Report Issues

Found a bug or inaccuracy? Open an issue with:
- Clear description
- Steps to reproduce
- Expected vs actual behavior
- Python version and OS

### 2. Improve Documentation

We welcome improvements to:
- Historical accuracy
- Technical explanations
- Code comments
- Examples and tutorials

### 3. Enhance Simulation

Possible improvements:
- More accurate timing models
- Additional relay circuits
- Visual relay state display
- Sound effects (relay clicking!)
- Paper tape image generation

### 4. Educational Content

Create:
- Lesson plans for teachers
- Video tutorials
- Interactive demonstrations
- Comparison with other vintage computers

---

## Code Style

### Python

- Follow PEP 8 style guidelines
- Use type hints where helpful
- Write docstrings for functions
- Keep functions focused and small

### Documentation

- Use Markdown formatting
- Include examples
- Link to references
- Keep historical accuracy

---

## Testing

### Manual Testing

```bash
# Run simulator
python simulation/mark2_miner.py 1

# Test encoder
python simulation/paper_tape_encoder.py --text "Hello" test.pt

# Test decoder
python simulation/paper_tape_decoder.py test.pt
```

### Verification Checklist

- [ ] Simulator runs without errors
- [ ] Paper tape encoding works
- [ ] Paper tape decoding works
- [ ] Documentation is accurate
- [ ] Wallet address is correct

---

## Historical Accuracy

We strive for historical accuracy. If you find errors in:
- Technical specifications
- Historical dates
- Relay counts
- Performance metrics

Please open an issue with references!

### Key References

1. Aiken, H. H. (1947). "Description of a Relay Calculator"
2. IEEE History Center: Harvard Mark II
3. Computer History Museum collections
4. Grace Hopper's papers and interviews

---

## Important Notes

### This is NOT a Real Miner

**Important**: This project is a **conceptual demonstration only**. The Harvard Mark II cannot:
- Perform SHA-256 hashing
- Connect to networks
- Mine cryptocurrency in any practical sense

This is an **educational and artistic project** that honors computing history.

### Wallet Address

The wallet address `RTC4325af95d26d59c3ef025963656d22af638bb96b` is included for bounty claim purposes. Do not send funds to this address unless you are the RustChain Foundation distributing bounties.

---

## License

MIT License - See LICENSE file for details.

You are free to:
- Use the code for any purpose
- Modify and distribute
- Create derivative works
- Use in educational settings

Please attribute the original source and keep the license notice.

---

## Questions?

- **GitHub Issues**: For bugs and feature requests
- **Discord**: https://discord.gg/VqVVS2CW9Q
- **RustChain Docs**: https://github.com/Scottcjn/Rustchain

---

## Acknowledgments

- **Howard H. Aiken** - Visionary computer designer
- **Grace Hopper** - Programming pioneer and debugger
- **Harvard University** - Preserving computing history
- **RustChain Foundation** - Supporting vintage computing
- **Computer History Museum** - Educational resources

---

**Last Updated**: 2026-03-13  
**Wallet**: RTC4325af95d26d59c3ef025963656d22af638bb96b  
**Issue**: #393 - LEGENDARY Tier

*"The Harvard Mark II wasn't just a calculator - it was a vision of automatic computing that shaped the future."*
