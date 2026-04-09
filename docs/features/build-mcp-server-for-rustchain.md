# Build an MCP Server for RustChain
> Last updated: 2026-04-09
## Overview
This feature implements a Model Context Protocol (MCP) server for RustChain, allowing AI agents to connect and utilize various blockchain operations. It aims to streamline the onboarding process for developers integrating AI agents with RustChain.
## How It Works
The MCP server is implemented in `integrations/rustchain-mcp/server.py`, which handles incoming requests and routes them to the appropriate functions for each tool. The tools include health checks, balance queries, and wallet management, all defined in the server's logic.
## Configuration
The server's default Node URL is set to `https://50.28.86.131`, but it can be configured as needed.
## Usage
To run the MCP server, execute the following command:
```bash
bash rustchain_mcp/run.sh
```
## References
- Closes issue #2859