#!/usr/bin/env python3
"""
RustChain Wallet Balance Checker
Bounty: #2860 — Create a Claude Code Slash Command That Checks RustChain Balance
Wallet: EVM 0x6FCBd5d14FB296933A4f5a515933B153bA24370E
"""

import sys
import json
import urllib.request
import urllib.error

NODE_URL = "https://50.28.86.131"
RTC_USD_RATE = 0.10  # approximate


def get_balance(wallet_name: str) -> dict:
    url = f"{NODE_URL}/wallet/balance?wallet_id={wallet_name}"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return {"error": f"Wallet '{wallet_name}' not found on chain"}
        return {"error": f"HTTP {e.code}: {e.reason}"}
    except urllib.error.URLError as e:
        return {"error": f"[BCOS] Node unreachable — {e.reason}"}
    except Exception as e:
        return {"error": str(e)}


def get_epoch() -> dict:
    url = f"{NODE_URL}/epoch"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            return json.loads(resp.read())
    except Exception:
        return {}


def format_output(wallet_name: str, balance_data: dict, epoch_data: dict) -> str:
    if "error" in balance_data:
        return f"Error: {balance_data['error']}"

    balance = balance_data.get("balance", 0)
    usd = balance * RTC_USD_RATE

    epoch = epoch_data.get("epoch", "N/A")
    miners = epoch_data.get("miners_online", epoch_data.get("active_miners", "N/A"))

    return (
        f"Wallet: {wallet_name}\n"
        f"Balance: {balance} RTC (${usd:.2f} USD)\n"
        f"Epoch: {epoch} | Miners online: {miners}"
    )


def main():
    if len(sys.argv) < 2:
        print("Usage: rtc-balance <wallet-name>")
        sys.exit(1)

    wallet_name = sys.argv[1]
    balance_data = get_balance(wallet_name)
    epoch_data = get_epoch()
    print(format_output(wallet_name, balance_data, epoch_data))


if __name__ == "__main__":
    main()
