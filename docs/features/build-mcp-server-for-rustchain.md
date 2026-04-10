# Build an MCP Server for RustChain
> Last updated: 2026-04-10
## Overview
This feature implements a Model Context Protocol (MCP) server for RustChain, allowing AI agents to connect and interact with blockchain operations efficiently.
## How It Works
The MCP server is implemented in `integrations/rustchain-mcp/server.py`, which handles incoming requests and routes them to the appropriate functions for processing. Each tool, such as `rustchain_health` and `rustchain_balance`, is defined to perform specific blockchain operations.
## Configuration
The server's default Node URL can be configured in the server settings, with a default value of `https://50.28.86.131`.
## Usage
To start the server, run `python integrations/rustchain-mcp/server.py`. Use an MCP-compatible client to connect and interact with the available tools.
## References
- Closes issue #2859