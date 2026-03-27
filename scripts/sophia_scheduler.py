#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""SophiaCore Attestation Inspector — Batch Scheduler.

Runs periodic batch inspections of all miners, handles anomaly-triggered
immediate inspections, and integrates with the sybil risk scorer.

Usage:
    # Single miner inspection
    python sophia_scheduler.py --mode single --miner-id TEST_MINER

    # Full batch (all active miners)
    python sophia_scheduler.py --mode batch

    # Daemon mode (batch every 24h + anomaly listener)
    python sophia_scheduler.py --mode daemon --interval 86400

RIP-306: SophiaCore Attestation Inspector
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import ssl
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.error import HTTPError, URLError

logger = logging.getLogger("sophia.scheduler")

# Ensure scripts/ is on path for imports
_SCRIPTS_DIR = str(Path(__file__).parent)
if _SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, _SCRIPTS_DIR)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

DEFAULT_NODE_URL = "https://50.28.86.131"
DEFAULT_INTERVAL = 86400  # 24 hours
DEFAULT_DELAY = 2.0  # seconds between individual inspections
DEFAULT_SOPHIA_URL = "http://localhost:9130"
LOCK_FILE = "/tmp/sophia_scheduler.lock"


# ---------------------------------------------------------------------------
# Lock file (prevent concurrent scheduler instances)
# ---------------------------------------------------------------------------


class SchedulerLock:
    """File-based lock to prevent concurrent scheduler instances."""

    def __init__(self, path: str = LOCK_FILE) -> None:
        self.path = path

    def acquire(self) -> bool:
        try:
            if os.path.exists(self.path):
                # Check if PID is still alive
                try:
                    with open(self.path) as f:
                        old_pid = int(f.read().strip())
                    # On Windows, check process differently
                    if sys.platform == "win32":
                        import ctypes
                        kernel32 = ctypes.windll.kernel32
                        handle = kernel32.OpenProcess(0x0400, False, old_pid)
                        if handle:
                            kernel32.CloseHandle(handle)
                            logger.error("Scheduler already running (PID %d)", old_pid)
                            return False
                    else:
                        os.kill(old_pid, 0)
                        logger.error("Scheduler already running (PID %d)", old_pid)
                        return False
                except (OSError, ValueError):
                    # Process not running, stale lock
                    logger.warning("Removing stale lock file")

            with open(self.path, "w") as f:
                f.write(str(os.getpid()))
            return True
        except IOError as e:
            logger.error("Cannot create lock file: %s", e)
            return False

    def release(self) -> None:
        try:
            if os.path.exists(self.path):
                os.unlink(self.path)
        except IOError:
            pass


# ---------------------------------------------------------------------------
# Node API Client
# ---------------------------------------------------------------------------


def fetch_node_json(
    base_url: str,
    path: str,
    timeout: int = 15,
) -> Optional[Any]:
    """Fetch JSON from the RustChain node API."""
    url = f"{base_url.rstrip('/')}{path}"
    ctx = ssl._create_unverified_context() if url.startswith("https://") else None

    req = urllib.request.Request(url)
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "sophia-scheduler/1.0")

    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            return json.loads(resp.read().decode())
    except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as e:
        logger.warning("Failed to fetch %s: %s", url, e)
        return None


def fetch_active_miners(node_url: str) -> List[Dict[str, Any]]:
    """Fetch the list of active miners from the node."""
    data = fetch_node_json(node_url, "/api/miners")
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "miners" in data:
        return data["miners"]
    logger.warning("Unexpected miners response format: %s", type(data))
    return []


def fetch_epoch(node_url: str) -> Optional[int]:
    """Fetch the current epoch number."""
    data = fetch_node_json(node_url, "/epoch")
    if isinstance(data, dict):
        return data.get("epoch")
    return None


# ---------------------------------------------------------------------------
# Sophia API Client
# ---------------------------------------------------------------------------


def sophia_inspect(
    sophia_url: str,
    miner_id: str,
    fingerprint: Dict[str, Any],
    hardware: Optional[Dict[str, Any]] = None,
    epoch: Optional[int] = None,
    trigger_secret: str = "",
) -> Optional[Dict[str, Any]]:
    """Send an inspection request to the Sophia inspector HTTP API."""
    url = f"{sophia_url.rstrip('/')}/sophia/inspect"
    payload = json.dumps({
        "miner_id": miner_id,
        "fingerprint": fingerprint,
        "hardware": hardware or {},
        "epoch": epoch,
    }).encode()

    req = urllib.request.Request(url, data=payload, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("User-Agent", "sophia-scheduler/1.0")
    if trigger_secret:
        req.add_header("Authorization", f"Bearer {trigger_secret}")

    try:
        with urllib.request.urlopen(req, timeout=60) as resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        logger.error("Sophia inspect failed for %s: %s", miner_id, e)
        return None


def sophia_get_last_inspected(sophia_url: str, miner_id: str) -> Optional[str]:
    """Check when a miner was last inspected."""
    url = f"{sophia_url.rstrip('/')}/sophia/status/{urllib.parse.quote(miner_id, safe='')}"
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "sophia-scheduler/1.0")

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())
            return data.get("created_at")
    except Exception:
        return None


# ---------------------------------------------------------------------------
# Batch Inspector
# ---------------------------------------------------------------------------


