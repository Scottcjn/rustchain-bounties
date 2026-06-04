tier: T1
target: rustchain
language: python
endpoints_used: [/health, /epoch, /api/miners]
wallet: RTC1410e82d545ce0b3ffd21ca83e2465a8f2c3a64e
starred: yes

# RustChain MCP Read Integration

This submission exposes a small MCP server with read-only RustChain tools backed by a live node.

Included tools:
- `get_health`: fetches `GET /health`
- `get_epoch`: fetches `GET /epoch`
- `get_miners`: fetches `GET /api/miners`

Default base URL: `http://rustchain.org:8088`
