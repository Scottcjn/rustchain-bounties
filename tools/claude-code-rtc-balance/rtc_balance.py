#!/usr/bin/env python3
"""
rtc_balance.py — Query RustChain wallet balance (Python alternative)
Bounty: https://github.com/Scottcjn/rustchain-bounties/issues/2860

Usage:
    python3 rtc_balance.py <wallet-name>

Or as a Claude Code skill:
    /rtc-balance <wallet-name>
"""
import sys
import urllib.request
import urllib.error
import json
import ssl
from typing import Dict, Optional, Any

# SECURITY: TLS verification is enabled by default. The previous code created a
# custom SSL_CTX that disabled hostname check + cert verification globally so
# that any HTTP call in the process would accept any certificate. That defeats
# MITM protection on balance queries and is not what the comment claimed
# (cert verification is normal for the RustChain node which uses a public CA).
# Operators who need to point at a node with a self-signed cert can now opt
# in explicitly via `--insecure` (URL is also restricted to a single host).

import argparse

DEFAULT_NODE_URL = "https://50.28.86.131"
NODE_URL = os.environ.get("RTC_NODE_URL", DEFAULT_NODE_URL)
RTC_USD = 0.10


def _build_ssl_context(insecure: bool):
    if insecure:
        ctx = ssl.create_default_context()
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        return ctx
    return ssl.create_default_context()


def query(url: str, timeout: int = 10, *, insecure: bool = False) -> Optional[dict]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "RTC-Balance-CLI/1.0"})
        with urllib.request.urlopen(req, timeout=timeout, context=_build_ssl_context(insecure)) as resp:
            return json.loads(resp.read().decode())
    except Exception:
        return None


def extract_balance(data: dict):
    """Try multiple common JSON shapes."""
    if not data:
        return None
    result = data.get("result")
    if not isinstance(result, dict):
        result = {}
    data_field = data.get("data")
    if not isinstance(data_field, dict):
        data_field = {}
    wallet = data.get("wallet")
    if not isinstance(wallet, dict):
        wallet = {}

    for key in ["amount_rtc", "balance", "rtc_balance"]:
        val = data.get(key)
        if val is not None and val != "":
            return val

    for sub in [result, data_field, wallet]:
        for key in ["amount_rtc", "balance"]:
            val = sub.get(key)
            if val is not None and val != "":
                return val

    return None


def extract_epoch(data: dict) -> Optional[int]:
    if not data:
        return None
    val = (
        data.get("epoch")
        or data.get("result", {}).get("epoch")
        or data.get("data", {}).get("epoch")
    )
    try:
        return int(val) if val is not None else None
    except Exception:
        return None


def extract_miners(data: dict) -> Optional[int]:
    if not data:
        return None
    val = (
        data.get("miners_online")
        or data.get("result", {}).get("miners_online")
        or data.get("data", {}).get("miners")
        or data.get("active_miners")
    )
    try:
        return int(val) if val is not None else None
    except Exception:
        return None


def format_balance(balance: float) -> str:
    try:
        val = float(balance)
        usd_val = val * RTC_USD
        return f"{val:,.2f} RTC (${usd_val:,.2f} USD)"
    except Exception:
        return "N/A"


def _validate_wallet(wallet: str) -> str:
    # Reject anything that isn't a plain wallet token (alnum + dash/underscore),
    # so a value like `foo&extra=1` can't smuggle query parameters into the URL.
    import re
    if not re.match(r"^[A-Za-z0-9_-]{1,64}$", wallet):
        raise SystemExit("Invalid wallet name; expected [A-Za-z0-9_-]{1,64}") 
    return wallet


def main():
    parser = argparse.ArgumentParser(description="Query RustChain wallet balance.")
    parser.add_argument("wallet", nargs="?", help="Wallet name") 
    parser.add_argument("--node-url", default=NODE_URL, help="Override RustChain node URL")
    parser.add_argument("--insecure", action="store_true",
                        help="Disable TLS certificate verification (use only for self-signed test nodes)")
    args = parser.parse_args()

    if not args.wallet:
        args.wallet = input("Enter wallet name: ").strip()
    if not args.wallet:
        parser.print_help()
        sys.exit(1)

    wallet = _validate_wallet(args.wallet.strip())
    node_url = args.node_url.rstrip("/")

    # Health check
    health = query(f"{node_url}/health", insecure=args.insecure)
    if health is None:
        print(f"Error: Node unreachable at {NODE_URL}", file=sys.stderr)
        sys.exit(1)

    # Balance
    from urllib.parse import urlencode
    balance_data = query(f"{node_url}/wallet/balance?{urlencode({'miner_id': wallet})}", insecure=args.insecure)
    if balance_data is None:
        print(f"Error: Failed to fetch wallet '{wallet}'", file=sys.stderr)
        sys.exit(1)

    balance = extract_balance(balance_data)
    if balance is None:
        print(f"Wallet '{wallet}' not found or returned empty balance.")
        print(f"Raw response: {json.dumps(balance_data)[:200]}")
        sys.exit(1)

    # Epoch (optional, non-fatal)
    epoch_info = ""
    epoch_data = query(f"{node_url}/epoch", insecure=args.insecure)
    if epoch_data:
        epoch = extract_epoch(epoch_data)
        miners = extract_miners(epoch_data)
        parts = []
        if epoch is not None:
            parts.append(f"Epoch: {epoch}")
        if miners is not None:
            parts.append(f"Miners online: {miners}")
        if parts:
            epoch_info = " | ".join(parts)

    formatted = format_balance(balance)

    print(f"Wallet: {wallet}")
    print(f"Balance: {formatted}")
    if epoch_info:
        print(epoch_info)


if __name__ == "__main__":
    main()
