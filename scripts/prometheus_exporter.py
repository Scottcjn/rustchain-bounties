#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""RustChain Prometheus metrics exporter.

Scrapes the RustChain node API (/health, /epoch, /api/miners) on a
configurable interval and exposes the data as Prometheus-compatible
metrics on an HTTP endpoint (default :9100/metrics).

Metrics exposed:
  rustchain_up                      – 1 if the node is reachable, 0 otherwise
  rustchain_node_uptime_seconds     – node uptime reported by /health
  rustchain_node_tip_age_slots      – tip_age_slots from /health
  rustchain_node_backup_age_hours   – backup_age_hours from /health
  rustchain_node_db_rw              – 1 if db_rw is true, 0 otherwise
  rustchain_epoch_current           – current epoch number
  rustchain_epoch_slot              – current slot within the epoch
  rustchain_epoch_blocks_per_epoch  – blocks per epoch (configuration gauge)
  rustchain_epoch_pot_rtc           – epoch reward pot in RTC
  rustchain_epoch_enrolled_miners   – miners enrolled in the current epoch
  rustchain_miners_active_total     – total number of active miners
  rustchain_miner_last_attest_timestamp – per-miner last attestation (unix ts)
  rustchain_miner_antiquity_multiplier  – per-miner antiquity multiplier
  rustchain_scrape_duration_seconds – time taken for the last scrape
  rustchain_scrape_errors_total     – cumulative scrape error count

