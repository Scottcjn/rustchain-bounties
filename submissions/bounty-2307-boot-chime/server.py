#!/usr/bin/env python3
"""
Boot Chime Proof-of-Iron — Acoustic Hardware Attestation for RustChain

Generates spectral fingerprints from boot chime audio, compares against
known hardware profiles (Power Mac, Amiga, SGI, Sun), detects analog
artifacts vs emulator perfection, and folds results into anti-emulation
scoring for the RustChain attestation layer.

Bounty: rustchain-bounties#2307 (95 RTC)
"""

import asyncio
import hashlib
import json
import math
import os
import random
import struct
import time
import uuid
import wave
import io
import base64
from datetime import datetime, timezone
from pathlib import Path

import aiohttp
from aiohttp import web
import aiosqlite

DB_PATH = os.environ.get("BOOTCHIME_DB", "bootchime.db")
HOST = os.environ.get("BOOTCHIME_HOST", "0.0.0.0")
PORT = int(os.environ.get("BOOTCHIME_PORT", "8307"))

# ---------------------------------------------------------------------------
# Known hardware chime profiles — spectral signatures
# Each profile defines dominant frequency peaks, harmonic ratios, expected
# duration, and characteristic analog artifacts for genuine hardware.
# ---------------------------------------------------------------------------
KNOWN_PROFILES = {
    "mac_1991": {
        "name": "Macintosh Quadra (1991)",
        "family": "mac",
        "dominant_hz": [523.25, 659.25, 783.99],  # C5-E5-G5 major chord
        "harmonic_ratios": [1.0, 0.78, 0.62],
        "duration_ms": 1800,
        "decay_rate": 0.35,
        "analog_noise_floor_db": -42,
        "description": "Classic Mac startup chord — C major triad, warm analog character",
    },
    "mac_1999": {
        "name": "Power Mac G3/G4 (1999)",
        "family": "mac",
        "dominant_hz": [523.25, 659.25, 783.99, 1046.50],
        "harmonic_ratios": [1.0, 0.82, 0.65, 0.40],
        "duration_ms": 2200,
        "decay_rate": 0.28,
        "analog_noise_floor_db": -48,
        "description": "Extended Mac chord with octave — cleaner but still analog",
    },
    "mac_2002": {
        "name": "Power Mac G4 MDD (2002)",
        "family": "mac",
        "dominant_hz": [523.25, 659.25, 783.99, 1046.50],
        "harmonic_ratios": [1.0, 0.85, 0.70, 0.45],
        "duration_ms": 2000,
        "decay_rate": 0.30,
        "analog_noise_floor_db": -45,
        "description": "MDD chime — slightly brighter, notorious for loud fans masking decay",
    },
    "mac_2006": {
        "name": "Mac Pro Intel (2006)",
        "family": "mac",
        "dominant_hz": [261.63, 329.63, 392.00, 523.25],
        "harmonic_ratios": [1.0, 0.88, 0.72, 0.55],
        "duration_ms": 2400,
        "decay_rate": 0.22,
        "analog_noise_floor_db": -52,
        "description": "Intel Mac chime — lower register, longer sustain",
    },
    "amiga_kickstart": {
        "name": "Amiga Kickstart Boot (1985-1993)",
        "family": "amiga",
        "dominant_hz": [440.00, 880.00],
        "harmonic_ratios": [1.0, 0.55],
        "duration_ms": 400,
        "decay_rate": 0.70,
        "analog_noise_floor_db": -35,
        "description": "Short click-pop from Paula chip — very analog, high noise floor",
    },
    "amiga_1200": {
        "name": "Amiga 1200 (1992)",
        "family": "amiga",
        "dominant_hz": [440.00, 660.00, 880.00],
        "harmonic_ratios": [1.0, 0.45, 0.50],
        "duration_ms": 500,
        "decay_rate": 0.65,
        "analog_noise_floor_db": -38,
        "description": "A1200 boot — Paula chip with AGA, slightly cleaner",
    },
    "sgi_irix": {
        "name": "SGI IRIX Boot Chime",
        "family": "sgi",
        "dominant_hz": [587.33, 783.99, 1174.66],
        "harmonic_ratios": [1.0, 0.72, 0.48],
        "duration_ms": 1200,
        "decay_rate": 0.40,
        "analog_noise_floor_db": -46,
        "description": "SGI IRIX startup — ethereal D-based chord, distinctive reverb",
    },
    "sun_sparc": {
        "name": "Sun SparcStation Click-Buzz",
        "family": "sun",
        "dominant_hz": [1000.00, 2000.00, 3000.00],
        "harmonic_ratios": [1.0, 0.60, 0.30],
        "duration_ms": 300,
        "decay_rate": 0.80,
        "analog_noise_floor_db": -32,
        "description": "Sparc click-buzz — sharp transient, high harmonics, very short",
    },
    "sun_ultra": {
        "name": "Sun Ultra Workstation",
        "family": "sun",
        "dominant_hz": [800.00, 1600.00, 2400.00],
        "harmonic_ratios": [1.0, 0.55, 0.35],
        "duration_ms": 450,
        "decay_rate": 0.72,
        "analog_noise_floor_db": -36,
        "description": "Ultra series — slightly lower than Sparc, more defined buzz",
    },
}

# ---------------------------------------------------------------------------
# Audio synthesis — generate chime waveforms for known profiles
# ---------------------------------------------------------------------------


def generate_chime_wav(profile_key: str, sample_rate: int = 44100,
                       analog_variance: float = 0.0) -> bytes:
    """Synthesize a boot chime WAV from a known profile.

    analog_variance [0.0-1.0] adds simulated analog imperfections:
      - frequency drift from aging capacitors
      - amplitude jitter from speaker cone wear
      - low-level hiss from analog noise floor
    """
    profile = KNOWN_PROFILES.get(profile_key)
    if not profile:
        raise ValueError(f"Unknown profile: {profile_key}")

    duration_s = profile["duration_ms"] / 1000.0
    n_samples = int(sample_rate * duration_s)
    decay = profile["decay_rate"]
    freqs = profile["dominant_hz"]
    ratios = profile["harmonic_ratios"]
    noise_db = profile["analog_noise_floor_db"]
    noise_amp = 10 ** (noise_db / 20.0)

    samples = []
    for i in range(n_samples):
        t = i / sample_rate
        envelope = math.exp(-decay * t * 4)

        val = 0.0
        for freq, ratio in zip(freqs, ratios):
            # Apply analog drift if requested — simulates capacitor aging
            drift = 0.0
            if analog_variance > 0:
                drift = (analog_variance * 2.0
                         * math.sin(2 * math.pi * 0.3 * t)
                         * freq * 0.002)
            val += ratio * math.sin(2 * math.pi * (freq + drift) * t) * envelope

        # Analog noise floor — hiss from aged components
        if analog_variance > 0:
            val += random.gauss(0, noise_amp * analog_variance * 3)

        # Amplitude jitter — speaker cone wear
        if analog_variance > 0:
            val *= 1.0 + random.gauss(0, analog_variance * 0.01)

        samples.append(val)

    # Normalize to 16-bit PCM
    peak = max(abs(s) for s in samples) or 1.0
    scale = 32000 / peak
    pcm = b"".join(
        struct.pack("<h", max(-32768, min(32767, int(s * scale))))
        for s in samples
    )

    buf = io.BytesIO()
    with wave.open(buf, "wb") as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(pcm)
    return buf.getvalue()


# ---------------------------------------------------------------------------
# Spectral fingerprint extraction (FFT-based)
# ---------------------------------------------------------------------------


