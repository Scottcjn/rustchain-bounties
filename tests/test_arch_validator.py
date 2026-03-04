# SPDX-License-Identifier: MIT
"""Tests for arch_validator — proves the spoofing vector from #551 is blocked.

Key scenario: a modern x86 claims device_arch=G4 to get 2.5x multiplier.
After the fix, this MUST be rejected and fall back to 1.0x.
"""

import unittest

from scripts.arch_validator import (
    classify_arch_server_side,
    validate_cache_timing,
    validate_cpu_brand,
    validate_simd_features,
    ValidationResult,
)


class TestCPUBrandValidation(unittest.TestCase):
    """Check 1: Cross-validate CPU brand string vs claimed device_arch."""

    def test_legit_g4_powerpc(self):
        ok, reasons = validate_cpu_brand("PowerPC G4 (7447A)", "PowerPC")
        self.assertTrue(ok)
        self.assertEqual(reasons, [])

    def test_legit_g5_powerpc(self):
        ok, reasons = validate_cpu_brand("PowerPC G5 (970MP)", "PowerPC")
        self.assertTrue(ok)

    def test_spoofed_intel_xeon_claiming_powerpc(self):
        """THE EXACT ATTACK FROM ISSUE #551."""
        ok, reasons = validate_cpu_brand("Intel Xeon E5-2680", "PowerPC")
        self.assertFalse(ok)
        self.assertTrue(any("Intel" in r for r in reasons))

    def test_spoofed_amd_ryzen_claiming_powerpc(self):
        ok, reasons = validate_cpu_brand("AMD Ryzen 9 7950X", "PowerPC")
        self.assertFalse(ok)

    def test_spoofed_apple_silicon_claiming_powerpc(self):
        ok, reasons = validate_cpu_brand("Apple M2 Max", "PowerPC")
        self.assertFalse(ok)

    def test_empty_cpu_brand(self):
        ok, reasons = validate_cpu_brand("", "PowerPC")
        self.assertFalse(ok)

    def test_none_cpu_brand(self):
        ok, reasons = validate_cpu_brand("   ", "PowerPC")
        self.assertFalse(ok)

    def test_legit_modern_x86(self):
        ok, reasons = validate_cpu_brand("AMD Ryzen 9 7950X", "x86_64")
        self.assertTrue(ok)

    def test_legit_apple_silicon(self):
        ok, reasons = validate_cpu_brand("Apple M2 Max", "ARM64")
        self.assertTrue(ok)

    def test_intel_claiming_arm(self):
        ok, reasons = validate_cpu_brand("Intel Core i9-13900K", "ARM64")
        self.assertFalse(ok)


class TestSIMDValidation(unittest.TestCase):
    """Check 2: SIMD features must match claimed architecture."""

    def test_legit_powerpc_altivec(self):
        ok, reasons = validate_simd_features(["altivec", "vec_perm"], "PowerPC")
        self.assertTrue(ok)

    def test_x86_avx2_claiming_powerpc(self):
        """x86 reporting avx2 but missing altivec — must fail."""
        ok, reasons = validate_simd_features(["avx2", "sse2"], "PowerPC")
        self.assertFalse(ok)
        self.assertTrue(any("altivec" in r or "vec_perm" in r for r in reasons))

    def test_no_features_reported(self):
        ok, reasons = validate_simd_features([], "PowerPC")
        self.assertFalse(ok)

    def test_none_features(self):
        ok, reasons = validate_simd_features(None, "PowerPC")
        self.assertFalse(ok)

    def test_legit_x86_64_features(self):
        ok, reasons = validate_simd_features(["sse2", "avx2"], "x86_64")
        self.assertTrue(ok)

    def test_legit_arm_neon(self):
        ok, reasons = validate_simd_features(["neon"], "ARM64")
        self.assertTrue(ok)


class TestCacheTimingValidation(unittest.TestCase):
    """Check 3: Cache timing must match architecture characteristics."""

    def test_legit_powerpc_cache(self):
        profile = {"l1_latency_ns": 3.0, "l2_latency_ns": 25.0}
        ok, reasons = validate_cache_timing(profile, "PowerPC")
        self.assertTrue(ok)

    def test_modern_x86_cache_claiming_powerpc(self):
        """Modern x86 has much faster L2 than PowerPC G4 — must fail."""
        profile = {"l1_latency_ns": 1.0, "l2_latency_ns": 5.0}
        ok, reasons = validate_cache_timing(profile, "PowerPC")
        self.assertFalse(ok)

    def test_no_cache_profile(self):
        ok, reasons = validate_cache_timing({}, "PowerPC")
        self.assertFalse(ok)

    def test_none_cache_profile(self):
        ok, reasons = validate_cache_timing(None, "PowerPC")
        self.assertFalse(ok)

    def test_legit_x86_64_cache(self):
        profile = {"l1_latency_ns": 1.5, "l2_latency_ns": 8.0}
        ok, reasons = validate_cache_timing(profile, "x86_64")
        self.assertTrue(ok)


