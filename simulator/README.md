# RustChain Mining Simulator

An interactive, browser-based educational tool that demonstrates how RustChain's Proof of Antiquity mining works without requiring real hardware.

## 🎯 Purpose

This simulator helps potential miners understand the RustChain mining process before committing to hardware setup. It visualizes:

1. **Hardware Fingerprinting** - How the network verifies genuine vintage hardware
2. **Attestation Submission** - The process of submitting proof to the network
3. **Epoch Participation** - Round-robin block creation and queue mechanics
4. **Reward Calculation** - How antiquity multipliers affect earnings

## ✨ Features

### Interactive Hardware Selection
- PowerBook G4 (2.5x multiplier)
- Power Mac G5 (2.0x multiplier)
- Modern x86 PC (1.0x multiplier)
- Virtual Machine (demonstrates VM detection/penalty)

### Step-by-Step Simulation
1. **Hardware Fingerprinting** - See how CPUID, timing analysis, and SMBIOS verification work
2. **Attestation Submission** - Watch the Ed25519 signing and payload creation
3. **Epoch Participation** - Visualize the round-robin queue and wait times
4. **Reward Distribution** - Compare earnings across different hardware tiers

### Earnings Calculator
Estimate potential earnings based on:
- Hardware type (multiplier)
- Blocks mined per day
- Mining duration
- RTC price

## 🚀 Usage

Simply open `index.html` in any modern web browser. No server or build process required.

```bash
# Clone or download the files
# Open index.html in your browser
open index.html
```

## 🎨 Design

- **Single-file application** - Everything in one HTML file for easy deployment
- **No dependencies** - Pure HTML, CSS, and vanilla JavaScript
- **Responsive design** - Works on desktop, tablet, and mobile
- **Dark theme** - Easy on the eyes for extended viewing

## 📁 Files

```
mining-simulator-2301/
├── index.html    # Complete simulator (HTML + CSS + JS)
└── README.md     # This file
```

## 🔗 Deployment

The simulator can be deployed anywhere static files are served:

- GitHub Pages
- Netlify
- Vercel
- Any web server

Suggested deployment target: `rustchain.org/simulator`

## 📝 Bounty Details

This simulator was created for [RustChain Bounty #2301](https://github.com/Scottcjn/rustchain-bounties/issues/2301):
- **Bounty**: 40 RTC (+10 RTC bonus for calculator)
- **Requirements**: Browser-based interactive mining simulator
- **Bonus**: Earnings calculator included

## 🏆 Key Implementation Details

### VM Detection Visualization
The simulator demonstrates how VMs are detected through:
- CPUID hypervisor bit checking
- Timing artifact analysis
- Hardware signature verification

### Realistic Simulation
- Actual epoch numbers and timing
- Realistic hardware fingerprinting process
- Accurate reward calculations based on multipliers

### Educational Value
- Clear explanations at each step
- Visual progress indicators
- Comparison table showing all hardware tiers

## 📄 License

Created for the RustChain community as part of the bounty program.

## 💰 Wallet Address

RTC Wallet: `rustchain1qxyz...` (to be provided in PR)

---

**Try it live**: Open `index.html` in your browser!
