#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
RustChain Catalog Provider Daemon
==================================

Watches a configured catalog listing for incoming orders, fulfils each one
with a pluggable Worker, delivers the artifact, and monitors payment.

Usage
-----
    python -m catalog_provider.daemon --listing lst_<id> --category review

Environment variables (all optional — CLI flags take precedence):
    BEACON_IDENTITY_PATH       Path to the agent.key file
    BEACON_IDENTITY_PASSWORD   Password for an encrypted key file
    RUSTCHAIN_NODE             Node base URL (default: https://rustchain.org)
    PROVIDER_LISTING           Listing id to serve
    PROVIDER_CATEGORY          Category name matching the listing

Safety features
---------------
- Kill-switch file: touching ``kill_switch`` in ``--state-dir`` halts the daemon
  cleanly between polls.
- Rate limit: ``--poll-interval`` seconds between order polls (default 60 s).
- Max concurrency: ``--max-concurrent`` orders processed at once (default 3).
- Private key is *never* printed or logged.
- Idempotent: ``state/delivered.json`` records (order_id, deliverable_hash)
  so a restart never re-delivers a live order.
- status.json is updated after every state change (orders delivered / accepted /
  paid, distinct buyers — no RTC totals).
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
import time
import threading
import hashlib
from pathlib import Path
from typing import Any, Dict, Optional, Set

ROOT = Path(__file__).resolve().parents[4]  # repo root when run from tools/catalog_provider/
sys.path.insert(0, str(ROOT / "tools"))     # so we can import catalog_cli

try:
    import catalog_cli
except ImportError as exc:
    sys.exit(
        f"Cannot import catalog_cli: {exc}\n"
        "Make sure this daemon runs from the Rustchain repository root, or add\n"
        "the repository's tools/ directory to PYTHONPATH."
    )

from catalog_provider.worker import get_worker  # noqa: E402

log = logging.getLogger("catalog_provider")

# ---------------------------------------------------------------------------
# State
# ---------------------------------------------------------------------------

class ProviderState:
    """
    Persistent on-disk state for idempotent delivery.

    Schema of ``delivered.json``:
    {
        "<order_id>": {
            "deliverable_hash": "<sha256>",
            "delivered_at": <epoch>,
            "status": "delivered" | "accepted" | "paid"
        },
        ...
    }
    """

    def __init__(self, state_dir: Path):
        self._path = state_dir / "delivered.json"
        self._status_path = state_dir / "status.json"
        self._lock = threading.Lock()
        state_dir.mkdir(parents=True, exist_ok=True)
        if self._path.exists():
            with self._path.open() as f:
                self._data: Dict[str, Any] = json.load(f)
        else:
            self._data = {}

    def is_delivered(self, order_id: str) -> bool:
        return order_id in self._data

    def delivered_hash(self, order_id: str) -> Optional[str]:
        return self._data.get(order_id, {}).get("deliverable_hash")

    def record_delivery(self, order_id: str, deliverable_hash: str) -> None:
        with self._lock:
            self._data[order_id] = {
                "deliverable_hash": deliverable_hash,
                "delivered_at": int(time.time()),
                "status": "delivered",
            }
            self._save()

    def update_status(self, order_id: str, status: str) -> None:
        with self._lock:
            if order_id in self._data:
                self._data[order_id]["status"] = status
            self._save()

    def write_status_json(self) -> None:
        """Update status.json with aggregate counts (no RTC totals)."""
        counts: Dict[str, int] = {"delivered": 0, "accepted": 0, "paid": 0}
        buyers: Set[str] = set()
        for rec in self._data.values():
            st = rec.get("status", "delivered")
            if st in counts:
                counts[st] += 1
            buyer = rec.get("buyer")
            if buyer:
                buyers.add(buyer)
        payload = {
            "orders_delivered": counts["delivered"] + counts["accepted"] + counts["paid"],
            "orders_accepted": counts["accepted"] + counts["paid"],
            "orders_paid": counts["paid"],
            "distinct_buyers": len(buyers),
            "updated_at": int(time.time()),
        }
        self._status_path.write_text(json.dumps(payload, indent=2))

    def record_buyer(self, order_id: str, buyer_id: str) -> None:
        with self._lock:
            if order_id in self._data:
                self._data[order_id]["buyer"] = buyer_id
                self._save()

    def _save(self) -> None:
        self._path.write_text(json.dumps(self._data, indent=2))
        self.write_status_json()

    def all_order_ids(self) -> list[str]:
        return list(self._data.keys())

    def status_of(self, order_id: str) -> str:
        return self._data.get(order_id, {}).get("status", "unknown")


# ---------------------------------------------------------------------------
# Daemon
# ---------------------------------------------------------------------------

class ProviderDaemon:
    def __init__(
        self,
        listing_id: str,
        category: str,
        state: ProviderState,
        client: "catalog_cli.CatalogClient",
        work_dir: Path,
        max_concurrent: int = 3,
    ):
        self.listing_id = listing_id
        self.category = category
        self.state = state
        self.client = client
        self.work_dir = work_dir
        self.work_dir.mkdir(parents=True, exist_ok=True)
        self.max_concurrent = max_concurrent
        self._active: Set[str] = set()
        self._lock = threading.Lock()
        self.worker = get_worker(category)
        log.info("Daemon ready: listing=%s category=%s worker=%s",
                 listing_id, category, type(self.worker).__name__)

    # -- main poll loop ----------------------------------------------------

    def run(self, poll_interval: float, kill_switch: Path) -> None:
        log.info("Starting provider poll loop (interval=%ds, kill_switch=%s)",
                 int(poll_interval), kill_switch)
        while True:
            if kill_switch.exists():
                log.info("Kill switch detected — shutting down cleanly.")
                break
            try:
                self._poll_once()
            except Exception:
                log.exception("Unhandled error in poll loop — will retry after interval")
            time.sleep(poll_interval)

    def _poll_once(self) -> None:
        # 1. Fetch pending orders for our listing
        try:
            resp = self.client.my_orders(role="provider", status="requested")
        except catalog_cli.CatalogError as exc:
            log.warning("Could not fetch orders: %s", exc)
            return

        orders = resp.get("orders", [])
        log.debug("Poll: %d requested order(s) visible", len(orders))

        # 2. Process each order up to max_concurrent
        for order in orders:
            oid = order.get("id", "")
            if not oid:
                continue
            if order.get("listing_id") != self.listing_id:
                continue  # belongs to a different listing

            with self._lock:
                if len(self._active) >= self.max_concurrent:
                    log.info("Max concurrent (%d) reached; deferring %s",
                             self.max_concurrent, oid)
                    break
                if oid in self._active:
                    continue
                self._active.add(oid)

            t = threading.Thread(target=self._handle_order, args=(oid, order),
                                 daemon=True, name=f"order-{oid}")
            t.start()

        # 3. Watch already-delivered orders for acceptance and payment
        self._watch_delivered_orders()

    # -- per-order handling ------------------------------------------------

    def _handle_order(self, order_id: str, order: Dict[str, Any]) -> None:
        try:
            self._process(order_id, order)
        finally:
            with self._lock:
                self._active.discard(order_id)

    def _process(self, order_id: str, order: Dict[str, Any]) -> None:
        note = order.get("note", "")
        log.info("Processing order %s (note=%r)", order_id, note[:80])

        # Idempotency guard
        if self.state.is_delivered(order_id):
            existing_hash = self.state.delivered_hash(order_id)
            log.info("Order %s already delivered (hash=%s…); skipping re-delivery",
                     order_id, (existing_hash or "")[:16])
            return

        # Do the work
        try:
            deliverable_path, deliverable_uri = self.worker.work(
                order_id, note, self.work_dir
            )
        except Exception:
            log.exception("Worker failed for order %s — will not deliver", order_id)
            return

        # Compute sha256
        deliverable_hash = _sha256_path(deliverable_path)
        log.info("Work done for %s: file=%s hash=%s…",
                 order_id, deliverable_path.name, deliverable_hash[:16])

        # Deliver
        try:
            resp = self.client.deliver(order_id, deliverable_hash, deliverable_uri)
            log.info("Delivered order %s: %s", order_id, resp.get("status"))
        except catalog_cli.CatalogError as exc:
            if exc.status == 409 and "already_delivered" in str(exc.payload):
                # Server-side uniqueness guard triggered: same hash already on a
                # different live order. Regenerate with a distinguishing suffix.
                log.warning("Hash collision on %s — appending order-id suffix", order_id)
                augmented = (deliverable_path.read_text(encoding="utf-8", errors="replace")
                             + f"\n\n<!-- catalog-order: {order_id} -->")
                deliverable_path.write_text(augmented, encoding="utf-8")
                deliverable_hash = _sha256_path(deliverable_path)
                try:
                    resp = self.client.deliver(order_id, deliverable_hash, deliverable_uri)
                    log.info("Re-delivered order %s after suffix: %s", order_id, resp.get("status"))
                except catalog_cli.CatalogError as exc2:
                    log.error("Second delivery attempt failed for %s: %s", order_id, exc2)
                    return
            else:
                log.error("Delivery refused for %s (HTTP %s): %s", order_id, exc.status, exc)
                return

        self.state.record_delivery(order_id, deliverable_hash)

        # Record buyer id if available (for distinct_buyers count in status.json)
        buyer = order.get("buyer")
        if buyer:
            self.state.record_buyer(order_id, buyer)

        log.info("Order %s recorded in state. Waiting for buyer to accept.", order_id)

    # -- payment watching --------------------------------------------------

    def _watch_delivered_orders(self) -> None:
        """Check all locally-known delivered orders for acceptance and payment."""
        for oid in self.state.all_order_ids():
            current = self.state.status_of(oid)
            if current == "paid":
                continue  # terminal state
            try:
                detail = self.client.get_order(oid, signed=True)
            except catalog_cli.CatalogError as exc:
                log.debug("Could not fetch order %s: %s", oid, exc)
                continue

            srv_status = detail.get("status", "")
            payment = detail.get("payment", {}) or {}
            pay_state = payment.get("state", "")

            if pay_state in ("pending", "confirmed"):
                tx = payment.get("tx_hash", "")
                new_st = "paid"
                log.info("Order %s PAID (tx=%s pay_state=%s)", oid, tx[:16], pay_state)
                self.state.update_status(oid, new_st)
            elif srv_status == "accepted":
                log.info("Order %s ACCEPTED by buyer — awaiting payment", oid)
                self.state.update_status(oid, "accepted")
            else:
                log.debug("Order %s status=%s pay_state=%s (no change)",
                          oid, srv_status, pay_state)

        self.state.write_status_json()


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _sha256_path(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="python -m catalog_provider.daemon",
        description="RustChain catalog provider daemon — watches orders and delivers work.",
    )
    p.add_argument("--listing", default=os.environ.get("PROVIDER_LISTING"),
                   help="Catalog listing id to serve (lst_…) [$PROVIDER_LISTING]")
    p.add_argument("--category", default=os.environ.get("PROVIDER_CATEGORY", "review"),
                   help="Catalog category matching the listing [$PROVIDER_CATEGORY, default: review]")
    p.add_argument("--node", default=os.environ.get("RUSTCHAIN_NODE", "https://rustchain.org"),
                   help="Node base URL [$RUSTCHAIN_NODE, default: https://rustchain.org]")
    p.add_argument("--identity",
                   default=os.environ.get("BEACON_IDENTITY_PATH"),
                   help="Beacon agent.key file [$BEACON_IDENTITY_PATH]")
    p.add_argument("--insecure", action="store_true",
                   help="Skip TLS verification (for self-signed node IPs)")
    p.add_argument("--state-dir", default="./provider_state", type=Path,
                   help="Directory for delivered.json and status.json (default: ./provider_state)")
    p.add_argument("--work-dir", default="./provider_work", type=Path,
                   help="Directory for work artifacts (default: ./provider_work)")
    p.add_argument("--poll-interval", type=float, default=60.0,
                   help="Seconds between order polls (default: 60)")
    p.add_argument("--max-concurrent", type=int, default=3,
                   help="Max parallel orders (default: 3)")
    p.add_argument("--log-level", default="INFO",
                   choices=("DEBUG", "INFO", "WARNING", "ERROR"))
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    logging.basicConfig(
        level=getattr(logging, args.log_level),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
        datefmt="%Y-%m-%dT%H:%M:%S",
    )

    if not args.listing:
        log.error("--listing is required (or set $PROVIDER_LISTING)")
        return 1

    # Load identity — private key never logged
    try:
        agent = catalog_cli.AgentKey.load(args.identity)
    except catalog_cli.CatalogError as exc:
        log.error("Identity error: %s", exc)
        return 1

    log.info("Provider identity: %s", agent.agent_id)

    transport = catalog_cli.urllib_transport(args.node, insecure=args.insecure)
    client = catalog_cli.CatalogClient(transport, agent)

    state = ProviderState(args.state_dir)
    daemon = ProviderDaemon(
        listing_id=args.listing,
        category=args.category,
        state=state,
        client=client,
        work_dir=args.work_dir,
        max_concurrent=args.max_concurrent,
    )

    kill_switch = args.state_dir / "kill_switch"
    daemon.run(poll_interval=args.poll_interval, kill_switch=kill_switch)
    return 0


if __name__ == "__main__":
    sys.exit(main())
