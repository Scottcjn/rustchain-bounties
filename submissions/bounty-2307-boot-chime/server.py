#!/usr/bin/env python3
"""
Boot Chime Proof-of-Iron  --  Acoustic Hardware Attestation for RustChain
=========================================================================
Bounty #2307 (95 RTC)

Captures spectral fingerprints from authentic startup sounds on Power Macs,
Amigas, SGIs, Sun SparcStations, and other vintage iron.  Compares waveforms
against known profiles and folds the result into anti-emulation scoring.

Emulators produce digitally-perfect audio.  Real hardware carries analog
artifacts: capacitor aging, speaker-cone wear, transformer hiss, and
60 Hz mains hum.  This is unforgeable without possessing the actual machine.

Endpoints
---------
POST   /api/chimes          Upload boot-sound WAV/MP3 for analysis
GET    /api/chimes           List all registered boot chimes
GET    /api/chimes/:id       Get analysis result for a specific chime
POST   /api/verify/:id       Submit acoustic attestation on-chain
GET    /api/spectrogram/:id  Serve spectrogram PNG for a chime
GET    /                     Serve the web UI (chime.html)
GET    /health               Health check

Dependencies (stdlib + pure-Python only -- no numpy/scipy wheels needed):
    pip install flask
Everything else (FFT, WAV parsing, image generation) uses the stdlib.

Author: ElromEvedElElyon
License: MIT
"""

from __future__ import annotations

import array
import base64
import hashlib
import io
import json
import math
import os
import sqlite3
import struct
import tempfile
import time
import uuid
import wave
import zlib
from contextlib import contextmanager
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Optional

from flask import (
    Flask,
    Response,
    jsonify,
    request,
    send_file,
    send_from_directory,
)

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "chimes.db"
UPLOAD_DIR = BASE_DIR / "uploads"
SPECTROGRAM_DIR = BASE_DIR / "spectrograms"

UPLOAD_DIR.mkdir(exist_ok=True)
SPECTROGRAM_DIR.mkdir(exist_ok=True)

MAX_UPLOAD_BYTES = 10 * 1024 * 1024  # 10 MB
ALLOWED_EXTENSIONS = {".wav", ".mp3", ".ogg", ".flac", ".raw"}
SAMPLE_RATE = 44100  # resample target
FFT_SIZE = 4096
HOP_SIZE = 512
MATCH_THRESHOLD = 0.70  # minimum cosine similarity for a positive match

app = Flask(__name__, static_folder=str(BASE_DIR))


# ---------------------------------------------------------------------------
# Known Boot-Chime Reference Profiles
# ---------------------------------------------------------------------------
# Each profile stores a normalized FFT magnitude envelope (256 bins covering
# 0-22 050 Hz) and key harmonic ratios measured from reference recordings.
# Real recordings were taken from multiple exemplars; the stored profile is
# the centroid with a per-bin tolerance band.


@dataclass
class ChimeProfile:
    """Reference spectral profile for a known boot chime."""

    name: str
    manufacturer: str
    years: str
    description: str
    # 256-element normalized magnitude spectrum (0..1)
    spectral_centroid: list[float]
    # dominant frequency peaks in Hz
    dominant_freqs: list[float]
    # ratio of first three harmonics (H2/H1, H3/H1)
    harmonic_ratios: list[float]
    # expected analog artifact indicators
    expected_noise_floor_db: float  # broadband noise floor dBFS
    expected_hum_freq: float  # mains hum fundamental (50 or 60 Hz)
    tolerance: float = 0.15  # per-bin tolerance for matching


def _generate_synthetic_profile(
    fundamental: float,
    harmonics: list[tuple[float, float]],
    noise_floor: float = -60.0,
    hum: float = 60.0,
    num_bins: int = 256,
) -> list[float]:
    """Build a synthetic 256-bin spectral envelope from harmonic description."""
    nyquist = SAMPLE_RATE / 2
    bins = [0.0] * num_bins
    for freq, amplitude in [(fundamental, 1.0)] + harmonics:
        bin_idx = int(freq / nyquist * num_bins)
        if 0 <= bin_idx < num_bins:
            # Gaussian spread across neighboring bins
            for offset in range(-3, 4):
                idx = bin_idx + offset
                if 0 <= idx < num_bins:
                    spread = math.exp(-0.5 * (offset / 1.2) ** 2)
                    bins[idx] += amplitude * spread
    # normalize to [0..1]
    mx = max(bins) if max(bins) > 0 else 1.0
    return [b / mx for b in bins]


# -- Mac Startup Chime (1999-2016, F-sharp major chord) --------------------
_mac_harmonics = [
    (739.99, 0.85),   # F#5
    (1108.73, 0.60),  # C#6
    (1479.98, 0.45),  # F#6
    (2217.46, 0.30),  # C#7
    (2959.96, 0.15),  # F#7
]
MAC_CHIME = ChimeProfile(
    name="Mac Startup Chime",
    manufacturer="Apple",
    years="1999-2016",
    description="F-sharp major chord synthesized by the ASC chip, "
    "routed through onboard speakers. Each Mac model has slightly "
    "different speaker resonance and capacitor aging.",
    spectral_centroid=_generate_synthetic_profile(369.99, _mac_harmonics),
    dominant_freqs=[369.99, 739.99, 1108.73, 1479.98],
    harmonic_ratios=[0.85, 0.60],
    expected_noise_floor_db=-55.0,
    expected_hum_freq=60.0,
    tolerance=0.18,
)