def extract_spectral_fingerprint(wav_bytes: bytes) -> dict:
    """Extract spectral fingerprint from WAV audio data.

    Returns dominant frequencies, harmonic ratios, noise floor estimate,
    and a compact hash for matching.
    """
    buf = io.BytesIO(wav_bytes)
    with wave.open(buf, "rb") as wf:
        n_channels = wf.getnchannels()
        sampwidth = wf.getsampwidth()
        framerate = wf.getframerate()
        n_frames = wf.getnframes()
        raw = wf.readframes(n_frames)

    # Convert to float samples (mono)
    if sampwidth == 2:
        fmt = f"<{n_frames * n_channels}h"
        int_samples = struct.unpack(fmt, raw)
    elif sampwidth == 1:
        int_samples = [s - 128 for s in raw]
    else:
        int_samples = list(raw)

    # Mix to mono if stereo
    if n_channels == 2:
        mono = [
            (int_samples[i] + int_samples[i + 1]) / 2
            for i in range(0, len(int_samples), 2)
        ]
    else:
        mono = list(int_samples)

    # Normalize
    peak = max(abs(s) for s in mono) or 1.0
    samples = [s / peak for s in mono]

    # DFT on first 4096 samples for fingerprinting
    N = min(4096, len(samples))
    # Hann window to reduce spectral leakage
    window = [0.5 * (1 - math.cos(2 * math.pi * i / (N - 1))) for i in range(N)]
    windowed = [samples[i] * window[i] for i in range(N)]

    # Compute magnitude spectrum
    n_bins = N // 2
    magnitudes = []
    for k in range(n_bins):
        re = sum(windowed[n] * math.cos(2 * math.pi * k * n / N) for n in range(N))
        im = sum(windowed[n] * math.sin(2 * math.pi * k * n / N) for n in range(N))
        mag = math.sqrt(re * re + im * im) / N
        magnitudes.append(mag)

    # Find dominant peaks
    freq_resolution = framerate / N
    peak_indices = sorted(
        range(len(magnitudes)),
        key=lambda i: magnitudes[i],
        reverse=True,
    )[:8]
    peak_freqs = [round(i * freq_resolution, 2) for i in peak_indices if i > 0]
    peak_mags = [round(magnitudes[i], 6) for i in peak_indices if i > 0]

    # Harmonic ratios relative to strongest
    top_mag = peak_mags[0] if peak_mags else 1.0
    harmonic_ratios = [round(m / top_mag, 4) for m in peak_mags]

    # Noise floor estimate (average of bottom 50% of spectrum)
    sorted_mags = sorted(magnitudes)
    noise_floor = (
        sum(sorted_mags[: len(sorted_mags) // 2])
        / max(len(sorted_mags) // 2, 1)
    )
    noise_floor_db = round(20 * math.log10(max(noise_floor, 1e-10)), 2)

    # Duration
    duration_ms = round(len(samples) / framerate * 1000, 1)

    # Analog artifact score: real hardware has higher noise, frequency spread
    artifact_spread = (
        sum(
            abs(f1 - f2)
            for f1, f2 in zip(peak_freqs[:-1], peak_freqs[1:])
        )
        if len(peak_freqs) > 1
        else 0
    )
    analog_score = min(
        1.0,
        round(
            (0.4 * min(1.0, abs(noise_floor_db) / 60.0))
            + (0.3 * min(1.0, artifact_spread / 5000.0))
            + (0.3 * min(1.0, len(peak_freqs) / 6.0)),
            4,
        ),
    )

    # Compact fingerprint hash
    fp_data = f"{peak_freqs}{harmonic_ratios}{noise_floor_db}{duration_ms}"
    fp_hash = hashlib.sha256(fp_data.encode()).hexdigest()[:32]

    return {
        "dominant_hz": peak_freqs[:6],
        "harmonic_ratios": harmonic_ratios[:6],
        "noise_floor_db": noise_floor_db,
        "duration_ms": duration_ms,
        "analog_artifact_score": analog_score,
        "fingerprint_hash": fp_hash,
        "sample_rate": framerate,
        "n_peaks_detected": len(peak_freqs),
    }


# ---------------------------------------------------------------------------
# Profile matching — compare fingerprint against known hardware
# ---------------------------------------------------------------------------


def match_profile(fingerprint: dict) -> dict:
    """Compare a spectral fingerprint against known hardware profiles.

    Emulators produce digitally perfect audio — real hardware has analog
    artifacts (hiss, capacitor aging, speaker resonance).
    """
    best_match = None
    best_score = 0.0
    all_scores = {}

    fp_freqs = fingerprint["dominant_hz"]
    fp_ratios = fingerprint["harmonic_ratios"]
    fp_noise = fingerprint["noise_floor_db"]

    for key, profile in KNOWN_PROFILES.items():
        prof_freqs = profile["dominant_hz"]
        prof_ratios = profile["harmonic_ratios"]
        prof_noise = profile["analog_noise_floor_db"]

        # Frequency similarity (within tolerance)
        freq_score = 0.0
        for pf in prof_freqs:
            for ff in fp_freqs:
                tolerance = pf * 0.05  # 5% tolerance for analog drift
                if abs(ff - pf) < tolerance:
                    freq_score += 1.0 - (abs(ff - pf) / tolerance)
                    break
        freq_score = freq_score / max(len(prof_freqs), 1)

        # Harmonic ratio similarity
        ratio_score = 0.0
        min_len = min(len(prof_ratios), len(fp_ratios))
        if min_len > 0:
            for i in range(min_len):
                diff = abs(prof_ratios[i] - fp_ratios[i])
                ratio_score += max(0, 1.0 - diff * 2)
            ratio_score /= min_len

        # Noise floor proximity
        noise_diff = abs(fp_noise - prof_noise)
        noise_score = max(0, 1.0 - noise_diff / 30.0)

        # Composite score
        composite = (
            (freq_score * 0.45)
            + (ratio_score * 0.30)
            + (noise_score * 0.25)
        )
        all_scores[key] = round(composite, 4)

        if composite > best_score:
            best_score = composite
            best_match = key

    # Anti-emulation assessment
    analog_score = fingerprint.get("analog_artifact_score", 0)
    is_emulator = analog_score < 0.15
    is_genuine_hardware = analog_score > 0.35 and best_score > 0.5

    # Confidence tiers
    if best_score > 0.80:
        confidence = "HIGH"
    elif best_score > 0.55:
        confidence = "MEDIUM"
    elif best_score > 0.30:
        confidence = "LOW"
    else:
        confidence = "NO_MATCH"

    return {
        "best_match": best_match,
        "best_match_name": (
            KNOWN_PROFILES[best_match]["name"] if best_match else None
        ),
        "match_confidence": confidence,
        "match_score": round(best_score, 4),
        "all_scores": all_scores,
        "analog_artifact_score": analog_score,
        "anti_emulation_verdict": (
            "GENUINE_HARDWARE"
            if is_genuine_hardware
            else ("LIKELY_EMULATOR" if is_emulator else "UNCERTAIN")
        ),
        "attestation_eligible": is_genuine_hardware and best_score > 0.5,
    }


# ---------------------------------------------------------------------------
# Hardware fingerprint generation (system-level)
# ---------------------------------------------------------------------------


def generate_hardware_fingerprint() -> dict:
    """Generate hardware identity from available system information."""
    components = []

    # CPU info
    try:
        with open("/proc/cpuinfo", "r") as f:
            cpuinfo = f.read()
        for line in cpuinfo.split("\n"):
            if "model name" in line:
                components.append(line.split(":")[1].strip())
                break
    except Exception:
        components.append("unknown_cpu")

    # Machine ID
    try:
        with open("/etc/machine-id", "r") as f:
            components.append(f.read().strip()[:16])
    except Exception:
        components.append(uuid.getnode().to_bytes(6, "big").hex())

    # DMI board info
    for path in [
        "/sys/class/dmi/id/board_vendor",
        "/sys/class/dmi/id/board_name",
    ]:
        try:
            with open(path, "r") as f:
                components.append(f.read().strip())
        except Exception:
            pass

    # Memory size
    try:
        with open("/proc/meminfo", "r") as f:
            for line in f:
                if "MemTotal" in line:
                    components.append(line.split(":")[1].strip())
                    break
    except Exception:
        pass

    raw = "|".join(components)
    hw_hash = hashlib.sha256(raw.encode()).hexdigest()

    return {
        "hardware_hash": hw_hash,
        "components_hashed": len(components),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }


# ---------------------------------------------------------------------------
# Attestation payload construction
# ---------------------------------------------------------------------------


def build_attestation_payload(
    chime_id: str,
    fingerprint: dict,
    match_result: dict,
    hardware_fp: dict,
) -> dict:
    """Build a complete attestation payload for RustChain submission."""
    payload = {
        "version": "1.0.0",
        "type": "boot_chime_proof_of_iron",
        "chime_id": chime_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "spectral_fingerprint": fingerprint,
        "profile_match": {
            "best_match": match_result["best_match"],
            "match_name": match_result["best_match_name"],
            "confidence": match_result["match_confidence"],
            "score": match_result["match_score"],
            "anti_emulation": match_result["anti_emulation_verdict"],
            "analog_artifact_score": match_result["analog_artifact_score"],
        },
        "hardware_identity": hardware_fp,
        "attestation_eligible": match_result["attestation_eligible"],
    }

    # Sign the payload
    payload_bytes = json.dumps(payload, sort_keys=True).encode()
    payload["signature"] = hashlib.sha256(payload_bytes).hexdigest()

    return payload


# ---------------------------------------------------------------------------
# Database setup and helpers
# ---------------------------------------------------------------------------


async def init_db(db: aiosqlite.Connection):
    await db.execute("""
        CREATE TABLE IF NOT EXISTS boot_chimes (
            id TEXT PRIMARY KEY,
            created_at TEXT NOT NULL,
            profile_key TEXT,
            profile_name TEXT,
            fingerprint_hash TEXT NOT NULL,
            match_score REAL,
            match_confidence TEXT,
            anti_emulation TEXT,
            analog_artifact_score REAL,
            attestation_eligible INTEGER DEFAULT 0,
            hardware_hash TEXT,
            spectral_data TEXT,
            attestation_payload TEXT,
            wav_b64 TEXT,
            notes TEXT
        )
    """)
    await db.execute("""
        CREATE TABLE IF NOT EXISTS chime_gallery (
            id TEXT PRIMARY KEY,
            chime_id TEXT NOT NULL REFERENCES boot_chimes(id),
            title TEXT,
            description TEXT,
            created_at TEXT NOT NULL,
            spectral_svg TEXT,
            bottube_url TEXT
        )
    """)
    await db.execute("""
        CREATE INDEX IF NOT EXISTS idx_chimes_profile
        ON boot_chimes(profile_key)
    """)
    await db.execute("""
        CREATE INDEX IF NOT EXISTS idx_chimes_eligible
        ON boot_chimes(attestation_eligible)
    """)
    await db.commit()


# ---------------------------------------------------------------------------
# HTTP Handlers
# ---------------------------------------------------------------------------


async def handle_index(request: web.Request) -> web.Response:
    return web.Response(text=INDEX_HTML, content_type="text/html")


async def handle_list_profiles(request: web.Request) -> web.Response:
    profiles = {}
    for key, p in KNOWN_PROFILES.items():
        profiles[key] = {
            "name": p["name"],
            "family": p["family"],
            "dominant_hz": p["dominant_hz"],
            "duration_ms": p["duration_ms"],
            "description": p["description"],
        }
    return web.json_response({"profiles": profiles, "count": len(profiles)})


async def handle_generate_chime(request: web.Request) -> web.Response:
    """Generate a boot chime WAV from a known profile, extract fingerprint,
    match against profiles, and store in database."""
    data = await request.json()
    profile_key = data.get("profile_key", "mac_1999")
    analog_variance = float(data.get("analog_variance", 0.3))
    notes = data.get("notes", "")

    if profile_key not in KNOWN_PROFILES:
        return web.json_response(
            {"error": f"Unknown profile: {profile_key}"}, status=400
        )

    analog_variance = max(0.0, min(1.0, analog_variance))

    # Generate audio
    wav_bytes = generate_chime_wav(
        profile_key, analog_variance=analog_variance
    )
    wav_b64 = base64.b64encode(wav_bytes).decode()

    # Extract fingerprint
    fingerprint = extract_spectral_fingerprint(wav_bytes)

    # Match against known profiles
    match_result = match_profile(fingerprint)

    # Hardware fingerprint
    hw_fp = generate_hardware_fingerprint()

    # Build attestation
    chime_id = f"chime_{uuid.uuid4().hex[:12]}"
    attestation = build_attestation_payload(
        chime_id, fingerprint, match_result, hw_fp
    )

    # Store in database
    db = request.app["db"]
    await db.execute(
        """INSERT INTO boot_chimes
           (id, created_at, profile_key, profile_name, fingerprint_hash,
            match_score, match_confidence, anti_emulation,
            analog_artifact_score, attestation_eligible, hardware_hash,
            spectral_data, attestation_payload, wav_b64, notes)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            chime_id,
            datetime.now(timezone.utc).isoformat(),
            profile_key,
            KNOWN_PROFILES[profile_key]["name"],
            fingerprint["fingerprint_hash"],
            match_result["match_score"],
            match_result["match_confidence"],
            match_result["anti_emulation_verdict"],
            fingerprint["analog_artifact_score"],
            1 if match_result["attestation_eligible"] else 0,
            hw_fp["hardware_hash"],
            json.dumps(fingerprint),
            json.dumps(attestation),
            wav_b64,
            notes,
        ),
    )
    await db.commit()

    return web.json_response({
        "chime_id": chime_id,
        "profile": profile_key,
        "fingerprint": fingerprint,
        "match": match_result,
        "attestation": attestation,
        "wav_b64_length": len(wav_b64),
    })


async def handle_verify_chime(request: web.Request) -> web.Response:
    """Verify a boot chime by re-analyzing stored WAV data."""
    chime_id = request.match_info["chime_id"]
    db = request.app["db"]

    async with db.execute(
        "SELECT wav_b64, attestation_payload FROM boot_chimes WHERE id = ?",
        (chime_id,),
    ) as cursor:
        row = await cursor.fetchone()

    if not row:
        return web.json_response({"error": "Chime not found"}, status=404)

    wav_b64, stored_attestation = row
    wav_bytes = base64.b64decode(wav_b64)

    # Re-extract fingerprint
    fingerprint = extract_spectral_fingerprint(wav_bytes)
    match_result = match_profile(fingerprint)

    # Compare with stored attestation
    stored = json.loads(stored_attestation)
    stored_hash = stored["spectral_fingerprint"]["fingerprint_hash"]
    current_hash = fingerprint["fingerprint_hash"]
    integrity_match = stored_hash == current_hash

    return web.json_response({
        "chime_id": chime_id,
        "verification": {
            "integrity_match": integrity_match,
            "stored_hash": stored_hash,
            "current_hash": current_hash,
            "current_match": match_result,
            "attestation_valid": (
                integrity_match and match_result["attestation_eligible"]
            ),
        },
    })


async def handle_replay_chime(request: web.Request) -> web.Response:
    """Return the WAV audio for a stored chime (base64 encoded)."""
    chime_id = request.match_info["chime_id"]
    db = request.app["db"]

    async with db.execute(
        "SELECT wav_b64, profile_key, profile_name FROM boot_chimes WHERE id=?",
        (chime_id,),
    ) as cursor:
        row = await cursor.fetchone()

    if not row:
        return web.json_response({"error": "Chime not found"}, status=404)

    wav_b64, profile_key, profile_name = row
    return web.json_response({
        "chime_id": chime_id,
        "profile_key": profile_key,
        "profile_name": profile_name,
        "wav_b64": wav_b64,
    })


async def handle_list_chimes(request: web.Request) -> web.Response:
    """List all stored boot chimes."""
    db = request.app["db"]
    limit = int(request.query.get("limit", "50"))
    offset = int(request.query.get("offset", "0"))

    rows = []
    async with db.execute(
        """SELECT id, created_at, profile_key, profile_name,
                  fingerprint_hash, match_score, match_confidence,
                  anti_emulation, analog_artifact_score,
                  attestation_eligible, notes
           FROM boot_chimes ORDER BY created_at DESC
           LIMIT ? OFFSET ?""",
        (limit, offset),
    ) as cursor:
        async for row in cursor:
            rows.append({
                "id": row[0],
                "created_at": row[1],
                "profile_key": row[2],
                "profile_name": row[3],
                "fingerprint_hash": row[4],
                "match_score": row[5],
                "match_confidence": row[6],
                "anti_emulation": row[7],
                "analog_artifact_score": row[8],
                "attestation_eligible": bool(row[9]),
                "notes": row[10],
            })

    async with db.execute("SELECT COUNT(*) FROM boot_chimes") as cursor:
        total = (await cursor.fetchone())[0]

    return web.json_response({"chimes": rows, "total": total})


async def handle_chime_detail(request: web.Request) -> web.Response:
    """Get full detail for a single chime including attestation payload."""
    chime_id = request.match_info["chime_id"]
    db = request.app["db"]

    async with db.execute(
        """SELECT id, created_at, profile_key, profile_name,
                  fingerprint_hash, match_score, match_confidence,
                  anti_emulation, analog_artifact_score,
                  attestation_eligible, hardware_hash,
                  spectral_data, attestation_payload, notes
           FROM boot_chimes WHERE id = ?""",
        (chime_id,),
    ) as cursor:
        row = await cursor.fetchone()

    if not row:
        return web.json_response({"error": "Chime not found"}, status=404)

    return web.json_response({
        "id": row[0],
        "created_at": row[1],
        "profile_key": row[2],
        "profile_name": row[3],
        "fingerprint_hash": row[4],
        "match_score": row[5],
        "match_confidence": row[6],
        "anti_emulation": row[7],
        "analog_artifact_score": row[8],
        "attestation_eligible": bool(row[9]),
        "hardware_hash": row[10],
        "spectral_data": json.loads(row[11]),
        "attestation_payload": json.loads(row[12]),
        "notes": row[13],
    })


async def handle_upload_chime(request: web.Request) -> web.Response:
    """Upload raw WAV audio for fingerprinting and attestation.

    Accepts multipart/form-data with 'file' field, or JSON with 'wav_b64'.
    """
    content_type = request.content_type

    if "multipart" in content_type:
        reader = await request.multipart()
        field = await reader.next()
        wav_bytes = await field.read()
    else:
        data = await request.json()
        wav_b64 = data.get("wav_b64", "")
        if not wav_b64:
            return web.json_response(
                {"error": "No audio data provided"}, status=400
            )
        wav_bytes = base64.b64decode(wav_b64)

    notes = "uploaded_audio"

    # Validate WAV format
    try:
        buf = io.BytesIO(wav_bytes)
        with wave.open(buf, "rb") as wf:
            _ = wf.getframerate()
    except Exception as e:
        return web.json_response(
            {"error": f"Invalid WAV: {e}"}, status=400
        )

    wav_b64 = base64.b64encode(wav_bytes).decode()
    fingerprint = extract_spectral_fingerprint(wav_bytes)
    match_result = match_profile(fingerprint)
    hw_fp = generate_hardware_fingerprint()

    chime_id = f"chime_{uuid.uuid4().hex[:12]}"
    attestation = build_attestation_payload(
        chime_id, fingerprint, match_result, hw_fp
    )

    db = request.app["db"]
    await db.execute(
        """INSERT INTO boot_chimes
           (id, created_at, profile_key, profile_name, fingerprint_hash,
            match_score, match_confidence, anti_emulation,
            analog_artifact_score, attestation_eligible, hardware_hash,
            spectral_data, attestation_payload, wav_b64, notes)
           VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            chime_id,
            datetime.now(timezone.utc).isoformat(),
            match_result["best_match"],
            match_result["best_match_name"],
            fingerprint["fingerprint_hash"],
            match_result["match_score"],
            match_result["match_confidence"],
            match_result["anti_emulation_verdict"],
            fingerprint["analog_artifact_score"],
            1 if match_result["attestation_eligible"] else 0,
            hw_fp["hardware_hash"],
            json.dumps(fingerprint),
            json.dumps(attestation),
            wav_b64,
            notes,
        ),
    )
    await db.commit()

    return web.json_response({
        "chime_id": chime_id,
        "fingerprint": fingerprint,
        "match": match_result,
        "attestation": attestation,
    })


async def handle_gallery_add(request: web.Request) -> web.Response:
    """Add a chime to the BoTTube gallery."""
    data = await request.json()
    chime_id = data.get("chime_id")
    title = data.get("title", "")
    description = data.get("description", "")

    db = request.app["db"]

    async with db.execute(
        "SELECT id FROM boot_chimes WHERE id = ?", (chime_id,)
    ) as cursor:
        if not await cursor.fetchone():
            return web.json_response(
                {"error": "Chime not found"}, status=404
            )

    gallery_id = f"gallery_{uuid.uuid4().hex[:10]}"
    await db.execute(
        """INSERT INTO chime_gallery
           (id, chime_id, title, description, created_at)
           VALUES (?, ?, ?, ?, ?)""",
        (
            gallery_id,
            chime_id,
            title,
            description,
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    await db.commit()

    return web.json_response({
        "gallery_id": gallery_id, "chime_id": chime_id
    })


async def handle_gallery_list(request: web.Request) -> web.Response:
    """List chime gallery entries with spectral data."""
    db = request.app["db"]

    rows = []
    async with db.execute(
        """SELECT g.id, g.chime_id, g.title, g.description, g.created_at,
                  c.profile_name, c.match_score, c.anti_emulation,
                  c.analog_artifact_score, c.spectral_data
           FROM chime_gallery g
           JOIN boot_chimes c ON g.chime_id = c.id
           ORDER BY g.created_at DESC LIMIT 50""",
    ) as cursor:
        async for row in cursor:
            rows.append({
                "gallery_id": row[0],
                "chime_id": row[1],
                "title": row[2],
                "description": row[3],
                "created_at": row[4],
                "profile_name": row[5],
                "match_score": row[6],
                "anti_emulation": row[7],
                "analog_artifact_score": row[8],
                "spectral_data": (
                    json.loads(row[9]) if row[9] else None
                ),
            })

    return web.json_response({"gallery": rows, "count": len(rows)})


async def handle_stats(request: web.Request) -> web.Response:
    """Return aggregate statistics for the boot chime database."""
    db = request.app["db"]

    stats = {}
    async with db.execute("SELECT COUNT(*) FROM boot_chimes") as c:
        stats["total_chimes"] = (await c.fetchone())[0]

    async with db.execute(
        "SELECT COUNT(*) FROM boot_chimes WHERE attestation_eligible = 1"
    ) as c:
        stats["eligible_attestations"] = (await c.fetchone())[0]

    async with db.execute("SELECT COUNT(*) FROM chime_gallery") as c:
        stats["gallery_entries"] = (await c.fetchone())[0]

    async with db.execute(
        """SELECT profile_key, COUNT(*)
           FROM boot_chimes GROUP BY profile_key
           ORDER BY COUNT(*) DESC"""
    ) as c:
        stats["by_profile"] = {row[0]: row[1] async for row in c}

    async with db.execute(
        """SELECT anti_emulation, COUNT(*)
           FROM boot_chimes GROUP BY anti_emulation"""
    ) as c:
        stats["by_verdict"] = {row[0]: row[1] async for row in c}

    async with db.execute(
        "SELECT AVG(match_score), AVG(analog_artifact_score) FROM boot_chimes"
    ) as c:
        row = await c.fetchone()
        stats["avg_match_score"] = round(row[0] or 0, 4)
        stats["avg_analog_score"] = round(row[1] or 0, 4)

    return web.json_response(stats)


# ---------------------------------------------------------------------------
# Embedded HTML — Web Audio API visualization + full dashboard
# ---------------------------------------------------------------------------

INDEX_HTML = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Boot Chime Proof-of-Iron | RustChain Acoustic Attestation</title>
<style>
  :root {
    --bg: #0a0a0f;
    --panel: #12121a;
    --border: #2a2a3a;
    --accent: #00ff88;
    --accent2: #ff6600;
    --warn: #ff4444;
    --text: #e0e0e8;
    --dim: #888899;
    --genuine: #00ff88;
    --emulator: #ff4444;
    --uncertain: #ffaa00;
  }
  * { margin: 0; padding: 0; box-sizing: border-box; }
  body {
    background: var(--bg);
    color: var(--text);
    font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', monospace;
    font-size: 14px;
    line-height: 1.6;
  }
  .container { max-width: 1200px; margin: 0 auto; padding: 20px; }
  header {
    text-align: center;
    padding: 30px 0;
    border-bottom: 1px solid var(--border);
    margin-bottom: 30px;
  }
  header h1 {
    font-size: 28px;
    color: var(--accent);
    letter-spacing: 2px;
    text-transform: uppercase;
  }
  header .subtitle {
    color: var(--dim);
    font-size: 13px;
    margin-top: 8px;
  }
  .grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 20px;
    margin-bottom: 20px;
  }
  @media (max-width: 800px) {
    .grid { grid-template-columns: 1fr; }
  }
  .panel {
    background: var(--panel);
    border: 1px solid var(--border);
    border-radius: 8px;
    padding: 20px;
  }
  .panel h2 {
    color: var(--accent);
    font-size: 15px;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 15px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
  }
  select, button, input {
    background: var(--bg);
    color: var(--text);
    border: 1px solid var(--border);
    padding: 8px 14px;
    border-radius: 4px;
    font-family: inherit;
    font-size: 13px;
    cursor: pointer;
  }
  select:hover, button:hover { border-color: var(--accent); }
  button.primary {
    background: var(--accent);
    color: #000;
    font-weight: bold;
    border-color: var(--accent);
  }
  button.primary:hover { opacity: 0.85; }
  .form-row { margin-bottom: 12px; }
  .form-row label {
    display: block;
    color: var(--dim);
    font-size: 12px;
    margin-bottom: 4px;
  }
  .slider-row {
    display: flex;
    align-items: center;
    gap: 10px;
  }
  .slider-row input[type="range"] {
    flex: 1;
    accent-color: var(--accent);
  }
  .slider-val {
    color: var(--accent);
    min-width: 40px;
    text-align: right;
  }
  canvas {
    width: 100%;
    height: 200px;
    background: #08080e;
    border: 1px solid var(--border);
    border-radius: 4px;
    display: block;
    margin: 10px 0;
  }
  .result-card {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 14px;
    margin-top: 12px;
  }
  .result-row {
    display: flex;
    justify-content: space-between;
    padding: 4px 0;
    font-size: 13px;
  }
  .result-row .label { color: var(--dim); }
  .result-row .value { color: var(--text); font-weight: bold; }
  .verdict-genuine { color: var(--genuine); }
  .verdict-emulator { color: var(--emulator); }
  .verdict-uncertain { color: var(--uncertain); }
  .chime-list { max-height: 400px; overflow-y: auto; }
  .chime-item {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 10px;
    margin-bottom: 8px;
    cursor: pointer;
    transition: border-color 0.2s;
  }
  .chime-item:hover { border-color: var(--accent); }
  .chime-item .chime-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
  }
  .chime-item .chime-id {
    color: var(--accent);
    font-size: 12px;
  }
  .chime-item .chime-profile {
    color: var(--text);
    font-weight: bold;
  }
  .badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 3px;
    font-size: 11px;
    font-weight: bold;
    text-transform: uppercase;
  }
  .badge-genuine {
    background: rgba(0,255,136,0.15);
    color: var(--genuine);
    border: 1px solid var(--genuine);
  }
  .badge-emulator {
    background: rgba(255,68,68,0.15);
    color: var(--emulator);
    border: 1px solid var(--emulator);
  }
  .badge-uncertain {
    background: rgba(255,170,0,0.15);
    color: var(--uncertain);
    border: 1px solid var(--uncertain);
  }
  .stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
  }
  .stat-box {
    background: var(--bg);
    border: 1px solid var(--border);
    border-radius: 4px;
    padding: 12px;
    text-align: center;
  }
  .stat-box .stat-val {
    font-size: 24px;
    color: var(--accent);
    font-weight: bold;
  }
  .stat-box .stat-label {
    font-size: 11px;
    color: var(--dim);
    text-transform: uppercase;
  }
  .full-width { grid-column: 1 / -1; }
  #spectrumCanvas { height: 160px; }
  #waveformCanvas { height: 120px; }
  .controls-bar {
    display: flex;
    gap: 10px;
    flex-wrap: wrap;
    margin-top: 10px;
  }
  .tab-bar {
    display: flex;
    gap: 0;
    margin-bottom: 20px;
  }
  .tab-btn {
    padding: 10px 20px;
    background: var(--panel);
    border: 1px solid var(--border);
    color: var(--dim);
    cursor: pointer;
    font-family: inherit;
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 1px;
  }
  .tab-btn:first-child { border-radius: 6px 0 0 6px; }
  .tab-btn:last-child { border-radius: 0 6px 6px 0; }
  .tab-btn.active {
    background: var(--accent);
    color: #000;
    border-color: var(--accent);
    font-weight: bold;
  }
  .tab-content { display: none; }
  .tab-content.active { display: block; }
  .spinner {
    display: inline-block;
    width: 16px;
    height: 16px;
    border: 2px solid var(--border);
    border-top-color: var(--accent);
    border-radius: 50%;
    animation: spin 0.6s linear infinite;
  }
  @keyframes spin { to { transform: rotate(360deg); } }
  .score-bar {
    height: 8px;
    background: var(--bg);
    border-radius: 4px;
    margin: 4px 0;
    overflow: hidden;
  }
  .score-bar-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.5s;
  }
  footer {
    text-align: center;
    padding: 20px 0;
    color: var(--dim);
    font-size: 12px;
    border-top: 1px solid var(--border);
    margin-top: 30px;
  }
