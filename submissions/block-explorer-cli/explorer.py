#!/usr/bin/env python3
"""
RustChain CLI Block Explorer

Query and explore the RustChain blockchain from the command line.
Supports block, transaction, address, and validator lookups.

Usage:
    python explorer.py block <height|latest>
    python explorer.py tx <hash>
    python explorer.py address <address>
    python explorer.py validators
    python explorer.py status
    python explorer.py search <query>
    python explorer.py blocks [--start N] [--count 10]
    python explorer.py peers
    python explorer.py propose-validators
    python explorer.py supply
"""

import argparse
import hashlib
import json
import os
import sys
import time
import secrets
from datetime import datetime, timezone
from typing import Dict, List, Optional, Any
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

# ── Configuration ─────────────────────────────────────────────────────

DEFAULT_RPC = "https://rpc.rustchain.io"
DEFAULT_API = "https://api.rustchain.io"
DEFAULT_REST = "https://rest.rustchain.io"
PAGE_SIZE = 20

# Colors for terminal output
class Colors:
    HEADER = "\033[95m"
    BLUE = "\033[94m"
    CYAN = "\033[96m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RESET = "\033[0m"

    @classmethod
    def disable(cls):
        cls.HEADER = cls.BLUE = cls.CYAN = cls.GREEN = ""
        cls.YELLOW = cls.RED = cls.BOLD = cls.DIM = cls.RESET = ""


# ── API Client ────────────────────────────────────────────────────────

class RustChainClient:
    """HTTP client for RustChain RPC/REST APIs."""

    def __init__(self, rpc_url: str = DEFAULT_RPC, rest_url: str = DEFAULT_REST, timeout: int = 30):
        self.rpc_url = rpc_url.rstrip("/")
        self.rest_url = rest_url.rstrip("/")
        self.timeout = timeout

    def _get(self, url: str) -> Optional[Dict]:
        """Make a GET request and return parsed JSON."""
        try:
            req = Request(url, headers={"Accept": "application/json", "User-Agent": "RustChainExplorer/1.0"})
            with urlopen(req, timeout=self.timeout) as resp:
                return json.loads(resp.read().decode())
        except HTTPError as e:
            print(f"{Colors.RED}HTTP {e.code}: {e.reason}{Colors.RESET}")
            return None
        except URLError as e:
            print(f"{Colors.RED}Connection error: {e.reason}{Colors.RESET}")
            return None
        except Exception as e:
            print(f"{Colors.RED}Error: {e}{Colors.RESET}")
            return None

    def get_status(self) -> Optional[Dict]:
        """Get node status."""
        return self._get(f"{self.rpc_url}/status")

    def get_block(self, height: Optional[int] = None) -> Optional[Dict]:
        """Get block by height (latest if None)."""
        if height:
            return self._get(f"{self.rpc_url}/block?height={height}")
        return self._get(f"{self.rpc_url}/block")

    def get_block_results(self, height: int) -> Optional[Dict]:
        """Get block results (events, gas, etc.)."""
        return self._get(f"{self.rpc_url}/block_results?height={height}")

    def get_tx(self, tx_hash: str) -> Optional[Dict]:
        """Get transaction by hash."""
        return self._get(f"{self.rpc_url}/tx?hash=0x{tx_hash}")

    def get_tx_search(self, query: str, page: int = 1, per_page: int = PAGE_SIZE) -> Optional[Dict]:
        """Search transactions."""
        return self._get(f"{self.rpc_url}/tx_search?query=\"{query}\"&page={page}&per_page={per_page}")

    def get_validators(self, height: Optional[int] = None, page: int = 1, per_page: int = 100) -> Optional[Dict]:
        """Get validator set."""
        url = f"{self.rpc_url}/validators?page={page}&per_page={per_page}"
        if height:
            url += f"&height={height}"
        return self._get(url)

    def get_abci_info(self) -> Optional[Dict]:
        """Get ABCI info (last block info)."""
        return self._get(f"{self.rpc_url}/abci_info")

    def get_consensus_state(self) -> Optional[Dict]:
        """Get consensus state."""
        return self._get(f"{self.rpc_url}/consensus_state")

    def get_net_info(self) -> Optional[Dict]:
        """Get network info (peers)."""
        return self._get(f"{self.rpc_url}/net_info")

    def get_node_info(self) -> Optional[Dict]:
        """Get node info."""
        return self._get(f"{self.rpc_url}/node_info")

    # REST API endpoints
    def get_account(self, address: str) -> Optional[Dict]:
        """Get account balance and info."""
        return self._get(f"{self.rest_url}/cosmos/auth/v1beta1/accounts/{address}")

    def get_bank_balance(self, address: str, denom: str = "urtc") -> Optional[Dict]:
        """Get bank balance for address."""
        return self._get(f"{self.rest_url}/cosmos/bank/v1beta1/balances/{address}")

    def get_bank_total(self, denom: Optional[str] = None) -> Optional[Dict]:
        """Get total supply."""
        url = f"{self.rest_url}/cosmos/bank/v1beta1/supply"
        if denom:
            url += f"/{denom}"
        return self._get(url)

    def get_staking_validators(self) -> Optional[Dict]:
        """Get staking validators."""
        return self._get(f"{self.rest_url}/cosmos/staking/v1beta1/validators")

    def get_delegations(self, validator: str) -> Optional[Dict]:
        """Get delegations to a validator."""
        return self._get(f"{self.rest_url}/cosmos/staking/v1beta1/validators/{validator}/delegations")

    def get_proposals(self) -> Optional[Dict]:
        """Get governance proposals."""
        return self._get(f"{self.rest_url}/cosmos/gov/v1beta1/proposals")


# ── Display Helpers ───────────────────────────────────────────────────

def format_time(iso_str: str) -> str:
    """Format ISO time string for display."""
    try:
        dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except (ValueError, AttributeError):
        return str(iso_str)


def format_utc(timestamp: str) -> str:
    """Format unix timestamp to readable time."""
    try:
        ts = int(timestamp)
        dt = datetime.fromtimestamp(ts, tz=timezone.utc)
        return dt.strftime("%Y-%m-%d %H:%M:%S UTC")
    except (ValueError, OSError):
        return str(timestamp)


def format_amount(amount: str, denom: str = "urtc") -> str:
    """Format token amount with denomination."""
    try:
        val = int(amount)
        if denom == "urtc":
            return f"{val / 1_000_000:.6f} RTC"
        return f"{val} {denom}"
    except (ValueError, TypeError):
        return f"{amount} {denom}"


def truncate(s: str, max_len: int = 20) -> str:
    """Truncate string with ellipsis."""
    if len(s) <= max_len:
        return s
    return s[:max_len - 3] + "..."


def print_separator():
    print(f"{Colors.DIM}{'─' * 60}{Colors.RESET}")


# ── Command Handlers ──────────────────────────────────────────────────

def cmd_status(client: RustChainClient):
    """Show blockchain status."""
    print(f"\n{Colors.BOLD}🔗 RustChain Status{Colors.RESET}")
    print_separator()

    result = client.get_status()
    if not result:
        return

    node_info = result.get("result", {}).get("node_info", result.get("result", {}).get("NodeInfo", {}))
    sync_info = result.get("result", {}).get("sync_info", {})

    if node_info:
        print(f"  Network:     {Colors.CYAN}{node_info.get('network', 'N/A')}{Colors.RESET}")
        print(f"  Version:     {node_info.get('version', 'N/A')}")
        print(f"  Moniker:     {node_info.get('moniker', 'N/A')}")

    if sync_info:
        latest = sync_info.get("latest_block_height", "N/A")
        catching = sync_info.get("catching_up", False)
        block_time = sync_info.get("latest_block_time", "N/A")

        status_color = Colors.GREEN if not catching else Colors.YELLOW
        print(f"  Height:      {Colors.BOLD}{latest}{Colors.RESET}")
        print(f"  Syncing:     {status_color}{'Yes' if catching else 'No'}{Colors.RESET}")
        if block_time != "N/A":
            print(f"  Block Time:  {format_time(block_time)}")


def cmd_block(client: RustChainClient, height: Optional[str]):
    """Show block details."""
    h = None if height in (None, "latest", "") else int(height)
    result = client.get_block(h)
    if not result:
        return

    block = result.get("result", {}).get("block", result.get("result", {}).get("Block", {}))
    block_id = result.get("result", {}).get("block_id", {})

    if not block:
        print(f"{Colors.RED}Block not found{Colors.RESET}")
        return

    header = block.get("header", {})

    print(f"\n{Colors.BOLD}📦 Block #{header.get('height', 'N/A')}{Colors.RESET}")
    print_separator()
    print(f"  Hash:        {Colors.CYAN}{block_id.get('hash', 'N/A')}{Colors.RESET}")
    print(f"  Time:        {format_time(header.get('time', 'N/A'))}")
    print(f"  Proposer:    {truncate(header.get('proposer_address', 'N/A'), 40)}")
    print(f"  Tx Count:    {Colors.BOLD}{len(block.get('data', {}).get('txs', []))}{Colors.RESET}")
    print(f"  Last Commit: {header.get('last_commit_hash', 'N/A')[:40]}...")
    print(f"  Data Hash:   {header.get('data_hash', 'N/A')[:40]}...")

    # Show transactions
    txs = block.get("data", {}).get("txs", [])
    if txs:
        print(f"\n  {Colors.BOLD}Transactions ({len(txs)}):{Colors.RESET}")
        for i, tx in enumerate(txs):
            tx_hash = hashlib.sha256(tx.encode() if isinstance(tx, str) else tx).hexdigest()
            print(f"    {i+1}. {Colors.YELLOW}{tx_hash[:16]}...{Colors.RESET}")


def cmd_blocks(client: RustChainClient, start: Optional[int], count: int):
    """List recent blocks."""
    # Get latest height first
    status = client.get_status()
    if not status:
        return

    sync_info = status.get("result", {}).get("sync_info", {})
    latest = int(sync_info.get("latest_block_height", "0"))
    if start is None:
        start = latest - count + 1

    print(f"\n{Colors.BOLD}📦 Recent Blocks{Colors.RESET}")
    print_separator()
    print(f"  {'Height':<10} {'Time':<22} {'Txs':<5} {'Proposer'}")
    print(f"  {'─'*10} {'─'*22} {'─'*5} {'─'*20}")

    for h in range(start + count - 1, start - 1, -1):
        if h < 1:
            continue
        result = client.get_block(h)
        if not result:
            continue
        block = result.get("result", {}).get("block", {})
        header = block.get("header", {})
        txs = block.get("data", {}).get("txs", [])
        proposer = truncate(header.get("proposer_address", ""), 20)

        try:
            dt = datetime.fromisoformat(header.get("time", "").replace("Z", "+00:00"))
            time_str = dt.strftime("%Y-%m-%d %H:%M:%S")
        except (ValueError, AttributeError):
            time_str = "N/A"

        print(f"  {Colors.BOLD}{h:<10}{Colors.RESET} {time_str:<22} {Colors.GREEN}{len(txs):<5}{Colors.RESET} {proposer}")


def cmd_tx(client: RustChainClient, tx_hash: str):
    """Show transaction details."""
    result = client.get_tx(tx_hash)
    if not result:
        return

    tx_result = result.get("result", {})

    print(f"\n{Colors.BOLD}💸 Transaction{Colors.RESET}")
    print_separator()
    print(f"  Hash:   {Colors.CYAN}{tx_hash}{Colors.RESET}")
    print(f"  Height: {tx_result.get('height', 'N/A')}")
    print(f"  Gas:    {tx_result.get('gas_used', 'N/A')} / {tx_result.get('gas_wanted', 'N/A')}")

    # Check if successful
    code = tx_result.get("code", 0)
    if code == 0:
        print(f"  Status: {Colors.GREEN}✅ Success{Colors.RESET}")
    else:
        print(f"  Status: {Colors.RED}❌ Failed (code {code}){Colors.RESET}")
        print(f"  Log:    {tx_result.get('log', 'N/A')}")

    # Show events
    events = tx_result.get("events", [])
    if events:
        print(f"\n  {Colors.BOLD}Events:{Colors.RESET}")
        for event in events[:5]:
            evt_type = event.get("type", "unknown")
            attrs = event.get("attributes", [])
            print(f"    {Colors.YELLOW}{evt_type}{Colors.RESET}")
            for attr in attrs[:3]:
                key = attr.get("key", "")
                value = attr.get("value", "")
                print(f"      {key}: {truncate(value, 40)}")


def cmd_address(client: RustChainClient, address: str):
    """Show address details and balance."""
    print(f"\n{Colors.BOLD}👤 Address: {address}{Colors.RESET}")
    print_separator()

    # Get account info
    acct = client.get_account(address)
    if acct:
        account = acct.get("account", {})
        print(f"  Type:       {account.get('@type', 'N/A').split('.')[-1]}")
        print(f"  Sequence:   {account.get('sequence', 'N/A')}")
        print(f"  Account #:  {account.get('account_number', 'N/A')}")

    # Get balance
    balance = client.get_bank_balance(address)
    if balance:
        balances = balance.get("balances", [])
        if balances:
            print(f"\n  {Colors.BOLD}Balances:{Colors.RESET}")
            for b in balances:
                print(f"    {Colors.GREEN}{format_amount(b.get('amount', '0'), b.get('denom', 'urtc'))}{Colors.RESET}")
        else:
            print(f"  Balance: {Colors.DIM}0 RTC{Colors.RESET}")

    # Search for recent transactions
    txs = client.get_tx_search(f"transfer.sender='{address}'")
    if txs:
        total = txs.get("result", {}).get("total_count", "0")
        print(f"\n  {Colors.BOLD}Transactions (as sender): {total}{Colors.RESET}")


def cmd_validators(client: RustChainClient):
    """Show validator set."""
    print(f"\n{Colors.BOLD}🏛️  Validators{Colors.RESET}")
    print_separator()

    # RPC validators
    result = client.get_validators()
    if result:
        validators = result.get("result", {}).get("validators", [])
        total = result.get("result", {}).get("total", "0")
        print(f"  Total: {total}")
        print()
        print(f"  {'#':<4} {'Address':<42} {'Voting Power':<15} {'Proposer Priority'}")
        print(f"  {'─'*4} {'─'*42} {'─'*15} {'─'*18}")

        for i, v in enumerate(validators[:20]):
            addr = v.get("address", "N/A")
            power = v.get("voting_power", "0")
            priority = v.get("proposer_priority", "0")
            print(f"  {i+1:<4} {Colors.CYAN}{addr[:40]}{Colors.RESET}  {Colors.GREEN}{int(power):>14}{Colors.RESET}  {priority}")

    # REST staking validators
    staking = client.get_staking_validators()
    if staking:
        vals = staking.get("validators", [])
        if vals:
            print(f"\n  {Colors.BOLD}Staking Validators:{Colors.RESET}")
            for v in vals[:10]:
                moniker = v.get("description", {}).get("moniker", "N/A")
                status = v.get("status", "N/A")
                tokens = v.get("tokens", "0")
                commission = v.get("commission", {}).get("commission_rates", {}).get("rate", "0")
                status_icon = "🟢" if status == "BOND_STATUS_BONDED" else "🔴"
                print(f"    {status_icon} {Colors.BOLD}{moniker}{Colors.RESET} — {format_amount(tokens)} — Commission: {float(commission)*100:.1f}%")


def cmd_peers(client: RustChainClient):
    """Show network peers."""
    result = client.get_net_info()
    if not result:
        return

    info = result.get("result", {})
    listening = info.get("listening", False)
    peers = info.get("peers", [])
    n_peers = info.get("n_peers", len(peers))

    print(f"\n{Colors.BOLD}🌐 Network Peers{Colors.RESET}")
    print_separator()
    print(f"  Listening: {Colors.GREEN if listening else Colors.RED}{listening}{Colors.RESET}")
    print(f"  Peers:     {n_peers}")

    if peers:
        print(f"\n  {'#':<4} {'Node ID':<20} {'Address':<30} {'Moniker'}")
        print(f"  {'─'*4} {'─'*20} {'─'*30} {'─'*20}")
        for i, p in enumerate(peers[:20]):
            node_info = p.get("node_info", {})
            node_id = node_info.get("id", "N/A")
            addr = p.get("remote_ip", "N/A")
            moniker = node_info.get("moniker", "N/A")
            print(f"  {i+1:<4} {Colors.CYAN}{node_id[:18]}{Colors.RESET}  {addr:<30} {moniker}")


def cmd_supply(client: RustChainClient):
    """Show token supply."""
    result = client.get_bank_total()
    if not result:
        return

    supply = result.get("supply", [])
    print(f"\n{Colors.BOLD}💰 Token Supply{Colors.RESET}")
    print_separator()

    if supply:
        for s in supply:
            denom = s.get("denom", "N/A")
            amount = s.get("amount", "0")
            print(f"  {format_amount(amount, denom)}")
    else:
        # Try single denom
        result2 = client.get_bank_total("urtc")
        if result2:
            amt = result2.get("amount", {}).get("amount", "N/A")
            print(f"  {format_amount(amt)}")
        else:
            print(f"  {Colors.DIM}Supply data unavailable{Colors.RESET}")


def cmd_proposals(client: RustChainClient):
    """Show governance proposals."""
    result = client.get_proposals()
    if not result:
        return

    proposals = result.get("proposals", [])
    print(f"\n{Colors.BOLD}📋 Governance Proposals{Colors.RESET}")
    print_separator()

    if not proposals:
        print(f"  {Colors.DIM}No proposals found{Colors.RESET}")
        return

    for p in proposals[:10]:
        pid = p.get("proposal_id", p.get("id", "N/A"))
        title = p.get("content", {}).get("title", "N/A")
        status = p.get("status", "N/A")
        status_color = Colors.GREEN if "PASSED" in status else (Colors.YELLOW if "VOTING" in status else Colors.DIM)
        print(f"  #{pid}: {Colors.BOLD}{title}{Colors.RESET}")
        print(f"       Status: {status_color}{status}{Colors.RESET}")
        print(f"       Type: {p.get('content', {}).get('@type', 'N/A').split('.')[-1]}")
        print()


def cmd_search(client: RustChainClient, query: str):
    """Search transactions."""
    result = client.get_tx_search(query)
    if not result:
        return

    txs = result.get("result", {}).get("txs", [])
    total = result.get("result", {}).get("total_count", "0")

    print(f"\n{Colors.BOLD}🔍 Search: \"{query}\"{Colors.RESET}")
    print_separator()
    print(f"  Total results: {total}")

    if txs:
        print(f"\n  {'Hash':<18} {'Height':<10} {'Status'}")
        print(f"  {'─'*18} {'─'*10} {'─'*10}")
        for tx in txs[:20]:
            h = tx.get("hash", "N/A")
            height = tx.get("height", "N/A")
            code = tx.get("tx_result", {}).get("code", 0)
            status = f"{Colors.GREEN}✅{Colors.RESET}" if code == 0 else f"{Colors.RED}❌{Colors.RESET}"
            print(f"  {Colors.CYAN}{h[:16]}{Colors.RESET}  {height:<10} {status}")


# ── CLI ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="RustChain CLI Block Explorer",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s status                        # Chain status
  %(prog)s block 1000                    # Block details
  %(prog)s block latest                  # Latest block
  %(prog)s blocks --count 5             # Recent 5 blocks
  %(prog)s tx ABC123...                  # Transaction details
  %(prog)s address rust1abc...           # Address balance
  %(prog)s validators                    # Validator list
  %(prog)s peers                         # Network peers
  %(prog)s proposals                     # Governance proposals
  %(prog)s supply                        # Token supply
  %(prog)s search "transfer.sender='rust1abc...'"
        """,
    )
    parser.add_argument("--rpc", default=DEFAULT_RPC, help="RPC endpoint URL")
    parser.add_argument("--rest", default=DEFAULT_REST, help="REST endpoint URL")
    parser.add_argument("--timeout", type=int, default=30, help="Request timeout")
    parser.add_argument("--no-color", action="store_true", help="Disable colored output")

    sub = parser.add_subparsers(dest="command")

    # status
    sub.add_parser("status", help="Show chain status")

    # block
    blk = sub.add_parser("block", help="Show block details")
    blk.add_argument("height", nargs="?", default="latest", help="Block height or 'latest'")

    # blocks
    blks = sub.add_parser("blocks", help="List recent blocks")
    blks.add_argument("--start", type=int, help="Start height")
    blks.add_argument("--count", type=int, default=10, help="Number of blocks")

    # tx
    txp = sub.add_parser("tx", help="Show transaction details")
    txp.add_argument("hash", help="Transaction hash")

    # address
    addr = sub.add_parser("address", help="Show address info and balance")
    addr.add_argument("address", help="RustChain address")

    # validators
    sub.add_parser("validators", help="Show validator set")

    # peers
    sub.add_parser("peers", help="Show network peers")

    # proposals
    sub.add_parser("proposals", help="Show governance proposals")

    # supply
    sub.add_parser("supply", help="Show token supply")

    # search
    srch = sub.add_parser("search", help="Search transactions")
    srch.add_argument("query", help="Search query (tm event syntax)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    if args.no_color:
        Colors.disable()

    client = RustChainClient(rpc_url=args.rpc, rest_url=args.rest, timeout=args.timeout)

    commands = {
        "status": lambda: cmd_status(client),
        "block": lambda: cmd_block(client, args.height),
        "blocks": lambda: cmd_blocks(client, args.start, args.count),
        "tx": lambda: cmd_tx(client, args.hash),
        "address": lambda: cmd_address(client, args.address),
        "validators": lambda: cmd_validators(client),
        "peers": lambda: cmd_peers(client),
        "proposals": lambda: cmd_proposals(client),
        "supply": lambda: cmd_supply(client),
        "search": lambda: cmd_search(client, args.query),
    }

    handler = commands.get(args.command)
    if handler:
        handler()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
