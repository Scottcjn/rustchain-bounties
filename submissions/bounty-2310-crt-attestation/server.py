"""
CRT Light Attestation Server
=============================
RustChain Bounty #2310 — Security by Cathode Ray (140 RTC)

Prototype side-channel proof system where a miner flashes a deterministic
pattern on a CRT monitor and a camera/photodiode captures scanline timing,
phosphor decay, and refresh quirks. The optical fingerprint becomes one more
thing emulators can never fake.

Endpoints:
  POST /api/attestations       — Submit CRT photo/video for analysis
  GET  /api/attestations       — List all attestations
  GET  /api/attestations/{id}  — Get single attestation result
  POST /api/verify             — Verify an attestation on-chain
  GET  /api/gallery            — CRT Gallery: phosphor decay comparisons
  GET  /                       — Serve the web UI

Author: ElromEvedElElyon
License: Apache-2.0
"""

import asyncio
import base64
import hashlib
import json
import math
import os
import random
import sqlite3
import struct
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from aiohttp import web

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DB_PATH = os.environ.get("CRT_DB_PATH", "crt_attestations.db")
UPLOAD_DIR = Path(os.environ.get("CRT_UPLOAD_DIR", "uploads"))
HOST = os.environ.get("CRT_HOST", "0.0.0.0")
PORT = int(os.environ.get("CRT_PORT", "8310"))

# Phosphor types and their characteristic decay constants (microseconds)
PHOSPHOR_PROFILES = {
    "P22": {
        "name": "P22 (Standard Color)",
        "decay_us": 20.0,
        "persistence": "medium-short",
        "color": "RGB tricolor",
        "description": "Most common CRT phosphor. Used in consumer TVs and monitors.",
    },
    "P43": {
        "name": "P43 (Green)",
        "decay_us": 1000.0,
        "persistence": "medium",
        "color": "green (YAG:Ce)",
        "description": "Yttrium aluminum garnet. Used in oscilloscopes and radar.",
    },
    "P4": {
        "name": "P4 (White)",
        "decay_us": 60.0,
        "persistence": "medium-short",
        "color": "white (dual-layer)",
        "description": "Black-and-white TV standard. Dual phosphor layer.",
    },
    "P31": {
        "name": "P31 (Green)",
        "decay_us": 32.0,
        "persistence": "medium-short",
        "color": "green (zinc silicate)",
        "description": "Classic green terminal phosphor. VT100 and similar.",
    },
    "P1": {
        "name": "P1 (Green)",
        "decay_us": 24.0,
        "persistence": "medium",
        "color": "green (zinc silicate)",
        "description": "Early oscilloscope phosphor. Moderate persistence.",
    },
}

# CRT monitor archetypes for the gallery
CRT_ARCHETYPES = {
    "trinitron": {
        "name": "Sony Trinitron (Aperture Grille)",
        "phosphor": "P22",
        "mask": "aperture_grille",
        "typical_drift_hz": 0.03,
        "scanline_jitter_us": 0.15,
        "brightness_nonlinearity": 0.12,
    },
    "shadow_mask": {
        "name": "Generic Shadow Mask",
        "phosphor": "P22",
        "mask": "shadow_mask",
        "typical_drift_hz": 0.08,
        "scanline_jitter_us": 0.35,
        "brightness_nonlinearity": 0.18,
    },
    "diamondtron": {
        "name": "Mitsubishi Diamondtron",
        "phosphor": "P22",
        "mask": "aperture_grille",
        "typical_drift_hz": 0.04,
        "scanline_jitter_us": 0.20,
        "brightness_nonlinearity": 0.10,
    },
    "vt100_terminal": {
        "name": "DEC VT100 Terminal",
        "phosphor": "P31",
        "mask": "none",
        "typical_drift_hz": 0.12,
        "scanline_jitter_us": 0.50,
        "brightness_nonlinearity": 0.22,
    },
    "oscilloscope": {
        "name": "Tektronix 2465 Oscilloscope",
        "phosphor": "P43",
        "mask": "none",
        "typical_drift_hz": 0.02,
        "scanline_jitter_us": 0.08,
        "brightness_nonlinearity": 0.06,
    },
}


# ---------------------------------------------------------------------------
# Database
# ---------------------------------------------------------------------------

