# RustChain Staking Tools

LangChain + MCP tools for staked self-improvement on RustChain.

**Bounty:** [#14383](https://github.com/Scottcjn/rustchain-bounties/issues/14383) — 100 RTC

## Quick Start

### LangChain

```python
from stake_tool import StakeAndAcquireTool

tool = StakeAndAcquireTool()  # reads from env
result = tool.run({"skill": "code-review", "bond_rtc": 50})
```

### MCP Server

```bash
export ELYAN_API_KEY="your-key"
export ELYAN_GATE_PUBKEY="hex-pubkey"
python docs/staking-tools/mcp/server.py
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `ELYAN_API_KEY` | Yes | API key for staking gate |
| `ELYAN_GATE_PUBKEY` | Yes | Ed25519 public key (hex) |
| `ELYAN_GATE_ENDPOINT` | No | Gate URL (default: gate.elyan.ai) |

## Fail-Safe Semantics

If gate unreachable → stake returned, surfaced to caller.

## Files

```
docs/staking-tools/
├── langchain/stake_tool.py    # LangChain Tool
├── mcp/server.py              # MCP Server
├── tests/test_stake_tool.py   # Unit tests
└── README.md                  # This file
```
