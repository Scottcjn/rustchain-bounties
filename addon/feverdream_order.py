#!/usr/bin/env python3
"""
feverdream-order: CLI to request a Feverdream video commission.

Workflow:
1. GET /api/feverdream/info to obtain a quote (RTC).
2. Sign a RustChain transfer of the quoted amount to `feverdream_studio`
   using a local wallet (Ed25519, same payload as /wallet/transfer/signed).
3. POST the order to /api/feverdream/order.
4. Poll the order status until ready and output the BoTTube watch URL.

Usage:
    feverdream-order --prompt "My prompt" --seconds 6 --wallet mykey.json [--node https://bottube.io]

"""

import argparse
import json
import sys
import time
import urllib.parse
from pathlib import Path

import requests

# Import the signing helpers from the repo
# The repo is expected to contain rustchain_crypto.py with `load_wallet` and `sign_payload`
try:
    from rustchain_crypto import load_wallet, sign_payload
except ImportError as e:
    sys.stderr.write("Failed to import rustchain_crypto module: {}\n".format(e))
    sys.exit(1)


DEFAULT_NODE = "https://bottube.io"


def get_quote(node: str, prompt: str, seconds: int) -> float:
    """
    Call the info endpoint to obtain a price quote (in RTC).
    Expected response JSON: {"quote": <float>, "currency": "RTC", ...}
    """
    endpoint = f"{node.rstrip('/')}/api/feverdream/info"
    params = {"prompt": prompt, "seconds": seconds}
    try:
        resp = requests.get(endpoint, params=params, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to fetch quote: {e}")

    data = resp.json()
    if "quote" not in data:
        raise RuntimeError(f"Unexpected quote response: {data}")
    return float(data["quote"])


def build_transfer_payload(to_address: str, amount: float) -> dict:
    """
    Build the minimal transfer payload expected by the RustChain wallet API.
    """
    # The RustChain transfer payload typically includes:
    #   from (derived from wallet), to, amount, nonce, and possibly a memo.
    # For our purpose we keep it minimal; the wallet signing function will
    # add any required fields (e.g., nonce) internally.
    return {
        "to": to_address,
        "amount": amount,
    }


def sign_transfer(wallet_path: Path, payload: dict) -> dict:
    """
    Sign the transfer payload using the Ed25519 private key from the wallet.
    Returns a dict containing the original payload plus `signature` and `pubkey`.
    """
    wallet = load_wallet(wallet_path)
    # wallet is expected to be a dict with keys: "private_key" (hex) and "public_key" (hex)
    if "private_key" not in wallet or "public_key" not in wallet:
        raise RuntimeError("Wallet JSON must contain 'private_key' and 'public_key' fields")

    signed = sign_payload(payload, wallet["private_key"])
    # sign_payload returns a dict with 'signature' field (hex). We'll attach pubkey.
    signed["pubkey"] = wallet["public_key"]
    return signed


def post_order(node: str, prompt: str, seconds: int, signed_transfer: dict) -> str:
    """
    Submit the order. Returns the order ID.
    Expected response JSON: {"order_id": "<id>", ...}
    """
    endpoint = f"{node.rstrip('/')}/api/feverdream/order"
    body = {
        "prompt": prompt,
        "seconds": seconds,
        "transfer": signed_transfer,
    }
    try:
        resp = requests.post(endpoint, json=body, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as e:
        raise RuntimeError(f"Failed to post order: {e}")

    data = resp.json()
    if "order_id" not in data:
        raise RuntimeError(f"Unexpected order response: {data}")
    return data["order_id"]


def poll_status(node: str, order_id: str, interval: int = 5, timeout: int = 300) -> dict:
    """
    Poll the order status endpoint until the order is ready or timeout occurs.
    Returns the final status JSON.
    """
    endpoint = f"{node.rstrip('/')}/api/feverdream/status/{urllib.parse.quote(order_id)}"
    deadline = time.time() + timeout
    while time.time() < deadline:
        try:
            resp = requests.get(endpoint, timeout=10)
            resp.raise_for_status()
        except requests.RequestException as e:
            sys.stderr.write(f"Status poll error: {e}\n")
            time.sleep(interval)
            continue

        data = resp.json()
        status = data.get("status", "").lower()
        if status in ("ready", "complete"):
            return data
        # Not ready yet; wait and retry
        time.sleep(interval)

    raise RuntimeError(f"Polling timed out after {timeout} seconds for order {order_id}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Commission a Feverdream video via RustChain.")
    parser.add_argument("--prompt", required=True, help="Prompt describing the video.")
    parser.add_argument("--seconds", type=int, required=True, help="Desired video length in seconds.")
    parser.add_argument("--wallet", type=Path, required=True, help="Path to RustChain wallet JSON file.")
    parser.add_argument("--node", default=DEFAULT_NODE, help="Base URL of the BoTTube node (default: %(default)s).")
    args = parser.parse_args()

    # Step 1: Get quote
    try:
        quote = get_quote(args.node, args.prompt, args.seconds)
        print(f"Quote received: {quote:.6f} RTC")
    except Exception as e:
        sys.stderr.write(f"Error obtaining quote: {e}\n")
        sys.exit(1)

    # Step 2: Build and sign transfer
    transfer_payload = build_transfer_payload("feverdream_studio", quote)
    try:
        signed_transfer = sign_transfer(args.wallet, transfer_payload)
    except Exception as e:
        sys.stderr.write(f"Error signing transfer: {e}\n")
        sys.exit(1)

    # Step 3: Submit order
    try:
        order_id = post_order(args.node, args.prompt, args.seconds, signed_transfer)
        print(f"Order submitted, ID: {order_id}")
    except Exception as e:
        sys.stderr.write(f"Error submitting order: {e}\n")
        sys.exit(1)

    # Step 4: Poll status
    try:
        final_status = poll_status(args.node, order_id)
        watch_url = final_status.get("watch_url")
        if not watch_url:
            raise RuntimeError("Watch URL not present in final status response")
        print(f"Video ready! Watch at: {watch_url}")
    except Exception as e:
        sys.stderr.write(f"Error polling order status: {e}\n")
        sys.exit(1)


if __name__ == "__main__":
    main()