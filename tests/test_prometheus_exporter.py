#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Tests for scripts/prometheus_exporter.py

Run: python -m pytest tests/test_prometheus_exporter.py -v
"""

import json
import os
import unittest
from unittest import mock

from scripts.prometheus_exporter import (
    ExporterConfig,
    MetricSample,
    MetricsCollector,
    ScrapeResult,
    _escape_label_value,
    fetch_endpoint,
    render_metrics,
    scrape_node,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


class FakeResp:
    """Minimal file-like returned by mocked urlopen."""

    def __init__(self, data: bytes, code: int = 200) -> None:
        self._data = data
        self.status = code

    def read(self) -> bytes:
        return self._data

    def __enter__(self) -> "FakeResp":
        return self

    def __exit__(self, *args: object) -> None:
        pass


HEALTH_OK: dict = {
    "ok": True,
    "uptime_s": 86400,
    "tip_age_slots": 0,
    "backup_age_hours": 0.1,
    "db_rw": True,
    "version": "2.2.1-rip200",
}

EPOCH_OK: dict = {
    "epoch": 73,
    "slot": 10554,
    "blocks_per_epoch": 144,
    "epoch_pot": 1.5,
    "enrolled_miners": 12,
}

MINERS_OK: list = [
    {
        "miner": "victus-x86-scott",
        "hardware_type": "Modern x86-64",
        "device_arch": "x86_64",
        "device_family": "Victus",
        "antiquity_multiplier": 1.0,
        "last_attest": 1700000000,
        "entropy_score": 0.85,
    },
    {
        "miner": "g4-ppc-alice",
        "hardware_type": "Vintage PowerPC",
        "device_arch": "powerpc",
        "device_family": "PowerMac G4",
        "antiquity_multiplier": 2.5,
        "last_attest": 1699999000,
        "entropy_score": 0.72,
    },
]


def _fake_urlopen(responses: dict):
    """Return a side_effect callable that maps URL suffixes to responses."""

    def _side_effect(req, timeout=15, context=None):
        url = req.full_url if hasattr(req, "full_url") else str(req)
        for suffix, payload in responses.items():
            if url.endswith(suffix):
                if isinstance(payload, Exception):
                    raise payload
                return FakeResp(json.dumps(payload).encode())
        return FakeResp(b"null", code=404)

    return _side_effect


# ---------------------------------------------------------------------------
# ExporterConfig
# ---------------------------------------------------------------------------


class TestExporterConfig(unittest.TestCase):
    def test_defaults(self):
        cfg = ExporterConfig()
        self.assertEqual(cfg.port, 9100)
        self.assertEqual(cfg.scrape_interval, 30)
        self.assertFalse(cfg.verify_tls)

    def test_from_env_defaults(self):
        env = {
            "RUSTCHAIN_NODE_URL": "",
            "EXPORTER_PORT": "",
            "SCRAPE_INTERVAL": "",
            "VERIFY_TLS": "",
            "HTTP_TIMEOUT": "",
        }
        # Clear env vars to test defaults
        saved = {}
        for key in env:
            saved[key] = os.environ.pop(key, None)
        try:
            cfg = ExporterConfig.from_env()
            self.assertIn("50.28.86.131", cfg.node_url)
            self.assertEqual(cfg.port, 9100)
            self.assertEqual(cfg.scrape_interval, 30)
            self.assertFalse(cfg.verify_tls)
            self.assertEqual(cfg.http_timeout, 15)
        finally:
            for key, val in saved.items():
                if val is not None:
                    os.environ[key] = val

    def test_from_env_custom(self):
        env = {
            "RUSTCHAIN_NODE_URL": "https://mynode:8443/",
            "EXPORTER_PORT": "9200",
            "SCRAPE_INTERVAL": "10",
            "VERIFY_TLS": "1",
            "HTTP_TIMEOUT": "5",
        }
        with mock.patch.dict(os.environ, env):
            cfg = ExporterConfig.from_env()
            self.assertEqual(cfg.node_url, "https://mynode:8443")
            self.assertEqual(cfg.port, 9200)
            self.assertEqual(cfg.scrape_interval, 10)
            self.assertTrue(cfg.verify_tls)
            self.assertEqual(cfg.http_timeout, 5)


# ---------------------------------------------------------------------------
# Label escaping
# ---------------------------------------------------------------------------


class TestEscapeLabelValue(unittest.TestCase):
    def test_plain(self):
        self.assertEqual(_escape_label_value("hello"), "hello")

    def test_quotes(self):
        self.assertEqual(_escape_label_value('say "hi"'), 'say \\"hi\\"')

    def test_backslash(self):
        self.assertEqual(_escape_label_value("a\\b"), "a\\\\b")

    def test_newline(self):
        self.assertEqual(_escape_label_value("line1\nline2"), "line1\\nline2")


# ---------------------------------------------------------------------------
# render_metrics
# ---------------------------------------------------------------------------


class TestRenderMetrics(unittest.TestCase):
    def test_empty(self):
        result = ScrapeResult()
        text = render_metrics(result)
        self.assertEqual(text.strip(), "")

    def test_simple_gauge(self):
        result = ScrapeResult(samples=[
            MetricSample(name="rustchain_up", value=1.0, help_text="Node is up"),
        ])
        text = render_metrics(result)
        self.assertIn("# HELP rustchain_up Node is up", text)
        self.assertIn("# TYPE rustchain_up gauge", text)
        self.assertIn("rustchain_up 1.0", text)

    def test_labelled_metric(self):
        result = ScrapeResult(samples=[
            MetricSample(
                name="rustchain_miner_antiquity_multiplier",
                value=2.5,
                labels={"miner": "g4-ppc-alice", "device_family": "PowerMac G4"},
                help_text="Miner multiplier",
            ),
        ])
        text = render_metrics(result)
        self.assertIn('device_family="PowerMac G4"', text)
        self.assertIn('miner="g4-ppc-alice"', text)
        self.assertIn("2.5", text)

    def test_help_emitted_once(self):
        result = ScrapeResult(samples=[
            MetricSample(name="m", value=1.0, labels={"a": "1"}, help_text="help"),
            MetricSample(name="m", value=2.0, labels={"a": "2"}, help_text="help"),
        ])
        text = render_metrics(result)
        self.assertEqual(text.count("# HELP m"), 1)
        self.assertEqual(text.count("# TYPE m"), 1)

    def test_counter_type(self):
        result = ScrapeResult(samples=[
            MetricSample(
                name="rustchain_scrape_errors_total",
                value=3.0,
                help_text="Errors",
                metric_type="counter",
            ),
        ])
        text = render_metrics(result)
        self.assertIn("# TYPE rustchain_scrape_errors_total counter", text)


# ---------------------------------------------------------------------------
# scrape_node (mocked HTTP)
# ---------------------------------------------------------------------------


class TestScrapeNode(unittest.TestCase):
    def _config(self) -> ExporterConfig:
        return ExporterConfig(
            node_url="https://testnode:443",
            port=9100,
            scrape_interval=30,
            verify_tls=False,
            http_timeout=5,
        )

    @mock.patch("scripts.prometheus_exporter.urllib.request.urlopen")
    def test_all_endpoints_ok(self, mock_urlopen):
        mock_urlopen.side_effect = _fake_urlopen({
            "/health": HEALTH_OK,
            "/epoch": EPOCH_OK,
            "/api/miners": MINERS_OK,
        })
        result = scrape_node(self._config())
        names = {s.name for s in result.samples}

        # Check all expected metric names are present.
        self.assertIn("rustchain_up", names)
        self.assertIn("rustchain_node_uptime_seconds", names)
        self.assertIn("rustchain_epoch_current", names)
        self.assertIn("rustchain_epoch_slot", names)
        self.assertIn("rustchain_epoch_pot_rtc", names)
        self.assertIn("rustchain_miners_active_total", names)
        self.assertIn("rustchain_miner_last_attest_timestamp", names)
        self.assertIn("rustchain_miner_antiquity_multiplier", names)
        self.assertIn("rustchain_scrape_duration_seconds", names)
        self.assertIn("rustchain_scrape_errors_total", names)

        # Verify specific values.
        up = [s for s in result.samples if s.name == "rustchain_up"][0]
        self.assertEqual(up.value, 1.0)

        uptime = [s for s in result.samples if s.name == "rustchain_node_uptime_seconds"][0]
        self.assertEqual(uptime.value, 86400.0)

        epoch = [s for s in result.samples if s.name == "rustchain_epoch_current"][0]
        self.assertEqual(epoch.value, 73.0)

        miners_total = [s for s in result.samples if s.name == "rustchain_miners_active_total"][0]
        self.assertEqual(miners_total.value, 2.0)

        # Check per-miner labels.
        attest_samples = [s for s in result.samples if s.name == "rustchain_miner_last_attest_timestamp"]
        self.assertEqual(len(attest_samples), 2)
        miner_ids = {s.labels["miner"] for s in attest_samples}
        self.assertIn("victus-x86-scott", miner_ids)
        self.assertIn("g4-ppc-alice", miner_ids)

        self.assertEqual(result.error_count, 0)

    @mock.patch("scripts.prometheus_exporter.urllib.request.urlopen")
    def test_health_down(self, mock_urlopen):
        from urllib.error import URLError

        mock_urlopen.side_effect = URLError("connection refused")
        result = scrape_node(self._config())

        up = [s for s in result.samples if s.name == "rustchain_up"][0]
        self.assertEqual(up.value, 0.0)
        self.assertGreater(result.error_count, 0)

    @mock.patch("scripts.prometheus_exporter.urllib.request.urlopen")
    def test_partial_failure_epoch_down(self, mock_urlopen):
        """Health succeeds but epoch returns an error."""
        def _side_effect(req, timeout=15, context=None):
            url = req.full_url if hasattr(req, "full_url") else str(req)
            if url.endswith("/health"):
                return FakeResp(json.dumps(HEALTH_OK).encode())
            if url.endswith("/api/miners"):
                return FakeResp(json.dumps(MINERS_OK).encode())
            raise TimeoutError("epoch timed out")

        mock_urlopen.side_effect = _side_effect
        result = scrape_node(self._config())

        up = [s for s in result.samples if s.name == "rustchain_up"][0]
        self.assertEqual(up.value, 1.0)

        names = {s.name for s in result.samples}
        self.assertNotIn("rustchain_epoch_current", names)
        self.assertIn("rustchain_miners_active_total", names)

        # One error from epoch.
        self.assertEqual(result.error_count, 1)

    @mock.patch("scripts.prometheus_exporter.urllib.request.urlopen")
    def test_miners_empty_list(self, mock_urlopen):
        mock_urlopen.side_effect = _fake_urlopen({
            "/health": HEALTH_OK,
            "/epoch": EPOCH_OK,
            "/api/miners": [],
        })
        result = scrape_node(self._config())
        miners_total = [s for s in result.samples if s.name == "rustchain_miners_active_total"][0]
        self.assertEqual(miners_total.value, 0.0)

        attest_samples = [s for s in result.samples if s.name == "rustchain_miner_last_attest_timestamp"]
        self.assertEqual(len(attest_samples), 0)

    @mock.patch("scripts.prometheus_exporter.urllib.request.urlopen")
    def test_miner_missing_fields(self, mock_urlopen):
        """Miner entries with missing optional fields should not crash."""
        miners_partial = [
            {"miner": "bare-miner"},  # no last_attest, no multiplier, no device info
            {},  # completely empty
            {"miner": ""},  # empty miner id
        ]
        mock_urlopen.side_effect = _fake_urlopen({
            "/health": HEALTH_OK,
            "/epoch": EPOCH_OK,
            "/api/miners": miners_partial,
        })
        result = scrape_node(self._config())

        miners_total = [s for s in result.samples if s.name == "rustchain_miners_active_total"][0]
        self.assertEqual(miners_total.value, 3.0)

        # bare-miner has no last_attest or multiplier, so those per-miner metrics are absent.
        attest_samples = [s for s in result.samples if s.name == "rustchain_miner_last_attest_timestamp"]
        self.assertEqual(len(attest_samples), 0)

    @mock.patch("scripts.prometheus_exporter.urllib.request.urlopen")
    def test_invalid_json(self, mock_urlopen):
        """Malformed JSON from the node should be handled gracefully."""
        def _side_effect(req, timeout=15, context=None):
            return FakeResp(b"NOT JSON AT ALL")

        mock_urlopen.side_effect = _side_effect
        result = scrape_node(self._config())

        up = [s for s in result.samples if s.name == "rustchain_up"][0]
        self.assertEqual(up.value, 0.0)
        self.assertGreater(result.error_count, 0)


# ---------------------------------------------------------------------------
# MetricsCollector
# ---------------------------------------------------------------------------


class TestMetricsCollector(unittest.TestCase):
    def test_initial_state_is_none(self):
        cfg = ExporterConfig(node_url="https://localhost:1")
        collector = MetricsCollector(cfg)
        self.assertIsNone(collector.latest)

    @mock.patch("scripts.prometheus_exporter.urllib.request.urlopen")
    def test_scrape_once(self, mock_urlopen):
        mock_urlopen.side_effect = _fake_urlopen({
            "/health": HEALTH_OK,
            "/epoch": EPOCH_OK,
            "/api/miners": MINERS_OK,
        })
        cfg = ExporterConfig(node_url="https://testnode:443")
        collector = MetricsCollector(cfg)
        result = collector.scrape_once()
        self.assertIsNotNone(result)
        self.assertIsNotNone(collector.latest)
        names = {s.name for s in result.samples}
        self.assertIn("rustchain_up", names)

    @mock.patch("scripts.prometheus_exporter.urllib.request.urlopen")
    def test_cumulative_error_counter(self, mock_urlopen):
        """Error counter should accumulate across scrape cycles."""
        from urllib.error import URLError

        mock_urlopen.side_effect = URLError("fail")
        cfg = ExporterConfig(node_url="https://testnode:443")
        collector = MetricsCollector(cfg)

        collector.scrape_once()
        first_errors = [
            s for s in collector.latest.samples if s.name == "rustchain_scrape_errors_total"
        ][0].value

        collector.scrape_once()
        second_errors = [
            s for s in collector.latest.samples if s.name == "rustchain_scrape_errors_total"
        ][0].value

        self.assertGreater(second_errors, first_errors)


# ---------------------------------------------------------------------------
# fetch_endpoint
# ---------------------------------------------------------------------------


class TestFetchEndpoint(unittest.TestCase):
    @mock.patch("scripts.prometheus_exporter.urllib.request.urlopen")
    def test_success(self, mock_urlopen):
        mock_urlopen.return_value = FakeResp(json.dumps({"ok": True}).encode())
        data, err = fetch_endpoint("https://node:443", "/health")
        self.assertIsNone(err)
        self.assertEqual(data, {"ok": True})

    @mock.patch("scripts.prometheus_exporter.urllib.request.urlopen")
    def test_timeout(self, mock_urlopen):
        mock_urlopen.side_effect = TimeoutError("timed out")
        data, err = fetch_endpoint("https://node:443", "/health")
        self.assertIsNone(data)
        self.assertEqual(err, "timeout")

    @mock.patch("scripts.prometheus_exporter.urllib.request.urlopen")
    def test_http_error(self, mock_urlopen):
        from urllib.error import HTTPError

        mock_urlopen.side_effect = HTTPError(
            url="https://node/health", code=429, msg="Too Many Requests",
            hdrs=None, fp=None,  # type: ignore[arg-type]
        )
        data, err = fetch_endpoint("https://node:443", "/health")
        self.assertIsNone(data)
        self.assertEqual(err, "http_429")


# ---------------------------------------------------------------------------
# End-to-end render
# ---------------------------------------------------------------------------


class TestEndToEndRender(unittest.TestCase):
    @mock.patch("scripts.prometheus_exporter.urllib.request.urlopen")
    def test_full_render_is_valid_prometheus_text(self, mock_urlopen):
        mock_urlopen.side_effect = _fake_urlopen({
            "/health": HEALTH_OK,
            "/epoch": EPOCH_OK,
            "/api/miners": MINERS_OK,
        })
        cfg = ExporterConfig(node_url="https://testnode:443")
        result = scrape_node(cfg)
        text = render_metrics(result)

        # Basic format validation.
        for line in text.splitlines():
            if not line:
                continue
            if line.startswith("#"):
                self.assertTrue(
                    line.startswith("# HELP") or line.startswith("# TYPE"),
                    f"Unexpected comment line: {line}",
                )
            else:
                # metric_name{labels} value  OR  metric_name value
                parts = line.split(" ")
                self.assertGreaterEqual(len(parts), 2, f"Malformed line: {line}")
                # Value should be a valid float.
                try:
                    float(parts[-1])
                except ValueError:
                    self.fail(f"Non-numeric value in line: {line}")


if __name__ == "__main__":
    unittest.main()
