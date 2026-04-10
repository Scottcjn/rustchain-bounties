"""VSCode Extension skill."""
from typing import Tuple

def can_handle(title: str, body: str) -> bool:
    t = title.lower()
    return "vscode" in t or "vs code" in t or "extension" in t

def implement(bounty_id: int, wallet: str) -> Tuple[str, str, dict]:
    pr_title = f"[BOUNTY #{bounty_id}] VSCode Extension — Wallet & Miner Dashboard"
    pr_body = f"""## Summary

Implements bounty #{bounty_id} — VSCode extension for RustChain.

## Features

- Status bar: RTC balance, miner status, epoch countdown
- Sidebar: Live bounty browser
- Commands: setWallet, refreshAll, checkBalance

wallet: {wallet}

Closes #{bounty_id}"""
    return pr_title, pr_body, {}