def init_db(db_path: str = DB_PATH) -> sqlite3.Connection:
    """Initialize SQLite database for attestation storage."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA foreign_keys=ON")
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS attestations (
            id              TEXT PRIMARY KEY,
            created_at      TEXT NOT NULL,
            status          TEXT NOT NULL DEFAULT 'pending',
            source_type     TEXT,
            source_filename TEXT,
            stated_refresh  REAL,
            measured_refresh REAL,
            refresh_drift   REAL,
            phosphor_type   TEXT,
            phosphor_decay_us REAL,
            scanline_jitter_us REAL,
            brightness_nonlinearity REAL,
            flyback_signature TEXT,
            mask_type       TEXT,
            is_crt          INTEGER DEFAULT 0,
            confidence      REAL DEFAULT 0.0,
            crt_fingerprint TEXT,
            attestation_hash TEXT,
            on_chain_tx     TEXT,
            verified        INTEGER DEFAULT 0,
            analysis_log    TEXT,
            spectrogram_data TEXT,
            error           TEXT
        );

        CREATE TABLE IF NOT EXISTS gallery_entries (
            id              TEXT PRIMARY KEY,
            attestation_id  TEXT REFERENCES attestations(id),
            monitor_name    TEXT,
            phosphor_type   TEXT,
            decay_curve     TEXT,
            comparison_type TEXT,
            created_at      TEXT NOT NULL
        );
    """)
    conn.commit()
    return conn


# ---------------------------------------------------------------------------
# CRT Analysis Engine (Simulated ML Classifier)
# ---------------------------------------------------------------------------

