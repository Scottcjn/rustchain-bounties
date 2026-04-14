#!/usr/bin/env python3
"""RTC Reward Script — awards RTC on PR merge."""

import argparse
import urllib.request
import urllib.error
import json
import sys


def api_get(node_url, path):
    url = f"{node_url.rstrip('/')}/{path.lstrip('/')}"
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        print(f"HTTP {e.code} from {url}: {e.read().decode()[:200]}")
        sys.exit(1)
    except Exception as e:
        print(f"Error connecting to {url}: {e}")
        sys.exit(1)


def api_post(node_url, path, data=None):
    url = f"{node_url.rstrip('/')}/{path.lstrip('/')}"
    body = json.dumps(data or {}).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            return json.loads(resp.read())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()[:200]
        print(f"HTTP {e.code} from {url}: {err_body}")
        sys.exit(1)
    except Exception as e:
        print(f"Error connecting to {url}: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Award RTC for merged PR")
    parser.add_argument("--node-url", required=True)
    parser.add_argument("--amount", required=True, type=int)
    parser.add_argument("--wallet-from", required=True)
    parser.add_argument("--admin-key", required=True)
    parser.add_argument("--recipient", required=True)
    parser.add_argument("--memo", default="PR merged — RTC reward")
    args = parser.parse_args()

    # Validate sender wallet balance
    print(f"Checking sender wallet: {args.wallet_from}")
    balance_data = api_get(args.node_url, f"/wallet/balance?miner_id={args.wallet_from}")
    balance = float(balance_data.get("balance", 0) or 0)
    print(f"Sender balance: {balance} RTC")

    if balance < args.amount:
        print(f"Insufficient balance ({balance} < {args.amount}) — skipping transfer.")
        sys.exit(0)  # Non-fatal in CI

    # Execute transfer
    print(f"Transferring {args.amount} RTC to {args.recipient}")
    result = api_post(
        args.node_url,
        "/wallet/transfer",
        {
            "from_wallet": args.wallet_from,
            "to_wallet": args.recipient,
            "amount": args.amount,
            "admin_key": args.admin_key,
            "memo": args.memo,
        },
    )
    print(f"Transfer result: {json.dumps(result, indent=2)}")

    tx_hash = result.get("tx_hash") or result.get("hash") or "pending"
    print(f"✅ Awarded {args.amount} RTC to {args.recipient} | tx: {tx_hash}")


if __name__ == "__main__":
    main()
