#!/usr/bin/env python3
"""
RustChain Balance Checker
Check wallet balance and network status via RustChain node API
"""

import sys
import json
import urllib.request
import urllib.error

NODE_URL = "https://50.28.86.131"
RTC_USD_RATE = 0.10  # $0.10 per RTC


def get_balance(wallet_id: str) -> dict:
    """Get wallet balance from RustChain node"""
    try:
        url = f"{NODE_URL}/wallet/balance?wallet_id={urllib.parse.quote(wallet_id)}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"error": f"HTTP {e.code}: {e.reason}"}
    except urllib.error.URLError as e:
        return {"error": f"Connection failed: {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


def get_epoch_info() -> dict:
    """Get current epoch and miner info"""
    try:
        url = f"{NODE_URL}/epoch"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode("utf-8"))
    except Exception as e:
        return {"error": str(e)}


def get_miner_count() -> int:
    """Get number of online miners"""
    try:
        url = f"{NODE_URL}/miners"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
            return len(data.get("miners", []))
    except Exception:
        return 0


def format_output(wallet_id: str, balance_data: dict, epoch_data: dict, miner_count: int) -> str:
    """Format the output message"""
    if "error" in balance_data:
        return f"Wallet: {wallet_id}\nError: {balance_data['error']}"

    balance = balance_data.get("balance", 0)
    usd_value = balance * RTC_USD_RATE

    epoch = epoch_data.get("epoch", "N/A") if isinstance(epoch_data, dict) else "N/A"

    return f"""Wallet: {wallet_id}
Balance: {balance} RTC (${usd_value:.2f} USD)
Epoch: {epoch} | Miners online: {miner_count}"""


def main():
    if len(sys.argv) < 2:
        print("Usage: check_balance.py <wallet_id>")
        sys.exit(1)

    wallet_id = sys.argv[1]

    # Fetch all data in parallel-ish (sequential for simplicity)
    balance_data = get_balance(wallet_id)
    epoch_data = get_epoch_info()
    miner_count = get_miner_count()

    output = format_output(wallet_id, balance_data, epoch_data, miner_count)
    print(output)


if __name__ == "__main__":
    main()