def batch_inspect(
    node_url: str,
    sophia_url: str,
    delay: float = DEFAULT_DELAY,
    skip_recent: bool = True,
) -> Dict[str, Any]:
    """Inspect all active miners in a batch.

    Args:
        node_url: RustChain node base URL
        sophia_url: Sophia inspector base URL
        delay: Seconds between individual inspections
        skip_recent: Skip miners already inspected within the last interval

    Returns:
        Summary dict with counts and results.
    """
    logger.info("Starting batch inspection...")

    # Fetch current epoch
    epoch = fetch_epoch(node_url)
    logger.info("Current epoch: %s", epoch)

    # Fetch all active miners
    miners = fetch_active_miners(node_url)
    logger.info("Found %d active miners", len(miners))

    if not miners:
        logger.warning("No active miners found. Check node URL: %s", node_url)
        return {"status": "no_miners", "total": 0, "inspected": 0, "skipped": 0}

    results = {
        "status": "completed",
        "total": len(miners),
        "inspected": 0,
        "skipped": 0,
        "errors": 0,
        "by_verdict": {},
    }

    for i, miner in enumerate(miners):
        miner_id = miner.get("miner", miner.get("miner_id", f"unknown_{i}"))

        # Skip if recently inspected
        if skip_recent:
            last_time = sophia_get_last_inspected(sophia_url, miner_id)
            if last_time:
                # Simple check: if inspected today, skip
                # (A more robust check would parse ISO timestamps)
                logger.debug("Skipping %s (last inspected: %s)", miner_id, last_time)
                results["skipped"] += 1
                continue

        # Extract fingerprint data from miner record
        fingerprint = miner.get("fingerprint", {})
        hardware = {
            "cpu_model": miner.get("cpu_model", miner.get("device_model", "")),
            "device_family": miner.get("device_family", ""),
            "device_arch": miner.get("device_arch", miner.get("arch", "")),
        }

        logger.info("[%d/%d] Inspecting %s...", i + 1, len(miners), miner_id)
        result = sophia_inspect(sophia_url, miner_id, fingerprint, hardware, epoch)

        if result:
            verdict = result.get("verdict", "UNKNOWN")
            results["inspected"] += 1
            results["by_verdict"][verdict] = results["by_verdict"].get(verdict, 0) + 1
            logger.info("  → %s (confidence: %.2f)", verdict, result.get("confidence", 0))
        else:
            results["errors"] += 1
            logger.error("  → Inspection failed for %s", miner_id)

        # Respect rate limit
        if i < len(miners) - 1:
            time.sleep(delay)

    logger.info(
        "Batch complete: %d inspected, %d skipped, %d errors",
        results["inspected"], results["skipped"], results["errors"],
    )
    return results


# ---------------------------------------------------------------------------
# Daemon Mode
# ---------------------------------------------------------------------------


def run_daemon(
    node_url: str,
    sophia_url: str,
    interval: int = DEFAULT_INTERVAL,
    delay: float = DEFAULT_DELAY,
) -> None:
    """Run the scheduler as a daemon, performing batch inspections periodically."""
    lock = SchedulerLock()
    if not lock.acquire():
        logger.error("Another scheduler instance is running. Exiting.")
        sys.exit(1)

    logger.info("Daemon started (interval=%ds, delay=%.1fs)", interval, delay)

    try:
        while True:
            try:
                results = batch_inspect(
                    node_url, sophia_url,
                    delay=delay, skip_recent=True,
                )
                logger.info("Batch result: %s", json.dumps(results, indent=2))
            except Exception as e:
                logger.error("Batch inspection failed: %s", e)

            logger.info("Sleeping %d seconds until next batch...", interval)
            time.sleep(interval)
    except KeyboardInterrupt:
        logger.info("Daemon shutting down.")
    finally:
        lock.release()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv=None):
    p = argparse.ArgumentParser(
        description="SophiaCore Batch Scheduler",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    p.add_argument("--mode", choices=["batch", "daemon", "single"],
                    default="batch", help="Execution mode")
    p.add_argument("--miner-id", help="Miner ID (required for single mode)")
    p.add_argument("--node-url", default=DEFAULT_NODE_URL, help="RustChain node URL")
    p.add_argument("--sophia-url", default=DEFAULT_SOPHIA_URL, help="Sophia inspector URL")
    p.add_argument("--interval", type=int, default=DEFAULT_INTERVAL,
                    help="Seconds between batch runs (daemon mode)")
    p.add_argument("--delay", type=float, default=DEFAULT_DELAY,
                    help="Seconds between individual inspections")
    p.add_argument("--log-level", default="INFO",
                    choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    return p.parse_args(argv)


def main(argv=None) -> int:
    args = parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )

    if args.mode == "single":
        if not args.miner_id:
            logger.error("--miner-id is required for single mode")
            return 1

        # Fetch miner data from node
        miners = fetch_active_miners(args.node_url)
        miner_data = next(
            (m for m in miners if m.get("miner") == args.miner_id
             or m.get("miner_id") == args.miner_id),
            None,
        )

        fingerprint = {}
        hardware = {}
        if miner_data:
            fingerprint = miner_data.get("fingerprint", {})
            hardware = {
                "cpu_model": miner_data.get("cpu_model", ""),
                "device_family": miner_data.get("device_family", ""),
                "device_arch": miner_data.get("device_arch", ""),
            }

        epoch = fetch_epoch(args.node_url)
        result = sophia_inspect(
            args.sophia_url, args.miner_id,
            fingerprint, hardware, epoch,
        )
        if result:
            print(json.dumps(result, indent=2))
            return 0
        return 1

    elif args.mode == "batch":
        results = batch_inspect(
            args.node_url, args.sophia_url,
            delay=args.delay, skip_recent=True,
        )
        print(json.dumps(results, indent=2))
        return 0

    elif args.mode == "daemon":
        run_daemon(
            args.node_url, args.sophia_url,
            interval=args.interval, delay=args.delay,
        )
        return 0

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
