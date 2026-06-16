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

# Handle self-signed cert on 50.28.86.131
SSL_CTX = ssl.create_default_context()
SSL_CTX.check_hostname = False
SSL_CTX.verify_mode = ssl.CERT_NONE

NODE_URL = "https://50.28.86.131"
RTC_USD = 0.10


def query(url: str, timeout: int = 10) -> Optional[dict]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "RTC-Balance-CLI/1.0"})
        with urllib.request.urlopen(req, timeout=timeout, context=SSL_CTX) as resp:
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


def main():
    if len(sys.argv) < 2:
        wallet = input("Enter wallet name: ").strip()
        if not wallet:
            print("Usage: rtc_balance.py <wallet-name>")
            sys.exit(1)
    else:
        wallet = sys.argv[1].strip()

    # Health check
    health = query(f"{NODE_URL}/health")
    if health is None:
        print(f"Error: Node unreachable at {NODE_URL}", file=sys.stderr)
        sys.exit(1)

    # Balance
    balance_data = query(f"{NODE_URL}/wallet/balance?miner_id={wallet}")
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
    epoch_data = query(f"{NODE_URL}/epoch")
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
