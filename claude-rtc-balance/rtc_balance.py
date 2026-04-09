#!/usr/bin/env python3
"""
RustChain Balance Checker
Fetches wallet balance from RustChain node
"""

import sys
import requests

NODE_URL = "https://50.28.86.131"
RTC_PRICE = 0.10  # USD per RTC


def check_balance(wallet: str) -> dict:
    """Fetch wallet balance from RustChain node."""
    try:
        resp = requests.get(
            f"{NODE_URL}/wallet/balance",
            params={"wallet_id": wallet},
            timeout=10
        )
        resp.raise_for_status()
        return resp.json()
    except requests.exceptions.RequestException as e:
        return {"error": str(e)}


def get_epoch() -> dict:
    """Fetch current epoch info."""
    try:
        resp = requests.get(f"{NODE_URL}/epoch", timeout=10)
        resp.raise_for_status()
        return resp.json()
    except:
        return {}


def get_miners_count() -> int:
    """Get count of active miners."""
    try:
        resp = requests.get(f"{NODE_URL}/api/miners", timeout=10)
        resp.raise_for_status()
        data = resp.json()
        return len(data.get("miners", []))
    except:
        return 0


def format_output(wallet: str, balance_data: dict, epoch_data: dict, miners: int) -> str:
    """Format the output message."""
    if "error" in balance_data:
        return f"❌ Error: {balance_data['error']}"

    balance = balance_data.get("balance", 0)
    last_claim = balance_data.get("lastClaim", "Never")
    epoch = epoch_data.get("epoch", "?")
    usd_value = balance * RTC_PRICE

    return f"""Wallet: {wallet}
Balance: {balance} RTC (${usd_value:.2f} USD)
Last Claim: {last_claim}
Epoch: {epoch} | Miners online: {miners}"""


def main():
    if len(sys.argv) < 2:
        print("Usage: rtc-balance <wallet_name>")
        sys.exit(1)

    wallet = sys.argv[1]
    
    print(f"Checking balance for: {wallet}")
    
    balance_data = check_balance(wallet)
    epoch_data = get_epoch()
    miners = get_miners_count()
    
    output = format_output(wallet, balance_data, epoch_data, miners)
    print(output)


if __name__ == "__main__":
    main()
