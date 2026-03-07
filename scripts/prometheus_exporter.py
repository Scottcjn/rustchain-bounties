#!/usr/bin/env python3
"""Prometheus metrics exporter for RustChain nodes.

A standalone sidecar that polls the RustChain node JSON APIs and
re-exposes them as Prometheus-compatible metrics on GET /metrics.

Usage:
    python prometheus_exporter.py --node-url https://50.28.86.131 --port 9120

Architecture:
    Uses a custom Prometheus collector (RustChainCollector) that fetches
    fresh data from the node on every scrape — no background threads,
    no stale data.  This is the standard exporter pattern used by
    node_exporter, blackbox_exporter, etc.

Bounty: #765 — Prometheus Metrics Exporter — Observable RustChain
"""

from __future__ import annotations

import argparse
import json
import logging
import math
import ssl
import time
import urllib.parse
import urllib.request
from typing import Any, Dict, List, Optional, Tuple
from urllib.error import HTTPError, URLError

from prometheus_client import CollectorRegistry, start_http_server
from prometheus_client.core import (
    CounterMetricFamily,
    GaugeMetricFamily,
    HistogramMetricFamily,
)

logger = logging.getLogger("rustchain_exporter")

# ---------------------------------------------------------------------------
# HTTP helpers
# ---------------------------------------------------------------------------

DEFAULT_NODE_URL = "https://50.28.86.131"
DEFAULT_PORT = 9120
DEFAULT_POLL_TIMEOUT = 15

# Histogram bucket boundaries for API latency
LATENCY_BUCKETS = (0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0)


def _request_json(
    url: str,
    timeout_s: int = DEFAULT_POLL_TIMEOUT,
    verify_tls: bool = False,
) -> Tuple[Optional[Any], Optional[str], float]:
    """Fetch JSON from *url*.  Returns (data, error_string, elapsed_seconds)."""
    ctx = None
    if url.startswith("https://") and not verify_tls:
        ctx = ssl._create_unverified_context()

    req = urllib.request.Request(url)
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "rustchain-prometheus-exporter/1.0")

    t0 = time.monotonic()
    try:
        with urllib.request.urlopen(req, timeout=timeout_s, context=ctx) as resp:
            raw = resp.read().decode("utf-8")
        elapsed = time.monotonic() - t0
        try:
            return json.loads(raw), None, elapsed
        except json.JSONDecodeError:
            return None, "invalid_json", elapsed
    except HTTPError as exc:
        return None, f"http_{exc.code}", time.monotonic() - t0
    except URLError as exc:
        return None, f"url_error:{exc.reason}", time.monotonic() - t0
    except TimeoutError:
        return None, "timeout", time.monotonic() - t0
    except Exception as exc:  # pragma: no cover — defensive
        return None, f"error:{type(exc).__name__}", time.monotonic() - t0


def fetch_endpoint(
    base_url: str,
    path: str,
    timeout_s: int = DEFAULT_POLL_TIMEOUT,
    verify_tls: bool = False,
) -> Tuple[Optional[Any], Optional[str], float]:
    """Fetch a RustChain API endpoint.  Thin wrapper around _request_json."""
    url = f"{base_url.rstrip('/')}{path}"
    return _request_json(url, timeout_s=timeout_s, verify_tls=verify_tls)


def fetch_wallet_balance(
    base_url: str,
    miner_id: str,
    timeout_s: int = DEFAULT_POLL_TIMEOUT,
    verify_tls: bool = False,
) -> Tuple[Optional[Dict[str, Any]], Optional[str], float]:
    """Fetch balance for a single wallet."""
    encoded = urllib.parse.quote(miner_id, safe="")
    url = f"{base_url.rstrip('/')}/wallet/balance?miner_id={encoded}"
    return _request_json(url, timeout_s=timeout_s, verify_tls=verify_tls)


# ---------------------------------------------------------------------------
# Custom Prometheus Collector
# ---------------------------------------------------------------------------


