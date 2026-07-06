# RustChain Staking Tool — LangChain + MCP

Stake RTC to acquire skills. LangChain tool + MCP server with fail-safe refund semantics.

## Quick Start

```bash
pip install langchain  # optional, for LangChain tool
```

### LangChain Tool

```python
from langchain_staking_tool import RustChainStakeTool

tool = RustChainStakeTool()
result = tool.run("rust_async:1.0", bond_rtc=5.0)
print(result)
# {'verdict': 'error', 'refunded': True, 'error': 'gate_unavailable:...', ...}
```

### MCP Server

```bash
echo '{"jsonrpc":"2.0","id":1,"method":"initialize"}' | python3 mcp_staking_server.py
echo '{"jsonrpc":"2.0","id":2,"method":"tools/list"}' | python3 mcp_staking_server.py
echo '{"jsonrpc":"2.0","id":3,"method":"tools/call","params":{"name":"stake_and_acquire","arguments":{"skill":"rust:1.0","bond_rtc":2.0}}}' | python3 mcp_staking_server.py
```

### SDK

```python
from staking_sdk import stake_and_acquire
result = stake_and_acquire("rust_async:1.0", 5.0)
print(result.to_dict())
```

## Tests

```bash
python3 test_staking.py
```

## Files

| File | What |
|---|---|
| `staking_sdk.py` | Core SDK — `stake_and_acquire()` + fail-safe |
| `langchain_staking_tool.py` | LangChain `BaseTool` (RustChainStakeTool) |
| `mcp_staking_server.py` | MCP 2024-11-05 stdio server |
| `test_staking.py` | Tests (fail-safe, MCP lifecycle) |
| `README.md` | This file |

## Fail-Safe Semantics

If the staking gate is unavailable (network error, 404, 503), the SDK:
1. Sets `refunded: true`
2. Returns the error reason to the caller
3. Never loses the stake — it's returned before it's ever sent