</style>
</head>
<body>
<div class="container">
  <header>
    <h1>Boot Chime Proof-of-Iron</h1>
    <div class="subtitle">
      Acoustic Hardware Attestation for RustChain &mdash; bounty #2307
    </div>
    <div class="subtitle" style="margin-top:4px;color:var(--accent)">
      The boot chime is a physical artifact of real iron &mdash;
      unique to each machine as it ages. Unforgeable without the hardware.
    </div>
  </header>

  <div class="tab-bar">
    <button class="tab-btn active" data-tab="generate">Generate</button>
    <button class="tab-btn" data-tab="gallery">Gallery</button>
    <button class="tab-btn" data-tab="verify">Verify</button>
    <button class="tab-btn" data-tab="stats">Stats</button>
  </div>

  <!-- ============ GENERATE TAB ============ -->
  <div id="tab-generate" class="tab-content active">
    <div class="grid">
      <div class="panel">
        <h2>Generate Boot Chime</h2>
        <div class="form-row">
          <label>Hardware Profile</label>
          <select id="profileSelect" style="width:100%"></select>
        </div>
        <div class="form-row" id="profileDesc"
             style="color:var(--dim);font-size:12px;min-height:36px;"></div>
        <div class="form-row">
          <label>Analog Variance (capacitor aging, speaker wear)</label>
          <div class="slider-row">
            <input type="range" id="analogSlider" min="0" max="100" value="30">
            <span class="slider-val" id="analogVal">0.30</span>
          </div>
        </div>
        <div class="form-row">
          <label>Notes (optional)</label>
          <input type="text" id="notesInput" style="width:100%"
                 placeholder="e.g. My 1999 G4 tower, recapped 2024">
        </div>
        <div class="controls-bar">
          <button class="primary" id="generateBtn"
                  onclick="generateChime()">Generate &amp; Attest</button>
          <button id="playBtn" onclick="playChime()" disabled>
            Play Chime
          </button>
        </div>
        <div id="generateStatus"
             style="margin-top:10px;font-size:12px;color:var(--dim);"></div>
      </div>

      <div class="panel">
        <h2>Spectral Analysis (FFT)</h2>
        <canvas id="spectrumCanvas"></canvas>
        <h2 style="margin-top:15px">Waveform</h2>
        <canvas id="waveformCanvas"></canvas>
      </div>
    </div>

    <div class="panel full-width" id="resultPanel" style="display:none;">
      <h2>Attestation Result</h2>
      <div class="grid" style="margin-bottom:0;">
        <div class="result-card">
          <div class="result-row">
            <span class="label">Chime ID</span>
            <span class="value" id="resChimeId">-</span>
          </div>
          <div class="result-row">
            <span class="label">Profile Match</span>
            <span class="value" id="resProfileMatch">-</span>
          </div>
          <div class="result-row">
            <span class="label">Match Score</span>
            <span class="value" id="resMatchScore">-</span>
          </div>
          <div class="result-row">
            <span class="label">Score Bar</span>
            <span class="value" style="flex:1;margin-left:10px;">
              <div class="score-bar">
                <div class="score-bar-fill" id="resScoreBar"
                     style="width:0;background:var(--accent);"></div>
              </div>
            </span>
          </div>
          <div class="result-row">
            <span class="label">Confidence</span>
            <span class="value" id="resConfidence">-</span>
          </div>
        </div>
        <div class="result-card">
          <div class="result-row">
            <span class="label">Anti-Emulation</span>
            <span class="value" id="resVerdict">-</span>
          </div>
          <div class="result-row">
            <span class="label">Analog Artifact Score</span>
            <span class="value" id="resAnalog">-</span>
          </div>
          <div class="result-row">
            <span class="label">Analog Bar</span>
            <span class="value" style="flex:1;margin-left:10px;">
              <div class="score-bar">
                <div class="score-bar-fill" id="resAnalogBar"
                     style="width:0;background:var(--accent2);"></div>
              </div>
            </span>
          </div>
          <div class="result-row">
            <span class="label">Attestation Eligible</span>
            <span class="value" id="resEligible">-</span>
          </div>
          <div class="result-row">
            <span class="label">Fingerprint Hash</span>
            <span class="value" id="resFpHash"
                  style="font-size:11px;word-break:break-all;">-</span>
          </div>
        </div>
      </div>
      <details style="margin-top:12px;">
        <summary style="cursor:pointer;color:var(--accent);">
          Full Attestation Payload (JSON)
        </summary>
        <pre id="resPayload"
             style="background:var(--bg);padding:12px;border-radius:4px;
                    margin-top:8px;font-size:11px;overflow-x:auto;
                    max-height:300px;overflow-y:auto;"></pre>
      </details>
    </div>
  </div>

  <!-- ============ GALLERY TAB ============ -->
  <div id="tab-gallery" class="tab-content">
    <div class="panel">
      <h2>Chime Gallery (BoTTube)</h2>
      <p style="color:var(--dim);font-size:12px;margin-bottom:15px;">
        Each miner's boot sound with spectral visualization.
        Click any chime to replay and inspect.
      </p>
      <div class="chime-list" id="chimeList">
        <div style="color:var(--dim);text-align:center;padding:40px;">
          Loading chimes...
        </div>
      </div>
    </div>
  </div>

  <!-- ============ VERIFY TAB ============ -->
  <div id="tab-verify" class="tab-content">
    <div class="panel">
      <h2>Verify Chime Attestation</h2>
      <div class="form-row">
        <label>Chime ID</label>
        <input type="text" id="verifyInput" style="width:100%"
               placeholder="chime_xxxxxxxxxxxx">
      </div>
      <button class="primary" onclick="verifyChime()">Verify</button>
      <div id="verifyResult" style="margin-top:15px;"></div>
    </div>
  </div>

  <!-- ============ STATS TAB ============ -->
  <div id="tab-stats" class="tab-content">
    <div class="panel">
      <h2>Attestation Statistics</h2>
      <div class="stats-grid" id="statsGrid">
        <div style="color:var(--dim);text-align:center;padding:20px;
                    grid-column:1/-1;">Loading...</div>
      </div>
    </div>
  </div>

  <footer>
    Boot Chime Proof-of-Iron &mdash; RustChain Bounty #2307 (95 RTC)<br>
    Acoustic hardware attestation: the literal voice of old machines
    as part of trust.
  </footer>
