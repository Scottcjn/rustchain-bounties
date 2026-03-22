"""
rustchain.cli
~~~~~~~~~~~~~

Click-based CLI wrapper for the RustChain Python SDK.

Provides a ``rustchain`` command for quick node interaction from the
terminal, satisfying the bonus requirement for the bounty.

Usage::

    $ rustchain health
    $ rustchain epoch
    $ rustchain miners --limit 5
    $ rustchain balance my-wallet-id
    $ rustchain transfer --from WALLET_A --to WALLET_B --amount 10 --signature SIG
    $ rustchain attestation MINER_ID
    $ rustchain blocks --limit 5
    $ rustchain transactions --limit 5
    $ rustchain stream  # real-time block feed via WebSocket
"""

from __future__ import annotations

import asyncio
import json
import sys
from typing import Any

import click

from rustchain.client import RustChainClient
from rustchain.errors import RustChainError


def _json_serializer(obj: Any) -> str:
    """Best-effort JSON serializer for dataclass-like objects."""
    from dataclasses import asdict, is_dataclass
    from datetime import datetime

    if is_dataclass(obj):
        d = asdict(obj)
        # Convert datetimes to ISO strings
        for k, v in d.items():
            if isinstance(v, datetime):
                d[k] = v.isoformat() + "Z"
            elif isinstance(v, list):
                d[k] = [
                    (asdict(item) if is_dataclass(item) else item)
                    for item in v
                ]
        return json.dumps(d, indent=2, default=str)
    return json.dumps(obj, indent=2, default=str)


def _print_result(result: Any) -> None:
    """Pretty-print a result object."""
    click.echo(_json_serializer(result))


def _get_client(ctx: click.Context) -> RustChainClient:
    """Extract the RustChainClient from the Click context."""
    return ctx.obj["client"]


@click.group()
@click.option(
    "--node",
    "-n",
    default="https://50.28.86.131",
    envvar="RUSTCHAIN_NODE_URL",
    help="RustChain node URL (env: RUSTCHAIN_NODE_URL)",
)
@click.option(
    "--timeout",
    "-t",
    default=30.0,
    type=float,
    help="Request timeout in seconds",
)
@click.option(
    "--api-key",
    default=None,
    envvar="RUSTCHAIN_API_KEY",
    help="API key for authenticated endpoints (env: RUSTCHAIN_API_KEY)",
)
@click.option(
    "--verify-ssl/--no-verify-ssl",
    default=False,
    help="Verify TLS certificates (default: no-verify)",
)
@click.version_option(package_name="rustchain-sdk")
@click.pass_context
def cli(
    ctx: click.Context,
    node: str,
    timeout: float,
    api_key: str | None,
    verify_ssl: bool,
) -> None:
    """RustChain CLI -- interact with RustChain nodes from the terminal."""
    ctx.ensure_object(dict)
    ctx.obj["client"] = RustChainClient(
        node,
        timeout=timeout,
        api_key=api_key,
        verify_ssl=verify_ssl,
    )
    ctx.obj["node"] = node


@cli.resultcallback()
@click.pass_context
def cleanup(ctx: click.Context, *args: Any, **kwargs: Any) -> None:
    """Close client when CLI exits."""
    client = ctx.obj.get("client")
    if client:
        client.close()


# -------------------------------------------------------------------
# Commands
# -------------------------------------------------------------------


@cli.command()
@click.pass_context
def health(ctx: click.Context) -> None:
    """Check node health status."""
    try:
        result = _get_client(ctx).health()
        _print_result(result)
    except RustChainError as e:
        click.secho(f"Error: {e.message}", fg="red", err=True)
        sys.exit(1)


@cli.command()
@click.pass_context
def epoch(ctx: click.Context) -> None:
    """Get current epoch information."""
    try:
        result = _get_client(ctx).epoch()
        _print_result(result)
    except RustChainError as e:
        click.secho(f"Error: {e.message}", fg="red", err=True)
        sys.exit(1)


@cli.command()
@click.option("--limit", "-l", default=50, help="Max miners to show")
@click.option("--offset", "-o", default=0, help="Pagination offset")
@click.pass_context
def miners(ctx: click.Context, limit: int, offset: int) -> None:
    """List active miners."""
    try:
        result = _get_client(ctx).miners(limit=limit, offset=offset)
        _print_result(result)
    except RustChainError as e:
        click.secho(f"Error: {e.message}", fg="red", err=True)
        sys.exit(1)


