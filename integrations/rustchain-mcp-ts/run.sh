#!/usr/bin/env bash
# Start the RustChain TypeScript MCP server
set -e
cd "$(dirname "$0")"
exec node dist/index.js
