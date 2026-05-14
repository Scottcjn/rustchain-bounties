#!/usr/bin/env python3
"""
RustChain Notification Bot
Monitors balance changes, epoch transitions, and sends alerts via Telegram/Discord.
"""

import json
import time
import logging
import argparse
from pathlib import Path
from datetime import datetime, timezone

import requests

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
log = logging.getLogger("rc-notify")


# ---------------------------------------------------------------------------
# Config loader
# ---------------------------------------------------------------------------

def load_config(path: str) -> dict:
    cfg_path = Path(path)
    if not cfg_path.exists():
        log.error("Config file not found: %s", path)
        raise SystemExit(1)
    with open(cfg_path) as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# RustChain API client
# ---------------------------------------------------------------------------

class RustChainClient:
    """Light-weight wrapper around RustChain REST API."""

    def __init__(self, base_url: str, timeout: int = 15):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()

    def _get(self, endpoint: str, params: dict | None = None) -> dict:
        url = f"{self.base_url}{endpoint}"
        resp = self.session.get(url, params=params, timeout=self.timeout)
        resp.raise_for_status()
        return resp.json()

    def get_balance(self, address: str) -> int:
        """Return balance (smallest unit) for *address*."""
        data = self._get(f"/accounts/{address}")
        return int(data.get("balance", 0))

    def get_epoch(self) -> dict:
        """Return current epoch info."""
        return self._get("/epoch")

    def get_network_info(self) -> dict:
        """Return general network info."""
        return self._get("/network/info")


# ---------------------------------------------------------------------------
# Notification senders
# ---------------------------------------------------------------------------

def send_telegram(token: str, chat_id: str, message: str) -> bool:
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as exc:
        log.error("Telegram send failed: %s", exc)
        return False


def send_discord(webhook_url: str, message: str) -> bool:
    payload = {"content": message}
    try:
        resp = requests.post(webhook_url, json=payload, timeout=10)
        resp.raise_for_status()
        return True
    except Exception as exc:
        log.error("Discord send failed: %s", exc)
        return False


# ---------------------------------------------------------------------------
# Notifier — decides *what* to send and via which channel
# ---------------------------------------------------------------------------

class Notifier:
    def __init__(self, config: dict):
        self.cfg = config
        self.channels = config.get("channels", {})
        self.rules = config.get("rules", {})

    def _send_all(self, message: str):
        tg = self.channels.get("telegram")
        if tg and tg.get("enabled"):
            send_telegram(tg["bot_token"], tg["chat_id"], message)
        dc = self.channels.get("discord")
        if dc and dc.get("enabled"):
            send_discord(dc["webhook_url"], message)

    def notify_balance_change(self, address: str, old: int, new: int):
        rule = self.rules.get("balance_change", {})
        threshold = rule.get("threshold", 0)
        diff = abs(new - old)
        if diff < threshold:
            return
        direction = "⬆️ increased" if new > old else "⬇️ decreased"
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        msg = (
            f"💰 *Balance Change Detected*\n"
            f"Address: `{address[:8]}…{address[-6:]}`\n"
            f"Balance {direction}: `{old}` → `{new}` (Δ `{diff}`)\n"
            f"_{ts}_"
        )
        self._send_all(msg)
        log.info("Balance change notification sent: %s → %s", old, new)

    def notify_epoch_change(self, old_epoch: int, new_epoch: int, epoch_data: dict):
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        msg = (
            f"🔄 *Epoch Transition*\n"
            f"Epoch: `{old_epoch}` → `{new_epoch}`\n"
            f"```json\n{json.dumps(epoch_data, indent=2)[:500]}\n```\n"
            f"_{ts}_"
        )
        self._send_all(msg)
        log.info("Epoch change notification sent: %s → %s", old_epoch, new_epoch)

    def notify_error(self, error_msg: str):
        rule = self.rules.get("errors", {})
        if not rule.get("enabled", True):
            return
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        msg = f"🚨 *RustChain Monitor Error*\n`{error_msg}`\n_{ts}_"
        self._send_all(msg)


# ---------------------------------------------------------------------------
# Monitor loop
# ---------------------------------------------------------------------------

def run_monitor(config_path: str, once: bool = False):
    cfg = load_config(config_path)
    api = RustChainClient(
        cfg["api"]["base_url"],
        timeout=cfg["api"].get("timeout", 15),
    )
    notifier = Notifier(cfg)

    wallets = cfg.get("wallets", [])
    poll_interval = cfg.get("poll_interval_seconds", 30)

    # State
    balances: dict[str, int] = {}
    current_epoch: int | None = None

    # Initial fetch
    for w in wallets:
        try:
            balances[w] = api.get_balance(w)
            log.info("Initial balance for %s: %s", w[:8] + "…", balances[w])
        except Exception as exc:
            log.error("Failed to fetch balance for %s: %s", w, exc)
    try:
        epoch_info = api.get_epoch()
        current_epoch = epoch_info.get("epoch", epoch_info.get("epoch_number", 0))
        log.info("Initial epoch: %s", current_epoch)
    except Exception as exc:
        log.error("Failed to fetch epoch: %s", exc)

    if once:
        return

    log.info("Monitoring started — polling every %ss", poll_interval)
    while True:
        try:
            # Check balances
            for w in wallets:
                try:
                    new_bal = api.get_balance(w)
                    old_bal = balances.get(w)
                    if old_bal is not None and new_bal != old_bal:
                        notifier.notify_balance_change(w, old_bal, new_bal)
                    balances[w] = new_bal
                except Exception as exc:
                    notifier.notify_error(str(exc))
                    log.error("Balance check error for %s: %s", w, exc)

            # Check epoch
            try:
                epoch_info = api.get_epoch()
                new_epoch = epoch_info.get("epoch", epoch_info.get("epoch_number", 0))
                if current_epoch is not None and new_epoch != current_epoch:
                    notifier.notify_epoch_change(current_epoch, new_epoch, epoch_info)
                current_epoch = new_epoch
            except Exception as exc:
                notifier.notify_error(str(exc))
                log.error("Epoch check error: %s", exc)

        except Exception as exc:
            log.critical("Unhandled error in monitor loop: %s", exc)

        time.sleep(poll_interval)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="RustChain Notification Bot")
    parser.add_argument(
        "-c", "--config",
        default="config.json",
        help="Path to config file (default: config.json)",
    )
    parser.add_argument(
        "--once",
        action="store_true",
        help="Run one check cycle and exit (useful for testing)",
    )
    args = parser.parse_args()
    run_monitor(args.config, once=args.once)


if __name__ == "__main__":
    main()
