"""
RustChain CLI
Command-line interface for the RustChain SDK.

Usage::

    rustchain balance <wallet_id>
    rustchain health
    rustchain epoch
    rustchain miners
    rustchain explorer blocks
    rustchain explorer txs <wallet_id>
"""

import argparse
import asyncio
import sys
from typing import List, Optional

from . import __version__
from .client import RustChainClient
from .explorer import ExplorerClient


def _fmt(data) -> str:
    """Simple JSON pretty-print for CLI output."""
    import json

    return json.dumps(data, indent=2, default=str)


async def _balance(wallet_id: str, **kwargs) -> None:
    client = RustChainClient(**kwargs)
    try:
        result = await client.balance_async(wallet_id)
        print(_fmt(result))
    finally:
        await asyncio.sleep(0)  # ensure async cleanup


async def _health(**kwargs) -> None:
    client = RustChainClient(**kwargs)
    try:
        result = await client.health_async()
        print(_fmt(result))
    finally:
        await asyncio.sleep(0)


async def _epoch(**kwargs) -> None:
    client = RustChainClient(**kwargs)
    try:
        result = await client.epoch_async()
        print(_fmt(result))
    finally:
        await asyncio.sleep(0)


async def _miners(limit: Optional[int], **kwargs) -> None:
    client = RustChainClient(**kwargs)
    try:
        result = await client.miners_async(limit=limit)
        print(_fmt(result))
    finally:
        await asyncio.sleep(0)


async def _explorer_blocks(limit: int, **kwargs) -> None:
    explorer = ExplorerClient(**kwargs)
    result = explorer.blocks(limit=limit)
    print(_fmt(result))


async def _explorer_txs(wallet_id: Optional[str], limit: int, **kwargs) -> None:
    explorer = ExplorerClient(**kwargs)
    result = explorer.transactions(wallet_id=wallet_id, limit=limit)
    print(_fmt(result))


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        prog="rustchain",
        description="RustChain Python SDK CLI",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    parser.add_argument(
        "--base-url", default=None, help="RustChain node URL"
    )
    parser.add_argument(
        "--api-key", default=None, help="API key for authenticated endpoints"
    )
    parser.add_argument(
        "--no-verify-ssl",
        action="store_true",
        help="Disable SSL certificate verification",
    )

    sub = parser.add_subparsers(dest="command", required=True)

    # rustchain balance <wallet_id>
    bal = sub.add_parser("balance", help="Check wallet balance")
    bal.add_argument("wallet_id", help="Wallet ID or address")

    # rustchain health
    sub.add_parser("health", help="Check node health")

    # rustchain epoch
    sub.add_parser("epoch", help="Get current epoch info")

    # rustchain miners [--limit N]
    miners = sub.add_parser("miners", help="List active miners")
    miners.add_argument("--limit", type=int, default=None, help="Limit results")

    # rustchain explorer blocks [--limit N]
    exp_blocks = sub.add_parser("blocks", help="Explorer: recent blocks")
    exp_blocks.add_argument("--limit", type=int, default=20)

    # rustchain explorer txs [wallet_id] [--limit N]
    exp_txs = sub.add_parser("txs", help="Explorer: recent transactions")
    exp_txs.add_argument("wallet_id", nargs="?", default=None)
    exp_txs.add_argument("--limit", type=int, default=20)

    args = parser.parse_args(argv)

    kwargs = {}
    if args.base_url:
        kwargs["base_url"] = args.base_url
    if args.api_key:
        kwargs["api_key"] = args.api_key
    if args.no_verify_ssl:
        kwargs["verify_ssl"] = False

    try:
        if args.command == "balance":
            asyncio.run(_balance(args.wallet_id, **kwargs))
        elif args.command == "health":
            asyncio.run(_health(**kwargs))
        elif args.command == "epoch":
            asyncio.run(_epoch(**kwargs))
        elif args.command == "miners":
            asyncio.run(_miners(limit=args.limit, **kwargs))
        elif args.command == "blocks":
            asyncio.run(_explorer_blocks(limit=args.limit, **kwargs))
        elif args.command == "txs":
            asyncio.run(_explorer_txs(wallet_id=args.wallet_id, limit=args.limit, **kwargs))
        return 0
    except KeyboardInterrupt:
        return 130
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
