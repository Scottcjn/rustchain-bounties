#!/usr/bin/env bash
set -euo pipefail

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

if [ -f "$DIR/.venv/bin/activate" ]; then
  source "$DIR/.venv/bin/activate"
fi

exec python -m rustchain_mcp.server
