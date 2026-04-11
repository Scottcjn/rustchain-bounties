#!/usr/bin/env python3
"""
RustChain balance checker — Claude Code slash command helper.
Usage: python3 check_balance.py <miner_id>
"""
import sys
import json
import ssl
import urllib.request
import urllib.error

NODE = "https://50.28.86.131"

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE


def fetch(path: str) -> dict:
    url = f"{NODE}{path}"
    req = urllib.request.Request(url, headers={"User-Agent": "rtc-balance/1.0"})
    resp = urllib.request.urlopen(req, context=ctx, timeout=8)
    return json.loads(resp.read().decode())


def check_balance(miner_id: str) -> None:
    # Miner balance
    try:
        data = fetch(f"/wallet/balance?miner_id={miner_id}")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Miner '{miner_id}' not found on RustChain.")
            return
        print(f"Node error: HTTP {e.code}")
        return
    except Exception as e:
        print(f"Node offline or unreachable: {e}")
        return

    if not data.get("ok", True) and data.get("error"):
        print(f"Error: {data['error']}")
        return

    balance = float(data.get("amount_rtc", 0))
    usd = balance * 0.10

    # Epoch info (best-effort, non-fatal)
    epoch_str = "?"
    miners_str = "?"
    try:
        epoch_data = fetch("/epoch")
        epoch_str = str(epoch_data.get("epoch", "?"))
        miners_str = str(epoch_data.get("enrolled_miners", "?"))
    except Exception:
        pass

    print(f"Miner:   {miner_id}")
    print(f"Balance: {balance:.2f} RTC (${usd:.2f} USD)")
    print(f"Epoch:   {epoch_str} | Miners online: {miners_str}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 check_balance.py <miner_id>")
        print("Example: python3 check_balance.py my-miner")
        sys.exit(1)

    miner_id = sys.argv[1].strip()
    if not miner_id:
        print("Error: miner_id cannot be empty.")
        sys.exit(1)

    check_balance(miner_id)


if __name__ == "__main__":
    main()
