# SPDX-License-Identifier: MIT
"""CLI wrapper: rustchain balance my-wallet, rustchain epoch, etc."""

import argparse
import json
import sys

from .client import RustChainClient


def main():
    parser = argparse.ArgumentParser(prog="rustchain", description="RustChain CLI")
    parser.add_argument("--node", default="https://50.28.86.131", help="Node URL")
    sub = parser.add_subparsers(dest="command")

    sub.add_parser("health", help="Node health check")
    sub.add_parser("epoch", help="Current epoch info")
    sub.add_parser("miners", help="List active miners")

    bp = sub.add_parser("balance", help="Check wallet balance")
    bp.add_argument("wallet_id", help="Wallet/miner ID")

    ap = sub.add_parser("attestation", help="Check attestation status")
    ap.add_argument("miner_id", help="Miner ID")

    args = parser.parse_args()
    client = RustChainClient(node_url=args.node)

    try:
        if args.command == "health":
            h = client.health()
            print(f"OK: {h.ok} | Version: {h.version} | Uptime: {h.uptime_s:.0f}s | DB: {'rw' if h.db_rw else 'ro'}")

        elif args.command == "epoch":
            e = client.epoch()
            print(f"Epoch: {e.epoch} | Slot: {e.slot} | Miners: {e.enrolled_miners} | Pot: {e.epoch_pot} RTC")

        elif args.command == "miners":
            miners = client.miners()
            for m in miners[:20]:
                print(f"  {m.miner[:40]:<40} | {m.device_arch:<10} | Antiquity: {m.antiquity_multiplier}")
            if len(miners) > 20:
                print(f"  ... and {len(miners)-20} more")

        elif args.command == "balance":
            b = client.balance(args.wallet_id)
            print(f"Wallet: {b.wallet_id} | Balance: {b.balance} RTC")

        elif args.command == "attestation":
            a = client.attestation_status(args.miner_id)
            print(json.dumps(a, indent=2))

        else:
            parser.print_help()
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