class TestFullClassification(unittest.TestCase):
    """End-to-end: classify_arch_server_side."""

    def _make_payload(self, arch, cpu, simd_flags, cache_data=None):
        """Helper to build attestation payloads."""
        return {
            "device": {
                "family": "PowerPC" if arch in ("g4", "g5") else "x86_64",
                "arch": arch,
                "cpu": cpu,
            },
            "fingerprint": {
                "all_passed": True,
                "checks": {
                    "cpu_features": {"passed": True, "data": {"flags": simd_flags}},
                    "cache_timing": {"passed": True, "data": cache_data or {}},
                },
            },
        }

    def test_legit_g4_gets_2_5x(self):
        """Legitimate PowerPC G4 should get 2.5x multiplier."""
        payload = self._make_payload(
            arch="g4",
            cpu="PowerPC G4 (7447A)",
            simd_flags=["altivec", "vec_perm"],
            cache_data={"l1_latency_ns": 3.0, "l2_latency_ns": 25.0},
        )
        result = classify_arch_server_side(payload)
        self.assertTrue(result.valid)
        self.assertEqual(result.multiplier, 2.5)
        self.assertEqual(result.verified_arch, "g4")

    def test_spoofed_x86_as_g4_gets_1x(self):
        """THE MAIN ATTACK: Intel Xeon claiming G4 must be rejected → 1.0x."""
        payload = self._make_payload(
            arch="g4",
            cpu="Intel Xeon E5-2680 v4",
            simd_flags=["avx2", "sse2"],
            cache_data={"l1_latency_ns": 1.0, "l2_latency_ns": 5.0},
        )
        result = classify_arch_server_side(payload)
        self.assertFalse(result.valid)
        self.assertEqual(result.multiplier, 1.0)
        self.assertFalse(result.checks["cpu_brand_match"])
        self.assertFalse(result.checks["simd_features"])

    def test_spoofed_ryzen_as_g4_gets_1x(self):
        """AMD Ryzen claiming G4 must be rejected."""
        payload = self._make_payload(
            arch="g4",
            cpu="AMD Ryzen 9 7950X",
            simd_flags=["avx2", "sse2"],
            cache_data={"l1_latency_ns": 0.8, "l2_latency_ns": 4.0},
        )
        result = classify_arch_server_side(payload)
        self.assertFalse(result.valid)
        self.assertEqual(result.multiplier, 1.0)

    def test_partial_spoof_correct_brand_wrong_simd(self):
        """Even with correct brand string, wrong SIMD → rejected."""
        payload = self._make_payload(
            arch="g4",
            cpu="PowerPC G4 (7447A)",
            simd_flags=["avx2"],  # Wrong! Should be altivec
            cache_data={"l1_latency_ns": 3.0, "l2_latency_ns": 25.0},
        )
        result = classify_arch_server_side(payload)
        self.assertFalse(result.valid)
        self.assertEqual(result.multiplier, 1.0)

    def test_partial_spoof_correct_brand_correct_simd_wrong_cache(self):
        """Correct brand + SIMD but x86 cache timings → rejected."""
        payload = self._make_payload(
            arch="g4",
            cpu="PowerPC G4 (7447A)",
            simd_flags=["altivec", "vec_perm"],
            cache_data={"l1_latency_ns": 0.5, "l2_latency_ns": 3.0},  # Too fast for G4
        )
        result = classify_arch_server_side(payload)
        self.assertFalse(result.valid)
        self.assertEqual(result.multiplier, 1.0)

    def test_legit_modern_x86_gets_1x(self):
        """Honest modern x86 should get 1.0x."""
        payload = self._make_payload(
            arch="modern_x86",
            cpu="AMD Ryzen 9 7950X",
            simd_flags=["sse2", "avx2"],
            cache_data={"l1_latency_ns": 1.5, "l2_latency_ns": 8.0},
        )
        result = classify_arch_server_side(payload)
        self.assertTrue(result.valid)
        self.assertEqual(result.multiplier, 1.0)

    def test_unknown_arch_gets_1x(self):
        payload = self._make_payload(
            arch="quantum_cpu",
            cpu="QuantumChip",
            simd_flags=[],
        )
        result = classify_arch_server_side(payload)
        self.assertFalse(result.valid)
        self.assertEqual(result.multiplier, 1.0)

    def test_empty_payload(self):
        result = classify_arch_server_side({})
        self.assertFalse(result.valid)
        self.assertEqual(result.multiplier, 1.0)

    def test_legit_g5_gets_2x(self):
        payload = self._make_payload(
            arch="g5",
            cpu="PowerPC G5 (970MP)",
            simd_flags=["altivec", "vec_perm"],
            cache_data={"l1_latency_ns": 2.5, "l2_latency_ns": 20.0},
        )
        result = classify_arch_server_side(payload)
        self.assertTrue(result.valid)
        self.assertEqual(result.multiplier, 2.0)


if __name__ == "__main__":
    unittest.main()
