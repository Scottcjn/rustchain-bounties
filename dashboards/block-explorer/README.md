# RustChain Block Explorer - Miner Dashboard

A real-time mining dashboard for the RustChain Proof-of-Antiquity blockchain.

## Features

- **Real-time Miner Status**: Live display of all active miners with online/offline indicators
- **Architecture Badges**: Visual identification of miner hardware (Modern x86, Apple Silicon, POWER8, ARM, etc.)
- **Antiquity Multipliers**: Display of proof-of-antiquity reward multipliers
- **Auto-refresh**: Automatic data refresh every 30 seconds
- **Search & Filter**: Search miners by name and filter by architecture
- **Sortable Columns**: Click column headers to sort by any field
- **Responsive Design**: Works on desktop and mobile devices
- **Dark Theme**: Matches RustChain branding (dark navy + gold accents)

## Quick Start

Simply open `index.html` in any modern web browser. No build step or server required.

```bash
# Serve locally (optional)
python3 -m http.server 8080
# Then visit http://localhost:8080
```

## API Endpoints Used

- `GET https://explorer.rustchain.org/api/miners` - List all miners with status

## Technical Details

- **Pure HTML/CSS/JS**: No frameworks or build tools required
- **Vanilla JavaScript**: Lightweight, fast, no dependencies
- **CSS Grid/Flexbox**: Modern responsive layout
- **Fetch API**: Async data loading with error handling

## Bounty Information

This dashboard fulfills **Tier 1** of the Block Explorer GUI Upgrade bounty:
- Real-time miner dashboard ✅
- Architecture badges ✅
- Antiquity multipliers displayed ✅
- Last attestation timestamps ✅
- Online/offline status ✅
- Sortable table layout ✅
- Auto-refresh every 30 seconds ✅

## Screenshot

The dashboard displays:
- Header with RustChain branding
- Stats bar showing total miners, online count, average multiplier, and architecture diversity
- Search and filter controls
- Sortable table with miner details
- Real-time status indicators

## Browser Support

- Chrome/Edge 80+
- Firefox 75+
- Safari 13+
- Mobile browsers (iOS Safari, Chrome Android)

---

Built for RustChain Bounty #686 - Block Explorer GUI Upgrade
