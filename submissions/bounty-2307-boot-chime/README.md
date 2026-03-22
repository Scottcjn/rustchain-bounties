# Boot Chime Proof-of-Iron -- Acoustic Hardware Attestation

**RustChain Bounty #2307 (95 RTC)**

No one else has done acoustic hardware attestation. The boot chime is a physical artifact of real iron -- unique to each machine as it ages. Recapped capacitors change the sound. Speaker cone wear changes the sound. This is unforgeable without possessing the actual hardware.

## What It Does

A server that captures spectral fingerprints from authentic startup sounds on Power Macs, Amigas, SGI workstations, Sun SparcStations, and other vintage hardware. It compares waveforms against known profiles and folds the result into anti-emulation scoring.

**Emulators produce digitally perfect audio.** Real hardware carries analog artifacts:
- Capacitor aging shifts frequency response
- Speaker-cone wear alters resonance peaks
- Transformer hiss raises the noise floor
- 50/60 Hz mains hum bleeds through analog paths
- Oscillator drift shifts fundamental frequencies

The system scores all of these and issues a hardware-authenticity verdict.

## Architecture

```
                    WAV Upload / Mic Recording
                            |
                    +-------v--------+
                    |   Flask Server  |
                    |   (server.py)   |
                    +-------+--------+
                            |
              +-------------+-------------+
              |             |             |
        FFT Analysis   Profile Match  Analog Scoring
              |             |             |
              v             v             v
        Spectral       Known Chime    Noise Floor
        Envelope       Database       Mains Hum
        Dominant       (7 profiles)   HF Rolloff
        Frequencies                   Spectral Roughness
              |             |             |
              +------+------+------+------+
                     |             |
               Spectrogram   Attestation Hash
                 (PNG)        (SHA-256)
                     |             |
                     v             v
                  SQLite        On-Chain
                  Storage       Submission
```

## Known Boot Chime Profiles

| Profile | Manufacturer | Years | Key Feature |
|---------|-------------|-------|-------------|
| Mac Startup Chime | Apple | 1999-2016 | F# major chord, ASC chip |
| Mac Quadra / Early PowerMac | Apple | 1991-1998 | Brighter timbre |
| Amiga Kickstart Boot Tone | Commodore | 1985-1994 | Paula chip 8-bit PCM |
| SGI IRIX Boot Chime | Silicon Graphics | 1992-2006 | HAL2/AD1843 crystalline |
| Sun SparcStation Click-Buzz | Sun Microsystems | 1989-2001 | AMD79C30A codec |
| NeXT Boot Sound | NeXT | 1988-1993 | DSP56001 orchestral hit |
| IBM PS/2 POST Beep | IBM | 1987-1995 | 8254 PIT square wave |

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/chimes` | Upload boot-sound WAV for analysis |
| `GET` | `/api/chimes` | List all registered boot chimes |
| `GET` | `/api/chimes/:id` | Get full analysis result |
| `POST` | `/api/verify/:id` | Submit acoustic attestation on-chain |
| `GET` | `/api/spectrogram/:id` | Get spectrogram PNG |
| `GET` | `/api/profiles` | List known reference profiles |
| `GET` | `/health` | Health check |

## Quick Start

```bash
cd submissions/bounty-2307-boot-chime
pip install flask
python server.py
# Open http://localhost:5307
```

### CLI Analysis

```bash
python server.py --analyze boot-chime.wav
```

Output:
```
======================================================================
  Boot Chime Proof-of-Iron  --  Acoustic Hardware Attestation
======================================================================

  File: boot-chime.wav
  Duration: 2.50s  |  Sample Rate: 44100 Hz

  --- Spectral Analysis ---
  Dominant Frequencies: 370.0 Hz, 740.0 Hz, 1108.7 Hz, 1480.0 Hz
  Harmonic Ratios (H2/H1, H3/H1): 0.847, 0.612

  --- Analog Assessment ---
           noise_floor: 0.80  [################    ]
             mains_hum: 0.70  [##############      ]
    spectral_roughness: 0.60  [############        ]
            hf_rolloff: 0.90  [##################  ]
             Composite: 0.7450
               Verdict: REAL_HARDWARE

  --- Hardware Match ---
  1. Mac Startup Chime                        89.2% (spectral=0.91 freq=0.87 harmonic=0.84) <<< MATCH
  2. Mac Quadra / Early PowerMac Chime        42.1% (spectral=0.45 freq=0.38 harmonic=0.40)
  3. NeXT Boot Sound                          28.7% (spectral=0.31 freq=0.25 harmonic=0.27)

  --- Attestation ---
  Hash: a3f8c91d...
  PoA-Signature: poa_chime2307_a3f8c91d4e7b2f01
======================================================================
```

## Web UI Features

- **Audio upload** -- drag-and-drop or file picker (WAV, 16-bit PCM)
- **Live microphone recording** -- capture boot chimes in real time with waveform visualization
- **Spectrogram display** -- FFT-based frequency-vs-time visualization
- **Hardware match results** -- ranked list with confidence scores
- **Analog assessment bars** -- visual breakdown of noise floor, mains hum, spectral roughness, HF rolloff
- **Attestation submission** -- one-click on-chain attestation
- **Chime gallery** -- browse all analyzed chimes
- **Profile browser** -- view all known reference profiles
- **Dark theme** -- designed for terminal-native users

## Technical Details

### FFT Implementation

Pure-Python Cooley-Tukey radix-2 decimation-in-time FFT. No numpy/scipy required. The 4096-point FFT gives ~10.7 Hz frequency resolution at 44.1 kHz sample rate.

### Analog Scoring Algorithm

Four independent scores are weighted to produce a composite:

| Factor | Weight | What It Detects |
|--------|--------|-----------------|
| Noise Floor | 30% | Broadband noise from analog circuits |
| Mains Hum | 25% | 50/60 Hz mains bleed-through |
| Spectral Roughness | 25% | Speaker resonance peaks |
| HF Rolloff | 20% | Natural speaker frequency limits |

- **REAL_HARDWARE**: composite >= 0.50
- **INCONCLUSIVE**: composite 0.30 - 0.50
- **LIKELY_EMULATOR**: composite < 0.30

### Spectrogram Generation

Pure-Python PNG generation using zlib compression. No PIL/Pillow needed. Viridis-like colormap for frequency magnitude visualization.

### Profile Matching

Three-axis matching with weighted combination:
- **Spectral similarity** (50%): Cosine similarity of 256-bin normalized envelopes
- **Frequency match** (30%): Proximity of dominant frequency peaks
- **Harmonic match** (20%): Ratio comparison of first harmonics

## Dependencies

- Python 3.8+
- Flask (`pip install flask`)
- Everything else uses Python stdlib (wave, struct, zlib, sqlite3, hashlib)

## File Structure

```
bounty-2307-boot-chime/
  server.py       -- Flask server + FFT engine + profile database
  chime.html      -- Web UI (single-file, no build step)
  README.md       -- This file
  uploads/        -- Uploaded audio files (auto-created)
  spectrograms/   -- Generated spectrogram PNGs (auto-created)
  chimes.db       -- SQLite database (auto-created)
```

## RTC Wallet

`RTC_WALLET_ELROM_2307`

## License

MIT

---

*PoA-Signature: poa_chime2307_acoustic_attestation*

*"Most chains try to silence hardware. RustChain can use the literal voice of old machines as part of trust."*
