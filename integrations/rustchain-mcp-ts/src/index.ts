/**
 * Entry point — runs the RustChain MCP server.
 *
 * Usage (stdio transport):
 *   node dist/index.js
 *
 * Usage (HTTP/SSE — Claude Desktop etc.):
 *   npx rustchain-mcp
 *
 * Environment variables:
 *   RUSTCHAIN_PRIMARY_URL     — primary node URL (default: https://50.28.86.131)
 *   RUSTCHAIN_FALLBACK_URLS   — comma-separated fallback node URLs
 *   RUSTCHAIN_TIMEOUT_MS      — request timeout in ms (default: 10000)
 */

import { server } from "./server.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";

async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
  // Keep the process alive — the transport handles stdio messaging
  await new Promise<void>((resolve) => {
    process.stdin.on("close", resolve);
  });
}

main().catch((err) => {
  console.error("Fatal:", err);
  process.exit(1);
});
