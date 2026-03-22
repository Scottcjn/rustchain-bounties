"""CLI tool for RustChain SDK."""

import asyncio
import json
import sys
from typing import Optional
from datetime import datetime

import click

from .client import RustChainClient
from .exceptions import RustChainError


def format_json(data):
    """Format data as JSON string."""
    if hasattr(data, "model_dump"):
        data = data.model_dump()
    return json.dumps(data, indent=2, default=str)


@click.group()
@click.version_option(version="0.1.0", prog_name="rustchain")
def cli():
    """RustChain CLI - Interact with RustChain nodes."""
    pass


@cli.command()
@click.option("--url", default="http://50.28.86.131:9100", help="RustChain node URL")
def health(url: str):
    """Check node health status."""
    async def _health():
        async with RustChainClient(base_url=url) as client:
            result = await client.health()
            click.echo(format_json(result))
    
    asyncio.run(_health())


@cli.command()
@click.option("--url", default="http://50.28.86.131:9100", help="RustChain node URL")
def epoch(url: str):
    """Get current epoch information."""
    async def _epoch():
        async with RustChainClient(base_url=url) as client:
            result = await client.epoch()
            click.echo(format_json(result))
    
    asyncio.run(_epoch())


@cli.command()
@click.option("--url", default="http://50.28.86.131:9100", help="RustChain node URL")
@click.option("--limit", default=10, help="Number of miners to return")
@click.option("--all", "all_miners", is_flag=True, help="Show all miners (including inactive)")
def miners(url: str, limit: int, all_miners: bool):
    """List active miners."""
    async def _miners():
        async with RustChainClient(base_url=url) as client:
            result = await client.miners(limit=limit, active_only=not all_miners)
            click.echo(format_json(result))
    
    asyncio.run(_miners())


@cli.command()
@click.argument("wallet_id")
@click.option("--url", default="http://50.28.86.131:9100", help="RustChain node URL")
def balance(wallet_id: str, url: str):
    """Check wallet balance.
    
    WALLET_ID: Wallet ID or address
    """
    async def _balance():
        async with RustChainClient(base_url=url) as client:
            result = await client.balance(wallet_id)
            click.echo(format_json(result))
    
    asyncio.run(_balance())


@cli.command()
@click.argument("from_address")
@click.argument("to_address")
@click.argument("amount", type=float)
@click.argument("signature")
@click.option("--url", default="http://50.28.86.131:9100", help="RustChain node URL")
@click.option("--fee", type=float, help="Custom transaction fee")
def transfer(from_address: str, to_address: str, amount: float, signature: str, url: str, fee: Optional[float]):
    """Transfer RTC between wallets.
    
    FROM_ADDRESS: Sender wallet address
    TO_ADDRESS: Recipient wallet address
    AMOUNT: Amount to transfer
    SIGNATURE: Transaction signature
    """
    async def _transfer():
        async with RustChainClient(base_url=url) as client:
            result = await client.transfer(
                from_address=from_address,
                to_address=to_address,
                amount=amount,
                signature=signature,
                fee=fee
            )
            click.echo(format_json(result))
    
    asyncio.run(_transfer())


@cli.command()
@click.argument("miner_id")
@click.option("--url", default="http://50.28.86.131:9100", help="RustChain node URL")
def attestation(miner_id: str, url: str):
    """Check miner attestation status.
    
    MINER_ID: Miner ID
    """
    async def _attestation():
        async with RustChainClient(base_url=url) as client:
            result = await client.attestation_status(miner_id)
            click.echo(format_json(result))
    
    asyncio.run(_attestation())


@cli.group()
def explorer():
    """Blockchain explorer commands."""
    pass


@explorer.command("blocks")
@click.option("--url", default="http://50.28.86.131:9100", help="RustChain node URL")
@click.option("--limit", default=10, help="Number of blocks to return")
@click.option("--page", default=1, help="Page number")
@click.option("--epoch", type=int, help="Filter by epoch")
def explorer_blocks(url: str, limit: int, page: int, epoch: Optional[int]):
    """List recent blocks."""
    async def _blocks():
        async with RustChainClient(base_url=url) as client:
            result = await client.explorer.blocks(limit=limit, page=page, epoch=epoch)
            click.echo(format_json(result))
    
    asyncio.run(_blocks())


@explorer.command("block")
@click.argument("height", type=int)
@click.option("--url", default="http://50.28.86.131:9100", help="RustChain node URL")
def explorer_block(height: int, url: str):
    """Get block by height.
    
    HEIGHT: Block height
    """
    async def _block():
        async with RustChainClient(base_url=url) as client:
            result = await client.explorer.block(height)
            click.echo(format_json(result))
    
    asyncio.run(_block())


@explorer.command("transactions")
@click.option("--url", default="http://50.28.86.131:9100", help="RustChain node URL")
@click.option("--limit", default=10, help="Number of transactions to return")
@click.option("--page", default=1, help="Page number")
@click.option("--wallet", help="Filter by wallet address")
def explorer_transactions(url: str, limit: int, page: int, wallet: Optional[str]):
    """List recent transactions."""
    async def _transactions():
        async with RustChainClient(base_url=url) as client:
            result = await client.explorer.transactions(limit=limit, page=page, wallet=wallet)
            click.echo(format_json(result))
    
    asyncio.run(_transactions())


@explorer.command("transaction")
@click.argument("tx_hash")
@click.option("--url", default="http://50.28.86.131:9100", help="RustChain node URL")
def explorer_transaction(tx_hash: str, url: str):
    """Get transaction by hash.
    
    TX_HASH: Transaction hash
    """
    async def _transaction():
        async with RustChainClient(base_url=url) as client:
            result = await client.explorer.transaction(tx_hash)
            click.echo(format_json(result))
    
    asyncio.run(_transaction())


def main():
    """Main entry point for CLI."""
    try:
        cli()
    except RustChainError as e:
        click.echo(f"Error: {e.message}", err=True)
        sys.exit(1)
    except KeyboardInterrupt:
        click.echo("\nInterrupted by user")
        sys.exit(130)


if __name__ == "__main__":
    main()