class RustChainCollector:
    """Custom collector called by prometheus_client on every ``/metrics`` scrape.

    Each call to :meth:`collect` makes fresh HTTP requests to the node,
    guaranteeing that Prometheus never receives stale data.

    All metrics (including the API latency histogram) are yielded from
    ``collect()`` as MetricFamily objects.  Nothing is registered in the
    global default registry, so multiple instances can coexist safely
    (e.g. in tests).
    """

    def __init__(
        self,
        node_url: str = DEFAULT_NODE_URL,
        poll_timeout: int = DEFAULT_POLL_TIMEOUT,
        verify_tls: bool = False,
        tracked_wallets: Optional[List[str]] = None,
    ) -> None:
        self.node_url = node_url.rstrip("/")
        self.poll_timeout = poll_timeout
        self.verify_tls = verify_tls
        self.tracked_wallets: List[str] = tracked_wallets or []

        # Persistent state across scrapes
        self._scrape_errors: Dict[str, int] = {}

        # Manual histogram accumulator: {endpoint: [observation, ...]}
        self._latency_observations: Dict[str, List[float]] = {}

    # ---- helpers -----------------------------------------------------------

    def _record_latency(self, endpoint: str, elapsed: float) -> None:
        self._latency_observations.setdefault(endpoint, []).append(elapsed)

    def _fetch(self, path: str) -> Tuple[Optional[Any], Optional[str]]:
        data, err, elapsed = fetch_endpoint(
            self.node_url,
            path,
            timeout_s=self.poll_timeout,
            verify_tls=self.verify_tls,
        )
        self._record_latency(path, elapsed)
        if err:
            self._scrape_errors[path] = self._scrape_errors.get(path, 0) + 1
            logger.warning("scrape error on %s: %s", path, err)
        return data, err

    def _fetch_balance(self, wallet: str) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
        data, err, elapsed = fetch_wallet_balance(
            self.node_url,
            wallet,
            timeout_s=self.poll_timeout,
            verify_tls=self.verify_tls,
        )
        self._record_latency("/wallet/balance", elapsed)
        if err:
            ep = f"/wallet/balance?miner_id={wallet}"
            self._scrape_errors[ep] = self._scrape_errors.get(ep, 0) + 1
            logger.warning("scrape error on /wallet/balance miner_id=%s: %s", wallet, err)
        return data, err

    def _build_histogram_family(self) -> HistogramMetricFamily:
        """Build a HistogramMetricFamily from accumulated latency observations."""
        hist = HistogramMetricFamily(
            "rustchain_api_request_duration_seconds",
            "Latency of the exporter's own HTTP polls to the RustChain node",
            labels=["endpoint"],
        )
        for endpoint, observations in self._latency_observations.items():
            buckets = []
            for bound in LATENCY_BUCKETS:
                count = sum(1 for obs in observations if obs <= bound)
                buckets.append([str(bound), count])
            total_sum = sum(observations)
            total_count = len(observations)
            hist.add_metric(
                [endpoint], buckets, sum_value=total_sum
            )
        return hist

    # ---- main collect ------------------------------------------------------

    def collect(self):  # noqa: C901 — complexity driven by metric count
        """Yield Prometheus metric families.  Called on every scrape."""

        # -- 1.  Fetch data --------------------------------------------------
        health, health_err = self._fetch("/health")
        epoch, epoch_err = self._fetch("/epoch")
        miners_list, miners_err = self._fetch("/api/miners")

        # -- 2.  Node health metrics -----------------------------------------
        node_up = GaugeMetricFamily(
            "rustchain_node_up",
            "Whether the RustChain node is reachable and healthy (1=up, 0=down)",
        )
        if isinstance(health, dict) and health.get("ok"):
            node_up.add_metric([], 1)
        else:
            node_up.add_metric([], 0)
        yield node_up

        uptime = GaugeMetricFamily(
            "rustchain_node_uptime_seconds",
            "Node uptime in seconds",
        )
        if isinstance(health, dict) and health.get("uptime_s") is not None:
            uptime.add_metric([], float(health["uptime_s"]))
        yield uptime

        version_info = GaugeMetricFamily(
            "rustchain_node_version_info",
            "Node version (always 1, version in label)",
            labels=["version"],
        )
        if isinstance(health, dict) and health.get("version"):
            version_info.add_metric([str(health["version"])], 1)
        yield version_info

        db_rw = GaugeMetricFamily(
            "rustchain_db_rw",
            "Whether the database is read-write (1=rw, 0=ro)",
        )
        if isinstance(health, dict) and health.get("db_rw") is not None:
            db_rw.add_metric([], 1 if health["db_rw"] else 0)
        yield db_rw

        backup_age = GaugeMetricFamily(
            "rustchain_backup_age_hours",
            "Age of the latest database backup in hours",
        )
        if isinstance(health, dict) and health.get("backup_age_hours") is not None:
            backup_age.add_metric([], float(health["backup_age_hours"]))
        yield backup_age

        tip_age = GaugeMetricFamily(
            "rustchain_tip_age_slots",
            "Age of the blockchain tip in slots (0 = fully synced)",
        )
        if isinstance(health, dict) and health.get("tip_age_slots") is not None:
            tip_age.add_metric([], float(health["tip_age_slots"]))
        yield tip_age

        # -- 3.  Epoch metrics -----------------------------------------------
        epoch_current = GaugeMetricFamily(
            "rustchain_epoch_current",
            "Current epoch number",
        )
        if isinstance(epoch, dict) and epoch.get("epoch") is not None:
            epoch_current.add_metric([], float(epoch["epoch"]))
        yield epoch_current

        epoch_slot = GaugeMetricFamily(
            "rustchain_epoch_slot",
            "Current slot number within the epoch",
        )
        if isinstance(epoch, dict) and epoch.get("slot") is not None:
            epoch_slot.add_metric([], float(epoch["slot"]))
        yield epoch_slot

        blocks_per_epoch = GaugeMetricFamily(
            "rustchain_epoch_blocks_per_epoch",
            "Number of blocks per epoch",
        )
        if isinstance(epoch, dict) and epoch.get("blocks_per_epoch") is not None:
            blocks_per_epoch.add_metric([], float(epoch["blocks_per_epoch"]))
        yield blocks_per_epoch

        enrolled = GaugeMetricFamily(
            "rustchain_epoch_enrolled_miners",
            "Number of miners enrolled in the current epoch",
        )
        if isinstance(epoch, dict) and epoch.get("enrolled_miners") is not None:
            enrolled.add_metric([], float(epoch["enrolled_miners"]))
        yield enrolled

        pot = GaugeMetricFamily(
            "rustchain_epoch_pot_rtc",
            "Epoch reward pot in RTC",
        )
        if isinstance(epoch, dict) and epoch.get("epoch_pot") is not None:
            pot.add_metric([], float(epoch["epoch_pot"]))
        yield pot

        # -- 4.  Miner metrics -----------------------------------------------
        miners_active = GaugeMetricFamily(
            "rustchain_miners_active",
            "Number of currently active (attesting) miners",
        )
        miners_data: list = []
        if isinstance(miners_list, list):
            miners_data = miners_list
            miners_active.add_metric([], float(len(miners_data)))
        else:
            miners_active.add_metric([], 0)
        yield miners_active

        miners_total = GaugeMetricFamily(
            "rustchain_miners_total",
            "Total number of miners seen in the API response",
        )
        miners_total.add_metric([], float(len(miners_data)))
        yield miners_total

        # Per-miner metrics
        now_ts = time.time()

        attest_age = GaugeMetricFamily(
            "rustchain_attestation_age_seconds",
            "Seconds since the miner last attested",
            labels=["miner"],
        )
        entropy = GaugeMetricFamily(
            "rustchain_miner_entropy_score",
            "Entropy score of the miner's hardware fingerprint",
            labels=["miner"],
        )
        antiquity = GaugeMetricFamily(
            "rustchain_miner_antiquity_multiplier",
            "Antiquity reward multiplier for the miner",
            labels=["miner"],
        )

        for m in miners_data:
            miner_id = str(m.get("miner", "unknown"))
            last = m.get("last_attest")
            if last is not None:
                try:
                    age = max(0.0, now_ts - float(last))
                    attest_age.add_metric([miner_id], age)
                except (TypeError, ValueError):
                    pass

            es = m.get("entropy_score")
            if es is not None:
                try:
                    entropy.add_metric([miner_id], float(es))
                except (TypeError, ValueError):
                    pass

            aq = m.get("antiquity_multiplier")
            if aq is not None:
                try:
                    antiquity.add_metric([miner_id], float(aq))
                except (TypeError, ValueError):
                    pass

        yield attest_age
        yield entropy
        yield antiquity

        # -- 5.  Wallet / balance metrics ------------------------------------
        wallet_balance = GaugeMetricFamily(
            "rustchain_wallet_balance_rtc",
            "Wallet balance in RTC",
            labels=["wallet"],
        )
        for wallet_name in self.tracked_wallets:
            bal_data, bal_err = self._fetch_balance(wallet_name)
            if isinstance(bal_data, dict) and bal_data.get("amount_rtc") is not None:
                try:
                    wallet_balance.add_metric(
                        [wallet_name], float(bal_data["amount_rtc"])
                    )
                except (TypeError, ValueError):
                    pass
        yield wallet_balance

        # -- 6.  API latency histogram ---------------------------------------
        yield self._build_histogram_family()

        # -- 7.  Scrape error counter ----------------------------------------
        scrape_errors = CounterMetricFamily(
            "rustchain_scrape_errors_total",
            "Total number of failed scrapes per endpoint",
            labels=["endpoint"],
        )
        for ep, count in self._scrape_errors.items():
            scrape_errors.add_metric([ep], float(count))
        yield scrape_errors


