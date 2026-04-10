# I Built an MCP Server That Lets Claude Talk to a Blockchain — And It Paid Me Crypto

*Originally published: April 2026 | Platform: Dev.to | Wallet: 暖暖*

---

What if your AI assistant could check your crypto wallet balance, monitor mining rewards, and browse open bounties — all from a single chat? That's exactly what I built: an MCP (Model Context Protocol) server that connects Claude Code directly to the RustChain blockchain.

Here's the walkthrough.

---

## What is RustChain?

[RustChain](https://github.com/Scottcjn/Rustchain) is a Proof-of-Antiquity (PoA) blockchain with a twist: **old hardware earns more than new hardware.** A PowerPC G4 Mac from 2002 gets a higher antiquity multiplier than a brand-new GPU server. The chain pays out RTC tokens every epoch (~10 minutes) to miners who attest their hardware fingerprint.

What makes it interesting from a developer standpoint is the REST API — the node exposes endpoints for balances, epoch info, miner lists, and more. That makes it a perfect candidate for an MCP integration.

---

## What is MCP?

Model Context Protocol (MCP) is Anthropic's open standard for connecting AI assistants to external tools and data sources. Think of it like a plugin system for Claude: you write a server that exposes "tools" (functions the AI can call), and Claude can invoke them during a conversation.

The key insight: **the LLM decides when to call your tools**, based on natural language context. You describe what a tool does, and Claude figures out when to use it.

---

## Building the Server

I used [FastMCP](https://github.com/jlowin/fastmcp) — a Python framework that turns decorated functions into MCP tools automatically.

### Setup

```bash
pip install fastmcp httpx
```

```python
# rustchain_mcp/server.py
from fastmcp import FastMCP
import httpx

NODE_URL = "https://50.28.86.131"
mcp = FastMCP("RustChain MCP")
```

### Tool 1: Check Node Health

```python
@mcp.tool()
async def rustchain_health() -> dict:
    """Check if the RustChain node is online and healthy."""
    async with httpx.AsyncClient(verify=False, timeout=10) as client:
        r = await client.get(f"{NODE_URL}/health")
        r.raise_for_status()
        data = r.json()
        return {
            "ok": data.get("ok"),
            "version": data.get("version"),
            "uptime_hours": round(data.get("uptime_s", 0) / 3600, 1),
        }
```

Simple: decorate a function with `@mcp.tool()`, give it a docstring Claude can understand, and return structured data.

### Tool 2: Wallet Balance (with USD conversion)

```python
@mcp.tool()
async def rustchain_balance(wallet_id: str) -> dict:
    """
    Get the RTC token balance for a wallet.
    
    Args:
        wallet_id: The miner/wallet identifier (e.g. 'my-miner-name')
    """
    async with httpx.AsyncClient(verify=False, timeout=10) as client:
        r = await client.get(
            f"{NODE_URL}/wallet/balance",
            params={"miner_id": wallet_id},
        )
        r.raise_for_status()
        data = r.json()
        amount_rtc = data.get("amount_rtc", 0)
        RTC_PRICE_USD = 0.10  # $0.10 per RTC
        return {
            "wallet": wallet_id,
            "balance_rtc": amount_rtc,
            "balance_usd": round(amount_rtc * RTC_PRICE_USD, 2),
        }
```

### Tool 3: Epoch Status

Each RustChain epoch lasts ~100 slots at 10 minutes each. At the end of every epoch, the pot is distributed proportionally to active miners.

```python
@mcp.tool()
async def rustchain_epoch() -> dict:
    """Get the current epoch number, slot progress, and reward pot size."""
    async with httpx.AsyncClient(verify=False, timeout=10) as client:
        r = await client.get(f"{NODE_URL}/epoch")
        r.raise_for_status()
        data = r.json()
        slots_left = data["blocks_per_epoch"] - data["slot"]
        mins_left = slots_left * 10  # 10 minutes per slot
        return {
            "epoch": data["epoch"],
            "slot": f"{data['slot']}/{data['blocks_per_epoch']}",
            "minutes_until_settlement": mins_left,
            "pot_rtc": data["epoch_pot"],
            "pot_usd": round(data["epoch_pot"] * 0.10, 2),
            "enrolled_miners": data["enrolled_miners"],
        }
```

### Tool 4: Active Miners List

```python
@mcp.tool()
async def rustchain_miners() -> dict:
    """List the currently active miners and their antiquity multipliers."""
    async with httpx.AsyncClient(verify=False, timeout=10) as client:
        r = await client.get(f"{NODE_URL}/api/miners")
        r.raise_for_status()
        data = r.json()
        miners = data.get("miners", [])
        return {
            "count": len(miners),
            "miners": [
                {
                    "id": m.get("miner_id"),
                    "multiplier": m.get("antiquity_multiplier", 1.0),
                    "arch": m.get("device_arch"),
                }
                for m in miners[:10]  # top 10
            ],
        }
```

### Tool 5: Browse Open Bounties

This one fetches live bounties from GitHub — letting Claude recommend tasks to work on:

```python
@mcp.tool()
async def rustchain_bounties(min_rtc: int = 0) -> dict:
    """
    List open RustChain bounties sorted by RTC reward value.
    
    Args:
        min_rtc: Minimum reward to include (default: 0 = show all)
    """
    url = (
        "https://api.github.com/repos/Scottcjn/rustchain-bounties/issues"
        "?state=open&labels=bounty&per_page=30"
    )
    async with httpx.AsyncClient(timeout=15) as client:
        r = await client.get(url, headers={"User-Agent": "rustchain-mcp/1.0"})
        r.raise_for_status()
        issues = r.json()

    def extract_rtc(title: str) -> int:
        import re
        m = re.search(r"(\d+)\s*RTC", title)
        return int(m.group(1)) if m else 0

    bounties = [
        {
            "number": i["number"],
            "rtc": extract_rtc(i["title"]),
            "title": i["title"],
            "url": i["html_url"],
        }
        for i in issues
        if extract_rtc(i["title"]) >= min_rtc
    ]
    bounties.sort(key=lambda x: -x["rtc"])

    return {"count": len(bounties), "bounties": bounties[:15]}
```

### Tool 6 & 7: Submit Attestation + Create Wallet

```python
@mcp.tool()
async def rustchain_submit_attestation(wallet_id: str, hardware_hash: str) -> dict:
    """
    Submit a hardware attestation to earn RTC tokens.
    
    Args:
        wallet_id: Your miner wallet ID
        hardware_hash: SHA-256 of your hardware fingerprint
    """
    async with httpx.AsyncClient(verify=False, timeout=15) as client:
        r = await client.post(
            f"{NODE_URL}/attest",
            json={"miner_id": wallet_id, "hardware_hash": hardware_hash},
        )
        r.raise_for_status()
        return r.json()


@mcp.tool()
async def rustchain_create_wallet(wallet_id: str) -> dict:
    """
    Register a new wallet/miner ID on the RustChain network.
    
    Args:
        wallet_id: Desired wallet name (alphanumeric + hyphens, 3-64 chars)
    """
    async with httpx.AsyncClient(verify=False, timeout=15) as client:
        r = await client.post(
            f"{NODE_URL}/wallet/create",
            json={"miner_id": wallet_id},
        )
        r.raise_for_status()
        return {"wallet_id": wallet_id, "created": True, **r.json()}
```

---

## Running the Server

```python
if __name__ == "__main__":
    mcp.run()
```

```bash
python -m rustchain_mcp.server
```

Add to your Claude Code config (`~/.claude/settings.json`):

```json
{
  "mcpServers": {
    "rustchain": {
      "command": "python",
      "args": ["-m", "rustchain_mcp.server"],
      "cwd": "/path/to/rustchain-mcp"
    }
  }
}
```

---

## Using It

Once connected, Claude Code can answer questions like:

> **Me:** What's my balance in my "暖暖" wallet?  
> **Claude:** Your wallet has **127.5 RTC** (~$12.75 USD).

> **Me:** What bounties can I do right now?  
> **Claude:** Here are the top bounties sorted by reward:
> - #2868: VS Code Extension — **30 RTC** ($3.00)  
> - #2859: MCP Server — **25 RTC** ($2.50)  
> - #2864: GitHub Action — **20 RTC** ($2.00)

> **Me:** When does the current epoch settle?  
> **Claude:** Epoch 128 settles in about **43 minutes**. The pot is 89.2 RTC ($8.92) shared among 7 miners.

The AI becomes your blockchain dashboard, bounty finder, and work tracker simultaneously.

---

## What I Learned

**1. MCP tools work best when they return structured data, not prose.**  
Claude is excellent at explaining structured JSON to users. Your tool doesn't need to format nicely — return raw facts and let the LLM present them.

**2. Docstrings are your API contract.**  
Claude reads the function docstring to decide when and how to call each tool. A good docstring matters more than perfect code.

**3. Async is worth it.**  
Blockchain APIs are slow. FastMCP handles async natively, so multiple tool calls in one conversation don't block each other.

**4. Self-signed certs need explicit handling.**  
The RustChain default node uses a self-signed TLS certificate. Set `verify=False` in httpx (or pass the cert) — otherwise all requests fail silently.

---

## The Result

The full MCP server is part of my PR to the [RustChain bounties repo](https://github.com/Scottcjn/rustchain-bounties). I earned **25 RTC** for submitting it — about $2.50, but more importantly a working tool I actually use daily.

The entire server is ~250 lines of Python. It took about 2 hours to build, test, and document.

If you're looking to get started with MCP development and want a real-world target to integrate with, RustChain's documented REST API is a great sandbox. The node is public, the bounties pay real tokens, and the community is active.

---

## Links

- [RustChain repo](https://github.com/Scottcjn/Rustchain)
- [Open bounties](https://github.com/Scottcjn/rustchain-bounties/issues?q=is%3Aopen+label%3Abounty)
- [MCP Server PR](https://github.com/Scottcjn/rustchain-bounties/pull/2950)
- [FastMCP framework](https://github.com/jlowin/fastmcp)
- [MCP specification](https://modelcontextprotocol.io)

---

*Wallet: 暖暖 | Bounty: [#2863](https://github.com/Scottcjn/rustchain-bounties/issues/2863)*
