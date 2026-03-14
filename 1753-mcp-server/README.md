# RustChain MCP Server

MCP (Model Context Protocol) server for querying RustChain blockchain data.

## Features

- Query block information
- Query transaction details
- Check account balance
- Get latest blocks
- Get network status

## Installation

```bash
pip install -r requirements.txt
```

## Usage

```bash
python mcp_server.py
```

## Tools

1. `get_block` - Get block by number or hash
2. `get_transaction` - Get transaction by hash
3. `get_balance` - Get account balance
4. `get_latest_blocks` - Get N latest blocks
5. `get_network_status` - Get network info

## Configuration

Set environment variables:
- `RUSTCHAIN_RPC_URL` - RustChain RPC endpoint (default: https://rpc.rustchain.com)

## License

MIT
