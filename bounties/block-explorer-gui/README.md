# RustChain Block Explorer GUI - Tier 1: Miner Dashboard

## Overview

Real-time miner dashboard for the RustChain Block Explorer, built with Alpine.js + Tailwind CSS.

**Bounty**: Tier 1 - 50 RTC  
**Issue**: https://github.com/Scottcjn/rustchain-bounties/issues/686

## Features

✅ **Active Miners Display**
- Architecture badges (G4, G5, POWER8, Apple Silicon, Modern)
- Visual antiquity multiplier bars
- Online/offline status indicators

✅ **Real-time Updates**
- Auto-refresh every 30 seconds
- Manual refresh button
- Last updated timestamp

✅ **Interactive Controls**
- Filter by status (All/Online/Offline)
- Sort by Name, Multiplier, or Last Attestation
- Responsive card layout

✅ **Design**
- Dark navy theme (#1a1a2e background, #16213e cards)
- Gold accents (#f39c12)
- Monospace fonts for data, sans-serif for headers
- Mobile-friendly responsive design

## Tech Stack

- **HTML5** - Single-page static application
- **Alpine.js 3.x** - Reactive state management (CDN)
- **Tailwind CSS 3.x** - Utility-first styling (CDN)
- **No build step required** - Drop-in HTML file

## API Integration

**Endpoint**: `GET https://explorer.rustchain.org/api/miners`

**Actual Response Format**:
```json
[
  {
    "miner": "g4-powerbook-115",
    "antiquity_multiplier": 2.5,
    "device_arch": "G4",
    "device_family": "PowerPC",
    "hardware_type": "PowerPC G4 (Vintage)",
    "last_attest": 1772774000,
    "entropy_score": 0,
    "first_attest": null
  }
]
```

**Field Mapping**:
- `miner` → Miner ID/Name
- `antiquity_multiplier` → Multiplier value
- `device_arch` / `hardware_type` → Architecture badge
- `last_attest` → Unix timestamp (seconds)

## Usage

### Local Testing
```bash
# Option 1: Simple HTTP server
cd block-explorer-gui
python -m http.server 8080

# Option 2: Live server (VS Code extension)
# Right-click index.html → "Open with Live Server"
```

### Deployment
Copy `index.html` to nginx server on port 5555:
```bash
scp index.html node1:/var/www/explorer/
```

## Files

```
block-explorer-gui/
├── index.html      # Main dashboard (single-file app)
└── README.md       # This file
```

## Screenshots

_TBD - Add screenshots after deployment_

## Next Steps (Tier 2 & 3)

### Tier 2: Agent Economy Marketplace (75 RTC)
- [ ] Open jobs listing
- [ ] Job lifecycle visualization
- [ ] Marketplace stats
- [ ] Agent reputation lookup
- [ ] Category filters

### Tier 3: Full Explorer Suite (150 RTC)
- [ ] Wallet balance lookup
- [ ] Epoch history & reward charts
- [ ] Network health dashboard (3 nodes)
- [ ] Hall of Rust integration
- [ ] Enhanced responsive design

## Development Notes

- **Offline Detection**: Miners are considered offline if last attestation > 5 minutes ago
- **Multiplier Bar**: Scaled to 100% max (multiplier × 10)
- **Auto-refresh**: Can be disabled in future if needed
- **Error Handling**: Displays user-friendly error messages on API failures

## Author

Developed by: 老程 (dev)  
Submission Date: 2026-03-06  
Estimated Completion: 2-3 days for full Tier 1-3 implementation