@cli.command()
@click.argument("wallet_id")
@click.pass_context
def balance(ctx: click.Context, wallet_id: str) -> None:
    """Check RTC balance for WALLET_ID."""
    try:
        result = _get_client(ctx).balance(wallet_id)
        _print_result(result)
    except RustChainError as e:
        click.secho(f"Error: {e.message}", fg="red", err=True)
        sys.exit(1)


@cli.command()
@click.option("--from", "from_wallet", required=True, help="Sender wallet ID")
@click.option("--to", "to_wallet", required=True, help="Recipient wallet ID")
@click.option("--amount", required=True, type=float, help="Amount of RTC")
@click.option("--signature", required=True, help="Transaction signature")
@click.pass_context
def transfer(
    ctx: click.Context,
    from_wallet: str,
    to_wallet: str,
    amount: float,
    signature: str,
) -> None:
    """Execute a signed RTC transfer."""
    try:
        result = _get_client(ctx).transfer(from_wallet, to_wallet, amount, signature)
        _print_result(result)
    except RustChainError as e:
        click.secho(f"Error: {e.message}", fg="red", err=True)
        sys.exit(1)


@cli.command()
@click.argument("miner_id")
@click.pass_context
def attestation(ctx: click.Context, miner_id: str) -> None:
    """Check attestation status for MINER_ID."""
    try:
        result = _get_client(ctx).attestation_status(miner_id)
        _print_result(result)
    except RustChainError as e:
        click.secho(f"Error: {e.message}", fg="red", err=True)
        sys.exit(1)


@cli.command()
@click.option("--limit", "-l", default=10, help="Max blocks to show")
@click.option("--offset", "-o", default=0, help="Pagination offset")
@click.pass_context
def blocks(ctx: click.Context, limit: int, offset: int) -> None:
    """List recent blocks from the explorer."""
    try:
        result = _get_client(ctx).explorer.blocks(limit=limit, offset=offset)
        _print_result(result)
    except RustChainError as e:
        click.secho(f"Error: {e.message}", fg="red", err=True)
        sys.exit(1)


@cli.command()
@click.option("--limit", "-l", default=10, help="Max transactions to show")
@click.option("--offset", "-o", default=0, help="Pagination offset")
@click.pass_context
def transactions(ctx: click.Context, limit: int, offset: int) -> None:
    """List recent transactions from the explorer."""
    try:
        result = _get_client(ctx).explorer.transactions(limit=limit, offset=offset)
        _print_result(result)
    except RustChainError as e:
        click.secho(f"Error: {e.message}", fg="red", err=True)
        sys.exit(1)


@cli.command()
@click.option(
    "--ws-url",
    default=None,
    help="WebSocket URL (default: derived from node URL)",
)
@click.pass_context
def stream(ctx: click.Context, ws_url: str | None) -> None:
    """Stream real-time blocks and transactions via WebSocket.

    Press Ctrl+C to stop.
    """
    from rustchain.websocket import RustChainWebSocket

    node_url: str = ctx.obj["node"]
    if ws_url is None:
        ws_url = node_url.replace("https://", "wss://").replace("http://", "ws://")
        ws_url = ws_url.rstrip("/") + "/ws"

    ws = RustChainWebSocket(ws_url)

    async def on_block(block: Any) -> None:
        click.secho(f"[BLOCK] #{block.height}  hash={block.block_hash}", fg="green")

    async def on_tx(tx: Any) -> None:
        click.secho(
            f"[TX] {tx.tx_hash[:16]}...  {tx.from_wallet} -> {tx.to_wallet}  {tx.amount} RTC",
            fg="cyan",
        )

    ws.on_block(on_block)
    ws.on_transaction(on_tx)

    click.echo(f"Connecting to {ws_url} ...")
    click.echo("Press Ctrl+C to stop.\n")

    try:
        asyncio.run(ws.connect())
    except KeyboardInterrupt:
        click.echo("\nDisconnected.")
    except Exception as e:
        click.secho(f"WebSocket error: {e}", fg="red", err=True)
        sys.exit(1)


def main() -> None:
    """Entry point for ``rustchain`` console script."""
    cli()


if __name__ == "__main__":
    main()
