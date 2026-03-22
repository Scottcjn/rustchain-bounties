"""CLI entry point: rustchain balance my-wallet

Copyright (c) 2026 思捷娅科技 (SJYKJ)
MIT License
"""

import argparse
import asyncio
import sys

from ..client import RustChainClient


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="rustchain",
        description="RustChain CLI — interact with RustChain nodes",
    )
    parser.add_argument(
        "--node", default="https://50.28.86.131", help="Node URL"
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # health
    sub.add_parser("health", help="Check node health")

    # stats
    sub.add_parser("stats", help="System statistics")

    # epoch
    sub.add_parser("epoch", help="Current epoch info")

    # balance
    bal = sub.add_parser("balance", help="Check RTC balance")
    bal.add_argument("wallet", help="Miner public key (hex)")

    # miners
    sub.add_parser("miners", help="List active miners")

    args = parser.parse_args(argv)

    client = RustChainClient(base_url=args.node)

    async def run() -> None:
        try:
            if args.command == "health":
                h = await client.health()
                print(f"OK: {h.ok}")
                print(f"Version: {h.version}")
                print(f"Uptime: {h.uptime_s}s")
            elif args.command == "stats":
                s = await client.stats()
                print(f"Chain: {s.chain_id}")
                print(f"Epoch: {s.epoch}")
                print(f"Miners: {s.total_miners}")
                print(f"Supply: {s.total_supply_rtc} RTC")
            elif args.command == "epoch":
                e = await client.epoch()
                print(f"Epoch: {e.epoch}")
                print(f"Slot: {e.slot}")
                print(f"Enrolled: {e.enrolled_miners}")
                print(f"Pot: {e.epoch_pot} RTC")
            elif args.command == "balance":
                b = await client.balance(args.wallet)
                print(f"{b} RTC")
            elif args.command == "miners":
                m = await client.miners()
                for miner in m:
                    pk = miner.get("miner_pk", miner.get("pk", "?"))[:16]
                    bal = miner.get("balance", "?")
                    print(f"  {pk}...  {bal} RTC")
        finally:
            await client.close()

    asyncio.run(run())
