# The Fossil Record — Attestation Archaeology Visualizer

Interactive D3.js stratigraphy visualization of every hardware attestation in RustChain history, color-coded by architecture. Like looking at geological layers, but for silicon.

## Features

- **Stacked Area Chart**: 8 architecture layers rendered as geological strata
  - Motorola 68K (deepest, dark amber)
  - PowerPC G3/G4 (warm copper)
  - PowerPC G5 (bronze)
  - SPARC (crimson)
  - MIPS (jade)
  - POWER8/9 (deep blue)
  - Apple Silicon (silver)
  - Modern x86 (pale grey)

- **Interactive Hover**: Click any point to see miner ID, device, RTC earned, fingerprint quality
- **Epoch Markers**: Vertical settlement lines every 25 epochs
- **First-Appearance Annotations**: Shows when each architecture first joined the network
- **Toggle Layers**: Click legend items to show/hide architectures
- **Stats Bar**: Total attestations, active architectures, epochs, RTC mined
- **Mobile Responsive**: Works on any screen size
- **Dark Theme**: Consistent with RustChain design

## Quick Start

```bash
pip install aiohttp aiosqlite
python server.py --port 8311
# Open http://localhost:8311
```

## API Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Serves the visualizer HTML |
| `GET /api/attestations` | Full attestation history (filterable) |
| `GET /api/attestations/summary` | Aggregated per-epoch data for chart |
| `GET /api/architectures` | Architecture catalog with colors |
| `GET /api/epochs` | Epoch settlement timeline |

### Query Parameters

- `/api/attestations?arch=g3g4` — Filter by architecture
- `/api/attestations?epoch_min=50&epoch_max=100` — Filter by epoch range

## Architecture

```
fossils.html ──→ D3.js stratigraphy chart
    │
    ├── /api/attestations/summary ──→ Stacked area data
    ├── /api/epochs ──→ Settlement markers
    └── /api/architectures ──→ Color/metadata catalog
                                    │
server.py ──→ aiohttp + aiosqlite ──┘
    │
    └── fossil_record.db (SQLite, auto-seeded)
```

## Deployment

Deployable at `rustchain.org/fossils` — just set the environment:

```bash
export PORT=80
export FOSSIL_DB=/var/data/fossil_record.db
python server.py
```

## Bounty

Closes #2311 — The Fossil Record (75 RTC)

**Wallet**: RTC_ElromEvedElElyon_2311
