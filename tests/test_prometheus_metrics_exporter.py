"""Unit tests for the RustChain Prometheus metrics exporter.

All tests use mocked HTTP responses — no live node required.
"""

from __future__ import annotations

import json
import time
import unittest
from unittest.mock import MagicMock, patch

from prometheus_client import CollectorRegistry, generate_latest

from scripts.prometheus_exporter import RustChainCollector, fetch_endpoint


# ---------------------------------------------------------------------------
# Fixtures: realistic JSON responses from the RustChain node
# ---------------------------------------------------------------------------

HEALTH_OK = {
    "backup_age_hours": 0.08,
    "db_rw": True,
    "ok": True,
    "tip_age_slots": 0,
    "uptime_s": 97760,
    "version": "2.2.1-rip200",
}

EPOCH_OK = {
    "blocks_per_epoch": 144,
    "enrolled_miners": 22,
    "epoch": 94,
    "epoch_pot": 1.5,
    "slot": 13580,
}

MINERS_OK = [
    {
        "miner": "dual-g4-125",
        "hardware_type": "Vintage PowerPC",
        "device_arch": "ppc",
        "device_family": "PowerMac G4",
        "antiquity_multiplier": 2.5,
        "last_attest": int(time.time()) - 300,
        "entropy_score": 0.87,
    },
    {
        "miner": "victus-x86-scott",
        "hardware_type": "Modern x86-64",
        "device_arch": "x86_64",
        "device_family": "HP Victus",
        "antiquity_multiplier": 1.0,
        "last_attest": int(time.time()) - 60,
        "entropy_score": 0.92,
    },
]

WALLET_OK = {
    "amount_i64": 8231900000,
    "amount_rtc": 82319.0,
    "miner_id": "founder_community",
}


def _make_collector(
    health=HEALTH_OK,
    epoch=EPOCH_OK,
    miners=MINERS_OK,
    wallet=WALLET_OK,
    health_err=None,
    epoch_err=None,
    miners_err=None,
    wallet_err=None,
    tracked_wallets=None,
):
    """Create a RustChainCollector with mocked HTTP calls."""

    def mock_fetch(base_url, path, timeout_s=15, verify_tls=False):
        mapping = {
            "/health": (health, health_err, 0.01),
            "/epoch": (epoch, epoch_err, 0.01),
            "/api/miners": (miners, miners_err, 0.01),
        }
        return mapping.get(path, (None, "unknown_path", 0.01))

    def mock_wallet_fetch(base_url, miner_id, timeout_s=15, verify_tls=False):
        if wallet_err:
            return None, wallet_err, 0.01
        return wallet, None, 0.01

    collector = RustChainCollector(
        node_url="http://mock-node:8099",
        poll_timeout=5,
        tracked_wallets=tracked_wallets or [],
    )

    # Patch the module-level fetch functions
    collector._orig_fetch = collector._fetch
    collector._orig_fetch_balance = collector._fetch_balance

    def patched_fetch(path):
        data, err, elapsed = mock_fetch(collector.node_url, path)
        if err:
            collector._scrape_errors[path] = collector._scrape_errors.get(path, 0) + 1
        return data, err

    def patched_fetch_balance(wallet_name):
        data, err, elapsed = mock_wallet_fetch(collector.node_url, wallet_name)
        if err:
            ep = f"/wallet/balance?miner_id={wallet_name}"
            collector._scrape_errors[ep] = collector._scrape_errors.get(ep, 0) + 1
        return data, err

    collector._fetch = patched_fetch
    collector._fetch_balance = patched_fetch_balance

    return collector


def _collect_to_text(collector):
    """Run the collector and return Prometheus text exposition format."""
    registry = CollectorRegistry()
    registry.register(collector)
    return generate_latest(registry).decode("utf-8")


def _metric_value(text: str, metric_name: str) -> str | None:
    """Extract the value of a metric line from Prometheus text output."""
    for line in text.splitlines():
        if line.startswith(metric_name + " ") or line.startswith(metric_name + "{"):
            # e.g. "rustchain_node_up 1.0" → "1.0"
            return line.rsplit(" ", 1)[-1]
    return None