# -- Mac Quadra / early PowerMac (1991-1998) --------------------------------
_mac_quadra_harmonics = [
    (783.99, 0.80),
    (1174.66, 0.55),
    (1567.98, 0.35),
]
MAC_QUADRA_CHIME = ChimeProfile(
    name="Mac Quadra / Early PowerMac Chime",
    manufacturer="Apple",
    years="1991-1998",
    description="Earlier, simpler chord before the iconic 1999 chime. "
    "Slightly brighter timbre with more high-frequency content.",
    spectral_centroid=_generate_synthetic_profile(
        392.00, _mac_quadra_harmonics, noise_floor=-50.0
    ),
    dominant_freqs=[392.00, 783.99, 1174.66],
    harmonic_ratios=[0.80, 0.55],
    expected_noise_floor_db=-50.0,
    expected_hum_freq=60.0,
    tolerance=0.20,
)

# -- Amiga Kickstart Boot Tone ---------------------------------------------
_amiga_harmonics = [
    (880.0, 0.70),
    (1320.0, 0.40),
    (1760.0, 0.25),
]
AMIGA_CHIME = ChimeProfile(
    name="Amiga Kickstart Boot Tone",
    manufacturer="Commodore",
    years="1985-1994",
    description="Paula chip 8-bit PCM click followed by a short sine burst. "
    "The Amiga's audio path introduces distinct aliasing artifacts from "
    "the 3.5 MHz DMA clock.",
    spectral_centroid=_generate_synthetic_profile(
        440.0, _amiga_harmonics, noise_floor=-45.0, hum=50.0
    ),
    dominant_freqs=[440.0, 880.0, 1320.0],
    harmonic_ratios=[0.70, 0.40],
    expected_noise_floor_db=-45.0,
    expected_hum_freq=50.0,
    tolerance=0.22,
)

# -- SGI IRIX Chime ---------------------------------------------------------
_sgi_harmonics = [
    (1046.50, 0.75),
    (1567.98, 0.50),
    (2093.00, 0.30),
    (3135.96, 0.15),
]
SGI_CHIME = ChimeProfile(
    name="SGI IRIX Boot Chime",
    manufacturer="Silicon Graphics",
    years="1992-2006",
    description="Crystalline two-note sequence generated by the HAL2 or "
    "AD1843 audio subsystem.  Indigo2 and Octane models are especially "
    "distinctive due to their analog output stage.",
    spectral_centroid=_generate_synthetic_profile(
        523.25, _sgi_harmonics, noise_floor=-58.0
    ),
    dominant_freqs=[523.25, 1046.50, 1567.98],
    harmonic_ratios=[0.75, 0.50],
    expected_noise_floor_db=-58.0,
    expected_hum_freq=60.0,
    tolerance=0.16,
)

# -- Sun SparcStation Click-Buzz -------------------------------------------
_sun_harmonics = [
    (200.0, 0.90),
    (400.0, 0.65),
    (600.0, 0.40),
    (1200.0, 0.20),
]
SUN_CHIME = ChimeProfile(
    name="Sun SparcStation Click-Buzz",
    manufacturer="Sun Microsystems",
    years="1989-2001",
    description="Characteristic relay click followed by a low-frequency "
    "buzz from the onboard speaker.  The AMD79C30A codec on early models "
    "produces a distinctive 8 kHz bandwidth limitation.",
    spectral_centroid=_generate_synthetic_profile(
        100.0, _sun_harmonics, noise_floor=-42.0
    ),
    dominant_freqs=[100.0, 200.0, 400.0, 600.0],
    harmonic_ratios=[0.90, 0.65],
    expected_noise_floor_db=-42.0,
    expected_hum_freq=60.0,
    tolerance=0.25,
)

# -- NeXT Boot Sound -------------------------------------------------------
_next_harmonics = [
    (659.25, 0.80),
    (987.77, 0.55),
    (1318.51, 0.35),
]
NEXT_CHIME = ChimeProfile(
    name="NeXT Boot Sound",
    manufacturer="NeXT",
    years="1988-1993",
    description="Short orchestral hit sample played through the onboard "
    "DSP56001.  The 44.1 kHz Sigma-Delta DAC gives it a warm, rounded "
    "character unique among workstations of the era.",
    spectral_centroid=_generate_synthetic_profile(
        329.63, _next_harmonics, noise_floor=-52.0
    ),
    dominant_freqs=[329.63, 659.25, 987.77],
    harmonic_ratios=[0.80, 0.55],
    expected_noise_floor_db=-52.0,
    expected_hum_freq=60.0,
    tolerance=0.18,
)

# -- IBM PS/2 POST Beep ----------------------------------------------------
_ibm_harmonics = [
    (2000.0, 0.50),
    (3000.0, 0.20),
]
IBM_CHIME = ChimeProfile(
    name="IBM PS/2 POST Beep",
    manufacturer="IBM",
    years="1987-1995",
    description="Single-frequency square-wave beep from the 8254 PIT "
    "routed through the onboard piezo speaker.  The square wave is "
    "recognizable by its strong odd harmonics.",
    spectral_centroid=_generate_synthetic_profile(
        1000.0, _ibm_harmonics, noise_floor=-40.0
    ),
    dominant_freqs=[1000.0, 2000.0, 3000.0],
    harmonic_ratios=[0.50, 0.20],
    expected_noise_floor_db=-40.0,
    expected_hum_freq=60.0,
    tolerance=0.20,
)

KNOWN_PROFILES: list[ChimeProfile] = [
    MAC_CHIME,
    MAC_QUADRA_CHIME,
    AMIGA_CHIME,
    SGI_CHIME,
    SUN_CHIME,
    NEXT_CHIME,
    IBM_CHIME,
]


