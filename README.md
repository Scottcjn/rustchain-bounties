## RustChain MCP Server 

### Overview
This is an MCP server that connects any AI agent to RustChain, allowing for easy access to various blockchain functionalities through a model context protocol (MCP).

### Installation
To install the RustChain MCP Server, use the following command:
```bash
mise install
```

### Running the Server
To start the server, simply run:
```bash
python3 integrations/rustchain-mcp/server.py
```

### Configuration
You may configure the server with the required options. Here's a quick start template:

```json
{
    "mcpServers": {
        "rustchain": {
            "command": "uvx",
            "args": ["rustchain-mcp"]
        }
    }
}
```

### Features
- `rustchain_health`: Checks the health of the node.
- `rustchain_balance`: Queries the wallet balance.
- Other commands like listing active miners, providing current epoch information, etc., will be implemented in future releases.

--- 