Environment variables:
  RUSTCHAIN_NODE_URL   – node base URL  (default: https://50.28.86.131)
  EXPORTER_PORT        – listen port    (default: 9100)
  SCRAPE_INTERVAL      – seconds        (default: 30)
  VERIFY_TLS           – "1" to verify  (default: 0, skip for self-signed)
  HTTP_TIMEOUT         – per-request timeout in seconds (default: 15)
"""

from __future__ import annotations

import json
import os
import ssl
import threading
import time
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone
from http.server import HTTPServer, BaseHTTPRequestHandler
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_NODE_URL = "https://50.28.86.131"
DEFAULT_PORT = 9100
DEFAULT_SCRAPE_INTERVAL = 30
DEFAULT_HTTP_TIMEOUT = 15


@dataclass
class ExporterConfig:
    """Runtime configuration populated from environment variables."""

    node_url: str = ""
    port: int = DEFAULT_PORT
    scrape_interval: int = DEFAULT_SCRAPE_INTERVAL
    verify_tls: bool = False
    http_timeout: int = DEFAULT_HTTP_TIMEOUT

    @classmethod
    def from_env(cls) -> "ExporterConfig":
        return cls(
            node_url=os.environ.get("RUSTCHAIN_NODE_URL", DEFAULT_NODE_URL).rstrip("/"),
            port=int(os.environ.get("EXPORTER_PORT", str(DEFAULT_PORT))),
            scrape_interval=int(os.environ.get("SCRAPE_INTERVAL", str(DEFAULT_SCRAPE_INTERVAL))),
            verify_tls=os.environ.get("VERIFY_TLS", "0") == "1",
            http_timeout=int(os.environ.get("HTTP_TIMEOUT", str(DEFAULT_HTTP_TIMEOUT))),
        )


# ---------------------------------------------------------------------------
# HTTP helpers (mirrors node_miner_weekly_scan.py style)
# ---------------------------------------------------------------------------


def _request_json(
    url: str,
    timeout_s: int = DEFAULT_HTTP_TIMEOUT,
    verify_tls: bool = False,
) -> Tuple[Optional[Any], Optional[str]]:
    """Fetch JSON from *url*.  Returns (parsed_data, error_string|None)."""
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "rustchain-prometheus-exporter/1.0")

    context: Optional[ssl.SSLContext] = None
    if url.startswith("https://") and not verify_tls:
        context = ssl._create_unverified_context()

    try:
        with urllib.request.urlopen(req, timeout=timeout_s, context=context) as resp:
            raw = resp.read().decode("utf-8")
        try:
            return json.loads(raw), None
        except json.JSONDecodeError:
            return None, "invalid_json"
    except HTTPError as e:
        return None, f"http_{e.code}"
    except URLError as e:
        return None, f"url_error:{e.reason}"
    except TimeoutError:
        return None, "timeout"
    except Exception as e:  # pragma: no cover – defensive
        return None, f"error:{type(e).__name__}"


def fetch_endpoint(
    base_url: str,
    path: str,
    timeout_s: int = DEFAULT_HTTP_TIMEOUT,
    verify_tls: bool = False,
) -> Tuple[Optional[Any], Optional[str]]:
    """Convenience wrapper matching the project's *fetch_json* pattern."""
    url = f"{base_url.rstrip('/')}{path}"
    return _request_json(url, timeout_s=timeout_s, verify_tls=verify_tls)


# ---------------------------------------------------------------------------
# Metric types
# ---------------------------------------------------------------------------


@dataclass
class MetricSample:
    """One time-series sample."""

    name: str
    value: float
    labels: Dict[str, str] = field(default_factory=dict)
    help_text: str = ""
    metric_type: str = "gauge"


# ---------------------------------------------------------------------------
# Scraper
# ---------------------------------------------------------------------------


@dataclass
class ScrapeResult:
    """Snapshot of all metrics from one scrape cycle."""

    samples: List[MetricSample] = field(default_factory=list)
    timestamp: float = 0.0
    duration: float = 0.0
    error_count: int = 0


def scrape_node(config: ExporterConfig) -> ScrapeResult:
    """Query the RustChain node and return a list of Prometheus samples."""
    start = time.monotonic()
    samples: List[MetricSample] = []
    errors = 0

    # --- /health ---------------------------------------------------------
    health, health_err = fetch_endpoint(
        config.node_url, "/health",
        timeout_s=config.http_timeout, verify_tls=config.verify_tls,
    )
    if health_err is not None or not isinstance(health, dict):
        errors += 1
        samples.append(MetricSample(
            name="rustchain_up", value=0.0,
            help_text="Whether the RustChain node is reachable (1=up, 0=down)",
        ))
    else:
        samples.append(MetricSample(
            name="rustchain_up", value=1.0,
            help_text="Whether the RustChain node is reachable (1=up, 0=down)",
        ))
        samples.append(MetricSample(
            name="rustchain_node_uptime_seconds",
            value=float(health.get("uptime_s", 0)),
            help_text="Node uptime in seconds",
        ))
        samples.append(MetricSample(
            name="rustchain_node_tip_age_slots",
            value=float(health.get("tip_age_slots", 0)),
            help_text="Age of the chain tip in slots",
        ))
        samples.append(MetricSample(
            name="rustchain_node_backup_age_hours",
            value=float(health.get("backup_age_hours", 0)),
            help_text="Age of the latest backup in hours",
        ))
        samples.append(MetricSample(
            name="rustchain_node_db_rw",
            value=1.0 if health.get("db_rw") else 0.0,
            help_text="Database read-write status (1=ok, 0=readonly/error)",
        ))

    # --- /epoch ----------------------------------------------------------
    epoch, epoch_err = fetch_endpoint(
        config.node_url, "/epoch",
        timeout_s=config.http_timeout, verify_tls=config.verify_tls,
    )
    if epoch_err is not None or not isinstance(epoch, dict):
        errors += 1
    else:
        samples.append(MetricSample(
            name="rustchain_epoch_current",
            value=float(epoch.get("epoch", 0)),
            help_text="Current epoch number",
        ))
        samples.append(MetricSample(
            name="rustchain_epoch_slot",
            value=float(epoch.get("slot", 0)),
            help_text="Current slot within the epoch",
        ))
        samples.append(MetricSample(
            name="rustchain_epoch_blocks_per_epoch",
            value=float(epoch.get("blocks_per_epoch", 0)),
            help_text="Number of blocks per epoch",
        ))
        samples.append(MetricSample(
            name="rustchain_epoch_pot_rtc",
            value=float(epoch.get("epoch_pot", 0)),
            help_text="Epoch reward pot in RTC",
        ))
        samples.append(MetricSample(
            name="rustchain_epoch_enrolled_miners",
            value=float(epoch.get("enrolled_miners", 0)),
            help_text="Miners enrolled in the current epoch",
        ))

    # --- /api/miners -----------------------------------------------------
    miners, miners_err = fetch_endpoint(
        config.node_url, "/api/miners",
        timeout_s=config.http_timeout, verify_tls=config.verify_tls,
    )
    if miners_err is not None or not isinstance(miners, list):
        errors += 1
    else:
        samples.append(MetricSample(
            name="rustchain_miners_active_total",
            value=float(len(miners)),
            help_text="Total number of active miners",
        ))
        for miner in miners:
            if not isinstance(miner, dict):
                continue
            miner_id = str(miner.get("miner", "")).strip()
            if not miner_id:
                continue

            labels = {"miner": miner_id}
            device_family = miner.get("device_family")
            if device_family:
                labels["device_family"] = str(device_family)
            device_arch = miner.get("device_arch")
            if device_arch:
                labels["device_arch"] = str(device_arch)
            hardware_type = miner.get("hardware_type")
            if hardware_type:
                labels["hardware_type"] = str(hardware_type)

            last_attest = miner.get("last_attest")
            if last_attest is not None:
                samples.append(MetricSample(
                    name="rustchain_miner_last_attest_timestamp",
                    value=float(last_attest),
                    labels=dict(labels),
                    help_text="Unix timestamp of the miner's last attestation",
                ))

            multiplier = miner.get("antiquity_multiplier")
            if multiplier is not None:
                samples.append(MetricSample(
                    name="rustchain_miner_antiquity_multiplier",
                    value=float(multiplier),
                    labels=dict(labels),
                    help_text="Miner antiquity multiplier for reward weighting",
                ))

    # --- meta metrics ----------------------------------------------------
    duration = time.monotonic() - start
    samples.append(MetricSample(
        name="rustchain_scrape_duration_seconds",
        value=duration,
        help_text="Time taken for the last node scrape in seconds",
    ))
    samples.append(MetricSample(
        name="rustchain_scrape_errors_total",
        value=float(errors),
        help_text="Cumulative count of scrape errors",
        metric_type="counter",
    ))

    return ScrapeResult(
        samples=samples,
        timestamp=time.time(),
        duration=duration,
        error_count=errors,
    )


# ---------------------------------------------------------------------------
# OpenMetrics / Prometheus text format renderer
# ---------------------------------------------------------------------------


def _escape_label_value(v: str) -> str:
    """Escape a Prometheus label value (backslash, double-quote, newline)."""
    return v.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")


def render_metrics(result: ScrapeResult) -> str:
    """Render *ScrapeResult* as Prometheus text exposition format."""
    lines: List[str] = []
    seen_help: set[str] = set()

    for sample in result.samples:
        # Emit HELP and TYPE lines once per metric name.
        if sample.name not in seen_help:
            seen_help.add(sample.name)
            if sample.help_text:
                lines.append(f"# HELP {sample.name} {sample.help_text}")
            lines.append(f"# TYPE {sample.name} {sample.metric_type}")

        if sample.labels:
            label_str = ",".join(
                f'{k}="{_escape_label_value(v)}"'
                for k, v in sorted(sample.labels.items())
            )
            lines.append(f"{sample.name}{{{label_str}}} {sample.value}")
        else:
            lines.append(f"{sample.name} {sample.value}")

    lines.append("")  # trailing newline
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Background scraper thread
# ---------------------------------------------------------------------------


class MetricsCollector:
    """Thread-safe container that runs periodic scrapes in the background."""

    def __init__(self, config: ExporterConfig) -> None:
        self._config = config
        self._lock = threading.Lock()
        self._result: Optional[ScrapeResult] = None
        self._total_errors: int = 0
        self._stop = threading.Event()

    @property
    def latest(self) -> Optional[ScrapeResult]:
        with self._lock:
            return self._result

    def _do_scrape(self) -> None:
        result = scrape_node(self._config)
        # Accumulate total errors across scrapes for the counter metric.
        with self._lock:
            self._total_errors += result.error_count
            # Patch the cumulative counter into the result.
            for s in result.samples:
                if s.name == "rustchain_scrape_errors_total":
                    s.value = float(self._total_errors)
            self._result = result

    def run_forever(self) -> None:  # pragma: no cover – blocks until stop
        """Blocking loop; intended to run in a daemon thread."""
        while not self._stop.is_set():
            self._do_scrape()
            self._stop.wait(timeout=self._config.scrape_interval)

    def stop(self) -> None:
        self._stop.set()

    def scrape_once(self) -> ScrapeResult:
        """Synchronous single scrape (useful for testing)."""
        self._do_scrape()
        assert self._result is not None
        return self._result


# ---------------------------------------------------------------------------
# HTTP server
# ---------------------------------------------------------------------------


def _make_handler(collector: MetricsCollector) -> type:
    """Factory that bakes the *collector* into a request handler class."""

    class _Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802 – stdlib convention
            if self.path == "/metrics":
                result = collector.latest
                if result is None:
                    self.send_response(503)
                    self.send_header("Content-Type", "text/plain; charset=utf-8")
                    self.end_headers()
                    self.wfile.write(b"# metrics not yet available\n")
                    return
                body = render_metrics(result).encode("utf-8")
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; version=0.0.4; charset=utf-8")
                self.end_headers()
                self.wfile.write(body)
            elif self.path == "/healthz":
                self.send_response(200)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"ok\n")
            else:
                self.send_response(404)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(b"not found\n")

        def log_message(self, fmt: str, *args: Any) -> None:  # type: ignore[override]
            # Quieter logs: only print requests to /metrics once per minute.
            pass

    return _Handler


def serve(config: ExporterConfig) -> None:  # pragma: no cover
    """Start the exporter: background scraper + HTTP server."""
    collector = MetricsCollector(config)

    scrape_thread = threading.Thread(target=collector.run_forever, daemon=True)
    scrape_thread.start()

    handler_cls = _make_handler(collector)
    server = HTTPServer(("0.0.0.0", config.port), handler_cls)
    ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    print(
        f"[{ts}] rustchain-prometheus-exporter listening on :{config.port}/metrics "
        f"(node={config.node_url}, interval={config.scrape_interval}s)"
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        collector.stop()
        server.server_close()


# ---------------------------------------------------------------------------
# Entrypoint
# ---------------------------------------------------------------------------


def main() -> int:  # pragma: no cover
    config = ExporterConfig.from_env()
    serve(config)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
