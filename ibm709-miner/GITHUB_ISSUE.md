# [BOUNTY: 200 RTC] Port Miner to IBM 709 (1958) - LEGENDARY Tier

**Bounty Tier**: LEGENDARY  
**Reward**: 200 RTC ($20)  
**Wallet**: `RTC4325af95d26d59c3ef025963656d22af638bb96b`  
**Antiquity Multiplier**: 5.0x (highest in RustChain!)

---

## 🎯 Objective

Port the RustChain Proof-of-Antiquity miner to the **IBM 709 (1958)**, IBM's first large-scale scientific computer and the **oldest architecture ever to mine a blockchain**.

## 🏛️ Historical Significance

The IBM 709:
- Announced: January 1957
- First installed: August 1958
- Technology: Vacuum tubes (later transistorized as IBM 7090)
- Used for: NASA Mercury program, NORAD ballistic tracking, weather prediction
- Predates: Integrated circuits (1959), ARPANET (1969), C language (1972)

This is **LEGENDARY tier** because it represents the vacuum tube era of computing - the absolute pinnacle of antiquity!

## 📋 Requirements

### Hardware/Emulation

Since real IBM 709 hardware is preserved only in museums, use **SIMH** to emulate the IBM 7090 (transistorized successor, binary-compatible):

```bash
# Install Open SIMH
git clone https://github.com/open-simh/simh.git
cd simh
make -f makefile all
```

### Miner Implementation

- **Language**: FAP (FORTRAN Assembly Program) - the assembly language for IBM 709
- **Memory**: Must fit in 32K words (36-bit) = ~144 KB
- **Networking**: IBM 709 has no network - use batch mode with tape export
- **Attestation**: Write to simulated 7-track tape, submit via modern host bridge

### Minimum Requirements

- [ ] Miner runs in SIMH IBM 7090 emulator
- [ ] Generates attestations every 10 minutes
- [ ] Exports attestations to tape image
- [ ] Python bridge script submits to RustChain node
- [ ] Runs for 24+ hours (simulated time)
- [ ] Wallet generated from hardware entropy

## 📁 Deliverables

Create a new directory `ibm709-miner/` with:

```
ibm709-miner/
├── README.md                    # Project overview and quickstart
├── ARCHITECTURE.md              # IBM 709 technical reference
├── IMPLEMENTATION.md            # Implementation details
├── src/
│   └── miner.fap                # FAP assembly source code
├── simh/
│   ├── ibm7090.ini              # SIMH configuration
│   └── submit_host.py           # Python submission bridge
├── build/
│   └── miner.bin                # Compiled binary
└── docs/
    └── (additional documentation)
```

## 💰 Bounty Claim

To claim this bounty:

1. **Fork** the RustChain repo
2. **Create** `ibm709-miner/` directory with all deliverables
3. **Test** miner in SIMH for 24+ hours
4. **Submit** PR with:
   - All source code
   - Documentation
   - Test results/screenshots
   - SIMH configuration
5. **Comment** on this issue with:
   - Screenshot of miner running in SIMH
   - Screenshot of tape output
   - Screenshot of successful attestation submission
   - Your wallet address for bounty payment

## 🔧 Technical Notes

### IBM 709 Architecture

| Feature | Specification |
|---------|---------------|
| Word Size | 36 bits |
| Memory | 32,768 words (magnetic-core) |
| Speed | 42,000 add/subtract per second |
| Technology | Vacuum tubes |
| Programming | FAP assembly, direct octal |
| I/O | 7-track tape, punch cards |
| Networking | None (predates ARPANET) |

### Emulation Approach

Since the IBM 709 has no networking:

1. **Batch Mining**: IBM 709 generates attestations locally
2. **Tape Export**: Write attestations to simulated tape
3. **Host Bridge**: Python script reads tape and submits to RustChain node

### Attestation Format (Tape)

```
Word 0:  Marker (0o777777777777)
Word 1-3: Wallet ID
Word 4:  Timestamp
Word 5-7: Attestation hash
Word 8:  Checksum
```

### Example FAP Code

```
         ENTRY   START
START    CLA     ZERO
         LXA     SAVE1,1
         TZE     INIT
LOOP     JSUB    COLLECT_ENTROPY
         JSUB    GEN_ATTEST
         WRT     TAPE
         TZE     LOOP
ZERO     DEC     0
SAVE1    BSS     1
         END     START
```

## 🎓 Educational Value

This project demonstrates:
- **Computer History**: Vacuum tube era architecture
- **Assembly Programming**: Programming at the metal
- **Blockchain Universality**: Proof-of-work transcends hardware generations
- **Historical Preservation**: Keeping vintage computing alive

## 📚 Resources

- [IBM 709 Reference Manual (1958)](http://bitsavers.org/pdf/ibm/709/A22-6501-0_709_Data_Processing_System_Reference_Manual_Apr58.pdf)
- [SIMH IBM 7090 Documentation](https://github.com/open-simh/simh/blob/master/IBM7090.md)
- [Computer History Museum - IBM 709](https://computerhistory.org/collections/catalog/102643736)
- [RustChain DOS Miner (reference)](https://github.com/Scottcjn/rustchain-dos-miner)

## ✅ Verification Checklist

Bounty reviewers will verify:

- [ ] Code compiles/assembles without errors
- [ ] Miner runs in SIMH without crashes
- [ ] Attestations are generated correctly
- [ ] Python bridge successfully submits to node
- [ ] Node accepts attestations
- [ ] Documentation is complete and accurate
- [ ] Code follows RustChain conventions
- [ ] Dev fee (0.001 RTC/epoch) is implemented

## 🏆 Related Bounties

- #168 - [BOUNTY] Mine on Exotic Hardware (umbrella issue)
- rustchain-dos-miner - DOS miner for 8086-Pentium (reference)
- #35 - POWER8 benchmark suite (75 RTC)

## 💡 Tips

- Start with the DOS miner as a reference for structure
- Use SIMH's debugging features (STEP, EXAMINE, DEPOSIT)
- Test tape I/O early - it's critical for the bridge
- Document any SIMH-specific quirks you encounter
- Take screenshots throughout development for the bounty claim

## 🤝 Questions?

Open a discussion or comment on this issue if you need help with:
- FAP assembly language
- SIMH configuration
- IBM 709 architecture details
- Attestation format

---

**Good luck, and welcome to the vacuum tube era of blockchain mining!** 🔌💻

*Every vintage computer has historical potential.*
