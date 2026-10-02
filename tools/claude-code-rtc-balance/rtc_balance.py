#!/usr/bin/env python3
"""
rtc_balance.py — Query RustChain wallet balance (Python alternative)
Bounty: https://github.com/Scottcjn/rustchain-bounties/issues/2860

Usage:
    python3 rtc_balance.py <wallet-name>

Or as a Claude Code skill:
    /rtc-balance <wallet-name>

Exit codes:
    0 - Success
    1 - Usage error (invalid arguments, missing wallet)
    2 - Network error (node unreachable, connection failed, timeout)
    3 - Bad response (non-200 HTTP status, malformed JSON)
    4 - Wallet not found / empty balance
"""
import sys
import os
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


class RTCBalanceError(Exception):
    """Base exception for RTC balance errors."""
    exit_code = 1

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message


class UsageError(RTCBalanceError):
    """Usage / argument error."""
    exit_code = 1


class NetworkError(RTCBalanceError):
    """Network / connection error."""
    exit_code = 2


class BadResponseError(RTCBalanceError):
    """Bad HTTP response (non-200, malformed JSON)."""
    exit_code = 3


class WalletNotFoundError(RTCBalanceError):
    """Wallet not found or empty balance."""
    exit_code = 4


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


def query(url: str, timeout: int = 10, *, insecure: bool = False) -> dict:
    """
    Query the given URL and return parsed JSON.
    Raises NetworkError on connection/timeout errors.
    Raises BadResponseError on non-200 status or malformed JSON.
    """
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "RTC-Balance-CLI/1.0"})
        with urllib.request.urlopen(req, timeout=timeout, context=_build_ssl_context(insecure)) as resp:
            if resp.status != 200:
                raise BadResponseError(f"HTTP {resp.status}: {resp.reason}")
            body = resp.read().decode()
            try:
                return json.loads(body)
            except json.JSONDecodeError as e:
                raise BadResponseError(f"Malformed JSON response: {e}")
    except BadResponseError:
        raise
    except NetworkError:
        raise
    except urllib.error.HTTPError as e:
        raise BadResponseError(f"HTTP {e.code}: {e.reason}")
    except urllib.error.URLError as e:
        raise NetworkError(f"Network error: {e.reason}")
    except ssl.SSLError as e:
        raise NetworkError(f"TLS error: {e}")
    except TimeoutError:
        raise NetworkError("Request timed out")
    except Exception as e:
        raise NetworkError(f"Unexpected error: {e}")


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
        raise UsageError("Invalid wallet name; expected [A-Za-z0-9_-]{1,64}")
    return wallet


def main():
    parser = argparse.ArgumentParser(
        description="Query RustChain wallet balance.",
        epilog="Exit codes: 0=ok, 1=usage, 2=network, 3=bad response, 4=wallet not found"
    )
    parser.add_argument("wallet", nargs="?", help="Wallet name")
    parser.add_argument("--node-url", default=NODE_URL, help="Override RustChain node URL")
    parser.add_argument("--insecure", action="store_true",
                        help="Disable TLS certificate verification (use only for self-signed test nodes)")
    args = parser.parse_args()

    if not args.wallet:
        args.wallet = input("Enter wallet name: ").strip()
    if not args.wallet:
        parser.print_help()
        raise UsageError("Wallet name required")

    try:
        wallet = _validate_wallet(args.wallet.strip())
    except RTCBalanceError:
        raise
    except Exception as e:
        raise UsageError(f"Invalid wallet name: {e}")

    node_url = args.node_url.rstrip("/")

    # Health check
    try:
        health = query(f"{node_url}/health", insecure=args.insecure)
    except NetworkError as e:
        raise NetworkError(f"Node unreachable at {node_url}: {e}")
    except BadResponseError as e:
        raise BadResponseError(f"Health check failed: {e}")

    if health is None:
        raise BadResponseError("Health check returned empty response")

    # Balance
    from urllib.parse import urlencode
    balance_url = f"{node_url}/wallet/balance?{urlencode({'miner_id': wallet})}"
    try:
        balance_data = query(balance_url, insecure=args.insecure)
    except NetworkError as e:
        raise NetworkError(f"Failed to fetch wallet '{wallet}': {e}")
    except BadResponseError as e:
        raise BadResponseError(f"Balance query failed: {e}")

    if balance_data is None:
        raise BadResponseError("Balance query returned empty response")

    balance = extract_balance(balance_data)
    if balance is None:
        raise WalletNotFoundError(
            f"Wallet '{wallet}' not found or returned empty balance. "
            f"Raw response: {json.dumps(balance_data)[:200]}"
        )

    # Epoch (optional, non-fatal)
    epoch_info = ""
    try:
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
    except (NetworkError, BadResponseError):
        # Non-fatal: epoch info is optional
        pass

    formatted = format_balance(balance)

    print(f"Wallet: {wallet}")
    print(f"Balance: {formatted}")
    if epoch_info:
        print(epoch_info)


if __name__ == "__main__":
    try:
        main()
    except RTCBalanceError as e:
        print(f"Error: {e.message}", file=sys.stderr)
        sys.exit(e.exit_code)
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        sys.exit(130)
    except Exception as e:
        print(f"Error: Unexpected error: {e}", file=sys.stderr)
        sys.exit(1)