def _metric_lines(text: str, prefix: str) -> list[str]:
    """Return all lines starting with a given metric prefix."""
    return [
        line
        for line in text.splitlines()
        if line.startswith(prefix) and not line.startswith("# ")
    ]


# ---------------------------------------------------------------------------
# Test cases
# ---------------------------------------------------------------------------


class TestHealthMetrics(unittest.TestCase):
    def test_node_up_when_healthy(self):
        text = _collect_to_text(_make_collector())
        self.assertEqual(_metric_value(text, "rustchain_node_up"), "1.0")

    def test_node_up_zero_when_down(self):
        text = _collect_to_text(_make_collector(health=None, health_err="timeout"))
        self.assertEqual(_metric_value(text, "rustchain_node_up"), "0.0")

    def test_uptime_seconds(self):
        text = _collect_to_text(_make_collector())
        self.assertEqual(_metric_value(text, "rustchain_node_uptime_seconds"), "97760.0")

    def test_version_info_label(self):
        text = _collect_to_text(_make_collector())
        lines = _metric_lines(text, "rustchain_node_version_info")
        self.assertTrue(len(lines) >= 1)
        self.assertIn('version="2.2.1-rip200"', lines[0])
        self.assertTrue(lines[0].endswith("1.0"))

    def test_db_rw_metric(self):
        text = _collect_to_text(_make_collector())
        self.assertEqual(_metric_value(text, "rustchain_db_rw"), "1.0")

    def test_backup_age_hours(self):
        text = _collect_to_text(_make_collector())
        self.assertEqual(_metric_value(text, "rustchain_backup_age_hours"), "0.08")

    def test_tip_age_slots(self):
        text = _collect_to_text(_make_collector())
        self.assertEqual(_metric_value(text, "rustchain_tip_age_slots"), "0.0")


class TestEpochMetrics(unittest.TestCase):
    def test_epoch_current(self):
        text = _collect_to_text(_make_collector())
        self.assertEqual(_metric_value(text, "rustchain_epoch_current"), "94.0")

    def test_epoch_slot(self):
        text = _collect_to_text(_make_collector())
        self.assertEqual(_metric_value(text, "rustchain_epoch_slot"), "13580.0")

    def test_blocks_per_epoch(self):
        text = _collect_to_text(_make_collector())
        self.assertEqual(
            _metric_value(text, "rustchain_epoch_blocks_per_epoch"), "144.0"
        )

    def test_enrolled_miners(self):
        text = _collect_to_text(_make_collector())
        self.assertEqual(
            _metric_value(text, "rustchain_epoch_enrolled_miners"), "22.0"
        )

    def test_epoch_pot_rtc(self):
        text = _collect_to_text(_make_collector())
        self.assertEqual(_metric_value(text, "rustchain_epoch_pot_rtc"), "1.5")


class TestMinerMetrics(unittest.TestCase):
    def test_active_miners_count(self):
        text = _collect_to_text(_make_collector())
        self.assertEqual(_metric_value(text, "rustchain_miners_active"), "2.0")

    def test_miners_total(self):
        text = _collect_to_text(_make_collector())
        self.assertEqual(_metric_value(text, "rustchain_miners_total"), "2.0")

    def test_per_miner_attestation_age(self):
        text = _collect_to_text(_make_collector())
        lines = _metric_lines(text, "rustchain_attestation_age_seconds")
        self.assertTrue(len(lines) >= 2, f"Expected >=2 attestation age lines, got: {lines}")
        miner_names = " ".join(lines)
        self.assertIn("dual-g4-125", miner_names)
        self.assertIn("victus-x86-scott", miner_names)

    def test_per_miner_entropy_score(self):
        text = _collect_to_text(_make_collector())
        lines = _metric_lines(text, "rustchain_miner_entropy_score")
        self.assertTrue(len(lines) >= 2)
        combined = " ".join(lines)
        self.assertIn("dual-g4-125", combined)

    def test_per_miner_antiquity_multiplier(self):
        text = _collect_to_text(_make_collector())
        lines = _metric_lines(text, "rustchain_miner_antiquity_multiplier")
        self.assertTrue(len(lines) >= 2)

    def test_no_miners_returns_zero(self):
        text = _collect_to_text(_make_collector(miners=[], miners_err=None))
        self.assertEqual(_metric_value(text, "rustchain_miners_active"), "0.0")

    def test_miners_error_returns_zero(self):
        text = _collect_to_text(
            _make_collector(miners=None, miners_err="http_500")
        )
        self.assertEqual(_metric_value(text, "rustchain_miners_active"), "0.0")


