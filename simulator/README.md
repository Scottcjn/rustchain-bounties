# RustChain Mining Simulator

Interactive web-based simulator that demonstrates how RustChain mining works without requiring real hardware.

## 🎯 Features

### Core Features (40 RTC Bounty)
- ✅ **Browser-based** — Pure HTML/CSS/JavaScript, no backend required
- ✅ **Hardware Selection** — Choose from 4 architectures:
  - PowerBook G4 (2.5x multiplier)
  - Power Mac G5 (2.0x multiplier)
  - Modern x86 (1.0x multiplier)
  - Virtual Machine (0.000000001x — shows why VMs don't work)
- ✅ **Mining Loop Simulation**:
  1. Hardware Detection (6 fingerprint checks)
  2. Attestation Submission (payload generation)
  3. Epoch Participation (round-robin visualization)
  4. Reward Calculation (antiquity multipliers)
- ✅ **Real-time Reward Comparison** — Side-by-side comparison chart
- ✅ **Link to Actual Miner** — Download section at the end

### Bonus Features (+10 RTC)
- ✅ **Animated Fingerprint Check Visualization** — Real-time animation of all 6 checks
- ✅ **"What Would You Earn?" Calculator** — Calculate potential earnings based on:
  - Hardware selection
  - Number of epochs
  - Network hash power (miners)

## 📦 Files

```
simulator/
├── index.html      # Main HTML structure
├── styles.css      # Responsive styling
├── simulator.js    # Simulation logic
└── README.md       # This file
```

## 🚀 Usage

### Local
Simply open `index.html` in a web browser — no server required!

### Deployment
Can be deployed to:
- `rustchain.org/simulator` (recommended)
- GitHub Pages
- Any static file hosting

## 🎓 Educational Value

### What Users Learn

1. **Proof-of-Antiquity Consensus**
   - Why vintage hardware earns higher rewards
   - How multipliers work (G4: 2.5x, G5: 2.0x, x86: 1.0x)
   - Why VMs are penalized (anti-emulation checks)

2. **RIP-PoA Fingerprint Checks**
   - Clock-Skew & Oscillator Drift
   - Cache Timing Fingerprint
   - SIMD Unit Identity
   - Thermal Drift Entropy
   - Instruction Path Jitter
   - Anti-Emulation Detection

3. **Mining Process**
   - Hardware detection and fingerprinting
   - Attestation payload format
   - Epoch enrollment and round-robin selection
   - Reward calculation with antiquity bonuses

## 🛠️ Technical Details

### No Dependencies
- Pure vanilla JavaScript (no frameworks)
- No build step required
- No external API calls

### Responsive Design
- Mobile-friendly layout
- Dark theme for readability
- Smooth animations

### Architecture-Specific Simulations
- **PowerPC G4/G5**: Shows AltiVec SIMD, mftb timing, big-endian
- **Modern x86**: Shows SSE/AVX, rdtsc timing, little-endian
- **VM**: Demonstrates why VMs fail (all checks show detection)

## 📸 Screenshots

(Add screenshots after deployment)

## 🔗 Links

- **RustChain Repository**: https://github.com/Scottcjn/rustchain-bounties
- **Issue #2301**: https://github.com/Scottcjn/rustchain-bounties/issues/2301
- **RustChain Miner**: https://github.com/Scottcjn/rustchain-bounties/tree/main/rustchain-miner

## 📝 License

MIT License (same as RustChain project)

## 🙏 Credits

Built for the RustChain community as part of Bounty #2301.

---

**RTC Wallet Address**: `your-wallet-address-here`