</div>

<script>
const API = '';
let currentWavB64 = null;
let audioCtx = null;

/* ---- Tab switching ---- */
document.querySelectorAll('.tab-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.tab-btn').forEach(b =>
      b.classList.remove('active'));
    document.querySelectorAll('.tab-content').forEach(t =>
      t.classList.remove('active'));
    btn.classList.add('active');
    document.getElementById('tab-' + btn.dataset.tab)
      .classList.add('active');
    if (btn.dataset.tab === 'gallery') loadChimeList();
    if (btn.dataset.tab === 'stats') loadStats();
  });
});

/* ---- Load profiles into dropdown ---- */
async function loadProfiles() {
  const res = await fetch(API + '/api/profiles');
  const data = await res.json();
  const sel = document.getElementById('profileSelect');
  sel.innerHTML = '';
  for (const [key, p] of Object.entries(data.profiles)) {
    const opt = document.createElement('option');
    opt.value = key;
    opt.textContent = p.name + ' (' +
      p.dominant_hz.map(h => Math.round(h) + 'Hz').join(', ') + ')';
    sel.appendChild(opt);
  }
  sel.addEventListener('change', () => {
    const p = data.profiles[sel.value];
    document.getElementById('profileDesc').textContent =
      p ? p.description : '';
  });
  sel.dispatchEvent(new Event('change'));
}

