#!/usr/bin/env python3
"""Wallet balance check script for Rustchain.

Exit codes:
    0 - Success: balance retrieved and printed
    1 - Usage error: invalid arguments or unknown wallet
    2 - Network error: unable to reach the API or connection failed
    3 - Bad response: non-200 status code or malformed JSON returned
"""

import sys
import json
import argparse
import urllib.request
import urllib.error


def parse_args():
    parser = argparse.ArgumentParser(
        description="Check wallet balance on Rustchain.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exit codes:\n"
            "  0  Success\n"
            "  1  Usage error (invalid args / unknown wallet)\n"
            "  2  Network error\n"
            "  3  Bad response (non-200 / malformed JSON)"
        ),
    )
    parser.add_argument("wallet", help="Wallet address to check")
    parser.add_argument(
        "--rpc",
        default="http://localhost:8545",
        help="JSON-RPC endpoint (default: http://localhost:8545)",
    )
    return parser.parse_args()


def get_wallet_balance(wallet: str, rpc_url: str) -> str:
    """Return the balance string for *wallet* from the given RPC endpoint.

    Raises:
        NetworkError   – on connection failure or non-200 response
        ResponseError  – on malformed JSON or an empty response body
        WalletError    – when the wallet address is not recognised
    """

    payload = json.dumps({
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [wallet, "latest"],
        "id": 1,
    }).encode("utf-8")

    req = urllib.request.Request(
        rpc_url,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.status
            if status != 200:
                raise ResponseError(
                    f"HTTP {status} from {rpc_url}"
                )
            body = resp.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise NetworkError(f"Network error: {exc.reason}") from exc

    try:
        result = json.loads(body)
    except (json.JSONDecodeError, ValueError) as exc:
        raise ResponseError(
            f"Malformed JSON response from {rpc_url}: {exc}"
        ) from exc

    if "error" in result:
        err = result["error"]
        msg = err.get("message", json.dumps(err)) if isinstance(err, dict) else str(err)
        raise ResponseError(f"RPC error: {msg}")

    balance_hex = result.get("result")
    if balance_hex is None:
        raise WalletError(f"Unknown wallet or no balance for: {wallet}")

    return balance_hex


class BaseError(Exception):
    """Parent for all script-specific exceptions."""


class NetworkError(BaseError):
    pass


class ResponseError(BaseError):
    pass


class WalletError(BaseError):
    pass


def main() -> int:
    args = parse_args()

    try:
        balance = get_wallet_balance(args.wallet, args.rpc)
    except NetworkError as exc:
        print(f"error: network failure — {exc}", file=sys.stderr)
        return 2
    except ResponseError as exc:
        print(f"error: bad response — {exc}", file=sys.stderr)
        return 3
    except WalletError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1

    print(balance)
    return 0


if __name__ == "__main__":
    sys.exit(main())
