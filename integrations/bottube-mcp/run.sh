#!/bin/bash
# SPDX-License-Identifier: MIT
# Run script for BoTTube MCP Server
set -e
cd "$(dirname "$0")"
exec python3 -m bottube_mcp.server "$@"