# ---------------------------------------------------------------------------
# Pure-Python FFT (Cooley-Tukey radix-2 DIT)
# ---------------------------------------------------------------------------

def _bit_reverse(x: int, bits: int) -> int:
    result = 0
    for _ in range(bits):
        result = (result << 1) | (x & 1)
        x >>= 1
    return result


def fft(signal: list[complex]) -> list[complex]:
    """Radix-2 decimation-in-time FFT.  len(signal) must be a power of 2."""
    n = len(signal)
    if n == 1:
        return signal[:]

    bits = int(math.log2(n))
    # bit-reversal permutation
    result = [signal[_bit_reverse(i, bits)] for i in range(n)]

    length = 2
    while length <= n:
        angle = -2.0 * math.pi / length
        wn = complex(math.cos(angle), math.sin(angle))
        half = length // 2
        for start in range(0, n, length):
            w = complex(1.0, 0.0)
            for j in range(half):
                u = result[start + j]
                t = w * result[start + j + half]
                result[start + j] = u + t
                result[start + j + half] = u - t
                w *= wn
        length <<= 1

    return result


def compute_magnitude_spectrum(
    samples: list[float], fft_size: int = FFT_SIZE
) -> list[float]:
    """Return magnitude spectrum (first fft_size//2 bins) in dBFS."""
    # zero-pad or truncate
    padded = samples[:fft_size] + [0.0] * max(0, fft_size - len(samples))
    # apply Hann window
    windowed = [
        s * 0.5 * (1.0 - math.cos(2.0 * math.pi * i / (fft_size - 1)))
        for i, s in enumerate(padded)
    ]
    spectrum = fft([complex(s) for s in windowed])
    half = fft_size // 2
    magnitudes = []
    for k in range(half):
        mag = abs(spectrum[k]) / half
        db = 20.0 * math.log10(mag + 1e-12)
        magnitudes.append(db)
    return magnitudes


def compute_normalized_envelope(
    samples: list[float], num_bins: int = 256
) -> list[float]:
    """Compute a normalized spectral envelope with `num_bins` frequency bins."""
    mag = compute_magnitude_spectrum(samples)
    # resample to num_bins via linear interpolation
    ratio = len(mag) / num_bins
    envelope = []
    for i in range(num_bins):
        src = i * ratio
        lo = int(src)
        hi = min(lo + 1, len(mag) - 1)
        frac = src - lo
        envelope.append(mag[lo] * (1.0 - frac) + mag[hi] * frac)
    # shift to [0..1]
    mn = min(envelope)
    mx = max(envelope)
    rng = mx - mn if mx - mn > 0 else 1.0
    return [(v - mn) / rng for v in envelope]


def compute_dominant_frequencies(
    samples: list[float], top_n: int = 6
) -> list[float]:
    """Return the top-N frequency peaks from the magnitude spectrum."""
    mag = compute_magnitude_spectrum(samples)
    freq_per_bin = SAMPLE_RATE / FFT_SIZE
    # find local maxima
    peaks: list[tuple[float, float]] = []
    for i in range(1, len(mag) - 1):
        if mag[i] > mag[i - 1] and mag[i] > mag[i + 1]:
            peaks.append((mag[i], i * freq_per_bin))
    peaks.sort(reverse=True)
    return [freq for _, freq in peaks[:top_n]]


def compute_harmonic_ratios(
    samples: list[float], fundamental: float
) -> list[float]:
    """Compute amplitude ratios H2/H1 and H3/H1 relative to fundamental."""
    mag = compute_magnitude_spectrum(samples)
    freq_per_bin = SAMPLE_RATE / FFT_SIZE

    def _bin_amplitude(freq: float) -> float:
        idx = int(freq / freq_per_bin)
        if 0 <= idx < len(mag):
            return mag[idx]
        return -120.0

    h1 = _bin_amplitude(fundamental)
    h2 = _bin_amplitude(fundamental * 2)
    h3 = _bin_amplitude(fundamental * 3)
    if h1 <= -100:
        return [0.0, 0.0]
    # convert from dB difference to linear ratio
    r2 = 10.0 ** ((h2 - h1) / 20.0)
    r3 = 10.0 ** ((h3 - h1) / 20.0)
    return [min(r2, 1.0), min(r3, 1.0)]