# ---------------------------------------------------------------------------
# CLI & entry point
# ---------------------------------------------------------------------------


def parse_args(argv: Optional[list] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Prometheus metrics exporter for RustChain nodes",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument(
        "--node-url",
        default=DEFAULT_NODE_URL,
        help="Base URL of the RustChain node to scrape",
    )
    p.add_argument(
        "--port",
        type=int,
        default=DEFAULT_PORT,
        help="Port to serve /metrics on",
    )
    p.add_argument(
        "--poll-timeout",
        type=int,
        default=DEFAULT_POLL_TIMEOUT,
        help="HTTP request timeout in seconds for each node API call",
    )
    p.add_argument(
        "--tracked-wallets",
        default="",
        help="Comma-separated wallet IDs to track balances for",
    )
    p.add_argument(
        "--verify-tls",
        action="store_true",
        help="Verify TLS certificates (off by default — official node uses self-signed TLS)",
    )
    p.add_argument(
        "--log-level",
        default="INFO",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        help="Logging level",
    )
    return p.parse_args(argv)


def main(argv: Optional[list] = None) -> None:
    args = parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    wallets = [w.strip() for w in args.tracked_wallets.split(",") if w.strip()]

    collector = RustChainCollector(
        node_url=args.node_url,
        poll_timeout=args.poll_timeout,
        verify_tls=args.verify_tls,
        tracked_wallets=wallets,
    )

    # Register in the default REGISTRY used by start_http_server
    from prometheus_client import REGISTRY

    REGISTRY.register(collector)

    logger.info(
        "Starting RustChain Prometheus exporter on :%d (node=%s)",
        args.port,
        args.node_url,
    )
    start_http_server(args.port)

    # Block forever
    try:
        while True:
            time.sleep(3600)
    except KeyboardInterrupt:
        logger.info("Shutting down.")


if __name__ == "__main__":
    main()
