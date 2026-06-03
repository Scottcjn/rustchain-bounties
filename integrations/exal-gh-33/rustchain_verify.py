#!/usr/bin/env python3
"""Verify live RustChain node data and a native RTC wallet balance."""

from __future__ import annotations

import argparse
import json
import sys
import urllib.parse
import urllib.request
from typing import Any


DEFAULT_NODE = "https://rustchain.org"
DEFAULT_WALLET = "RTC14f06ee294f327f5685d3de5e1ed501cffab33e7"


class VerificationError(RuntimeError):
    """Raised when live node data cannot be verified."""


def fetch_json(base_url: str, path: str, timeout: float) -> Any:
    url = urllib.parse.urljoin(base_url.rstrip("/") + "/", path.lstrip("/"))
    request = urllib.request.Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "rustchain-live-balance-verifier/1.0",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        payload = response.read().decode("utf-8")
    return json.loads(payload)


def number_from(mapping: dict[str, Any], *keys: str) -> float:
    for key in keys:
        value = mapping.get(key)
        if isinstance(value, (int, float)):
            return float(value)
        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                pass
    raise VerificationError(f"missing numeric field; tried {', '.join(keys)}")


def miner_ids(miners_payload: Any) -> set[str]:
    if isinstance(miners_payload, dict):
        miners = miners_payload.get("miners", [])
    else:
        miners = miners_payload

    ids: set[str] = set()
    if not isinstance(miners, list):
        raise VerificationError("miners payload is not a list")

    for miner in miners:
        if isinstance(miner, dict):
            miner_id = miner.get("miner") or miner.get("miner_id") or miner.get("id") or miner.get("wallet")
            if isinstance(miner_id, str):
                ids.add(miner_id)
        elif isinstance(miner, str):
            ids.add(miner)
    return ids


def verify(args: argparse.Namespace) -> list[str]:
    health = fetch_json(args.node, "/health", args.timeout)
    if not isinstance(health, dict) or health.get("ok") is not True:
        raise VerificationError("health endpoint did not report ok=true")

    epoch = fetch_json(args.node, "/epoch", args.timeout)
    if not isinstance(epoch, dict):
        raise VerificationError("epoch endpoint did not return an object")
    epoch_number = int(number_from(epoch, "epoch"))
    slot_number = int(number_from(epoch, "slot"))
    epoch_pot = number_from(epoch, "epoch_pot", "pot")

    miners_payload = fetch_json(args.node, "/api/miners", args.timeout)
    active_miners = miner_ids(miners_payload)
    if not active_miners:
        raise VerificationError("no active miners returned")

    wallet_query = urllib.parse.urlencode({"miner_id": args.wallet})
    balance = fetch_json(args.node, f"/wallet/balance?{wallet_query}", args.timeout)
    if not isinstance(balance, dict):
        raise VerificationError("balance endpoint did not return an object")
    if balance.get("miner_id") != args.wallet:
        raise VerificationError("balance response miner_id does not match requested wallet")

    amount_rtc = number_from(balance, "amount_rtc", "balance_rtc", "balance")
    if amount_rtc < 0:
        raise VerificationError("balance amount cannot be negative")

    active = args.wallet in active_miners
    version = health.get("version", "unknown")
    tip_age_slots = health.get("tip_age_slots", "unknown")

    pagination = miners_payload.get("pagination", {}) if isinstance(miners_payload, dict) else {}
    enrolled = pagination.get("total_enrolled", "unknown") if isinstance(pagination, dict) else "unknown"

    return [
        f"RustChain live node ok: version={version} tip_age_slots={tip_age_slots}",
        f"Epoch verified: epoch={epoch_number} slot={slot_number} pot={epoch_pot:g} RTC",
        f"Miners verified: active={len(active_miners)} enrolled={enrolled} wallet_in_active_set={'yes' if active else 'no'}",
        f"Balance verified: wallet={args.wallet} amount_rtc={amount_rtc:g}",
        "T2 verification passed",
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description="Verify live RustChain state and a wallet balance.")
    parser.add_argument("--node", default=DEFAULT_NODE, help=f"RustChain node URL (default: {DEFAULT_NODE})")
    parser.add_argument("--wallet", default=DEFAULT_WALLET, help="Native RTC wallet/miner_id to verify")
    parser.add_argument("--timeout", type=float, default=10.0, help="HTTP timeout in seconds")
    args = parser.parse_args()

    try:
        for line in verify(args):
            print(line)
    except (OSError, json.JSONDecodeError, ValueError, VerificationError) as exc:
        print(f"verification failed: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