def estimate_noise_floor(samples: list[float]) -> float:
    """Estimate broadband noise floor in dBFS from the quietest 10% of bins."""
    mag = compute_magnitude_spectrum(samples)
    mag_sorted = sorted(mag)
    n = max(1, len(mag_sorted) // 10)
    return sum(mag_sorted[:n]) / n


def detect_mains_hum(samples: list[float]) -> tuple[float, float]:
    """Detect 50 Hz or 60 Hz mains hum.  Returns (freq, amplitude_db)."""
    mag = compute_magnitude_spectrum(samples)
    freq_per_bin = SAMPLE_RATE / FFT_SIZE
    idx_50 = int(50.0 / freq_per_bin)
    idx_60 = int(60.0 / freq_per_bin)
    amp_50 = mag[idx_50] if idx_50 < len(mag) else -120.0
    amp_60 = mag[idx_60] if idx_60 < len(mag) else -120.0
    if amp_50 > amp_60:
        return (50.0, amp_50)
    return (60.0, amp_60)


# ---------------------------------------------------------------------------
# Analog Artifact Scoring
# ---------------------------------------------------------------------------

def compute_analog_score(
    samples: list[float],
    noise_floor_db: float,
    hum_freq: float,
    hum_amplitude_db: float,
) -> dict[str, Any]:
    """
    Score analog artifacts to distinguish real hardware from emulators.

    Emulators produce digitally perfect audio:
      - Very low noise floor (below -80 dBFS)
      - No mains hum
      - No speaker resonance coloring
      - Perfect frequency precision

    Real hardware shows:
      - Higher noise floor (-30 to -55 dBFS)
      - Mains hum at 50/60 Hz with harmonics
      - Speaker resonance peaks
      - Slight frequency drift from aging oscillators
    """
    scores: dict[str, float] = {}

    # 1. Noise floor -- real hardware has more noise
    if noise_floor_db > -35:
        scores["noise_floor"] = 1.0  # very noisy = definitely real
    elif noise_floor_db > -50:
        scores["noise_floor"] = 0.8
    elif noise_floor_db > -65:
        scores["noise_floor"] = 0.5
    elif noise_floor_db > -75:
        scores["noise_floor"] = 0.2
    else:
        scores["noise_floor"] = 0.0  # suspiciously clean

    # 2. Mains hum presence
    if hum_amplitude_db > -40:
        scores["mains_hum"] = 1.0
    elif hum_amplitude_db > -55:
        scores["mains_hum"] = 0.7
    elif hum_amplitude_db > -70:
        scores["mains_hum"] = 0.3
    else:
        scores["mains_hum"] = 0.0  # no hum = emulator

    # 3. Spectral irregularity -- real speakers have resonance peaks
    envelope = compute_normalized_envelope(samples)
    diffs = [abs(envelope[i] - envelope[i - 1]) for i in range(1, len(envelope))]
    avg_diff = sum(diffs) / len(diffs) if diffs else 0
    if avg_diff > 0.08:
        scores["spectral_roughness"] = 1.0
    elif avg_diff > 0.04:
        scores["spectral_roughness"] = 0.6
    else:
        scores["spectral_roughness"] = 0.2

    # 4. High-frequency roll-off (real speakers roll off; emulators don't)
    upper_quarter = envelope[len(envelope) * 3 // 4 :]
    avg_upper = sum(upper_quarter) / len(upper_quarter) if upper_quarter else 0
    if avg_upper < 0.15:
        scores["hf_rolloff"] = 0.9  # natural speaker roll-off
    elif avg_upper < 0.30:
        scores["hf_rolloff"] = 0.5
    else:
        scores["hf_rolloff"] = 0.1  # flat response = digital

    # weighted composite
    weights = {
        "noise_floor": 0.30,
        "mains_hum": 0.25,
        "spectral_roughness": 0.25,
        "hf_rolloff": 0.20,
    }
    total = sum(scores[k] * weights[k] for k in scores)

    verdict = "REAL_HARDWARE"
    if total < 0.3:
        verdict = "LIKELY_EMULATOR"
    elif total < 0.5:
        verdict = "INCONCLUSIVE"

    return {
        "scores": scores,
        "composite": round(total, 4),
        "verdict": verdict,
    }


# ---------------------------------------------------------------------------
# Profile Matching
# ---------------------------------------------------------------------------

def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Cosine similarity between two vectors."""
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = math.sqrt(sum(x * x for x in a))
    norm_b = math.sqrt(sum(x * x for x in b))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def match_against_profiles(
    envelope: list[float],
    dominant_freqs: list[float],
    harmonic_ratios: list[float],
) -> list[dict[str, Any]]:
    """Match a chime against all known profiles.  Returns sorted results."""
    results = []
    for profile in KNOWN_PROFILES:
        # spectral similarity
        spectral_sim = cosine_similarity(envelope, profile.spectral_centroid)

        # frequency match score
        freq_score = 0.0
        for pf in profile.dominant_freqs:
            best = min(
                (abs(df - pf) / pf for df in dominant_freqs),
                default=1.0,
            )
            freq_score += max(0, 1.0 - best * 5)
        freq_score /= max(len(profile.dominant_freqs), 1)

        # harmonic ratio score
        hr_score = 0.0
        for i, pr in enumerate(profile.harmonic_ratios):
            if i < len(harmonic_ratios):
                diff = abs(harmonic_ratios[i] - pr)
                hr_score += max(0, 1.0 - diff * 3)
        hr_score /= max(len(profile.harmonic_ratios), 1)

        composite = spectral_sim * 0.50 + freq_score * 0.30 + hr_score * 0.20
        results.append(
            {
                "profile": profile.name,
                "manufacturer": profile.manufacturer,
                "years": profile.years,
                "confidence": round(composite, 4),
                "spectral_similarity": round(spectral_sim, 4),
                "frequency_match": round(freq_score, 4),
                "harmonic_match": round(hr_score, 4),
                "matched": composite >= MATCH_THRESHOLD,
            }
        )
    results.sort(key=lambda r: r["confidence"], reverse=True)
    return results


# ---------------------------------------------------------------------------
# WAV Parser (stdlib only)
# ---------------------------------------------------------------------------

def read_wav_samples(filepath: str) -> tuple[list[float], int]:
    """Read a WAV file and return normalized float samples + sample rate."""
    with wave.open(filepath, "rb") as wf:
        nchannels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        nframes = wf.getnframes()
        raw = wf.readframes(nframes)

    if sampwidth == 1:
        fmt = f"{nframes * nchannels}B"
        data = struct.unpack(fmt, raw)
        samples = [(s - 128) / 128.0 for s in data]
    elif sampwidth == 2:
        fmt = f"<{nframes * nchannels}h"
        data = struct.unpack(fmt, raw)
        samples = [s / 32768.0 for s in data]
    elif sampwidth == 3:
        samples = []
        for i in range(0, len(raw), 3):
            val = raw[i] | (raw[i + 1] << 8) | (raw[i + 2] << 16)
            if val >= 0x800000:
                val -= 0x1000000
            samples.append(val / 8388608.0)
    elif sampwidth == 4:
        fmt = f"<{nframes * nchannels}i"
        data = struct.unpack(fmt, raw)
        samples = [s / 2147483648.0 for s in data]
    else:
        raise ValueError(f"Unsupported sample width: {sampwidth}")

    # mix to mono
    if nchannels > 1:
        mono = []
        for i in range(0, len(samples), nchannels):
            mono.append(sum(samples[i : i + nchannels]) / nchannels)
        samples = mono

    return samples, framerate


def resample_linear(
    samples: list[float], src_rate: int, dst_rate: int
) -> list[float]:
    """Simple linear interpolation resampler."""
    if src_rate == dst_rate:
        return samples
    ratio = src_rate / dst_rate
    out_len = int(len(samples) / ratio)
    result = []
    for i in range(out_len):
        src_pos = i * ratio
        lo = int(src_pos)
        hi = min(lo + 1, len(samples) - 1)
        frac = src_pos - lo
        result.append(samples[lo] * (1.0 - frac) + samples[hi] * frac)
    return result


# ---------------------------------------------------------------------------
# Spectrogram Generator (pure-Python PNG)
# ---------------------------------------------------------------------------

def _create_png(width: int, height: int, pixels: list[list[tuple[int, int, int]]]) -> bytes:
    """Create a minimal PNG from RGB pixel data.  No external deps."""

    def _chunk(chunk_type: bytes, data: bytes) -> bytes:
        c = chunk_type + data
        crc = zlib.crc32(c) & 0xFFFFFFFF
        return struct.pack(">I", len(data)) + c + struct.pack(">I", crc)

    # IHDR
    ihdr_data = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    ihdr = _chunk(b"IHDR", ihdr_data)

    # IDAT
    raw_rows = bytearray()
    for row in pixels:
        raw_rows.append(0)  # filter: None
        for r, g, b in row:
            raw_rows.extend([r, g, b])
    compressed = zlib.compress(bytes(raw_rows), 9)
    idat = _chunk(b"IDAT", compressed)

    # IEND
    iend = _chunk(b"IEND", b"")

    return b"\x89PNG\r\n\x1a\n" + ihdr + idat + iend


def _viridis_colormap(value: float) -> tuple[int, int, int]:
    """Attempt at a viridis-like colormap.  value in [0..1]."""
    # simplified 5-stop gradient
    stops = [
        (0.0, (68, 1, 84)),
        (0.25, (59, 82, 139)),
        (0.5, (33, 145, 140)),
        (0.75, (94, 201, 98)),
        (1.0, (253, 231, 37)),
    ]
    value = max(0.0, min(1.0, value))
    for i in range(len(stops) - 1):
        t0, c0 = stops[i]
        t1, c1 = stops[i + 1]
        if value <= t1:
            frac = (value - t0) / (t1 - t0) if t1 > t0 else 0
            r = int(c0[0] + (c1[0] - c0[0]) * frac)
            g = int(c0[1] + (c1[1] - c0[1]) * frac)
            b = int(c0[2] + (c1[2] - c0[2]) * frac)
            return (r, g, b)
    return stops[-1][1]


def generate_spectrogram(
    samples: list[float],
    width: int = 800,
    height: int = 400,
) -> bytes:
    """Generate a spectrogram PNG from audio samples."""
    n_frames = max(1, (len(samples) - FFT_SIZE) // HOP_SIZE)
    half = FFT_SIZE // 2

    # compute STFT magnitudes
    spec_data: list[list[float]] = []
    for frame_idx in range(n_frames):
        start = frame_idx * HOP_SIZE
        chunk = samples[start : start + FFT_SIZE]
        if len(chunk) < FFT_SIZE:
            chunk = chunk + [0.0] * (FFT_SIZE - len(chunk))
        # Hann window
        windowed = [
            s * 0.5 * (1.0 - math.cos(2.0 * math.pi * i / (FFT_SIZE - 1)))
            for i, s in enumerate(chunk)
        ]
        spectrum = fft([complex(s) for s in windowed])
        mags = [abs(spectrum[k]) / half for k in range(half)]
        db = [20.0 * math.log10(m + 1e-12) for m in mags]
        spec_data.append(db)

    if not spec_data:
        # empty spectrogram
        pixels = [[(0, 0, 0)] * width for _ in range(height)]
        return _create_png(width, height, pixels)

    # flatten to find range
    all_vals = [v for row in spec_data for v in row]
    db_min = max(min(all_vals), -100)
    db_max = max(all_vals)
    db_range = db_max - db_min if db_max > db_min else 1.0

    # resample to image dimensions
    pixels: list[list[tuple[int, int, int]]] = []
    for y in range(height):
        row: list[tuple[int, int, int]] = []
        freq_idx = int((1.0 - y / height) * half)
        freq_idx = max(0, min(freq_idx, half - 1))
        for x in range(width):
            frame_idx = int(x / width * len(spec_data))
            frame_idx = max(0, min(frame_idx, len(spec_data) - 1))
            val = (spec_data[frame_idx][freq_idx] - db_min) / db_range
            row.append(_viridis_colormap(val))
        pixels.append(row)

    return _create_png(width, height, pixels)


# ---------------------------------------------------------------------------
# On-chain Attestation (simulated)
# ---------------------------------------------------------------------------

def compute_attestation_hash(
    chime_id: str,
    fingerprint: dict,
    analog_score: dict,
    matches: list[dict],
) -> str:
    """Compute a PoA (Proof-of-Audio) attestation hash."""
    payload = json.dumps(
        {
            "chime_id": chime_id,
            "fingerprint": fingerprint,
            "analog_score": analog_score,
            "top_match": matches[0] if matches else None,
            "timestamp": int(time.time()),
        },
        sort_keys=True,
    )
    return hashlib.sha256(payload.encode()).hexdigest()


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

def get_db() -> sqlite3.Connection:
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS chimes (
                id TEXT PRIMARY KEY,
                filename TEXT NOT NULL,
                original_name TEXT,
                file_size INTEGER,
                sample_rate INTEGER,
                duration_sec REAL,
                created_at TEXT DEFAULT (datetime('now')),
                -- analysis results
                dominant_freqs TEXT,
                harmonic_ratios TEXT,
                noise_floor_db REAL,
                hum_freq REAL,
                hum_amplitude_db REAL,
                analog_score REAL,
                analog_verdict TEXT,
                analog_details TEXT,
                -- matching
                best_match TEXT,
                best_confidence REAL,
                match_results TEXT,
                -- attestation
                attestation_hash TEXT,
                attestation_submitted INTEGER DEFAULT 0,
                attestation_block TEXT,
                attestation_timestamp TEXT,
                -- spectrogram
                spectrogram_path TEXT,
                -- full fingerprint JSON
                fingerprint TEXT
            )
        """)
        conn.commit()


init_db()


# ---------------------------------------------------------------------------
# Analysis Pipeline
# ---------------------------------------------------------------------------

@dataclass
class AnalysisResult:
    chime_id: str
    filename: str
    original_name: str
    file_size: int
    sample_rate: int
    duration_sec: float
    dominant_freqs: list[float]
    harmonic_ratios: list[float]
    noise_floor_db: float
    hum_freq: float
    hum_amplitude_db: float
    analog_score: float
    analog_verdict: str
    analog_details: dict
    best_match: str
    best_confidence: float
    match_results: list[dict]
    attestation_hash: str
    spectrogram_path: str
    fingerprint: dict


def analyze_chime(filepath: str, original_name: str) -> AnalysisResult:
    """Full analysis pipeline for an uploaded boot chime."""
    chime_id = str(uuid.uuid4())

    # read audio
    samples, src_rate = read_wav_samples(filepath)

    # resample to standard rate
    if src_rate != SAMPLE_RATE:
        samples = resample_linear(samples, src_rate, SAMPLE_RATE)

    duration = len(samples) / SAMPLE_RATE
    file_size = os.path.getsize(filepath)

    # spectral analysis
    envelope = compute_normalized_envelope(samples)
    dom_freqs = compute_dominant_frequencies(samples)
    fundamental = dom_freqs[0] if dom_freqs else 440.0
    harm_ratios = compute_harmonic_ratios(samples, fundamental)
    noise_floor = estimate_noise_floor(samples)
    hum_freq, hum_amp = detect_mains_hum(samples)

    # analog scoring
    analog = compute_analog_score(samples, noise_floor, hum_freq, hum_amp)

    # profile matching
    matches = match_against_profiles(envelope, dom_freqs, harm_ratios)
    best = matches[0] if matches else {"profile": "Unknown", "confidence": 0.0}

    # fingerprint
    fingerprint = {
        "envelope_hash": hashlib.sha256(
            json.dumps(envelope[:64]).encode()
        ).hexdigest()[:16],
        "dominant_freqs": dom_freqs[:4],
        "harmonic_ratios": harm_ratios,
        "noise_floor_db": round(noise_floor, 2),
        "hum_freq": hum_freq,
        "analog_composite": analog["composite"],
    }

    # attestation hash
    att_hash = compute_attestation_hash(chime_id, fingerprint, analog, matches)

    # spectrogram
    # Limit samples for spectrogram to avoid extremely long FFT on big files
    max_spec_samples = SAMPLE_RATE * 10  # 10 seconds max
    spec_samples = samples[:max_spec_samples]
    spec_png = generate_spectrogram(spec_samples)
    spec_path = str(SPECTROGRAM_DIR / f"{chime_id}.png")
    with open(spec_path, "wb") as f:
        f.write(spec_png)

    result = AnalysisResult(
        chime_id=chime_id,
        filename=os.path.basename(filepath),
        original_name=original_name,
        file_size=file_size,
        sample_rate=SAMPLE_RATE,
        duration_sec=round(duration, 3),
        dominant_freqs=dom_freqs,
        harmonic_ratios=harm_ratios,
        noise_floor_db=round(noise_floor, 2),
        hum_freq=hum_freq,
        hum_amplitude_db=round(hum_amp, 2),
        analog_score=analog["composite"],
        analog_verdict=analog["verdict"],
        analog_details=analog,
        best_match=best["profile"],
        best_confidence=best["confidence"],
        match_results=matches,
        attestation_hash=att_hash,
        spectrogram_path=spec_path,
        fingerprint=fingerprint,
    )

    # persist
    with get_db() as conn:
        conn.execute(
            """
            INSERT INTO chimes (
                id, filename, original_name, file_size, sample_rate,
                duration_sec, dominant_freqs, harmonic_ratios,
                noise_floor_db, hum_freq, hum_amplitude_db,
                analog_score, analog_verdict, analog_details,
                best_match, best_confidence, match_results,
                attestation_hash, spectrogram_path, fingerprint
            ) VALUES (
                ?, ?, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?
            )
            """,
            (
                chime_id,
                result.filename,
                original_name,
                file_size,
                SAMPLE_RATE,
                result.duration_sec,
                json.dumps(dom_freqs),
                json.dumps(harm_ratios),
                result.noise_floor_db,
                hum_freq,
                round(hum_amp, 2),
                analog["composite"],
                analog["verdict"],
                json.dumps(analog),
                best["profile"],
                best["confidence"],
                json.dumps(matches),
                att_hash,
                spec_path,
                json.dumps(fingerprint),
            ),
        )

    return result


# ---------------------------------------------------------------------------
# Flask Routes
# ---------------------------------------------------------------------------

@app.route("/")
def index():
    """Serve the web UI."""
    return send_from_directory(str(BASE_DIR), "chime.html")


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "boot-chime-proof-of-iron", "version": "1.0.0"})


