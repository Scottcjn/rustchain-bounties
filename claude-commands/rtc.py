#!/usr/bin/env python3
"""
rtc.py — RustChain CLI for Claude Code
======================================
Check wallet balance, network status, and bounties from the terminal.

Usage:
    python rtc.py balance <wallet>
    python rtc.py status
    python rtc.py bounties [limit]
    python rtc.py miners [limit]

Requires: Python 3.10+
"""

import os
import sys
import json
import http.client
import argparse
from urllib.parse import urlencode

NODE_URL = "https://50.28.86.131"
RTC_PRICE = 0.10  # USD per RTC


def api_get(path: str) -> dict | None:
    url = NODE_URL.replace("https://", "").replace("http://", "")
    host = url.split("/")[0]
    path_part = "/" + "/".join(url.split("/")[1:]) if "/" in url else ""
    path_full = path_part + "/" + path if path_part else "/" + path

    try:
        conn = http.client.HTTPSConnection(host, timeout=10)
        conn.request("GET", path_full, headers={"Accept": "application/json"})
        resp = conn.getresponse()
        data = resp.read().decode()
        conn.close()
        if resp.status == 200:
            return json.loads(data)
    except Exception as e:
        print(f"API error: {e}", file=sys.stderr)
    return None


def gh_get(path: str) -> dict | None:
    try:
        conn = http.client.HTTPSConnection("api.github.com", timeout=10)
        conn.request("GET", path, headers={
            "Accept": "application/json",
            "User-Agent": "RustChain-CLI/1.0"
        })
        resp = conn.getresponse()
        data = resp.read().decode()
        conn.close()
        if resp.status == 200:
            return json.loads(data)
    except Exception as e:
        print(f"GitHub API error: {e}", file=sys.stderr)
    return None


