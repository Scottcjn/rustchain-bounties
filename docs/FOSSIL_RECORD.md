# Fossil Record — Attestation Archaeology Visualizer

Built for bounty **#2311**.

## What it is

`widgets/fossil-record.html` is a self-contained attestation timeline / stratigraphy viewer for RustChain.
It renders architecture layers over time:

- **X-axis** — time / epoch progression
- **Y-axis** — architecture strata (oldest at the bottom)
- **Width** — number of active miners in that architecture at the sampled moment
- **Color** — architecture family
- **Hover** — miner IDs, fingerprint quality, RTC earned, epoch, timestamp
- **Markers** — epoch settlement lines + first-seen architecture points

## Important reality check

The public endpoint `GET /api/miners` exposes a **current snapshot**, not full historical attestation records.
That means a true “since genesis” fossil record requires one of these inputs:

1. **SQLite export** from the node database, or
2. **Accumulated snapshots** sampled over time from `/api/miners`

This implementation supports both.

## Files

- `widgets/fossil-record.html` — interactive visualization
- `scripts/build_fossil_record.py` — normalize SQLite or JSON/JSONL history into chart-ready JSON
- `scripts/sample_miners_history.py` — collect live `/api/miners` snapshots into JSONL
- `widgets/data/miners-snapshots.sample.json` — sample seed history
- `widgets/data/fossil-record.sample.json` — prebuilt demo dataset

## Quick start

### 1) View the demo

Open:

```bash
open widgets/fossil-record.html
```

It loads `widgets/data/fossil-record.sample.json` by default.

### 2) Build from a JSONL snapshot archive

```bash
python3 scripts/build_fossil_record.py   --input-json widgets/data/miners-history.jsonl   --output widgets/data/fossil-record.json
```

Then point the HTML at `fossil-record.json` (or replace the sample file).

### 3) Build from SQLite history

```bash
python3 scripts/build_fossil_record.py   --input-sqlite /path/to/rustchain.db   --output widgets/data/fossil-record.json
```

The script auto-detects common attestation table names (`attestations`, `attestation_history`, `miner_attestations`, `attestation_events`).

### 4) Start sampling live data

```bash
python3 scripts/sample_miners_history.py   --url https://bulbous-bouffant.metalseed.net/api/miners   --output widgets/data/miners-history.jsonl   --count 12   --interval 300
```

This captures one hour of history at 5-minute intervals. Run it longer to accumulate a deeper “fossil record”.

## Deployment notes

The page is static HTML/CSS/JS with no external dependencies, so it can be dropped directly into a simple site path such as:

- `rustchain.org/fossils`
- GitHub Pages
- nginx static hosting

## Known limitations

- Without SQLite/history export, no tool can reconstruct “every attestation since genesis” from a single `/api/miners` call.
- Public miner snapshots currently expose limited per-event metadata, so `rtc_earned` / fingerprint quality are best when sourced from database exports.
- The builder normalizes several likely schemas, but a production RustChain DB export may need a tiny column mapping tweak if the table differs.
