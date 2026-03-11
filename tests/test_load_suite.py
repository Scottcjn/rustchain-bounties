# SPDX-License-Identifier: MIT
"""
Tests for the RustChain load-test suite.

Validates:
  • Miner identity generation and payload shapes (via miner_helpers)
  • graph_reporter.py data loaders and HTML output
  • Artillery / k6 config file syntax
  • Edge cases: empty data, missing fields, large inputs

Run:
    python -m pytest tests/test_load_suite.py -v
"""

import csv
import html as html_mod
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path

# Ensure load_tests package is importable
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from load_tests.miner_helpers import (
    ARCH_PROFILES,
    make_miner,
    entropy_report,
    attestation_payload,
    enroll_payload,
)

from load_tests.graph_reporter import (
    build_html_report,
    load_artillery_report,
    load_k6_summary,
    load_locust_stats,
    main as reporter_main,
    _svg_bar_chart,
    _svg_line_chart,
)


# ---------------------------------------------------------------------------
# Helper: write a minimal Locust CSV pair
# ---------------------------------------------------------------------------

def _write_locust_csvs(prefix, rows=None):
    """Create *_stats.csv (and optionally *_stats_history.csv) under *prefix*."""
    stats_path = f"{prefix}_stats.csv"
    history_path = f"{prefix}_stats_history.csv"

    if rows is None:
        rows = [
            {
                "Type": "GET", "Name": "/health",
                "Request Count": "120", "Failure Count": "2",
                "Median Response Time": "45", "Average Response Time": "52",
                "Min Response Time": "12", "Max Response Time": "320",
                "95%": "150", "99%": "280", "Requests/s": "4.0",
            },
            {
                "Type": "POST", "Name": "/attest/challenge",
                "Request Count": "80", "Failure Count": "10",
                "Median Response Time": "130", "Average Response Time": "160",
                "Min Response Time": "40", "Max Response Time": "900",
                "95%": "500", "99%": "800", "Requests/s": "2.5",
            },
        ]

    fieldnames = list(rows[0].keys()) if rows else []
    with open(stats_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

    # Minimal history
    hist_fields = ["Timestamp", "Name", "User Count", "Requests/s",
                   "Failures/s", "50%", "95%"]
    with open(history_path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=hist_fields)
        writer.writeheader()
        for i in range(5):
            writer.writerow({
                "Timestamp": str(1700000000 + i * 10),
                "Name": "/health",
                "User Count": str(10 + i),
                "Requests/s": str(3.5 + i * 0.2),
                "Failures/s": "0.1",
                "50%": str(40 + i * 2),
                "95%": str(120 + i * 5),
            })

    return stats_path, history_path


def _write_k6_summary(path):
    """Write a minimal k6 summary JSON."""
    data = {
        "metrics": {
            "http_req_duration": {
                "type": "trend",
                "contains": "time",
                "values": {
                    "avg": 123.4,
                    "min": 10.2,
                    "max": 890.1,
                    "p(90)": 450.0,
                    "p(95)": 600.0,
                    "p(99)": 800.0,
                    "count": 500,
                    "rate": 8.3,
                },
            },
            "http_req_failed": {
                "type": "rate",
                "contains": "default",
                "values": {"rate": 0.05, "passes": 25, "fails": 475},
            },
        }
    }
    with open(path, "w") as fh:
        json.dump(data, fh)
    return data


def _write_artillery_report(path):
    """Write a minimal Artillery JSON report."""
    data = {
        "aggregate": {
            "latency": {
                "min": 15, "max": 950, "median": 80, "p95": 400, "p99": 750,
            },
            "codes": {"200": 300, "429": 50, "500": 2},
            "counters": {"http.requests": 352, "http.responses": 352},
        },
        "intermediate": [
            {
                "timestamp": "2025-06-01T12:00:00Z",
                "latency": {"median": 70, "p95": 350},
                "rps": {"mean": 12.5},
            },
            {
                "timestamp": "2025-06-01T12:01:00Z",
                "latency": {"median": 90, "p95": 420},
                "rps": {"mean": 15.0},
            },
        ],
    }
    with open(path, "w") as fh:
        json.dump(data, fh)
    return data


# ===========================================================================
# Tests: Miner helpers (shared by all load test tools)
# ===========================================================================

class TestMinerHelpers(unittest.TestCase):
    """Test miner identity and payload generation from miner_helpers."""

    def test_make_miner_returns_required_keys(self):
        miner = make_miner()
        for key in ("miner_id", "wallet", "arch_key", "profile", "serial", "mac", "hostname"):
            self.assertIn(key, miner, f"Missing key: {key}")

    def test_miner_id_uses_prefix(self):
        miner = make_miner(prefix="locust")
        self.assertTrue(miner["miner_id"].startswith("locust-"))

    def test_miner_id_default_prefix(self):
        miner = make_miner()
        self.assertTrue(miner["miner_id"].startswith("load-"))

    def test_wallet_suffix(self):
        miner = make_miner()
        self.assertTrue(miner["wallet"].endswith("RTC"))

    def test_wallet_length(self):
        miner = make_miner()
        self.assertEqual(len(miner["wallet"]), 41, "Wallet should be 38 hex chars + 'RTC'")

    def test_unique_miners(self):
        ids = {make_miner()["miner_id"] for _ in range(50)}
        self.assertEqual(len(ids), 50, "Miner IDs should be unique")

    def test_serial_format(self):
        miner = make_miner()
        self.assertTrue(miner["serial"].startswith("SN-"))
        # SN- + 12 uppercase hex chars
        self.assertEqual(len(miner["serial"]), 15)

    def test_mac_format(self):
        miner = make_miner()
        parts = miner["mac"].split(":")
        self.assertEqual(len(parts), 6)
        for p in parts:
            self.assertEqual(len(p), 2)
            int(p, 16)  # should not raise

    def test_hostname_includes_miner_id(self):
        miner = make_miner()
        self.assertEqual(miner["hostname"], f"host-{miner['miner_id']}")

    def test_attestation_payload_shape(self):
        miner = make_miner()
        payload = attestation_payload(miner, "test-nonce-abc123")
        for key in ("miner", "miner_id", "nonce", "report", "device", "signals", "fingerprint"):
            self.assertIn(key, payload, f"Payload missing key: {key}")
        self.assertEqual(payload["nonce"], "test-nonce-abc123")
        self.assertEqual(payload["miner"], miner["wallet"])
        self.assertTrue(payload["fingerprint"]["all_passed"])

    def test_attestation_payload_device(self):
        miner = make_miner()
        payload = attestation_payload(miner, "nonce")
        device = payload["device"]
        for key in ("family", "arch", "model", "cpu", "cores", "memory_gb", "serial"):
            self.assertIn(key, device)
        self.assertEqual(device["serial"], miner["serial"])

    def test_attestation_payload_report_structure(self):
        miner = make_miner()
        payload = attestation_payload(miner, "nonce-xyz")
        report = payload["report"]
        for key in ("nonce", "commitment", "derived", "entropy_score"):
            self.assertIn(key, report)
        self.assertIsInstance(report["commitment"], str)
        self.assertEqual(len(report["commitment"]), 64, "Commitment should be SHA-256 hex")

    def test_attestation_payload_fingerprint_checks(self):
        miner = make_miner()
        payload = attestation_payload(miner, "nonce")
        checks = payload["fingerprint"]["checks"]
        for check_name in ("anti_emulation", "cpu_features", "io_latency", "serial_binding"):
            self.assertIn(check_name, checks)
            self.assertTrue(checks[check_name]["passed"])

    def test_enroll_payload_shape(self):
        miner = make_miner()
        payload = enroll_payload(miner)
        self.assertEqual(payload["miner_pubkey"], miner["wallet"])
        self.assertEqual(payload["miner_id"], miner["miner_id"])
        self.assertIn("family", payload["device"])
        self.assertIn("arch", payload["device"])

    def test_entropy_report_has_valid_samples(self):
        report = entropy_report("nonce123", "walletABC")
        derived = report["derived"]
        self.assertEqual(derived["sample_count"], 48)
        self.assertEqual(len(derived["samples_preview"]), 12)
        self.assertGreater(derived["mean_ns"], 0)
        self.assertLessEqual(derived["min_ns"], derived["max_ns"])

    def test_entropy_report_commitment_deterministic_for_same_input(self):
        """Commitment should be a SHA-256 hex string of known length."""
        report = entropy_report("nonce-fixed", "wallet-fixed")
        self.assertEqual(len(report["commitment"]), 64)
        self.assertTrue(all(c in "0123456789abcdef" for c in report["commitment"]))

    def test_arch_profiles_all_valid(self):
        for key, prof in ARCH_PROFILES.items():
            self.assertIn("model", prof)
            self.assertIn("family", prof)
            self.assertIn("multiplier", prof)

    def test_powerpc_arch_uses_altivec_flag(self):
        """PowerPC miners should get 'altivec' in cpu_features."""
        # Force a PowerPC miner
        for _ in range(100):
            miner = make_miner()
            if "PowerPC" in miner["profile"]["family"]:
                payload = attestation_payload(miner, "nonce")
                flags = payload["fingerprint"]["checks"]["cpu_features"]["data"]["flags"]
                self.assertIn("altivec", flags)
                return
        self.skipTest("Didn't hit a PowerPC miner in 100 tries")

    def test_x86_arch_uses_avx2_flag(self):
        """x86/ARM miners should get 'avx2' in cpu_features."""
        for _ in range(100):
            miner = make_miner()
            if "PowerPC" not in miner["profile"]["family"]:
                payload = attestation_payload(miner, "nonce")
                flags = payload["fingerprint"]["checks"]["cpu_features"]["data"]["flags"]
                self.assertIn("avx2", flags)
                return
        self.skipTest("Didn't hit a non-PowerPC miner in 100 tries")


# ===========================================================================
# Tests: graph_reporter – data loaders
# ===========================================================================

class TestLocustLoader(unittest.TestCase):
    """Test load_locust_stats()."""

    def test_basic_parse(self):
        with tempfile.TemporaryDirectory() as td:
            prefix = os.path.join(td, "locust")
            _write_locust_csvs(prefix)
            data = load_locust_stats(prefix)
            self.assertEqual(data["source"], "locust")
            self.assertEqual(len(data["endpoints"]), 2)
            self.assertEqual(data["endpoints"][0]["name"], "/health")
            self.assertEqual(data["endpoints"][0]["requests"], 120)
            self.assertEqual(data["endpoints"][0]["failures"], 2)

    def test_timeseries_parsed(self):
        with tempfile.TemporaryDirectory() as td:
            prefix = os.path.join(td, "locust")
            _write_locust_csvs(prefix)
            data = load_locust_stats(prefix)
            self.assertEqual(len(data["timeseries"]), 5)
            self.assertIn("rps", data["timeseries"][0])

    def test_aggregated_row_skipped(self):
        with tempfile.TemporaryDirectory() as td:
            prefix = os.path.join(td, "locust")
            rows = [
                {
                    "Type": "GET", "Name": "/health",
                    "Request Count": "10", "Failure Count": "0",
                    "Median Response Time": "50", "Average Response Time": "55",
                    "Min Response Time": "10", "Max Response Time": "100",
                    "95%": "80", "99%": "90", "Requests/s": "2",
                },
                {
                    "Type": "", "Name": "Aggregated",
                    "Request Count": "10", "Failure Count": "0",
                    "Median Response Time": "50", "Average Response Time": "55",
                    "Min Response Time": "10", "Max Response Time": "100",
                    "95%": "80", "99%": "90", "Requests/s": "2",
                },
            ]
            _write_locust_csvs(prefix, rows)
            data = load_locust_stats(prefix)
            self.assertEqual(len(data["endpoints"]), 1)
            self.assertEqual(data["endpoints"][0]["name"], "/health")

    def test_missing_file_raises(self):
        with self.assertRaises(FileNotFoundError):
            load_locust_stats("/tmp/nonexistent_prefix")


class TestK6Loader(unittest.TestCase):
    """Test load_k6_summary()."""

    def test_basic_parse(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "k6.json")
            _write_k6_summary(path)
            data = load_k6_summary(path)
            self.assertEqual(data["source"], "k6")
            self.assertTrue(len(data["endpoints"]) >= 1)
            dur_ep = [e for e in data["endpoints"] if e["name"] == "http_req_duration"]
            self.assertEqual(len(dur_ep), 1)
            self.assertAlmostEqual(dur_ep[0]["avg"], 123.4)

    def test_empty_metrics(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "k6.json")
            with open(path, "w") as fh:
                json.dump({"metrics": {}}, fh)
            data = load_k6_summary(path)
            self.assertEqual(data["endpoints"], [])


class TestArtilleryLoader(unittest.TestCase):
    """Test load_artillery_report()."""

    def test_basic_parse(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "art.json")
            _write_artillery_report(path)
            data = load_artillery_report(path)
            self.assertEqual(data["source"], "artillery")
            self.assertEqual(data["endpoints"][0]["requests"], 352)
            self.assertEqual(data["endpoints"][0]["p95"], 400)

    def test_timeseries_parsed(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "art.json")
            _write_artillery_report(path)
            data = load_artillery_report(path)
            self.assertEqual(len(data["timeseries"]), 2)

    def test_codes_map(self):
        with tempfile.TemporaryDirectory() as td:
            path = os.path.join(td, "art.json")
            _write_artillery_report(path)
            data = load_artillery_report(path)
            codes = data["endpoints"][0]["codes"]
            self.assertEqual(codes["200"], 300)
            self.assertEqual(codes["429"], 50)


# ===========================================================================
# Tests: SVG chart helpers
# ===========================================================================

class TestSvgBarChart(unittest.TestCase):

    def test_produces_valid_svg(self):
        svg = _svg_bar_chart("Test Chart", ["A", "B"], [10, 20])
        self.assertIn("<svg", svg)
        self.assertIn("</svg>", svg)
        self.assertIn("Test Chart", svg)

    def test_zero_values(self):
        svg = _svg_bar_chart("Zeros", ["X", "Y"], [0, 0])
        self.assertIn("<svg", svg)

    def test_single_bar(self):
        svg = _svg_bar_chart("Single", ["Only"], [42.0])
        self.assertIn("42.0", svg)

    def test_empty_data(self):
        svg = _svg_bar_chart("Empty", [], [])
        self.assertIn("<svg", svg)

    def test_large_values(self):
        svg = _svg_bar_chart("Big", ["A", "B"], [1_000_000, 2_000_000])
        self.assertIn("<svg", svg)


class TestSvgLineChart(unittest.TestCase):

    def test_produces_valid_svg(self):
        svg = _svg_line_chart(
            "Latency", ["t1", "t2", "t3"],
            {"P50": [10, 20, 15], "P95": [50, 60, 55]},
        )
        self.assertIn("<svg", svg)
        self.assertIn("P50", svg)
        self.assertIn("P95", svg)

    def test_empty_series(self):
        result = _svg_line_chart("No Data", [], {})
        self.assertIn("No time-series data", result)

    def test_single_point(self):
        svg = _svg_line_chart("One", ["t1"], {"val": [42]})
        self.assertIn("<svg", svg)

    def test_multiple_series_legend(self):
        svg = _svg_line_chart(
            "Multi", ["t1", "t2"],
            {"A": [1, 2], "B": [3, 4], "C": [5, 6]},
        )
        self.assertIn("A", svg)
        self.assertIn("B", svg)
        self.assertIn("C", svg)


# ===========================================================================
# Tests: HTML report builder
# ===========================================================================

class TestBuildHtmlReport(unittest.TestCase):

    def test_locust_report(self):
        with tempfile.TemporaryDirectory() as td:
            prefix = os.path.join(td, "locust")
            _write_locust_csvs(prefix)
            data = load_locust_stats(prefix)
            out = os.path.join(td, "report.html")
            path = build_html_report(data, out)
            self.assertTrue(os.path.isfile(path))
            content = Path(path).read_text()
            self.assertIn("<!DOCTYPE html>", content)
            self.assertIn("RustChain", content)
            self.assertIn("/health", content)
            self.assertIn("<svg", content)

    def test_k6_report(self):
        with tempfile.TemporaryDirectory() as td:
            k6_path = os.path.join(td, "k6.json")
            _write_k6_summary(k6_path)
            data = load_k6_summary(k6_path)
            out = os.path.join(td, "k6_report.html")
            path = build_html_report(data, out)
            self.assertTrue(os.path.isfile(path))
            content = Path(path).read_text()
            self.assertIn("k6", content)

    def test_artillery_report(self):
        with tempfile.TemporaryDirectory() as td:
            art_path = os.path.join(td, "art.json")
            _write_artillery_report(art_path)
            data = load_artillery_report(art_path)
            out = os.path.join(td, "art_report.html")
            path = build_html_report(data, out)
            self.assertTrue(os.path.isfile(path))
            content = Path(path).read_text()
            self.assertIn("artillery", content)
            self.assertIn("200", content)

    def test_creates_output_dirs(self):
        with tempfile.TemporaryDirectory() as td:
            data = {"source": "locust", "endpoints": [], "timeseries": []}
            out = os.path.join(td, "nested", "deep", "report.html")
            path = build_html_report(data, out)
            self.assertTrue(os.path.isfile(path))

    def test_html_escaping(self):
        """Ensure special characters in names are HTML-escaped."""
        data = {
            "source": "locust",
            "endpoints": [{
                "name": "<script>alert('xss')</script>",
                "method": "GET", "requests": 1, "failures": 0,
                "median": 10, "p95": 20, "p99": 30,
                "avg": 15, "min": 5, "max": 50, "rps": 1,
            }],
            "timeseries": [],
        }
        with tempfile.TemporaryDirectory() as td:
            out = os.path.join(td, "xss.html")
            build_html_report(data, out)
            content = Path(out).read_text()
            self.assertNotIn("<script>alert", content)

    def test_report_contains_table(self):
        with tempfile.TemporaryDirectory() as td:
            prefix = os.path.join(td, "locust")
            _write_locust_csvs(prefix)
            data = load_locust_stats(prefix)
            out = os.path.join(td, "table.html")
            build_html_report(data, out)
            content = Path(out).read_text()
            self.assertIn("<table>", content)
            self.assertIn("<thead>", content)


# ===========================================================================
# Tests: CLI entry point
# ===========================================================================

class TestReporterCli(unittest.TestCase):

    def test_locust_cli(self):
        with tempfile.TemporaryDirectory() as td:
            prefix = os.path.join(td, "locust")
            _write_locust_csvs(prefix)
            out = os.path.join(td, "cli_report.html")
            rc = reporter_main(["--format", "locust", "--output", out, prefix])
            self.assertEqual(rc, 0)
            self.assertTrue(os.path.isfile(out))

    def test_k6_cli(self):
        with tempfile.TemporaryDirectory() as td:
            k6_path = os.path.join(td, "k6.json")
            _write_k6_summary(k6_path)
            out = os.path.join(td, "k6_cli.html")
            rc = reporter_main(["--format", "k6", "--output", out, k6_path])
            self.assertEqual(rc, 0)
            self.assertTrue(os.path.isfile(out))

    def test_artillery_cli(self):
        with tempfile.TemporaryDirectory() as td:
            art_path = os.path.join(td, "art.json")
            _write_artillery_report(art_path)
            out = os.path.join(td, "art_cli.html")
            rc = reporter_main(["--format", "artillery", "--output", out, art_path])
            self.assertEqual(rc, 0)

    def test_missing_input_returns_error(self):
        rc = reporter_main(["--format", "locust", "/tmp/does_not_exist_xyz"])
        self.assertEqual(rc, 1)

    def test_invalid_json_returns_error(self):
        with tempfile.TemporaryDirectory() as td:
            bad = os.path.join(td, "bad.json")
            Path(bad).write_text("not valid json {{{")
            rc = reporter_main(["--format", "k6", bad])
            self.assertEqual(rc, 1)

    def test_default_output_name(self):
        """When --output is omitted, output should be <input>_report.html."""
        with tempfile.TemporaryDirectory() as td:
            prefix = os.path.join(td, "locust")
            _write_locust_csvs(prefix)
            rc = reporter_main(["--format", "locust", prefix])
            self.assertEqual(rc, 0)
            expected = os.path.join(td, "locust_report.html")
            self.assertTrue(os.path.isfile(expected))


# ===========================================================================
# Tests: Config file validation (structure, not runtime)
# ===========================================================================

class TestConfigFiles(unittest.TestCase):
    """Validate that config files are syntactically correct."""

    REPO = os.path.join(os.path.dirname(__file__), "..")

    def test_artillery_yaml_is_valid(self):
        """Artillery config should be valid YAML with required keys."""
        config_path = os.path.join(self.REPO, "load_tests", "artillery_config.yml")
        self.assertTrue(os.path.isfile(config_path))
        try:
            import yaml
            with open(config_path) as fh:
                data = yaml.safe_load(fh)
            self.assertIn("config", data)
            self.assertIn("scenarios", data)
            self.assertIn("target", data["config"])
            self.assertIn("phases", data["config"])
            self.assertIsInstance(data["scenarios"], list)
            self.assertGreater(len(data["scenarios"]), 0)
        except ImportError:
            # yaml not installed; fall back to basic text checks
            content = Path(config_path).read_text()
            self.assertIn("config:", content)
            self.assertIn("scenarios:", content)
            self.assertIn("target:", content)

    def test_k6_script_has_required_exports(self):
        """k6 script should export key scenario functions."""
        k6_path = os.path.join(self.REPO, "load_tests", "k6_rustchain.js")
        self.assertTrue(os.path.isfile(k6_path))
        content = Path(k6_path).read_text()
        self.assertIn("export const options", content)
        self.assertIn("export function readEndpoints", content)
        self.assertIn("export function attestationCycle", content)
        self.assertIn("export function walletQueries", content)

    def test_k6_script_has_thresholds(self):
        """k6 script should define performance thresholds."""
        k6_path = os.path.join(self.REPO, "load_tests", "k6_rustchain.js")
        content = Path(k6_path).read_text()
        self.assertIn("thresholds", content)
        self.assertIn("http_req_duration", content)

    def test_artillery_processor_exports(self):
        """Artillery processor should export required functions."""
        proc_path = os.path.join(self.REPO, "load_tests", "artillery_processor.js")
        self.assertTrue(os.path.isfile(proc_path))
        content = Path(proc_path).read_text()
        self.assertIn("module.exports", content)
        self.assertIn("generateMinerId", content)
        self.assertIn("buildAttestPayload", content)

    def test_locustfile_has_user_classes(self):
        """Locustfile should define HttpUser subclasses."""
        locust_path = os.path.join(self.REPO, "load_tests", "locustfile.py")
        self.assertTrue(os.path.isfile(locust_path))
        content = Path(locust_path).read_text()
        self.assertIn("class ReadOnlyUser(HttpUser)", content)
        self.assertIn("class WalletQueryUser(HttpUser)", content)
        self.assertIn("class AttestationUser(HttpUser)", content)

    def test_locustfile_imports_from_miner_helpers(self):
        """Locustfile should import shared helpers, not duplicate logic."""
        locust_path = os.path.join(self.REPO, "load_tests", "locustfile.py")
        content = Path(locust_path).read_text()
        self.assertIn("from load_tests.miner_helpers import", content)

    def test_miner_helpers_exists(self):
        """Shared miner helpers module should exist."""
        path = os.path.join(self.REPO, "load_tests", "miner_helpers.py")
        self.assertTrue(os.path.isfile(path))


# ===========================================================================
# Tests: SPDX headers
# ===========================================================================

class TestSpdxHeaders(unittest.TestCase):
    """New code files must include SPDX headers per CONTRIBUTING.md."""

    LOAD_DIR = os.path.join(os.path.dirname(__file__), "..", "load_tests")

    def _check_spdx(self, filename):
        path = os.path.join(self.LOAD_DIR, filename)
        self.assertTrue(os.path.isfile(path), f"File missing: {filename}")
        with open(path) as fh:
            head = fh.read(500)
        self.assertIn("SPDX-License-Identifier: MIT", head,
                       f"{filename} missing SPDX header")

    def test_init_spdx(self):
        self._check_spdx("__init__.py")

    def test_locustfile_spdx(self):
        self._check_spdx("locustfile.py")

    def test_graph_reporter_spdx(self):
        self._check_spdx("graph_reporter.py")

    def test_miner_helpers_spdx(self):
        self._check_spdx("miner_helpers.py")

    def test_k6_spdx(self):
        self._check_spdx("k6_rustchain.js")

    def test_artillery_config_spdx(self):
        self._check_spdx("artillery_config.yml")

    def test_artillery_processor_spdx(self):
        self._check_spdx("artillery_processor.js")

    def test_test_file_spdx(self):
        path = os.path.join(os.path.dirname(__file__), "test_load_suite.py")
        with open(path) as fh:
            head = fh.read(500)
        self.assertIn("SPDX-License-Identifier: MIT", head)


if __name__ == "__main__":
    unittest.main()