class CRTAnalyzer:
    """
    Simulated CRT phosphor pattern analyzer.

    In production this would use OpenCV + numpy for real signal processing.
    Here we simulate the ML classifier output based on image metadata and
    injected CRT-characteristic noise to demonstrate the attestation flow.
    """

    def __init__(self):
        self.rng = random.Random()

    def _phosphor_decay_model(
        self, phosphor: str, age_years: float = 15.0
    ) -> Dict[str, Any]:
        """
        Model phosphor decay curve with aging effects.

        Real phosphors follow: I(t) = I0 * exp(-t / tau)
        Aging increases tau (slower decay) and reduces I0 (dimmer).
        """
        profile = PHOSPHOR_PROFILES.get(phosphor, PHOSPHOR_PROFILES["P22"])
        base_tau = profile["decay_us"]

        # Aging increases decay time by ~2% per year
        aged_tau = base_tau * (1.0 + 0.02 * age_years)

        # Generate sampled decay curve (256 points over 5x tau)
        t_max = aged_tau * 5.0
        n_points = 256
        curve = []
        for i in range(n_points):
            t = (i / n_points) * t_max
            # Base exponential decay
            intensity = math.exp(-t / aged_tau)
            # Add phosphor-specific noise (real CRTs have crystal grain noise)
            noise = self.rng.gauss(0, 0.005)
            # Add afterglow for certain phosphors
            afterglow = 0.0
            if phosphor in ("P43", "P31"):
                afterglow = 0.03 * math.exp(-t / (aged_tau * 8.0))
            curve.append(max(0.0, min(1.0, intensity + noise + afterglow)))

        return {
            "phosphor": phosphor,
            "phosphor_name": profile["name"],
            "base_decay_us": base_tau,
            "aged_decay_us": round(aged_tau, 2),
            "age_years": age_years,
            "persistence": profile["persistence"],
            "curve_points": n_points,
            "t_max_us": round(t_max, 2),
            "decay_curve": curve,
        }

    def _refresh_analysis(
        self, stated_hz: float, archetype: str = "trinitron"
    ) -> Dict[str, Any]:
        """
        Analyze refresh rate drift.

        Real CRTs drift due to:
        - Flyback transformer aging
        - Capacitor drift in horizontal/vertical oscillators
        - Temperature variations
        """
        arch = CRT_ARCHETYPES.get(archetype, CRT_ARCHETYPES["shadow_mask"])
        drift_hz = arch["typical_drift_hz"]

        # Simulate measured refresh with aging drift
        direction = self.rng.choice([-1, 1])
        actual_drift = self.rng.gauss(drift_hz, drift_hz * 0.3) * direction
        measured_hz = stated_hz + actual_drift

        # Generate per-frame timing samples (64 frames)
        frame_times = []
        nominal_period = 1.0 / stated_hz
        for _ in range(64):
            jitter = self.rng.gauss(0, arch["scanline_jitter_us"] * 1e-6)
            frame_times.append(nominal_period + jitter + (actual_drift / stated_hz**2))

        avg_period = sum(frame_times) / len(frame_times)
        measured_from_frames = 1.0 / avg_period if avg_period > 0 else stated_hz

        return {
            "stated_hz": stated_hz,
            "measured_hz": round(measured_from_frames, 4),
            "drift_hz": round(measured_from_frames - stated_hz, 4),
            "drift_ppm": round(
                ((measured_from_frames - stated_hz) / stated_hz) * 1e6, 1
            ),
            "frame_samples": len(frame_times),
            "jitter_us": round(arch["scanline_jitter_us"], 3),
            "jitter_stddev_us": round(
                (sum((ft - avg_period) ** 2 for ft in frame_times) / len(frame_times))
                ** 0.5
                * 1e6,
                3,
            ),
        }

    def _scanline_analysis(self, archetype: str = "trinitron") -> Dict[str, Any]:
        """
        Analyze scanline timing jitter from flyback transformer wear.

        Each horizontal scanline has a retrace period controlled by the flyback.
        Aging causes increased jitter in retrace timing.
        """
        arch = CRT_ARCHETYPES.get(archetype, CRT_ARCHETYPES["shadow_mask"])

        # Simulate 480 scanlines (standard NTSC)
        n_lines = 480
        base_h_period = 63.5  # microseconds (15.734 kHz)
        jitter = arch["scanline_jitter_us"]

        scanline_timings = []
        for line in range(n_lines):
            # Flyback jitter increases with line number (transformer heats up)
            heat_factor = 1.0 + 0.1 * (line / n_lines)
            timing = base_h_period + self.rng.gauss(0, jitter * heat_factor)
            scanline_timings.append(timing)

        avg_timing = sum(scanline_timings) / len(scanline_timings)
        variance = sum((t - avg_timing) ** 2 for t in scanline_timings) / len(
            scanline_timings
        )
        stddev = variance**0.5

        return {
            "total_scanlines": n_lines,
            "avg_h_period_us": round(avg_timing, 4),
            "stddev_us": round(stddev, 4),
            "peak_jitter_us": round(
                max(abs(t - avg_timing) for t in scanline_timings), 4
            ),
            "flyback_signature": hashlib.sha256(
                struct.pack(f"{n_lines}f", *scanline_timings)
            ).hexdigest()[:32],
            "heat_drift_detected": True,
            "mask_type": arch["mask"],
        }

    def _brightness_analysis(self, archetype: str = "trinitron") -> Dict[str, Any]:
        """
        Analyze brightness nonlinearity from aging electron gun.

        Real CRTs have gamma curves that drift as the electron gun ages.
        The cathode emission decreases unevenly across the brightness range.
        """
        arch = CRT_ARCHETYPES.get(archetype, CRT_ARCHETYPES["shadow_mask"])
        nonlinearity = arch["brightness_nonlinearity"]

        # Generate 256-point transfer curve (input vs measured brightness)
        n_points = 256
        gamma = 2.2  # Standard CRT gamma
        transfer_curve = []
        for i in range(n_points):
            input_level = i / (n_points - 1)
            # Ideal gamma response
            ideal = input_level**gamma
            # Aging causes S-curve distortion at extremes
            age_distortion = nonlinearity * math.sin(input_level * math.pi) * 0.1
            # Electron gun wear reduces output at high brightness
            wear = nonlinearity * (input_level**3) * 0.15
            measured = max(0.0, min(1.0, ideal + age_distortion - wear))
            transfer_curve.append(measured)

        # Calculate deviation from ideal
        ideal_curve = [(i / (n_points - 1)) ** gamma for i in range(n_points)]
        avg_deviation = sum(
            abs(m - d) for m, d in zip(transfer_curve, ideal_curve)
        ) / n_points

        return {
            "gamma_nominal": gamma,
            "measured_gamma": round(gamma + self.rng.gauss(0, 0.05), 3),
            "nonlinearity_index": round(nonlinearity, 4),
            "avg_deviation": round(avg_deviation, 6),
            "peak_deviation": round(
                max(abs(m - d) for m, d in zip(transfer_curve, ideal_curve)), 6
            ),
            "transfer_curve": transfer_curve,
            "electron_gun_wear": round(nonlinearity * 100, 1),
        }

    def _lcd_detection(self) -> Dict[str, Any]:
        """
        Generate characteristics that would indicate an LCD/OLED (non-CRT).

        LCDs have:
        - Zero phosphor decay (sample-and-hold)
        - Perfect refresh timing (crystal oscillator)
        - Linear brightness response (digital DAC)
        - No scanline jitter
        """
        return {
            "is_crt": False,
            "confidence": 0.98,
            "reasons": [
                "Zero phosphor decay detected — sample-and-hold display",
                "Refresh timing jitter < 0.001 us — crystal oscillator precision",
                "Linear brightness transfer — digital pixel addressing",
                "No scanline timing variation — no flyback transformer",
                "No mask/grille pattern detected",
            ],
            "phosphor_decay_us": 0.0,
            "scanline_jitter_us": 0.0,
            "brightness_nonlinearity": 0.0,
        }

    def generate_spectrogram(
        self, decay_curve: List[float], refresh_data: Dict, scanline_data: Dict
    ) -> Dict[str, Any]:
        """
        Generate spectrogram data for visualization.

        Combines phosphor decay, refresh timing, and scanline data into
        a frequency-domain representation.
        """
        n_bins = 64
        freq_bins = []
        for i in range(n_bins):
            freq = (i + 1) * 15.734  # kHz multiples of H-frequency
            # Fundamental and harmonics of horizontal frequency
            amplitude = 1.0 / (1 + i * 0.5)
            # Add refresh rate peak
            if abs(freq - refresh_data.get("measured_hz", 60) * 1000) < 500:
                amplitude += 0.8
            # Add noise floor from phosphor
            noise = self.rng.gauss(0, 0.02)
            freq_bins.append(
                {
                    "freq_khz": round(freq / 1000, 2),
                    "amplitude": round(max(0, amplitude + noise), 4),
                }
            )

        return {
            "n_bins": n_bins,
            "freq_range_khz": [
                freq_bins[0]["freq_khz"],
                freq_bins[-1]["freq_khz"],
            ],
            "bins": freq_bins,
            "dominant_freq_khz": 15.734,
            "harmonics_detected": min(8, n_bins),
        }

    def analyze(
        self,
        source_type: str = "webcam",
        stated_refresh: float = 60.0,
        simulate_lcd: bool = False,
    ) -> Dict[str, Any]:
        """
        Run full CRT attestation analysis.

        Returns a comprehensive analysis result including:
        - Phosphor decay characterization
        - Refresh rate measurement and drift
        - Scanline timing analysis
        - Brightness nonlinearity
        - CRT fingerprint hash
        """
        analysis_id = str(uuid.uuid4())
        started = time.time()
        log_entries = []

        log_entries.append(
            f"[{datetime.now(timezone.utc).isoformat()}] Analysis started — "
            f"source={source_type}, stated_refresh={stated_refresh}Hz"
        )

        if simulate_lcd:
            lcd_result = self._lcd_detection()
            log_entries.append(
                "[WARN] LCD/OLED display detected — attestation will FAIL"
            )
            return {
                "id": analysis_id,
                "is_crt": False,
                "confidence": lcd_result["confidence"],
                "detection": lcd_result,
                "crt_fingerprint": None,
                "analysis_duration_ms": round((time.time() - started) * 1000, 2),
                "log": log_entries,
            }

        # Pick a random archetype for simulation
        archetype_key = self.rng.choice(list(CRT_ARCHETYPES.keys()))
        archetype = CRT_ARCHETYPES[archetype_key]
        phosphor = archetype["phosphor"]
        age = self.rng.uniform(8.0, 25.0)

        log_entries.append(
            f"[INFO] Detected monitor archetype: {archetype['name']}"
        )
        log_entries.append(
            f"[INFO] Phosphor type: {phosphor} — estimated age: {age:.1f} years"
        )

        # Run all analyses
        phosphor_data = self._phosphor_decay_model(phosphor, age)
        log_entries.append(
            f"[INFO] Phosphor decay: tau={phosphor_data['aged_decay_us']}us "
            f"(base={phosphor_data['base_decay_us']}us)"
        )

        refresh_data = self._refresh_analysis(stated_refresh, archetype_key)
        log_entries.append(
            f"[INFO] Refresh: measured={refresh_data['measured_hz']}Hz "
            f"(drift={refresh_data['drift_hz']}Hz, "
            f"{refresh_data['drift_ppm']}ppm)"
        )

        scanline_data = self._scanline_analysis(archetype_key)
        log_entries.append(
            f"[INFO] Scanline jitter: stddev={scanline_data['stddev_us']}us, "
            f"peak={scanline_data['peak_jitter_us']}us"
        )

        brightness_data = self._brightness_analysis(archetype_key)
        log_entries.append(
            f"[INFO] Brightness: gamma={brightness_data['measured_gamma']}, "
            f"nonlinearity={brightness_data['nonlinearity_index']}"
        )

        spectrogram = self.generate_spectrogram(
            phosphor_data["decay_curve"], refresh_data, scanline_data
        )
        log_entries.append(
            f"[INFO] Spectrogram: {spectrogram['n_bins']} bins, "
            f"dominant={spectrogram['dominant_freq_khz']}kHz"
        )

        # CRT confidence scoring
        confidence_factors = {
            "phosphor_decay": 1.0 if phosphor_data["aged_decay_us"] > 5.0 else 0.1,
            "refresh_drift": min(1.0, abs(refresh_data["drift_ppm"]) / 100),
            "scanline_jitter": min(1.0, scanline_data["stddev_us"] / 0.5),
            "brightness_nonlinearity": min(
                1.0, brightness_data["nonlinearity_index"] / 0.2
            ),
            "flyback_present": 1.0,
        }
        overall_confidence = sum(confidence_factors.values()) / len(confidence_factors)
        is_crt = overall_confidence > 0.5

        log_entries.append(
            f"[INFO] Confidence factors: {json.dumps({k: round(v, 3) for k, v in confidence_factors.items()})}"
        )
        log_entries.append(
            f"[{'PASS' if is_crt else 'FAIL'}] CRT detection: "
            f"confidence={overall_confidence:.3f}, is_crt={is_crt}"
        )

        # Generate CRT fingerprint hash
        fingerprint_data = (
            f"{phosphor}:{phosphor_data['aged_decay_us']}:"
            f"{refresh_data['measured_hz']}:{refresh_data['drift_ppm']}:"
            f"{scanline_data['flyback_signature']}:"
            f"{brightness_data['measured_gamma']}:"
            f"{brightness_data['nonlinearity_index']}:"
            f"{archetype_key}"
        )
        crt_fingerprint = hashlib.sha256(fingerprint_data.encode()).hexdigest()

        log_entries.append(f"[INFO] CRT fingerprint: {crt_fingerprint}")

        duration_ms = round((time.time() - started) * 1000, 2)
        log_entries.append(f"[INFO] Analysis complete in {duration_ms}ms")

        # Compact decay curve for storage (sample every 4th point)
        sampled_curve = phosphor_data["decay_curve"][::4]

        return {
            "id": analysis_id,
            "is_crt": is_crt,
            "confidence": round(overall_confidence, 4),
            "monitor": {
                "archetype": archetype_key,
                "name": archetype["name"],
                "mask_type": archetype["mask"],
                "estimated_age_years": round(age, 1),
            },
            "phosphor": {
                "type": phosphor,
                "name": phosphor_data["phosphor_name"],
                "base_decay_us": phosphor_data["base_decay_us"],
                "aged_decay_us": phosphor_data["aged_decay_us"],
                "persistence": phosphor_data["persistence"],
                "decay_curve_sampled": [round(v, 4) for v in sampled_curve],
            },
            "refresh": refresh_data,
            "scanline": {
                "total_lines": scanline_data["total_scanlines"],
                "avg_h_period_us": scanline_data["avg_h_period_us"],
                "jitter_stddev_us": scanline_data["stddev_us"],
                "peak_jitter_us": scanline_data["peak_jitter_us"],
                "flyback_signature": scanline_data["flyback_signature"],
                "heat_drift": scanline_data["heat_drift_detected"],
            },
            "brightness": {
                "gamma_nominal": brightness_data["gamma_nominal"],
                "gamma_measured": brightness_data["measured_gamma"],
                "nonlinearity_index": brightness_data["nonlinearity_index"],
                "avg_deviation": brightness_data["avg_deviation"],
                "electron_gun_wear_pct": brightness_data["electron_gun_wear"],
            },
            "spectrogram": spectrogram,
            "confidence_factors": {
                k: round(v, 4) for k, v in confidence_factors.items()
            },
            "crt_fingerprint": crt_fingerprint,
            "analysis_duration_ms": duration_ms,
            "log": log_entries,
        }


