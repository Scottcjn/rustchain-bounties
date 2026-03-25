"""CLI wrapper for RustChain SDK."""
import argparse
import json
import sys
from .client import RustChainClient
from .exceptions import RustChainError

def main():
    parser = argparse.ArgumentParser(prog="rustchain", description="RustChain CLI")
    parser.add_argument("--url", default="https://50.28.86.131", help="Node URL")
    sub = parser.add_subparsers(dest="command")
    
    sub.add_parser("health", help="Node health check")
    sub.add_parser("epoch", help="Current epoch info")
    sub.add_parser("miners", help="List active miners")
    
    bal = sub.add_parser("balance", help="Check wallet balance")
    bal.add_argument("wallet_id", help="Wallet address")
    
    att = sub.add_parser("attestation", help="Check attestation status")
    att.add_argument("miner_id", help="Miner ID")
    
    blk = sub.add_parser("blocks", help="Recent blocks")
    blk.add_argument("--limit", type=int, default=10)
    
    txn = sub.add_parser("transactions", help="Recent transactions")
    txn.add_argument("--limit", type=int, default=10)
    
    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)
    
    try:
        with RustChainClient(base_url=args.url) as client:
            if args.command == "health":
                result = client.health()
            elif args.command == "epoch":
                result = client.epoch()
            elif args.command == "miners":
                result = client.miners()
            elif args.command == "balance":
                result = client.balance(args.wallet_id)
            elif args.command == "attestation":
                result = client.attestation_status(args.miner_id)
            elif args.command == "blocks":
                result = client.explorer.blocks(limit=args.limit)
            elif args.command == "transactions":
                result = client.explorer.transactions(limit=args.limit)
            else:
                parser.print_help()
                sys.exit(1)
            print(json.dumps(result, indent=2))
    except RustChainError as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
