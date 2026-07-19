## Streaming & long-running tools

Currently, `rustchain-mcp` does not support streaming or progressive results for long-running tools. The server will block until the tool completes. For more details, see the implementation in `src/server.rs:handle_tool_call`.

### MCP Capabilities
The server advertises the following capabilities:
- `toolCall`: Supported
- `streamingResults`: Not supported
- `progressNotifications`: Not supported

For more information on the MCP protocol, refer to the [MCP specification](https://example.com/mcp-spec).