# ---------------------------------------------------------------------------
# On-Chain Attestation
# ---------------------------------------------------------------------------

def generate_attestation_hash(
    crt_fingerprint: str, attestation_id: str, timestamp: str
) -> str:
    """
    Generate a hash suitable for on-chain attestation.

    Combines the CRT fingerprint with attestation metadata to produce
    a unique hash that can be anchored to the RustChain.
    """
    payload = f"RUSTCHAIN_CRT_ATTESTATION:v1:{attestation_id}:{crt_fingerprint}:{timestamp}"
    return hashlib.sha256(payload.encode()).hexdigest()


def simulate_on_chain_submission(attestation_hash: str) -> Dict[str, Any]:
    """
    Simulate submitting an attestation hash to RustChain.

    In production, this would call the RustChain node RPC to anchor
    the attestation hash in a transaction.
    """
    tx_hash = hashlib.sha256(
        f"tx:{attestation_hash}:{time.time()}".encode()
    ).hexdigest()

    return {
        "success": True,
        "tx_hash": tx_hash,
        "block_height": random.randint(100000, 999999),
        "confirmations": 0,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "chain": "rustchain-testnet",
        "attestation_type": "crt_fingerprint",
    }


# ---------------------------------------------------------------------------
# HTTP Handlers
# ---------------------------------------------------------------------------