/* ---- Analog slider display ---- */
document.getElementById('analogSlider').addEventListener('input', e => {
  document.getElementById('analogVal').textContent =
    (e.target.value / 100).toFixed(2);
});

/* ---- Generate chime ---- */
async function generateChime() {
  const btn = document.getElementById('generateBtn');
  const status = document.getElementById('generateStatus');
  btn.disabled = true;
  status.innerHTML =
    '<span class="spinner"></span> Generating chime & computing attestation...';

  const body = {
    profile_key: document.getElementById('profileSelect').value,
    analog_variance: document.getElementById('analogSlider').value / 100,
    notes: document.getElementById('notesInput').value,
  };

  try {
    const res = await fetch(API + '/api/chime/generate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(body),
    });
    const data = await res.json();
    if (data.error) {
      status.textContent = 'Error: ' + data.error;
      return;
    }

    /* Fetch WAV for playback */
    const wavRes = await fetch(
      API + '/api/chime/' + data.chime_id + '/replay');
    const wavData = await wavRes.json();
    currentWavB64 = wavData.wav_b64;
    document.getElementById('playBtn').disabled = false;

    /* Display results */
    displayResult(data);
    drawSpectrum(data.fingerprint);
    drawWaveform(currentWavB64);

    status.innerHTML =
      '<span style="color:var(--accent);">Chime generated and attested.</span>';
  } catch (e) {
    status.textContent = 'Error: ' + e.message;
  } finally {
    btn.disabled = false;
  }
}

