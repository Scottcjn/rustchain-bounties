# SPDX-License-Identifier: MIT
"""
Pure-Python miner identity and payload helpers for load testing.

Shared by locustfile.py, and importable by test_load_suite.py without
pulling in framework-specific dependencies (locust / gevent).
"""

import hashlib
import json
import random
import time
import uuid
from typing import Any, Dict, List

# ---------------------------------------------------------------------------
# Hardware architecture profiles (mirrors scripts/stress_test/miner_simulator)
# ---------------------------------------------------------------------------

ARCH_PROFILES = {
    "g4": {"model": "PowerPC G4 (7447A)", "family": "PowerPC", "multiplier": 2.5},
    "g5": {"model": "PowerPC G5 (970MP)", "family": "PowerPC", "multiplier": 2.0},
    "apple_silicon": {"model": "Apple M2 Max", "family": "ARM64", "multiplier": 1.2},
    "modern_x86": {"model": "AMD Ryzen 9 7950X", "family": "x86_64", "multiplier": 1.0},
}


def make_miner(prefix: str = "load") -> Dict[str, Any]:
    """Return a dict with a fresh simulated miner identity.

    Args:
        prefix: Short string prepended to the miner_id (e.g. "locust", "k6").
    """
    arch_key = random.choice(list(ARCH_PROFILES.keys()))
    profile = ARCH_PROFILES[arch_key]
    uid = uuid.uuid4().hex[:8]
    miner_id = f"{prefix}-{arch_key}-{uid}"
    raw = f"{miner_id}-{time.time()}-{random.random()}"
    wallet = hashlib.sha256(raw.encode()).hexdigest()[:38] + "RTC"
    serial = f"SN-{uuid.uuid4().hex[:12].upper()}"
    mac = ":".join(f"{random.randint(0, 255):02x}" for _ in range(6))
    return {
        "miner_id": miner_id,
        "wallet": wallet,
        "arch_key": arch_key,
        "profile": profile,
        "serial": serial,
        "mac": mac,
        "hostname": f"host-{miner_id}",
    }


def entropy_report(nonce: str, wallet: str) -> Dict[str, Any]:
    """Build a simulated entropy report (mirrors MinerSimulator)."""
    base = random.uniform(20_000, 30_000)
    samples = [base + random.gauss(0, 500) for _ in range(12)]
    derived = {
        "mean_ns": sum(samples) / len(samples),
        "variance_ns": random.uniform(100_000, 500_000),
        "min_ns": min(samples),
        "max_ns": max(samples),
        "sample_count": 48,
        "samples_preview": samples,
    }
    commitment = hashlib.sha256(
        (nonce + wallet + json.dumps(derived, sort_keys=True)).encode()
    ).hexdigest()
    return {
        "nonce": nonce,
        "commitment": commitment,
        "derived": derived,
        "entropy_score": derived["variance_ns"],
    }


def attestation_payload(miner: Dict[str, Any], nonce: str) -> Dict[str, Any]:
    """Build the full /attest/submit payload."""
    profile = miner["profile"]
    report = entropy_report(nonce, miner["wallet"])
    return {
        "miner": miner["wallet"],
        "miner_id": miner["miner_id"],
        "nonce": nonce,
        "report": report,
        "device": {
            "family": profile["family"],
            "arch": miner["arch_key"],
            "model": profile["model"],
            "cpu": profile["model"],
            "cores": random.choice([1, 2, 4, 8, 16]),
            "memory_gb": random.choice([2, 4, 8, 16, 32, 64]),
            "serial": miner["serial"],
        },
        "signals": {
            "macs": [miner["mac"]],
            "hostname": miner["hostname"],
        },
        "fingerprint": {
            "all_passed": True,
            "checks": {
                "anti_emulation": {"passed": True, "data": {"vm_indicators": []}},
                "cpu_features": {
                    "passed": True,
                    "data": {
                        "flags": [
                            "altivec"
                            if "PowerPC" in profile["family"]
                            else "avx2"
                        ]
                    },
                },
                "io_latency": {
                    "passed": True,
                    "data": {"p95_ns": random.randint(100, 500)},
                },
                "serial_binding": {
                    "passed": True,
                    "data": {"serial": miner["serial"]},
                },
            },
        },
    }


def enroll_payload(miner: Dict[str, Any]) -> Dict[str, Any]:
    """Build the /epoch/enroll payload."""
    return {
        "miner_pubkey": miner["wallet"],
        "miner_id": miner["miner_id"],
        "device": {
            "family": miner["profile"]["family"],
            "arch": miner["arch_key"],
        },
    }