analyzer = CRTAnalyzer()


async def handle_index(request: web.Request) -> web.Response:
    """Serve the web UI."""
    html_path = Path(__file__).parent / "attestation.html"
    if html_path.exists():
        return web.FileResponse(html_path)
    return web.Response(text="CRT Attestation UI not found", status=404)


async def handle_submit_attestation(request: web.Request) -> web.Response:
    """
    POST /api/attestations
    Submit a CRT photo/video for analysis.

    Accepts multipart/form-data with:
      - file: CRT capture (image/video)
      - stated_refresh: Expected refresh rate in Hz (default: 60)
      - source_type: "webcam" or "photodiode" (default: "webcam")
      - simulate_lcd: "true" to test LCD rejection (default: false)
    """
    db: sqlite3.Connection = request.app["db"]

    # Parse request
    content_type = request.content_type
    stated_refresh = 60.0
    source_type = "webcam"
    source_filename = None
    simulate_lcd = False

    if content_type == "multipart/form-data":
        reader = await request.multipart()
        async for part in reader:
            if part.name == "file":
                source_filename = part.filename or "capture.bin"
                # Read file data (we don't actually process pixels in simulation)
                file_data = await part.read(chunk_size=8192)
                # Save upload
                UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
                upload_path = UPLOAD_DIR / f"{uuid.uuid4()}_{source_filename}"
                upload_path.write_bytes(file_data)
            elif part.name == "stated_refresh":
                text = await part.text()
                try:
                    stated_refresh = float(text)
                except ValueError:
                    pass
            elif part.name == "source_type":
                source_type = await part.text()
            elif part.name == "simulate_lcd":
                text = await part.text()
                simulate_lcd = text.lower() in ("true", "1", "yes")
    else:
        # JSON body
        try:
            body = await request.json()
        except Exception:
            body = {}
        stated_refresh = float(body.get("stated_refresh", 60.0))
        source_type = body.get("source_type", "webcam")
        simulate_lcd = body.get("simulate_lcd", False)
        source_filename = body.get("filename")

    # Run analysis
    result = analyzer.analyze(
        source_type=source_type,
        stated_refresh=stated_refresh,
        simulate_lcd=simulate_lcd,
    )

    attestation_id = result["id"]
    now = datetime.now(timezone.utc).isoformat()

    # Generate attestation hash if CRT detected
    attestation_hash = None
    if result["is_crt"] and result.get("crt_fingerprint"):
        attestation_hash = generate_attestation_hash(
            result["crt_fingerprint"], attestation_id, now
        )

    # Store in database
    db.execute(
        """
        INSERT INTO attestations (
            id, created_at, status, source_type, source_filename,
            stated_refresh, measured_refresh, refresh_drift,
            phosphor_type, phosphor_decay_us, scanline_jitter_us,
            brightness_nonlinearity, flyback_signature, mask_type,
            is_crt, confidence, crt_fingerprint, attestation_hash,
            analysis_log, spectrogram_data
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            attestation_id,
            now,
            "completed" if result["is_crt"] else "rejected",
            source_type,
            source_filename,
            stated_refresh,
            result.get("refresh", {}).get("measured_hz"),
            result.get("refresh", {}).get("drift_hz"),
            result.get("phosphor", {}).get("type"),
            result.get("phosphor", {}).get("aged_decay_us"),
            result.get("scanline", {}).get("jitter_stddev_us"),
            result.get("brightness", {}).get("nonlinearity_index"),
            result.get("scanline", {}).get("flyback_signature"),
            result.get("monitor", {}).get("mask_type"),
            1 if result["is_crt"] else 0,
            result["confidence"],
            result.get("crt_fingerprint"),
            attestation_hash,
            json.dumps(result.get("log", [])),
            json.dumps(result.get("spectrogram", {})),
        ),
    )
    db.commit()

    # Build response
    response = {
        "id": attestation_id,
        "status": "completed" if result["is_crt"] else "rejected",
        "created_at": now,
        "is_crt": result["is_crt"],
        "confidence": result["confidence"],
        "crt_fingerprint": result.get("crt_fingerprint"),
        "attestation_hash": attestation_hash,
        "analysis": result,
    }

    return web.json_response(response, status=201)


async def handle_get_attestation(request: web.Request) -> web.Response:
    """GET /api/attestations/{id} — Get a single attestation result."""
    db: sqlite3.Connection = request.app["db"]
    att_id = request.match_info["id"]

    row = db.execute(
        "SELECT * FROM attestations WHERE id = ?", (att_id,)
    ).fetchone()

    if not row:
        return web.json_response({"error": "Attestation not found"}, status=404)

    result = dict(row)
    # Parse JSON fields
    if result.get("analysis_log"):
        try:
            result["analysis_log"] = json.loads(result["analysis_log"])
        except (json.JSONDecodeError, TypeError):
            pass
    if result.get("spectrogram_data"):
        try:
            result["spectrogram_data"] = json.loads(result["spectrogram_data"])
        except (json.JSONDecodeError, TypeError):
            pass

    return web.json_response(result)


async def handle_list_attestations(request: web.Request) -> web.Response:
    """GET /api/attestations — List all attestations."""
    db: sqlite3.Connection = request.app["db"]

    limit = int(request.query.get("limit", "50"))
    offset = int(request.query.get("offset", "0"))
    status_filter = request.query.get("status")

    query = "SELECT id, created_at, status, is_crt, confidence, phosphor_type, crt_fingerprint, attestation_hash, verified FROM attestations"
    params: list = []

    if status_filter:
        query += " WHERE status = ?"
        params.append(status_filter)

    query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
    params.extend([limit, offset])

    rows = db.execute(query, params).fetchall()
    total = db.execute(
        "SELECT COUNT(*) FROM attestations"
        + (" WHERE status = ?" if status_filter else ""),
        [status_filter] if status_filter else [],
    ).fetchone()[0]

    return web.json_response(
        {
            "attestations": [dict(row) for row in rows],
            "total": total,
            "limit": limit,
            "offset": offset,
        }
    )


async def handle_verify(request: web.Request) -> web.Response:
    """
    POST /api/verify
    Verify an attestation on-chain.

    Body: { "attestation_id": "..." }
    """
    db: sqlite3.Connection = request.app["db"]

    try:
        body = await request.json()
    except Exception:
        return web.json_response({"error": "Invalid JSON"}, status=400)

    att_id = body.get("attestation_id")
    if not att_id:
        return web.json_response(
            {"error": "attestation_id required"}, status=400
        )

    row = db.execute(
        "SELECT * FROM attestations WHERE id = ?", (att_id,)
    ).fetchone()

    if not row:
        return web.json_response({"error": "Attestation not found"}, status=404)

    row_dict = dict(row)

    if not row_dict.get("is_crt"):
        return web.json_response(
            {"error": "Cannot verify non-CRT attestation"}, status=400
        )

    if row_dict.get("verified"):
        return web.json_response(
            {
                "status": "already_verified",
                "on_chain_tx": row_dict.get("on_chain_tx"),
            }
        )

    # Submit to chain
    chain_result = simulate_on_chain_submission(row_dict["attestation_hash"])

    # Update database
    db.execute(
        """
        UPDATE attestations
        SET verified = 1, on_chain_tx = ?, status = 'verified'
        WHERE id = ?
        """,
        (chain_result["tx_hash"], att_id),
    )
    db.commit()

    return web.json_response(
        {
            "status": "verified",
            "attestation_id": att_id,
            "crt_fingerprint": row_dict.get("crt_fingerprint"),
            "attestation_hash": row_dict.get("attestation_hash"),
            "chain": chain_result,
        }
    )


async def handle_gallery(request: web.Request) -> web.Response:
    """
    GET /api/gallery
    CRT Gallery: phosphor decay curves from different monitor types.
    Bonus requirement — compare CRT vs LCD characteristics.
    """
    gallery = []

    for key, arch in CRT_ARCHETYPES.items():
        phosphor = arch["phosphor"]
        age = random.uniform(10.0, 22.0)

        decay_data = analyzer._phosphor_decay_model(phosphor, age)
        sampled_curve = [round(v, 4) for v in decay_data["decay_curve"][::4]]

        gallery.append(
            {
                "monitor": key,
                "name": arch["name"],
                "phosphor": phosphor,
                "phosphor_name": PHOSPHOR_PROFILES[phosphor]["name"],
                "mask_type": arch["mask"],
                "estimated_age": round(age, 1),
                "decay_tau_us": decay_data["aged_decay_us"],
                "persistence": decay_data["persistence"],
                "decay_curve": sampled_curve,
                "t_max_us": decay_data["t_max_us"],
            }
        )

    # LCD comparison (zero decay)
    lcd_curve = [1.0] * 32 + [0.0] * 32  # instant on/off
    gallery.append(
        {
            "monitor": "lcd_reference",
            "name": "LCD/OLED Reference (Non-CRT)",
            "phosphor": "NONE",
            "phosphor_name": "No phosphor (sample-and-hold)",
            "mask_type": "pixel_grid",
            "estimated_age": 0,
            "decay_tau_us": 0.0,
            "persistence": "none",
            "decay_curve": lcd_curve,
            "t_max_us": 0.0,
            "is_reference": True,
            "note": "LCD pixels are sample-and-hold — zero phosphor decay. Instantly detectable.",
        }
    )

    return web.json_response(
        {
            "gallery": gallery,
            "phosphor_profiles": PHOSPHOR_PROFILES,
            "description": (
                "CRT Gallery showing phosphor decay curves from different monitor "
                "archetypes. Each CRT has a unique decay signature based on phosphor "
                "type, age, and wear. LCD/OLED displays have zero decay — they are "
                "trivially distinguishable."
            ),
        }
    )


# ---------------------------------------------------------------------------
# Application Setup
# ---------------------------------------------------------------------------

def create_app() -> web.Application:
    """Create and configure the aiohttp application."""
    app = web.Application(client_max_size=50 * 1024 * 1024)  # 50MB upload limit

    # Database
    app["db"] = init_db()

    # Routes
    app.router.add_get("/", handle_index)
    app.router.add_post("/api/attestations", handle_submit_attestation)
    app.router.add_get("/api/attestations", handle_list_attestations)
    app.router.add_get("/api/attestations/{id}", handle_get_attestation)
    app.router.add_post("/api/verify", handle_verify)
    app.router.add_get("/api/gallery", handle_gallery)

    # CORS middleware
    @web.middleware
    async def cors_middleware(request, handler):
        if request.method == "OPTIONS":
            response = web.Response()
        else:
            response = await handler(request)
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, DELETE, OPTIONS"
        )
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    app.middlewares.append(cors_middleware)

    return app


if __name__ == "__main__":
    print(f"CRT Light Attestation Server starting on {HOST}:{PORT}")
    print(f"Database: {DB_PATH}")
    print(f"Upload dir: {UPLOAD_DIR}")
    print("Endpoints:")
    print(f"  GET  http://{HOST}:{PORT}/                  — Web UI")
    print(f"  POST http://{HOST}:{PORT}/api/attestations  — Submit capture")
    print(f"  GET  http://{HOST}:{PORT}/api/attestations  — List all")
    print(f"  GET  http://{HOST}:{PORT}/api/attestations/{{id}} — Get one")
    print(f"  POST http://{HOST}:{PORT}/api/verify        — Verify on-chain")
    print(f"  GET  http://{HOST}:{PORT}/api/gallery       — CRT Gallery")
    app = create_app()
    web.run_app(app, host=HOST, port=PORT)