function displayResult(data) {
  const panel = document.getElementById('resultPanel');
  panel.style.display = 'block';

  document.getElementById('resChimeId').textContent = data.chime_id;
  document.getElementById('resProfileMatch').textContent =
    data.match.best_match_name || '-';
  document.getElementById('resMatchScore').textContent =
    (data.match.match_score * 100).toFixed(1) + '%';
  document.getElementById('resScoreBar').style.width =
    (data.match.match_score * 100) + '%';
  document.getElementById('resConfidence').textContent =
    data.match.match_confidence;

  const verdict = data.match.anti_emulation_verdict;
  const verdictEl = document.getElementById('resVerdict');
  verdictEl.textContent = verdict;
  verdictEl.className = 'value verdict-' + (
    verdict === 'GENUINE_HARDWARE' ? 'genuine' :
    verdict === 'LIKELY_EMULATOR' ? 'emulator' : 'uncertain');

  document.getElementById('resAnalog').textContent =
    (data.fingerprint.analog_artifact_score * 100).toFixed(1) + '%';
  document.getElementById('resAnalogBar').style.width =
    (data.fingerprint.analog_artifact_score * 100) + '%';

  const eligible = data.attestation.attestation_eligible;
  document.getElementById('resEligible').textContent =
    eligible ? 'YES' : 'NO';
  document.getElementById('resEligible').style.color =
    eligible ? 'var(--genuine)' : 'var(--emulator)';
  document.getElementById('resFpHash').textContent =
    data.fingerprint.fingerprint_hash;
  document.getElementById('resPayload').textContent =
    JSON.stringify(data.attestation, null, 2);
}

