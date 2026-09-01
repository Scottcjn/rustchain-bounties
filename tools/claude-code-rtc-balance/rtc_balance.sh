#!/usr/bin/env bash
# rtc_balance.sh — Query RustChain wallet balance from terminal
# Bounty: https://github.com/Scottcjn/rustchain-bounties/issues/2860
# Author: CLAUDE.md / AI Agent
# License: MIT

set -euo pipefail

NODE_URL="${RTC_NODE_URL:-https://50.28.86.131}"
WALLET="${1:-}"
INSECURE="${RTC_INSECURE:-0}"
RTC_USD=0.10

# SECURITY: `curl -k` (or `-sk`) disables TLS certificate verification globally.
# That's appropriate only when the operator deliberately points at a self-signed
# test node. Default to verifying; allow opt-out via `RTC_INSECURE=1`.
CURL_TLS_OPTS=()
if [[ "$INSECURE" == "1" ]]; then
    CURL_TLS_OPTS=(-k)
fi

# SECURITY: build the wallet URL with proper percent-encoding so an untrusted
# wallet string cannot smuggle query parameters or fragments into the URL.
urlencode() {
    python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=""))' "$1"
}

usage() {
    cat <<EOF
Usage: rtc-balance <wallet-name>

Query a RustChain wallet balance from the terminal.

Example:
  rtc-balance my-wallet-name

Environment:
  RTC_NODE_URL   Override the default node URL (default: https://50.28.86.131)
EOF
    exit 1
}

if [[ -z "$WALLET" ]]; then
    usage
fi

# Strip trailing/leading whitespace
WALLET=$(echo "$WALLET" | xargs)

# Health check
if ! curl "${CURL_TLS_OPTS[@]}" -sf --max-time 5 "$NODE_URL/health" > /dev/null 2>&1; then
    echo "Error: Node unreachable at $NODE_URL" >&2
    echo "Check your internet connection or try again in a moment." >&2
    exit 1
fi

# Query balance
RAW=$(curl "${CURL_TLS_OPTS[@]}" -sf --max-time 10 "$NODE_URL/wallet/balance?miner_id=$(urlencode "$WALLET")")
CODE=$?

if [[ $CODE -ne 0 ]]; then
    echo "Error: Failed to query wallet '$WALLET' (curl exit $CODE)" >&2
    exit 1
fi

# Parse JSON response — handle multiple possible shapes
balance=$(echo "$RAW" | python3 -c '
import sys, json
try:
    d = json.load(sys.stdin)
    # Check amount_rtc first (most common for RustChain)
    for key in ["amount_rtc", "balance", "rtc_balance"]:
        val = d.get(key)
        if val is not None and val != "":
            print(val)
            break
    else:
        # Try nested result/data keys
        for parent in ["result", "data"]:
            sub = d.get(parent, {})
            for key in ["amount_rtc", "balance"]:
                val = sub.get(key)
                if val is not None and val != "":
                    print(val)
                    break
            else:
                continue
            break
        else:
            print("N/A")
except Exception:
    print("N/A")
' 2>/dev/null)

# Query epoch info (non-fatal if it fails)
epoch_info=""
if epoch_raw=$(curl "${CURL_TLS_OPTS[@]}" -sf --max-time 10 "$NODE_URL/epoch" 2>/dev/null); then
    epoch_info=$(echo "$epoch_raw" | python3 -c '
import sys, json
try:
    d = json.load(sys.stdin)
    epoch = (
        d.get("epoch") or
        d.get("result", {}).get("epoch") or
        d.get("data", {}).get("epoch") or
        d.get("current_epoch") or
        None
    )
    miners = (
        d.get("miners_online") or
        d.get("result", {}).get("miners_online") or
        d.get("data", {}).get("miners") or
        d.get("active_miners") or
        None
    )
    parts = []
    if epoch: parts.append(f"Epoch: {epoch}")
    if miners: parts.append(f"Miners online: {miners}")
    print(" | ".join(parts))
except Exception:
    pass
' 2>/dev/null)
fi

# Calculate USD value
if [[ "$balance" != "N/A" && "$balance" != "" ]]; then
    usd_val=$(python3 -c "
bal = float('$balance')
usd = float('$RTC_USD')
print(f'{bal * usd:.2f}')
" 2>/dev/null || echo "?")
    printf "Wallet: %s\n" "$WALLET"
    printf "Balance: %s RTC (\$%s USD)\n" "$balance" "$usd_val"
    if [[ -n "$epoch_info" ]]; then
        printf "%s\n" "$epoch_info"
    fi
else
    echo "Wallet: $WALLET"
    echo "Balance: N/A (wallet not found or node returned empty)"
    exit 1
fi
