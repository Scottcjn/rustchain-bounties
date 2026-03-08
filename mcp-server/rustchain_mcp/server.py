"""
Entry point for RustChain MCP Server.
"""

from rustchain_mcp import main

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