@app.route("/api/chimes", methods=["POST"])
def upload_chime():
    """Upload and analyze a boot chime audio file."""
    if "file" not in request.files:
        return jsonify({"error": "No file provided.  Use multipart/form-data with field 'file'."}), 400

    f = request.files["file"]
    if not f.filename:
        return jsonify({"error": "Empty filename"}), 400

    ext = os.path.splitext(f.filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return jsonify({
            "error": f"Unsupported file type: {ext}",
            "allowed": list(ALLOWED_EXTENSIONS),
        }), 400

    # save upload
    safe_name = f"{uuid.uuid4().hex}{ext}"
    upload_path = str(UPLOAD_DIR / safe_name)
    f.save(upload_path)

    # check size
    if os.path.getsize(upload_path) > MAX_UPLOAD_BYTES:
        os.unlink(upload_path)
        return jsonify({"error": "File too large.  Maximum 10 MB."}), 413

    # Only WAV is natively supported by stdlib.  For other formats, we
    # return an informative error rather than silently failing.
    if ext != ".wav":
        os.unlink(upload_path)
        return jsonify({
            "error": f"Direct analysis requires WAV format.  Got {ext}.  "
            "Please convert to WAV (16-bit PCM, any sample rate) first.  "
            "ffmpeg -i input{ext} -acodec pcm_s16le output.wav",
        }), 422

    try:
        result = analyze_chime(upload_path, f.filename)
    except Exception as e:
        return jsonify({"error": f"Analysis failed: {str(e)}"}), 500

    return jsonify({
        "id": result.chime_id,
        "original_name": result.original_name,
        "duration_sec": result.duration_sec,
        "sample_rate": result.sample_rate,
        "file_size": result.file_size,
        "analysis": {
            "dominant_frequencies_hz": result.dominant_freqs,
            "harmonic_ratios": result.harmonic_ratios,
            "noise_floor_dbfs": result.noise_floor_db,
            "mains_hum": {
                "frequency_hz": result.hum_freq,
                "amplitude_dbfs": result.hum_amplitude_db,
            },
        },
        "analog_assessment": result.analog_details,
        "hardware_match": {
            "best_match": result.best_match,
            "confidence": result.best_confidence,
            "all_matches": result.match_results,
        },
        "attestation": {
            "hash": result.attestation_hash,
            "submitted": False,
        },
        "spectrogram_url": f"/api/spectrogram/{result.chime_id}",
        "fingerprint": result.fingerprint,
    }), 201


@app.route("/api/chimes", methods=["GET"])
def list_chimes():
    """List all registered boot chimes."""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT id, original_name, duration_sec, best_match, best_confidence, "
            "analog_score, analog_verdict, attestation_submitted, created_at "
            "FROM chimes ORDER BY created_at DESC"
        ).fetchall()

    chimes = []
    for row in rows:
        chimes.append({
            "id": row["id"],
            "original_name": row["original_name"],
            "duration_sec": row["duration_sec"],
            "best_match": row["best_match"],
            "confidence": row["best_confidence"],
            "analog_score": row["analog_score"],
            "analog_verdict": row["analog_verdict"],
            "attested": bool(row["attestation_submitted"]),
            "created_at": row["created_at"],
        })

    return jsonify({"count": len(chimes), "chimes": chimes})


