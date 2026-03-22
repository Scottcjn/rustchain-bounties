# CRT Light Attestation

**RustChain Bounty #2310 — Security by Cathode Ray (140 RTC)**

Side-channel proof system where a miner flashes a deterministic pattern on a CRT monitor and a camera or photodiode captures scanline timing, phosphor decay, and refresh quirks. That optical fingerprint becomes one more thing emulators can never fake.

## Overview

CRT monitors produce signals that are physically impossible to replicate on modern displays:

- **Phosphor decay** — LCD/OLED have zero decay (sample-and-hold). Instantly detected.
- **Unique aging** — Each CRT ages differently: electron gun wear, phosphor burn-in, flyback drift.
- **No VMs** — Virtual machines have no CRT. Period.
- **Scanline jitter** — Flyback transformer wear creates unique timing signatures.
- **Brightness nonlinearity** — Aging electron guns produce nonlinear gamma drift.

A 20-year-old Trinitron produces fundamentally different optical signals than a 20-year-old shadow mask — and both are trivially distinguishable from any LCD.

## Architecture

```
                    +-----------------------+
                    |     CRT Monitor       |
                    |  (Deterministic       |
                    |   Pattern Display)    |
                    +-----------+-----------+
                                |
                    +-----------v-----------+
                    |   Capture Device      |
                    |  (Webcam/Photodiode)  |
                    +-----------+-----------+
                                |
                    +-----------v-----------+
                    |   CRT Analyzer        |
                    |  - Phosphor decay     |
                    |  - Refresh drift      |
                    |  - Scanline jitter    |
                    |  - Brightness curve   |
                    +-----------+-----------+
                                |
                    +-----------v-----------+
                    |  Fingerprint Hash     |
                    |  (SHA-256 of all      |
                    |   optical features)   |
                    +-----------+-----------+
                                |
                    +-----------v-----------+
                    |  RustChain            |
                    |  Attestation          |
                    |  (On-Chain Anchor)    |
                    +-----------------------+
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Web UI |
| `POST` | `/api/attestations` | Submit CRT capture for analysis |
| `GET` | `/api/attestations` | List all attestations |
| `GET` | `/api/attestations/{id}` | Get single attestation result |
| `POST` | `/api/verify` | Verify attestation on-chain |
| `GET` | `/api/gallery` | CRT Gallery (phosphor decay comparisons) |

### POST /api/attestations

Submit a CRT capture for analysis. Accepts multipart/form-data or JSON.

**Form fields:**
- `file` — CRT capture image or video
- `source_type` — `webcam`, `photodiode`, `dslr`, or `phone`
- `stated_refresh` — Expected refresh rate in Hz (default: 60)
- `simulate_lcd` — Set to `true` to test LCD rejection

**JSON body:**
```json
{
  "source_type": "webcam",
  "stated_refresh": 72.0,
  "simulate_lcd": false
}
```

**Response (201):**
```json
{
  "id": "uuid",
  "status": "completed",
  "is_crt": true,
  "confidence": 0.8234,
  "crt_fingerprint": "sha256...",
  "attestation_hash": "sha256...",
  "analysis": {
    "monitor": { "archetype": "trinitron", "name": "Sony Trinitron", "mask_type": "aperture_grille" },
    "phosphor": { "type": "P22", "aged_decay_us": 26.0 },
    "refresh": { "measured_hz": 59.97, "drift_ppm": -500.0 },
    "scanline": { "flyback_signature": "abc123...", "jitter_stddev_us": 0.18 },
    "brightness": { "gamma_measured": 2.15, "nonlinearity_index": 0.12 },
    "spectrogram": { "bins": [...] },
    "crt_fingerprint": "sha256..."
  }
}
```

### POST /api/verify

Verify a CRT attestation on-chain.

```json
{ "attestation_id": "uuid" }
```

## Analysis Pipeline

### 1. Phosphor Decay Characterization

Models the exponential decay curve with aging effects:

```
I(t) = I0 * exp(-t / tau_aged)
```

Where `tau_aged = tau_base * (1 + 0.02 * age_years)`. Different phosphor types have distinct decay constants:

| Phosphor | Decay (us) | Use |
|----------|-----------|-----|
| P22 | 20 | Standard color monitors |
| P43 | 1000 | Oscilloscopes, radar |
| P4 | 60 | B&W television |
| P31 | 32 | Green terminals (VT100) |
| P1 | 24 | Early oscilloscopes |

### 2. Refresh Rate Drift

CRTs drift due to flyback transformer aging and capacitor drift. The analyzer measures actual refresh rate vs stated and computes drift in parts-per-million (ppm).

### 3. Scanline Timing Jitter

Each horizontal scanline has a retrace period controlled by the flyback transformer. Aging increases jitter, and the transformer heats up during a frame, causing progressive drift.

### 4. Brightness Nonlinearity

CRT gamma curves drift as the electron gun ages. The cathode emission decreases unevenly across the brightness range, creating a unique transfer function.

### 5. Fingerprint Generation

All measurements are combined into a SHA-256 fingerprint:

```
sha256(phosphor:decay_us:measured_hz:drift_ppm:flyback_sig:gamma:nonlinearity:archetype)
```

### 6. On-Chain Attestation

The fingerprint is wrapped in an attestation payload and hashed for chain submission:

```
sha256(RUSTCHAIN_CRT_ATTESTATION:v1:{id}:{fingerprint}:{timestamp})
```

## CRT Gallery (Bonus)

The `/api/gallery` endpoint provides phosphor decay curves from five CRT archetypes plus an LCD reference, demonstrating why CRT signals are unforgeable:

- **Sony Trinitron** (aperture grille, P22)
- **Generic Shadow Mask** (shadow mask, P22)
- **Mitsubishi Diamondtron** (aperture grille, P22)
- **DEC VT100 Terminal** (P31 green phosphor)
- **Tektronix 2465 Oscilloscope** (P43 long persistence)
- **LCD Reference** (zero decay — instant detection)

## Running

```bash
# Install dependency
pip install aiohttp

# Start server
python server.py

# Or with custom config
CRT_PORT=9000 CRT_DB_PATH=/tmp/crt.db python server.py
```

The server starts on port 8310 by default. Open `http://localhost:8310` for the web UI.

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `CRT_HOST` | `0.0.0.0` | Bind address |
| `CRT_PORT` | `8310` | Server port |
| `CRT_DB_PATH` | `crt_attestations.db` | SQLite database path |
| `CRT_UPLOAD_DIR` | `uploads` | Upload directory |

## Why This Is Unforgeable

1. **LCD/OLED monitors have zero phosphor decay** — sample-and-hold pixel addressing produces a flat brightness curve where a CRT would show exponential decay. Instantly detected.

2. **Each CRT ages uniquely** — electron gun wear reduces cathode emission, phosphors burn in non-uniformly, flyback transformers drift. No two 20-year-old CRTs produce identical signals.

3. **Virtual machines have no CRT** — there is no display adapter in existence that can simulate phosphor decay, scanline jitter, and flyback timing simultaneously through a virtual framebuffer.

4. **A Trinitron and a shadow mask are distinguishable** — aperture grille vs shadow mask produce different spatial frequency patterns in the captured signal.

## Files

```
bounty-2310-crt-attestation/
  server.py          — Backend (Python + aiohttp), CRT analyzer, API
  attestation.html   — Single-page web UI
  README.md          — This file
```

## License

Apache-2.0