def cmd_balance(wallet: str) -> int:
    if not wallet:
        print("Usage: rtc.py balance <wallet>")
        return 1

    health = api_get("/health")
    balance_data = api_get(f"/wallet/balance?wallet_id={wallet}")

    print(f"\n⚡ RustChain Wallet Balance")
    print(f"{'━' * 40}")
    print(f"👛 Wallet: {wallet}")

    if balance_data:
        bal = balance_data.get("amount_rtc", balance_data.get("balance", 0))
        usd = bal * RTC_PRICE
        print(f"💰 Balance: {bal:,.4f} RTC")
        print(f"💵 USD (~): ${usd:,.4f}")
    else:
        print(f"❌ Wallet '{wallet}' not found or node unreachable")

    if health:
        miners = api_get("/api/miners")
        miner_count = len(miners.get("miners", [])) if miners else 0
        uptime_h = health.get("uptime_s", 0) / 3600
        EPOCH_LENGTH, SLOT_TIME_S = 2016, 15
        slots_elapsed = health.get("uptime_s", 0) / SLOT_TIME_S
        epoch = int(slots_elapsed / EPOCH_LENGTH)
        slot_in = int(slots_elapsed % EPOCH_LENGTH)
        remaining = EPOCH_LENGTH - slot_in
        rem_s = remaining * SLOT_TIME_S
        h = int(rem_s // 3600)
        m = int((rem_s % 3600) // 60)
        print(f"⛏ Miners online: {miner_count}")
        print(f"📅 Epoch: {epoch} | Next in: {h}h {m}m")
        print(f"🔧 Node: {NODE_URL}")

    print()
    return 0


def cmd_status() -> int:
    health = api_get("/health")

    print(f"\n🔧 RustChain Network Status")
    print(f"{'━' * 40}")

    if not health:
        print(f"❌ Node unreachable: {NODE_URL}")
        return 1

    ok = health.get("ok", False)
    version = health.get("version", "unknown")
    uptime_s = health.get("uptime_s", 0)
    uptime_h = uptime_s / 3600

    miners = api_get("/api/miners")
    miner_count = len(miners.get("miners", [])) if miners else 0

    EPOCH_LENGTH, SLOT_TIME_S = 2016, 15
    slots_elapsed = uptime_s / SLOT_TIME_S
    epoch = int(slots_elapsed / EPOCH_LENGTH)
    slot_in = int(slots_elapsed % EPOCH_LENGTH)
    remaining = EPOCH_LENGTH - slot_in
    rem_s = remaining * SLOT_TIME_S
    h = int(rem_s // 3600)
    m = int((rem_s % 3600) // 60)

    status_icon = "🟢" if ok else "🔴"
    print(f"{status_icon} Status: {'Online' if ok else 'Offline'}")
    print(f"📋 Version: {version}")
    print(f"⏱ Uptime: {uptime_h:,.0f} hours")
    print(f"⛏ Active Miners: {miner_count}")
    print(f"📅 Epoch: {epoch}")
    print(f"⏰ Next epoch in: {h}h {m}m")
    print(f"🌐 Node: {NODE_URL}")
    print()
    return 0


def cmd_bounties(limit: int = 10) -> int:
    print(f"\n💰 Open RustChain Bounties")
    print(f"{'━' * 40}")

    data = gh_get(f"/repos/Scottcjn/rustchain-bounties/issues?state=open&labels=bounty&per_page=50")
    if not data:
        print("❌ Could not fetch bounties (check internet connection)")
        return 1

    for i, issue in enumerate(data[:limit], 1):
        title_raw = issue.get("title", "")
        # Extract reward
        import re
        reward_match = re.search(r'(\d+)\s*RTC', title_raw, re.IGNORECASE)
        reward = f"{reward_match.group(1)} RTC" if reward_match else "?"
        # Clean title
        clean = re.sub(r'^\[BOUNTY.*?\]\s*', '', title_raw, flags=re.IGNORECASE).strip()
        num = issue.get("number", "?")
        print(f"#{num:>4} | {reward:>8} | {clean[:50]}")

    print(f"\nView all: https://github.com/Scottcjn/rustchain-bounties/issues\n")
    return 0


def cmd_miners(limit: int = 10) -> int:
    print(f"\n⛏ Top RustChain Miners")
    print(f"{'━' * 40}")

    data = api_get("/api/miners")
    if not data:
        print("❌ Could not fetch miners (node unreachable)")
        return 1

    miners = data.get("miners", [])
    miners.sort(key=lambda m: m.get("antiquity_multiplier", 0), reverse=True)

    for i, m in enumerate(miners[:limit], 1):
        name = m.get("miner", "?")
        mult = m.get("antiquity_multiplier", 0)
        hw = m.get("hardware_type", "unknown")
        active = "🟢" if m.get("is_active") else "🔴"
        print(f"{i:>2}. {active} {name}")
        print(f"    ⚙ {hw} | ×{mult:.3f} antiquity")

    print(f"\nTotal miners: {len(miners)}\n")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="RustChain CLI — Check wallet balance, network status, and bounties"
    )
    sub = parser.add_subparsers(dest="cmd")

    p_bal = sub.add_parser("balance", help="Check wallet balance")
    p_bal.add_argument("wallet", help="Wallet name")

    sub.add_parser("status", help="Check network status")

    p_bount = sub.add_parser("bounties", help="List open bounties")
    p_bount.add_argument("limit", nargs="?", type=int, default=10, help="Max bounties to show")

    p_miners = sub.add_parser("miners", help="List active miners")
    p_miners.add_argument("limit", nargs="?", type=int, default=10, help="Max miners to show")

    args = parser.parse_args()

    if args.cmd == "balance":
        return cmd_balance(args.wallet)
    elif args.cmd == "status":
        return cmd_status()
    elif args.cmd == "bounties":
        return cmd_bounties(args.limit)
    elif args.cmd == "miners":
        return cmd_miners(args.limit)
    else:
        parser.print_help()
        return 0


if __name__ == "__main__":
    sys.exit(main())