class TestWalletMetrics(unittest.TestCase):
    def test_wallet_balance(self):
        text = _collect_to_text(
            _make_collector(tracked_wallets=["founder_community"])
        )
        lines = _metric_lines(text, "rustchain_wallet_balance_rtc")
        self.assertTrue(len(lines) >= 1, f"Expected wallet balance line, got: {lines}")
        self.assertIn("founder_community", lines[0])
        self.assertIn("82319.0", lines[0])

    def test_no_tracked_wallets(self):
        text = _collect_to_text(_make_collector(tracked_wallets=[]))
        lines = _metric_lines(text, "rustchain_wallet_balance_rtc")
        self.assertEqual(len(lines), 0)


class TestScrapeErrors(unittest.TestCase):
    def test_scrape_error_increments_on_failure(self):
        collector = _make_collector(health=None, health_err="timeout")
        _collect_to_text(collector)  # first scrape
        _collect_to_text(collector)  # second scrape — error count goes to 2
        text = _collect_to_text(collector)  # third scrape — 3

        lines = _metric_lines(text, "rustchain_scrape_errors_total")
        self.assertTrue(len(lines) >= 1, f"Expected scrape errors, got: {lines}")
        # The /health endpoint should have an error count of 3
        health_lines = [l for l in lines if "/health" in l]
        self.assertTrue(len(health_lines) >= 1)
        self.assertIn("3.0", health_lines[0])


class TestPrometheusTextFormat(unittest.TestCase):
    def test_output_is_valid_prometheus_format(self):
        text = _collect_to_text(_make_collector())
        # Every non-empty, non-comment line should be "<metric_name>{labels} value"
        for line in text.splitlines():
            if not line or line.startswith("#"):
                continue
            parts = line.rsplit(" ", 1)
            self.assertEqual(
                len(parts),
                2,
                f"Invalid Prometheus line format: {line!r}",
            )
            # Value should be parseable as float
            try:
                float(parts[1])
            except ValueError:
                self.fail(f"Non-numeric metric value in line: {line!r}")

    def test_help_and_type_comments_present(self):
        text = _collect_to_text(_make_collector())
        self.assertIn("# HELP rustchain_node_up", text)
        self.assertIn("# TYPE rustchain_node_up gauge", text)
        self.assertIn("# HELP rustchain_epoch_current", text)
        self.assertIn("# TYPE rustchain_epoch_current gauge", text)


class TestPartialFailures(unittest.TestCase):
    """Verify that a failure on one endpoint doesn't block others."""

    def test_health_down_epoch_still_exported(self):
        text = _collect_to_text(
            _make_collector(health=None, health_err="timeout")
        )
        self.assertEqual(_metric_value(text, "rustchain_node_up"), "0.0")
        # Epoch should still be present
        self.assertEqual(_metric_value(text, "rustchain_epoch_current"), "94.0")

    def test_epoch_down_miners_still_exported(self):
        text = _collect_to_text(
            _make_collector(epoch=None, epoch_err="http_503")
        )
        # Miners should still show up
        self.assertEqual(_metric_value(text, "rustchain_miners_active"), "2.0")

    def test_all_endpoints_down(self):
        text = _collect_to_text(
            _make_collector(
                health=None,
                epoch=None,
                miners=None,
                health_err="timeout",
                epoch_err="timeout",
                miners_err="timeout",
            )
        )
        self.assertEqual(_metric_value(text, "rustchain_node_up"), "0.0")
        self.assertEqual(_metric_value(text, "rustchain_miners_active"), "0.0")
        # Should still produce valid output, not crash
        self.assertIn("# HELP", text)


if __name__ == "__main__":
    unittest.main()
