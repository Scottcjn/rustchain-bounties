#!/usr/bin/env python3
"""
RustChain balance checker — Claude Code slash command helper.
Usage: python3 check_balance.py <wallet_id>
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


def check_balance(wallet_id: str) -> None:
    # Wallet balance
    try:
        data = fetch(f"/wallet/balance?wallet_id={wallet_id}")
    except urllib.error.HTTPError as e:
        if e.code == 404:
            print(f"Wallet '{wallet_id}' not found on RustChain.")
            return
        print(f"Node error: HTTP {e.code}")
        return
    except Exception as e:
        print(f"Node offline or unreachable: {e}")
        return

    balance = float(data.get("balance", 0))
    usd = balance * 0.10

    # Epoch info (best-effort, non-fatal)
    epoch_str = "?"
    miners_str = "?"
    try:
        epoch_data = fetch("/epoch")
        epoch_str = str(epoch_data.get("epoch", "?"))
        miners_str = str(epoch_data.get("miners_online", "?"))
    except Exception:
        pass

    print(f"Wallet:  {wallet_id}")
    print(f"Balance: {balance:.2f} RTC (${usd:.2f} USD)")
    print(f"Epoch:   {epoch_str} | Miners online: {miners_str}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python3 check_balance.py <wallet_id>")
        print("Example: python3 check_balance.py my-wallet")
        sys.exit(1)

    wallet_id = sys.argv[1].strip()
    if not wallet_id:
        print("Error: wallet_id cannot be empty.")
        sys.exit(1)

    check_balance(wallet_id)


if __name__ == "__main__":
    main()
