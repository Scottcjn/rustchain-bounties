# Boot Chime Proof-of-Iron -- Acoustic Hardware Attestation

**RustChain Bounty #2307 (95 RTC)**

Acoustic hardware attestation system that captures spectral fingerprints from
boot chime audio, compares them against known vintage hardware profiles, detects
analog artifacts vs emulator perfection, and folds results into anti-emulation
scoring for the RustChain attestation layer.

> No one else has done acoustic hardware attestation. The boot chime is a
> physical artifact of real iron -- unique to each machine as it ages.
> Recapped capacitors change the sound. Speaker cone wear changes the sound.
> This is unforgeable without possessing the actual hardware.

## Features

### Spectral Fingerprinting
- FFT-based spectral analysis of boot chime audio
- Dominant frequency peak detection with harmonic ratio extraction
- Hann-windowed DFT on 4096-sample windows
- Compact SHA-256 fingerprint hash for rapid matching

### Known Hardware Profiles (9 profiles across 4 families)

| Family | Profile | Frequencies | Duration |
|--------|---------|-------------|----------|
| **Mac** | Quadra (1991) | C5-E5-G5 major chord | 1800ms |
| **Mac** | Power Mac G3/G4 (1999) | C5-E5-G5-C6 | 2200ms |
| **Mac** | G4 MDD (2002) | Extended chord | 2000ms |
| **Mac** | Mac Pro Intel (2006) | Lower register | 2400ms |
| **Amiga** | Kickstart (1985-1993) | A4-A5 Paula chip | 400ms |
| **Amiga** | A1200 (1992) | A4-E5-A5 AGA | 500ms |
| **SGI** | IRIX Boot Chime | D5-G5-D6 ethereal | 1200ms |
| **Sun** | SparcStation Click-Buzz | 1-2-3 kHz harmonics | 300ms |
| **Sun** | Ultra Workstation | 0.8-1.6-2.4 kHz | 450ms |

### Anti-Emulation Detection
Emulators produce digitally perfect audio. Real hardware has analog artifacts:
- **Capacitor aging**: frequency drift over decades of use
- **Speaker cone wear**: amplitude jitter in the output
- **Analog noise floor**: characteristic hiss from aged components
- **Harmonic spread**: non-ideal resonance from physical enclosures

The system scores each chime on an analog artifact scale (0.0-1.0):
- Score > 0.35 with match > 0.5 = **GENUINE_HARDWARE**
- Score < 0.15 = **LIKELY_EMULATOR**
- Otherwise = **UNCERTAIN**

### Hardware Identity
- Reads CPU model, machine ID, DMI board info, memory size
- SHA-256 hash ties the attestation to specific physical hardware
- Combined with audio fingerprint for full proof-of-iron

### Chime Gallery (BoTTube Bonus)
- Browse all attested boot chimes with spectral visualization
- Each entry shows waveform, FFT peaks, match score, and verdict
- Click to replay any chime through Web Audio API

### Web Audio API Visualization
- Real-time animated FFT spectrum during chime playback
- Static spectral peak display with frequency labels
- Waveform view with envelope overlay
- Noise floor indicator line

## Architecture

```
server.py (aiohttp + aiosqlite)
  |
  +-- Audio Synthesis Engine
  |     Generate WAV from profile (with analog variance)
  |
  +-- Spectral Fingerprint Extractor
  |     DFT -> peak detection -> harmonic ratios -> hash
  |
  +-- Profile Matcher
  |     Compare against 9 known hardware profiles
  |     Frequency similarity + harmonic ratios + noise floor
  |
  +-- Anti-Emulation Scorer
  |     Analog artifact detection (genuine vs emulator)
  |
  +-- Attestation Builder
  |     Package fingerprint + match + hardware ID + signature
  |
  +-- SQLite Persistence
  |     boot_chimes + chime_gallery tables
  |
  +-- REST API (11 endpoints)
  |
  +-- Embedded HTML Dashboard
        Web Audio API playback + canvas visualization
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/` | Web dashboard with visualization |
| `GET` | `/api/profiles` | List known hardware chime profiles |
| `POST` | `/api/chime/generate` | Generate chime from profile, attest |
| `POST` | `/api/chime/upload` | Upload WAV for fingerprinting |
| `GET` | `/api/chime/{id}` | Get full chime detail + attestation |
| `GET` | `/api/chime/{id}/verify` | Re-verify stored chime integrity |
| `GET` | `/api/chime/{id}/replay` | Get WAV audio (base64) |
| `GET` | `/api/chimes` | List all chimes (paginated) |
| `POST` | `/api/gallery` | Add chime to BoTTube gallery |
| `GET` | `/api/gallery` | List gallery entries |
| `GET` | `/api/stats` | Aggregate attestation statistics |

## Setup

### Requirements

```
Python 3.8+
aiohttp
aiosqlite
```

### Install

```bash
pip install aiohttp aiosqlite
```

### Run

```bash
python server.py
```

Server starts on `http://0.0.0.0:8307` by default.

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `BOOTCHIME_DB` | `bootchime.db` | SQLite database path |
| `BOOTCHIME_HOST` | `0.0.0.0` | Bind address |
| `BOOTCHIME_PORT` | `8307` | HTTP port |

## Usage Examples

### Generate a Boot Chime

```bash
curl -X POST http://localhost:8307/api/chime/generate \
  -H "Content-Type: application/json" \
  -d '{"profile_key": "mac_1999", "analog_variance": 0.4}'
```

### Upload Real Audio

```bash
curl -X POST http://localhost:8307/api/chime/upload \
  -F "file=@my_mac_boot.wav"
```

### Verify Attestation

```bash
curl http://localhost:8307/api/chime/chime_abc123def456/verify
```

## How Matching Works

1. **Frequency Matching (45% weight)**: Each detected peak is compared against
   the profile's known frequencies with 5% tolerance for analog drift.

2. **Harmonic Ratio Matching (30% weight)**: The relative amplitudes of
   harmonics are compared. Real hardware produces consistent but imperfect
   harmonic relationships.

3. **Noise Floor Matching (25% weight)**: The estimated noise floor is compared
   against the profile's expected analog noise level. Different hardware
   families have characteristically different noise floors.

4. **Anti-Emulation Assessment**: The analog artifact score combines noise
   floor magnitude, frequency spread patterns, and peak count to distinguish
   genuine analog output from digitally perfect emulator audio.

## RTC Wallet

`RTC_WALLET_ADDRESS_HERE`

## License

MIT -- Built for the RustChain network.
