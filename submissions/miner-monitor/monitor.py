#!/usr/bin/env python3
"""
RustChain Miner Monitor
=======================
Periodically queries a RustChain node for health, stats, epoch info, and wallet balance.
Sends notifications on balance changes and logs historical data to CSV.
"""

import csv
import json
import logging
import os
import signal
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests
from requests.exceptions import RequestException

# ---------------------------------------------------------------------------
# Load config
# ---------------------------------------------------------------------------
CONFIG_PATH = Path(__file__).parent / "config.json"

DEFAULT_CONFIG = {
    "node_url": "https://50.28.86.131",
    "wallet": "zp6",
    "poll_interval_seconds": 60,
    "history_csv": "history.csv",
    "log_level": "INFO",
    "verify_ssl": False,
    "notify_command": "",
}


def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            cfg = json.load(f)
    else:
        cfg = {}
    merged = {**DEFAULT_CONFIG, **cfg}
    # write defaults back so user can see all options
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump(merged, f, indent=2)
    return merged


# ---------------------------------------------------------------------------
# Notification
# ---------------------------------------------------------------------------
def notify(message: str, command: str) -> None:
    """Send notification via shell command if configured."""
    if not command:
        return
    try:
        os.system(command.replace("{msg}", message.replace('"', '\\"')))
    except Exception as exc:
        logging.warning("Notification failed: %s", exc)


# ---------------------------------------------------------------------------
# API helpers
# ---------------------------------------------------------------------------
def build_session(verify_ssl: bool) -> requests.Session:
    s = requests.Session()
    s.verify = verify_ssl
    # retry-friendly defaults
    s.headers.update({"User-Agent": "RustChainMinerMonitor/1.0"})
    return s


def fetch_json(session: requests.Session, url: str, timeout: int = 10) -> dict | None:
    try:
        resp = session.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.json()
    except RequestException as exc:
        logging.error("Request failed %s: %s", url, exc)
        return None
    except ValueError:
        logging.error("Invalid JSON from %s", url)
        return None


def fetch_text(session: requests.Session, url: str, timeout: int = 10) -> str | None:
    try:
        resp = session.get(url, timeout=timeout)
        resp.raise_for_status()
        return resp.text
    except RequestException as exc:
        logging.error("Request failed %s: %s", url, exc)
        return None


# ---------------------------------------------------------------------------
# CSV logging
# ---------------------------------------------------------------------------
CSV_FIELDS = [
    "timestamp",
    "health_status",
    "block_height",
    "peers",
    "epoch",
    "epoch_block",
    "balance",
    "pending_balance",
]


def init_csv(path: str) -> None:
    if not os.path.exists(path):
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
            writer.writeheader()


def append_csv(path: str, row: dict) -> None:
    with open(path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writerow(row)


# ---------------------------------------------------------------------------
# Main loop
# ---------------------------------------------------------------------------
def run(cfg: dict) -> None:
    logging.basicConfig(
        level=getattr(logging, cfg["log_level"].upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(message)s",
    )

    session = build_session(cfg["verify_ssl"])
    base = cfg["node_url"].rstrip("/")
    wallet = cfg["wallet"]
    interval = cfg["poll_interval_seconds"]
    csv_path = cfg["history_csv"]

    init_csv(csv_path)

    last_balance: str | None = None

    logging.info("RustChain Miner Monitor started")
    logging.info("Node: %s  Wallet: %s  Interval: %ds", base, wallet, interval)

    def _shutdown(signum, frame):
        logging.info("Shutting down …")
        sys.exit(0)

    signal.signal(signal.SIGINT, _shutdown)
    signal.signal(signal.SIGTERM, _shutdown)

    while True:
        ts = datetime.now(timezone.utc).isoformat()

        # health
        health_raw = fetch_text(session, f"{base}/health")
        health_status = health_raw.strip() if health_raw else "ERROR"

        # stats
        stats = fetch_json(session, f"{base}/api/stats") or {}
        block_height = stats.get("block_height", stats.get("height", ""))
        peers = stats.get("peers", stats.get("peer_count", ""))

        # epoch
        epoch_data = fetch_json(session, f"{base}/epoch") or {}
        epoch = epoch_data.get("epoch", epoch_data.get("current_epoch", ""))
        epoch_block = epoch_data.get("block", epoch_data.get("epoch_block", ""))

        # balance
        bal_data = fetch_json(session, f"{base}/balance/{wallet}") or {}
        balance = str(bal_data.get("balance_rtc", 0))
        pending = str(bal_data.get("pending_rtc", 0))

        # detect balance change
        if last_balance is not None and balance != last_balance:
            msg = f"💰 Balance changed: {last_balance} → {balance}"
            logging.info(msg)
            notify(msg, cfg["notify_command"])

        last_balance = balance

        row = {
            "timestamp": ts,
            "health_status": health_status,
            "block_height": block_height,
            "peers": peers,
            "epoch": epoch,
            "epoch_block": epoch_block,
            "balance": balance,
            "pending_balance": pending,
        }
        append_csv(csv_path, row)

        logging.info(
            "Health=%s  Height=%s  Peers=%s  Epoch=%s  Balance=%s",
            health_status, block_height, peers, epoch, balance,
        )

        time.sleep(interval)


if __name__ == "__main__":
    config = load_config()
    run(config)
