# RustChain Attestation Archaeology Visualizer

> **Bounty #2311 - Attestation Archaeology Visualizer (75 RTC)**

Interactive visualization timeline showing attestation history of all miners, colored by architecture layers.

## 🎯 Features

### Core Features
- ✅ **Interactive Timeline** - X-axis shows time (epochs), Y-axis shows architecture stacks
- ✅ **Architecture Layering** - Oldest architectures at the bottom, newest at the top
- ✅ **Color Coding** - Each architecture family has its unique color:
  - 68K: Deep amber
  - G3/G4: Warm copper
  - G5: Bronze
  - SPARC: Dark red
  - MIPS: Emerald
  - POWER8: Dark blue
  - Apple Silicon: Silver
  - Modern x86: Light gray
- ✅ **Hover Information** - Shows Miner ID, Device, RTC Earnings, Fingerprint Quality
- ✅ **Epoch Settlement Markers** - Vertical lines indicating epoch settlements
- ✅ **Real-time Statistics** - Total miners, attestations, RTC earned
- ✅ **Data Export** - Export attestation history to CSV

### Technical Features
- 📦 **Zero Dependencies** - Pure HTML/CSS/JavaScript with D3.js
- 🔄 **API Integration** - Can fetch data from RustChain API when available
- 🎨 **Fallback Mock Data** - Uses realistic mock data when API unavailable
- 📱 **Responsive Design** - Works on desktop and mobile devices
- 🌙 **Dark Theme** - Modern dark UI for readability

## 📦 Files

```
fossils/
├── index.html      # Main HTML structure
├── styles.css      # Dark theme styling
├── data.js         # Data management and API integration
├── visualizer.js   # D3.js visualization logic
└── README.md       # This file
```

## 🚀 Usage

### Local
Simply open `index.html` in a web browser - no server required!

### Deployment
Can be deployed to:
- `rustchain.org/fossils` (recommended)
- GitHub Pages
- Any static file hosting

### API Configuration
By default, the visualizer tries to fetch data from `http://50.28.86.131:9100`. To change this:

```javascript
// In data.js, modify the fetchFromAPI function
const apiData = await fetchFromAPI('http://your-custom-node:9100');
```

## 📊 Visualization

### Timeline Structure
- **X-Axis**: Time represented as epochs (e.g., Epoch 0, Epoch 10, Epoch 20...)
- **Y-Axis**: Architecture families stacked from oldest (bottom) to newest (top)
- **Points/Circles**: Individual attestations
- **Vertical Lines**: Epoch settlement markers (every 10 epochs)

### Color Scheme
| Architecture | Color | Layer |
|--------------|-------|-------|
| 68K | Deep amber (#ff8c00) | 1 (bottom) |
| G3/G4 | Warm copper (#cd7f32) | 2-3 |
| G5 | Bronze (#b87333) | 4 |
| SPARC | Dark red (#8b0000) | 5 |
| MIPS | Emerald (#50c878) | 6 |
| POWER8 | Dark blue (#00008b) | 7 |
| Apple Silicon | Silver (#c0c0c0) | 8 |
| Modern x86 | Light gray (#d3d3d3) | 9 (top) |

### Hover Information
When hovering over an attestation point, the tooltip shows:
- Miner ID
- Device name
- Architecture
- Epoch
- RTC earned
- Fingerprint quality

## 🔧 Technical Details

### Data Structure
Each attestation record contains:
```javascript
{
    minerId: 'miner_0001',
    epoch: 42,
    architecture: 'G4',
    device: 'PowerBook G4',
    rtcEarned: 12.5,
    fingerprintQuality: 0.95,
    timestamp: '2026-03-23T10:00:00Z'
}
```

### API Endpoints Used
When API is available:
- `GET /api/miners?limit=100` - List active miners
- `GET /api/miners/{miner_id}/attestation` - Get miner attestation status

### Mock Data Generation
When API is unavailable, the visualizer generates realistic mock data:
- 50-80 miners
- 100 epochs
- Random device names per architecture
- Realistic RTC earnings based on architecture multipliers
- Fingerprint quality range: 0.7-1.0

## 🎓 Educational Value

This visualizer helps users understand:
1. **RustChain's Proof-of-Antiquity** - Older hardware earns higher rewards
2. **Hardware Diversity** - Shows the variety of hardware mining on RustChain
3. **Epoch Mechanism** - Visualizes how attestations are grouped by epochs
4. **Fingerprint Quality** - Shows hardware attestation confidence levels

## 📸 Screenshots

(Add screenshots after deployment)

## 🔗 Links

- **RustChain Repository**: https://github.com/Scottcjn/rustchain-bounties
- **Bounty #2311**: https://github.com/Scottcjn/rustchain-bounties/issues/2311
- **RustChain Node API**: http://50.28.86.131:9100
- **Block Explorer**: http://50.28.86.131/explorer

## 📝 License

MIT License (same as RustChain project)

## 🙏 Credits

Built for the RustChain community as part of Bounty #2311.

---

**RTC Wallet Address**: `9dRRMiHiJwjF3VW8pXtKDtpmmxAPFy3zWgV2JY5H6eeT`