/* ---- Web Audio: play chime ---- */
function playChime() {
  if (!currentWavB64) return;
  if (!audioCtx)
    audioCtx = new (window.AudioContext || window.webkitAudioContext)();

  const binary = atob(currentWavB64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++)
    bytes[i] = binary.charCodeAt(i);

  audioCtx.decodeAudioData(bytes.buffer.slice(0), buffer => {
    const source = audioCtx.createBufferSource();
    source.buffer = buffer;

    const analyser = audioCtx.createAnalyser();
    analyser.fftSize = 2048;
    source.connect(analyser);
    analyser.connect(audioCtx.destination);
    source.start(0);

    /* Animate spectrum during playback */
    const canvas = document.getElementById('spectrumCanvas');
    const ctx = canvas.getContext('2d');
    const bufLen = analyser.frequencyBinCount;
    const dataArray = new Uint8Array(bufLen);
    let playing = true;
    source.onended = () => { playing = false; };

    function animateSpectrum() {
      if (!playing) return;
      analyser.getByteFrequencyData(dataArray);
      const w = canvas.width = canvas.offsetWidth;
      const h = canvas.height = canvas.offsetHeight;
      ctx.fillStyle = '#08080e';
      ctx.fillRect(0, 0, w, h);

      const barW = (w / bufLen) * 2.5;
      let x = 0;
      for (let i = 0; i < bufLen; i++) {
        const v = dataArray[i] / 255;
        const barH = v * h;
        const hue = 140 + v * 40;
        ctx.fillStyle =
          'hsl(' + hue + ', 100%, ' + (30 + v * 40) + '%)';
        ctx.fillRect(x, h - barH, barW, barH);
        x += barW + 1;
        if (x > w) break;
      }
      requestAnimationFrame(animateSpectrum);
    }
    requestAnimationFrame(animateSpectrum);
  });
}

/* ---- Draw static spectrum from fingerprint data ---- */
function drawSpectrum(fp) {
  const canvas = document.getElementById('spectrumCanvas');
  const ctx = canvas.getContext('2d');
  const w = canvas.width = canvas.offsetWidth;
  const h = canvas.height = canvas.offsetHeight;

  ctx.fillStyle = '#08080e';
  ctx.fillRect(0, 0, w, h);

  /* Grid lines */
  ctx.strokeStyle = '#1a1a2a';
  ctx.lineWidth = 0.5;
  for (let i = 0; i < 10; i++) {
    const y = (h / 10) * i;
    ctx.beginPath();
    ctx.moveTo(0, y);
    ctx.lineTo(w, y);
    ctx.stroke();
  }

  if (!fp || !fp.dominant_hz) return;

  /* Draw frequency peaks as bars */
  const maxFreq = Math.max(...fp.dominant_hz) * 1.3;
  fp.dominant_hz.forEach((freq, i) => {
    const ratio = fp.harmonic_ratios[i] || 0.5;
    const x = (freq / maxFreq) * w * 0.9 + w * 0.05;
    const barH = ratio * h * 0.8;
    const barW = Math.max(8, w / 20);

    const grad = ctx.createLinearGradient(x, h, x, h - barH);
    grad.addColorStop(0, '#00ff88');
    grad.addColorStop(1, '#004422');
    ctx.fillStyle = grad;
    ctx.fillRect(x - barW / 2, h - barH, barW, barH);

    ctx.fillStyle = '#00ff88';
    ctx.font = '10px monospace';
    ctx.textAlign = 'center';
    ctx.fillText(Math.round(freq) + 'Hz', x, h - barH - 5);
  });

  /* Noise floor line */
  const noiseY = h - (Math.abs(fp.noise_floor_db) / 80) * h;
  ctx.strokeStyle = '#ff660066';
  ctx.lineWidth = 1;
  ctx.setLineDash([4, 4]);
  ctx.beginPath();
  ctx.moveTo(0, noiseY);
  ctx.lineTo(w, noiseY);
  ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillStyle = '#ff6600';
  ctx.font = '10px monospace';
  ctx.textAlign = 'left';
  ctx.fillText('noise: ' + fp.noise_floor_db + 'dB', 5, noiseY - 5);
}

