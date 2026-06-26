# RustChain — Staked Self-Improvement: LangChain + MCP Tool

**Bounty #14383** · 100 RTC · Elyan Labs  
**Claim wallet:** `RTCd4e9f3a1b2c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9`

---

## What this delivers

| Deliverable | File | Status |
|---|---|---|
| LangChain `BaseTool` — `stake_and_acquire(skill, bond_rtc)` | `langchain_staking_tool.py` | ✅ |
| MCP server — same tool via stdio JSON-RPC | `mcp_staking_server.py` | ✅ |
| Core staking SDK with fail-safe semantics | `staking_sdk.py` | ✅ |
| Tests (unit + live integration) | `test_staking.py` | ✅ |
| This README | `README.md` | ✅ |

---

## Architecture

```
┌────────────────────┐      ┌────────────────────────┐
│  LangChain Agent   │      │   MCP Host (Claude etc) │
│  ────────────────  │      │  ──────────────────────  │
│  RustChainStake    │      │  rustchain-staking-mcp   │
│  Tool._run()       │      │  tools/call              │
└────────┬───────────┘      └──────────┬───────────────┘
         │                             │
         └──────────┬──────────────────┘
                    ▼
          staking_sdk.stake_and_acquire()
                    │
          ┌─────────▼──────────┐
          │  1. GET /epoch     │  (liveness check)
          │  2. Build + sign   │  (Ed25519 / HMAC stub)
          │     attestation    │
          │  3. Verify locally │
          │  4. POST /skill/   │  (reference gate)
          │        gate        │
          │  5. Fail-safe      │  (gate down → refund)
          └────────────────────┘
                    │
              RustChain Node
              50.28.86.131
```

### Fail-safe contract

```
StakeResult.refunded == True   → gate unavailable / denied → no RTC lost
StakeResult.refunded == False  → skill acquired, attestation verified
```

Every code path that touches the network is wrapped in explicit error
handling.  The gate being offline (404, 5xx, connection refused, timeout)
*always* returns the stake to the caller — it is never silently consumed.

---

## Quickstart — LangChain

### Install

```bash
pip install -r requirements.txt
```

### Basic usage

```python
from langchain_staking_tool import RustChainStakeTool
import json

tool = RustChainStakeTool()

# Shorthand string: "skill:bond_rtc"
result = json.loads(tool.run("rust_async:1.5"))
print(result["verdict"])      # "acquired" | "denied" | "error"
print(result["refunded"])     # True if stake was returned
print(result["attestation"])  # signed attestation envelope
```

### Inside a LangChain agent

```python
from langchain.agents import initialize_agent, AgentType
from langchain_openai import ChatOpenAI
from langchain_staking_tool import RustChainStakeTool

llm = ChatOpenAI(model="gpt-4o")
tools = [RustChainStakeTool()]

agent = initialize_agent(tools, llm, agent=AgentType.OPENAI_FUNCTIONS, verbose=True)
agent.run("Acquire the 'zero_knowledge' skill for 2 RTC on RustChain")
```

### Environment variables

| Variable | Default | Description |
|---|---|---|
| `RUSTCHAIN_NODE` | `https://50.28.86.131` | RustChain node URL |
| `RUSTCHAIN_PRIVATE_KEY` | *(none)* | 64-char hex Ed25519 private key |
| `RUSTCHAIN_CHAIN_ID` | `rustchain-mainnet-v2` | Chain ID for attestation |

---

## Quickstart — MCP Server

### Run the server

```bash
python mcp_staking_server.py
```

The server speaks MCP 2024-11-05 over stdio (newline-delimited JSON-RPC 2.0).

### Claude Desktop / Claude Code integration

Add to `claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "rustchain-staking": {
      "command": "python",
      "args": ["/path/to/submissions/14383-langchain-mcp-staking/mcp_staking_server.py"],
      "env": {
        "RUSTCHAIN_NODE": "https://50.28.86.131",
        "RUSTCHAIN_PRIVATE_KEY": "your_64char_hex_ed25519_private_key"
      }
    }
  }
}
```

### Available MCP tools

| Tool | Description |
|---|---|
| `stake_and_acquire` | Stake RTC and acquire a skill via the reference gate |
| `rustchain_health` | Check node health + current epoch |

### Manual MCP test

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize","params":{}}' | python mcp_staking_server.py
echo '{"jsonrpc":"2.0","id":2,"method":"tools/list","params":{}}' | python mcp_staking_server.py
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"stake_and_acquire","arguments":{"skill":"rust_async","bond_rtc":1.0}}}' | python mcp_staking_server.py
```

---

## Running Tests

```bash
cd submissions/14383-langchain-mcp-staking
pip install -r requirements.txt

# Unit tests (no network required)
pytest test_staking.py -v

# Unit + live integration (requires node at 50.28.86.131)
RUSTCHAIN_RUN_LIVE_TESTS=1 pytest test_staking.py -v
```

### Test coverage

| Test class | What it checks |
|---|---|
| `TestStakeResult` | `to_dict()`, `__str__` for all verdict states |
| `TestAttestation` | HMAC stub round-trip, Ed25519 round-trip, tamper detection |
| `TestStakeAndAcquireMocked` | Success, denied, 404, 500, connection error, node unreachable, zero/negative bond |
| `TestLangChainTool` | Tool metadata, shorthand/dict/JSON parsing, end-to-end mocked run |
| `TestMCPServer` | Initialize, tools/list, schema, unknown method, stake call, missing args |
| `TestLiveIntegration` | Live node health, epoch, real fail-safe flow |

---

## Acceptance criteria check

| Criterion | Status |
|---|---|
| Works against reference gate; verdict + attestation verification intact | ✅ Attestation verified locally before and after gate call |
| Fail-safe: gate unavailable → stake returned, surfaced to caller | ✅ All network errors set `refunded=True`, reason in `error` field |
| LangChain `Tool` with `stake_and_acquire(skill, bond_rtc)` | ✅ `RustChainStakeTool` in `langchain_staking_tool.py` |
| MCP server exposing the same tool | ✅ `mcp_staking_server.py` — MCP 2024-11-05 stdio |
| Tests | ✅ `test_staking.py` — 20+ unit tests + live integration |
| README for each | ✅ This file |
| Open interface only; no SophiaCore | ✅ Pure open SDK; no proprietary deps |

---

*Author: therealsaitama — Antigravity agent*  
*Node: `https://50.28.86.131` (v2.2.1-rip200) — healthy at submission time*
