# SPDX-License-Identifier: MIT
"""Server-side architecture validation for RustChain attestation.

Fixes RIP-201: Prevents bucket normalization spoofing where a modern x86
can claim device_arch=G4 and receive the 2.5x vintage_powerpc multiplier.

Validation strategy:
1. Cross-validate CPU brand string vs claimed device_arch
2. Require SIMD evidence (AltiVec/vec_perm) for PowerPC claims
3. Require cache timing profile matching architecture characteristics
4. Classify miners into reward buckets from verified server-side features
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# --- Architecture Definitions ---

ARCH_FAMILIES = {
    "g4": "PowerPC",
    "g5": "PowerPC",
    "68k": "Motorola68K",
    "486": "x86",
    "pentium1": "x86",
    "apple_silicon": "ARM64",
    "modern_x86": "x86_64",
}

# CPU brand string patterns that MUST match for each family
FAMILY_CPU_PATTERNS = {
    "PowerPC": [
        re.compile(r"(?i)power\s*pc"),
        re.compile(r"(?i)power\s*mac"),
        re.compile(r"(?i)7\d{3}"),  # 7400, 7447, 7450 etc.
        re.compile(r"(?i)970"),  # G5
        re.compile(r"(?i)ppc"),
    ],
    "Motorola68K": [
        re.compile(r"(?i)680[0-4]0"),
        re.compile(r"(?i)motorola"),
        re.compile(r"(?i)68k"),
    ],
    "x86": [
        re.compile(r"(?i)intel"),
        re.compile(r"(?i)amd"),
        re.compile(r"(?i)486"),
        re.compile(r"(?i)pentium"),
        re.compile(r"(?i)x86"),
    ],
    "x86_64": [
        re.compile(r"(?i)intel"),
        re.compile(r"(?i)amd"),
        re.compile(r"(?i)ryzen"),
        re.compile(r"(?i)xeon"),
        re.compile(r"(?i)core\s*i[3579]"),
        re.compile(r"(?i)x86.64"),
    ],
    "ARM64": [
        re.compile(r"(?i)apple\s*m[0-9]"),
        re.compile(r"(?i)arm"),
        re.compile(r"(?i)aarch64"),
    ],
}

# Patterns that MUST NOT match (anti-spoofing)
FAMILY_REJECT_PATTERNS = {
    "PowerPC": [
        re.compile(r"(?i)intel"),
        re.compile(r"(?i)amd"),
        re.compile(r"(?i)ryzen"),
        re.compile(r"(?i)xeon"),
        re.compile(r"(?i)core\s*i[3579]"),
        re.compile(r"(?i)apple\s*m[0-9]"),
    ],
    "Motorola68K": [
        re.compile(r"(?i)intel"),
        re.compile(r"(?i)amd"),
        re.compile(r"(?i)power"),
    ],
    "ARM64": [
        re.compile(r"(?i)intel"),
        re.compile(r"(?i)amd"),
        re.compile(r"(?i)power\s*pc"),
    ],
}

# Required SIMD features per family
REQUIRED_SIMD_FEATURES = {
    "PowerPC": {"altivec", "vec_perm"},
    "x86": {"mmx"},
    "x86_64": {"sse2", "avx2"},
    "ARM64": {"neon"},
}

# Cache timing profile ranges per family (p95 latency in ns)
# PowerPC G4 has distinctly different cache characteristics than modern x86
CACHE_TIMING_RANGES = {
    "PowerPC": {"l1_min_ns": 1.5, "l1_max_ns": 8.0, "l2_min_ns": 10.0, "l2_max_ns": 60.0},
    "Motorola68K": {"l1_min_ns": 5.0, "l1_max_ns": 30.0, "l2_min_ns": 30.0, "l2_max_ns": 200.0},
    "x86": {"l1_min_ns": 1.0, "l1_max_ns": 5.0, "l2_min_ns": 5.0, "l2_max_ns": 30.0},
    "x86_64": {"l1_min_ns": 0.5, "l1_max_ns": 4.0, "l2_min_ns": 3.0, "l2_max_ns": 20.0},
    "ARM64": {"l1_min_ns": 0.5, "l1_max_ns": 4.0, "l2_min_ns": 3.0, "l2_max_ns": 25.0},
}

# Multipliers per arch bucket (from TOKENOMICS.md)
ARCH_MULTIPLIERS = {
    "g4": 2.5,
    "g5": 2.0,
    "68k": 3.0,
    "486": 2.5,
    "pentium1": 2.5,
    "apple_silicon": 1.2,
    "modern_x86": 1.0,
}


@dataclass
class ValidationResult:
    """Result of architecture validation."""
    valid: bool
    claimed_arch: str
    verified_arch: Optional[str]
    verified_family: Optional[str]
    multiplier: float
    checks: Dict[str, bool] = field(default_factory=dict)
    reasons: List[str] = field(default_factory=list)


def validate_cpu_brand(cpu_brand: str, claimed_family: str) -> Tuple[bool, List[str]]:
    """Check 1: Cross-validate CPU brand string vs claimed architecture family.

    Returns (passed, reasons).
    """
    if not cpu_brand or not cpu_brand.strip():
        return False, ["cpu_brand is empty or missing"]

    reasons = []
    brand = cpu_brand.strip()

    # Check reject patterns first — these are hard failures
    reject_patterns = FAMILY_REJECT_PATTERNS.get(claimed_family, [])
    for pattern in reject_patterns:
        if pattern.search(brand):
            reasons.append(
                f"cpu_brand '{brand}' matches reject pattern '{pattern.pattern}' "
                f"for family '{claimed_family}'"
            )
            return False, reasons

    # Check that at least one positive pattern matches
    accept_patterns = FAMILY_CPU_PATTERNS.get(claimed_family, [])
    if accept_patterns:
        matched = any(p.search(brand) for p in accept_patterns)
        if not matched:
            reasons.append(
                f"cpu_brand '{brand}' does not match any known pattern "
                f"for family '{claimed_family}'"
            )
            return False, reasons

    return True, []


def validate_simd_features(
    reported_features: List[str],
    claimed_family: str,
) -> Tuple[bool, List[str]]:
    """Check 2: Verify SIMD features match claimed architecture.

    PowerPC must report AltiVec/vec_perm, not AVX2/SSE.
    """
    if not reported_features:
        return False, [f"no SIMD features reported for family '{claimed_family}'"]

    required = REQUIRED_SIMD_FEATURES.get(claimed_family)
    if not required:
        return True, []  # No specific requirement for this family

    features_lower = {f.lower().strip() for f in reported_features}
    missing = required - features_lower

    if missing:
        return False, [
            f"missing required SIMD features for '{claimed_family}': {sorted(missing)}, "
            f"reported: {sorted(features_lower)}"
        ]

    return True, []


def validate_cache_timing(
    cache_profile: Dict[str, Any],
    claimed_family: str,
) -> Tuple[bool, List[str]]:
    """Check 3: Verify cache timing profile matches architecture characteristics.

    PowerPC G4 has distinctly different L1/L2 latency than modern x86.
    """
    expected = CACHE_TIMING_RANGES.get(claimed_family)
    if not expected:
        return True, []  # No range defined

    if not cache_profile:
        return False, [f"no cache timing profile provided for family '{claimed_family}'"]

    reasons = []
    l1_ns = cache_profile.get("l1_latency_ns")
    l2_ns = cache_profile.get("l2_latency_ns")

    if l1_ns is not None:
        if not (expected["l1_min_ns"] <= l1_ns <= expected["l1_max_ns"]):
            reasons.append(
                f"L1 latency {l1_ns}ns outside expected range "
                f"[{expected['l1_min_ns']}, {expected['l1_max_ns']}] for '{claimed_family}'"
            )

    if l2_ns is not None:
        if not (expected["l2_min_ns"] <= l2_ns <= expected["l2_max_ns"]):
            reasons.append(
                f"L2 latency {l2_ns}ns outside expected range "
                f"[{expected['l2_min_ns']}, {expected['l2_max_ns']}] for '{claimed_family}'"
            )

    if l1_ns is None and l2_ns is None:
        reasons.append(f"no L1/L2 latency data in cache profile for '{claimed_family}'")

    return len(reasons) == 0, reasons


def classify_arch_server_side(
    attestation_payload: Dict[str, Any],
) -> ValidationResult:
    """Main entry point: classify a miner into a reward bucket from verified
    server-side features, NOT from raw client-reported architecture strings.

    This replaces the old trust-the-client approach that allowed spoofing.
    """
    device = attestation_payload.get("device", {})
    fingerprint = attestation_payload.get("fingerprint", {})
    checks_data = fingerprint.get("checks", {})

    claimed_arch = device.get("arch", "").strip()
    cpu_brand = device.get("cpu", "") or device.get("model", "")
    claimed_family = ARCH_FAMILIES.get(claimed_arch)

    # Unknown arch → reject with 1.0x
    if not claimed_family:
        return ValidationResult(
            valid=False,
            claimed_arch=claimed_arch,
            verified_arch=None,
            verified_family=None,
            multiplier=1.0,
            checks={},
            reasons=[f"unknown architecture: '{claimed_arch}'"],
        )

    all_reasons: List[str] = []
    check_results: Dict[str, bool] = {}

    # Check 1: CPU brand vs claimed arch
    brand_ok, brand_reasons = validate_cpu_brand(cpu_brand, claimed_family)
    check_results["cpu_brand_match"] = brand_ok
    all_reasons.extend(brand_reasons)

    # Check 2: SIMD features
    cpu_features = checks_data.get("cpu_features", {}).get("data", {}).get("flags", [])
    simd_ok, simd_reasons = validate_simd_features(cpu_features, claimed_family)
    check_results["simd_features"] = simd_ok
    all_reasons.extend(simd_reasons)

    # Check 3: Cache timing profile
    cache_profile = checks_data.get("cache_timing", {}).get("data", {})
    cache_ok, cache_reasons = validate_cache_timing(cache_profile, claimed_family)
    check_results["cache_timing"] = cache_ok
    all_reasons.extend(cache_reasons)

    # Decision: ALL checks must pass for vintage multiplier
    all_passed = brand_ok and simd_ok and cache_ok

    if all_passed:
        multiplier = ARCH_MULTIPLIERS.get(claimed_arch, 1.0)
        return ValidationResult(
            valid=True,
            claimed_arch=claimed_arch,
            verified_arch=claimed_arch,
            verified_family=claimed_family,
            multiplier=multiplier,
            checks=check_results,
            reasons=[],
        )
    else:
        # Failed validation → fallback to 1.0x (no vintage bonus)
        return ValidationResult(
            valid=False,
            claimed_arch=claimed_arch,
            verified_arch=None,
            verified_family=None,
            multiplier=1.0,
            checks=check_results,
            reasons=all_reasons,
        )