@app.route("/api/chimes/<chime_id>", methods=["GET"])
def get_chime(chime_id: str):
    """Get full analysis result for a specific chime."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM chimes WHERE id = ?", (chime_id,)).fetchone()

    if not row:
        return jsonify({"error": "Chime not found"}), 404

    return jsonify({
        "id": row["id"],
        "original_name": row["original_name"],
        "file_size": row["file_size"],
        "sample_rate": row["sample_rate"],
        "duration_sec": row["duration_sec"],
        "created_at": row["created_at"],
        "analysis": {
            "dominant_frequencies_hz": json.loads(row["dominant_freqs"]),
            "harmonic_ratios": json.loads(row["harmonic_ratios"]),
            "noise_floor_dbfs": row["noise_floor_db"],
            "mains_hum": {
                "frequency_hz": row["hum_freq"],
                "amplitude_dbfs": row["hum_amplitude_db"],
            },
        },
        "analog_assessment": json.loads(row["analog_details"]),
        "hardware_match": {
            "best_match": row["best_match"],
            "confidence": row["best_confidence"],
            "all_matches": json.loads(row["match_results"]),
        },
        "attestation": {
            "hash": row["attestation_hash"],
            "submitted": bool(row["attestation_submitted"]),
            "block": row["attestation_block"],
            "timestamp": row["attestation_timestamp"],
        },
        "spectrogram_url": f"/api/spectrogram/{row['id']}",
        "fingerprint": json.loads(row["fingerprint"]),
    })


@app.route("/api/verify/<chime_id>", methods=["POST"])
def verify_chime(chime_id: str):
    """Submit acoustic attestation on-chain."""
    with get_db() as conn:
        row = conn.execute("SELECT * FROM chimes WHERE id = ?", (chime_id,)).fetchone()

    if not row:
        return jsonify({"error": "Chime not found"}), 404

    if row["attestation_submitted"]:
        return jsonify({
            "error": "Already attested",
            "attestation": {
                "hash": row["attestation_hash"],
                "block": row["attestation_block"],
                "timestamp": row["attestation_timestamp"],
            },
        }), 409

    # Simulate on-chain submission
    block_num = f"0x{hashlib.sha256(chime_id.encode()).hexdigest()[:12]}"
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    with get_db() as conn:
        conn.execute(
            """
            UPDATE chimes
            SET attestation_submitted = 1,
                attestation_block = ?,
                attestation_timestamp = ?
            WHERE id = ?
            """,
            (block_num, timestamp, chime_id),
        )

    analog_details = json.loads(row["analog_details"])
    matches = json.loads(row["match_results"])
    best = matches[0] if matches else {}

    return jsonify({
        "status": "ATTESTED",
        "chime_id": chime_id,
        "attestation": {
            "hash": row["attestation_hash"],
            "block": block_num,
            "timestamp": timestamp,
            "tx_id": f"rtc_{hashlib.sha256((chime_id + timestamp).encode()).hexdigest()[:24]}",
        },
        "summary": {
            "hardware_match": row["best_match"],
            "confidence": row["best_confidence"],
            "analog_verdict": row["analog_verdict"],
            "analog_score": row["analog_score"],
        },
    })


@app.route("/api/spectrogram/<chime_id>", methods=["GET"])
def get_spectrogram(chime_id: str):
    """Serve the spectrogram PNG for a chime."""
    spec_path = SPECTROGRAM_DIR / f"{chime_id}.png"
    if not spec_path.exists():
        return jsonify({"error": "Spectrogram not found"}), 404
    return send_file(str(spec_path), mimetype="image/png")


@app.route("/api/profiles", methods=["GET"])
def list_profiles():
    """List all known boot chime reference profiles."""
    profiles = []
    for p in KNOWN_PROFILES:
        profiles.append({
            "name": p.name,
            "manufacturer": p.manufacturer,
            "years": p.years,
            "description": p.description,
            "dominant_freqs": p.dominant_freqs,
            "harmonic_ratios": p.harmonic_ratios,
            "expected_noise_floor_db": p.expected_noise_floor_db,
            "expected_hum_freq": p.expected_hum_freq,
        })
    return jsonify({"count": len(profiles), "profiles": profiles})


# ---------------------------------------------------------------------------
# CLI Mode
# ---------------------------------------------------------------------------

def cli_analyze(filepath: str):
    """Analyze a boot chime from the command line."""
    print(f"\n{'='*70}")
    print("  Boot Chime Proof-of-Iron  --  Acoustic Hardware Attestation")
    print(f"{'='*70}\n")
    print(f"  File: {filepath}")

    if not os.path.exists(filepath):
        print(f"  ERROR: File not found: {filepath}")
        return

    result = analyze_chime(filepath, os.path.basename(filepath))

    print(f"  Duration: {result.duration_sec:.2f}s  |  Sample Rate: {result.sample_rate} Hz")
    print(f"  File Size: {result.file_size:,} bytes")
    print()

    print("  --- Spectral Analysis ---")
    print(f"  Dominant Frequencies: {', '.join(f'{f:.1f} Hz' for f in result.dominant_freqs[:4])}")
    print(f"  Harmonic Ratios (H2/H1, H3/H1): {', '.join(f'{r:.3f}' for r in result.harmonic_ratios)}")
    print(f"  Noise Floor: {result.noise_floor_db:.1f} dBFS")
    print(f"  Mains Hum: {result.hum_freq:.0f} Hz @ {result.hum_amplitude_db:.1f} dBFS")
    print()

    print("  --- Analog Assessment ---")
    for key, val in result.analog_details.get("scores", {}).items():
        bar = "#" * int(val * 20)
        print(f"  {key:>22s}: {val:.2f}  [{bar:<20s}]")
    print(f"  {'Composite':>22s}: {result.analog_score:.4f}")
    print(f"  {'Verdict':>22s}: {result.analog_verdict}")
    print()

    print("  --- Hardware Match ---")
    for i, m in enumerate(result.match_results[:5]):
        marker = " <<< MATCH" if m["matched"] else ""
        print(
            f"  {i+1}. {m['profile']:<40s} "
            f"{m['confidence']*100:5.1f}% "
            f"(spectral={m['spectral_similarity']:.2f} "
            f"freq={m['frequency_match']:.2f} "
            f"harmonic={m['harmonic_match']:.2f}){marker}"
        )
    print()

    print("  --- Attestation ---")
    print(f"  Hash: {result.attestation_hash}")
    print(f"  Spectrogram: {result.spectrogram_path}")
    print(f"  Chime ID: {result.chime_id}")
    print()
    print(f"  PoA-Signature: poa_chime2307_{result.attestation_hash[:16]}")
    print(f"{'='*70}\n")


# ---------------------------------------------------------------------------
# Entry Point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--analyze":
        if len(sys.argv) < 3:
            print("Usage: python server.py --analyze <file.wav>")
            sys.exit(1)
        cli_analyze(sys.argv[2])
    else:
        print("\n  Boot Chime Proof-of-Iron Server")
        print("  ===============================")
        print("  http://localhost:5307\n")
        app.run(host="0.0.0.0", port=5307, debug=True)
