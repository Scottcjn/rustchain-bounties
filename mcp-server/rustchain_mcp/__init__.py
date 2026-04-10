"""
RustChain MCP Server
====================
Exposes RustChain as MCP tools for Claude Code, Cursor, Windsurf, and any MCP-compatible IDE.

Usage:
    # Configure your MCP client (Claude Code, Cursor, etc.)
    {
      "mcpServers": {
        "rustchain": {
          "command": "python",
          "args": ["-m", "rustchain_mcp"]
        }
      }
    }
"""

__version__ = "0.1.0"