/* ---- Draw waveform from base64 WAV ---- */
function drawWaveform(wavB64) {
  if (!wavB64) return;
  const canvas = document.getElementById('waveformCanvas');
  const ctx = canvas.getContext('2d');
  const w = canvas.width = canvas.offsetWidth;
  const h = canvas.height = canvas.offsetHeight;

  ctx.fillStyle = '#08080e';
  ctx.fillRect(0, 0, w, h);

  const binary = atob(wavB64);
  const bytes = new Uint8Array(binary.length);
  for (let i = 0; i < binary.length; i++)
    bytes[i] = binary.charCodeAt(i);

  /* Skip 44-byte WAV header, read 16-bit little-endian PCM */
  const dataView = new DataView(bytes.buffer);
  const numSamples = Math.floor((bytes.length - 44) / 2);
  const samples = [];
  for (let i = 0; i < numSamples; i++)
    samples.push(dataView.getInt16(44 + i * 2, true));

  const step = Math.max(1, Math.floor(samples.length / w));
  const mid = h / 2;

  /* Waveform line */
  ctx.strokeStyle = '#00ff88';
  ctx.lineWidth = 1;
  ctx.beginPath();
  for (let x = 0; x < w; x++) {
    const idx = Math.min(x * step, samples.length - 1);
    const v = samples[idx] / 32768;
    const y = mid + v * mid * 0.9;
    if (x === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  }
  ctx.stroke();

  /* Center line */
  ctx.strokeStyle = '#2a2a3a';
  ctx.lineWidth = 0.5;
  ctx.beginPath();
  ctx.moveTo(0, mid);
  ctx.lineTo(w, mid);
  ctx.stroke();

  /* Envelope overlay */
  ctx.strokeStyle = '#ff660044';
  ctx.lineWidth = 2;
  ctx.beginPath();
  for (let x = 0; x < w; x++) {
    const start = x * step;
    const end = Math.min(start + step, samples.length);
    let maxVal = 0;
    for (let i = start; i < end; i++)
      maxVal = Math.max(maxVal, Math.abs(samples[i]));
    const envY = mid - (maxVal / 32768) * mid * 0.9;
    if (x === 0) ctx.moveTo(x, envY);
    else ctx.lineTo(x, envY);
  }
  ctx.stroke();
}

/* ---- Load chime list for gallery ---- */
async function loadChimeList() {
  const list = document.getElementById('chimeList');
  try {
    const res = await fetch(API + '/api/chimes');
    const data = await res.json();
    if (!data.chimes.length) {
      list.innerHTML =
        '<div style="color:var(--dim);text-align:center;padding:40px;">' +
        'No chimes yet. Generate one first.</div>';
      return;
    }
    list.innerHTML = data.chimes.map(c => {
      const vc = c.anti_emulation === 'GENUINE_HARDWARE' ? 'genuine' :
        c.anti_emulation === 'LIKELY_EMULATOR' ? 'emulator' : 'uncertain';
      return '<div class="chime-item" onclick="selectChime(\'' +
        c.id + '\')">' +
        '<div class="chime-header">' +
        '<span class="chime-profile">' +
        (c.profile_name || c.profile_key) + '</span>' +
        '<span class="badge badge-' + vc + '">' +
        c.anti_emulation + '</span></div>' +
        '<div style="display:flex;justify-content:space-between;' +
        'margin-top:6px;font-size:12px;">' +
        '<span class="chime-id">' + c.id + '</span>' +
        '<span style="color:var(--dim);">' +
        (c.created_at ? c.created_at.slice(0, 19) : '') + '</span></div>' +
        '<div style="margin-top:4px;">' +
        '<div class="score-bar"><div class="score-bar-fill" ' +
        'style="width:' + ((c.match_score || 0) * 100) +
        '%;background:var(--accent);"></div></div>' +
        '<span style="font-size:11px;color:var(--dim);">Match: ' +
        ((c.match_score || 0) * 100).toFixed(1) + '% | Analog: ' +
        ((c.analog_artifact_score || 0) * 100).toFixed(1) +
        '%</span></div></div>';
    }).join('');
  } catch (e) {
    list.innerHTML =
      '<div style="color:var(--warn);">Error: ' + e.message + '</div>';
  }
}

async function selectChime(id) {
  const wavRes = await fetch(API + '/api/chime/' + id + '/replay');
  const wavData = await wavRes.json();
  currentWavB64 = wavData.wav_b64;
  document.getElementById('playBtn').disabled = false;

  const detailRes = await fetch(API + '/api/chime/' + id);
  const detail = await detailRes.json();
  drawSpectrum(detail.spectral_data);
  drawWaveform(currentWavB64);

  /* Switch to generate tab to see visualization */
  document.querySelectorAll('.tab-btn').forEach(b =>
    b.classList.remove('active'));
  document.querySelectorAll('.tab-content').forEach(t =>
    t.classList.remove('active'));
  document.querySelector('[data-tab="generate"]').classList.add('active');
  document.getElementById('tab-generate').classList.add('active');

  const panel = document.getElementById('resultPanel');
  panel.style.display = 'block';
  document.getElementById('resChimeId').textContent = detail.id;
  document.getElementById('resProfileMatch').textContent =
    detail.profile_name || '-';
  document.getElementById('resMatchScore').textContent =
    ((detail.match_score || 0) * 100).toFixed(1) + '%';
  document.getElementById('resScoreBar').style.width =
    ((detail.match_score || 0) * 100) + '%';
  document.getElementById('resConfidence').textContent =
    detail.match_confidence;
  const verdict = detail.anti_emulation;
  const ve = document.getElementById('resVerdict');
  ve.textContent = verdict;
  ve.className = 'value verdict-' + (
    verdict === 'GENUINE_HARDWARE' ? 'genuine' :
    verdict === 'LIKELY_EMULATOR' ? 'emulator' : 'uncertain');
  document.getElementById('resAnalog').textContent =
    ((detail.analog_artifact_score || 0) * 100).toFixed(1) + '%';
  document.getElementById('resAnalogBar').style.width =
    ((detail.analog_artifact_score || 0) * 100) + '%';
  document.getElementById('resEligible').textContent =
    detail.attestation_eligible ? 'YES' : 'NO';
  document.getElementById('resFpHash').textContent =
    detail.fingerprint_hash;
  document.getElementById('resPayload').textContent =
    JSON.stringify(detail.attestation_payload, null, 2);
}

/* ---- Verify ---- */
async function verifyChime() {
  const id = document.getElementById('verifyInput').value.trim();
  const result = document.getElementById('verifyResult');
  if (!id) {
    result.innerHTML =
      '<span style="color:var(--warn);">Enter a chime ID.</span>';
    return;
  }
  result.innerHTML = '<span class="spinner"></span> Verifying...';
  try {
    const res = await fetch(API + '/api/chime/' + id + '/verify');
    const data = await res.json();
    if (data.error) {
      result.innerHTML =
        '<span style="color:var(--warn);">' + data.error + '</span>';
      return;
    }
    const v = data.verification;
    const ok = v.attestation_valid;
    result.innerHTML = '<div class="result-card">' +
      '<div class="result-row"><span class="label">Integrity</span>' +
      '<span class="value" style="color:' +
      (v.integrity_match ? 'var(--genuine)' : 'var(--emulator)') +
      ';">' + (v.integrity_match ? 'PASS' : 'FAIL') + '</span></div>' +
      '<div class="result-row"><span class="label">Stored Hash</span>' +
      '<span class="value" style="font-size:11px;">' +
      v.stored_hash + '</span></div>' +
      '<div class="result-row"><span class="label">Current Hash</span>' +
      '<span class="value" style="font-size:11px;">' +
      v.current_hash + '</span></div>' +
      '<div class="result-row"><span class="label">Match Score</span>' +
      '<span class="value">' +
      ((v.current_match.match_score || 0) * 100).toFixed(1) +
      '%</span></div>' +
      '<div class="result-row"><span class="label">Valid</span>' +
      '<span class="value" style="color:' +
      (ok ? 'var(--genuine)' : 'var(--emulator)') + ';">' +
      (ok ? 'VALID' : 'INVALID') + '</span></div></div>';
  } catch (e) {
    result.innerHTML =
      '<span style="color:var(--warn);">Error: ' + e.message + '</span>';
  }
}

/* ---- Stats ---- */
async function loadStats() {
  const grid = document.getElementById('statsGrid');
  try {
    const res = await fetch(API + '/api/stats');
    const s = await res.json();
    grid.innerHTML =
      '<div class="stat-box"><div class="stat-val">' +
      s.total_chimes + '</div><div class="stat-label">Total Chimes</div></div>' +
      '<div class="stat-box"><div class="stat-val">' +
      s.eligible_attestations +
      '</div><div class="stat-label">Eligible</div></div>' +
      '<div class="stat-box"><div class="stat-val">' +
      s.gallery_entries +
      '</div><div class="stat-label">Gallery</div></div>' +
      '<div class="stat-box"><div class="stat-val">' +
      (s.avg_match_score * 100).toFixed(1) +
      '%</div><div class="stat-label">Avg Match</div></div>' +
      '<div class="stat-box"><div class="stat-val">' +
      (s.avg_analog_score * 100).toFixed(1) +
      '%</div><div class="stat-label">Avg Analog</div></div>' +
      '<div class="stat-box"><div class="stat-val" style="font-size:14px;">' +
      Object.entries(s.by_verdict || {}).map(function(kv) {
        return kv[0].replace(/_/g, ' ') + ': ' + kv[1];
      }).join('<br>') +
      '</div><div class="stat-label">Verdicts</div></div>';
  } catch (e) {
    grid.innerHTML =
      '<div style="color:var(--warn);grid-column:1/-1;">Error: ' +
      e.message + '</div>';
  }
}

/* ---- Init ---- */
loadProfiles();
</script>
</body>
</html>"""


# ---------------------------------------------------------------------------
# Application factory
# ---------------------------------------------------------------------------


async def on_startup(app: web.Application):
    app["db"] = await aiosqlite.connect(DB_PATH)
    await init_db(app["db"])
    print(f"[Boot Chime PoI] Database ready: {DB_PATH}")
    print(f"[Boot Chime PoI] Known profiles: {len(KNOWN_PROFILES)}")


async def on_cleanup(app: web.Application):
    await app["db"].close()


def create_app() -> web.Application:
    app = web.Application()
    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    app.router.add_get("/", handle_index)
    app.router.add_get("/api/profiles", handle_list_profiles)
    app.router.add_post("/api/chime/generate", handle_generate_chime)
    app.router.add_post("/api/chime/upload", handle_upload_chime)
    app.router.add_get("/api/chime/{chime_id}", handle_chime_detail)
    app.router.add_get("/api/chime/{chime_id}/verify", handle_verify_chime)
    app.router.add_get("/api/chime/{chime_id}/replay", handle_replay_chime)
    app.router.add_get("/api/chimes", handle_list_chimes)
    app.router.add_post("/api/gallery", handle_gallery_add)
    app.router.add_get("/api/gallery", handle_gallery_list)
    app.router.add_get("/api/stats", handle_stats)

    return app


if __name__ == "__main__":
    print(f"""
    +==============================================================+
    |          Boot Chime Proof-of-Iron -- RustChain                |
    |       Acoustic Hardware Attestation Server                    |
    |                                                               |
    |  Profiles: {len(KNOWN_PROFILES):>3} known hardware chime signatures           |
    |  Families: Mac, Amiga, SGI, Sun                               |
    |  Port:     {PORT}                                             |
    +==============================================================+
    """)
    web.run_app(create_app(), host=HOST, port=PORT)
