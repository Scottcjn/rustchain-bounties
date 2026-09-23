#!/usr/bin/env bash
# rtc_balance.sh — Query RustChain wallet balance from terminal
# Bounty: https://github.com/Scottcjn/rustchain-bounties/issues/2860
# Author: CLAUDE.md / AI Agent
# License: MIT

set -euo pipefail

# Exit codes:
#   0 - Success
#   1 - Usage error (invalid arguments, missing wallet)
#   2 - Network error (node unreachable, connection failed, timeout)
#   3 - Bad response (non-200 HTTP status, malformed JSON)
#   4 - Wallet not found / empty balance

# SECURITY: `curl -k` (or `-sk`) disables TLS certificate verification globally.
# That's appropriate only when the operator deliberately points at a self-signed
# test node. Default to verifying; allow opt-out via `RTC_INSECURE=1`.
CURL_TLS_OPTS=()

# SECURITY: build the wallet URL with proper percent-encoding so an untrusted
# wallet string cannot smuggle query parameters or fragments into the URL.
urlencode() {
    python3 -c 'import sys, urllib.parse; print(urllib.parse.quote(sys.argv[1], safe=""))' "$1"
}

usage() {
    cat <<EOF
Usage: rtc-balance <wallet-name> [--node-url URL] [--insecure]

Query a RustChain wallet balance from the terminal.

Example:
  rtc-balance my-wallet-name
  rtc-balance my-wallet-name --node-url https://custom-node.example.com
  rtc-balance my-wallet-name --insecure

Options:
  --node-url URL   Override the default node URL (default: https://50.28.86.131)
  --insecure       Disable TLS certificate verification (for self-signed test nodes)
  -h, --help       Show this help message

Environment:
  RTC_NODE_URL   Override the default node URL (default: https://50.28.86.131)
  RTC_INSECURE   Set to 1 to disable TLS verification (for self-signed test nodes)

Exit codes:
  0 - Success
  1 - Usage error
  2 - Network error
  3 - Bad response
  4 - Wallet not found
EOF
    exit 1
}

# Validate wallet name (alphanumeric, dash, underscore only)
validate_wallet() {
    local wallet="$1"
    if [[ ! "$wallet" =~ ^[A-Za-z0-9_-]{1,64}$ ]]; then
        echo "Error: Invalid wallet name; expected [A-Za-z0-9_-]{1,64}" >&2
        exit 1
    fi
}

# Default values
NODE_URL="${RTC_NODE_URL:-https://50.28.86.131}"
INSECURE="${RTC_INSECURE:-0}"
RTC_USD=0.10
WALLET=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --node-url)
            NODE_URL="$2"
            shift 2
            ;;
        --insecure)
            INSECURE=1
            shift
            ;;
        -h|--help)
            usage
            ;;
        -*)
            echo "Error: Unknown option: $1" >&2
            usage
            ;;
        *)
            if [[ -z "$WALLET" ]]; then
                WALLET="$1"
            else
                echo "Error: Unexpected argument: $1" >&2
                usage
            fi
            shift
            ;;
    esac
done

if [[ "$INSECURE" == "1" ]]; then
    CURL_TLS_OPTS=(-k)
fi

if [[ -z "$WALLET" ]]; then
    usage
fi

# Strip trailing/leading whitespace
WALLET=$(echo "$WALLET" | xargs)
validate_wallet "$WALLET"

# Health check - distinguish between network errors and HTTP errors
health_output=$(curl "${CURL_TLS_OPTS[@]}" -sS --max-time 5 "$NODE_URL/health" 2>&1) || CURL_EXIT=$?

if [[ ${CURL_EXIT:-0} -ne 0 ]]; then
    # Network error (connection refused, timeout, DNS failure, etc.)
    echo "Error: Node unreachable at $NODE_URL" >&2
    echo "Check your internet connection or try again in a moment." >&2
    exit 2
fi

# Check HTTP status for health endpoint
health_http_code=$(echo "$health_output" | tail -1)
if [[ ! "$health_http_code" =~ ^[0-9]{3}$ ]]; then
    # If we can't determine HTTP code, try to parse JSON to verify it's valid
    if ! echo "$health_output" | python3 -c 'import sys, json; json.load(sys.stdin)' >/dev/null 2>&1; then
        echo "Error: Health check returned malformed response" >&2
        exit 3
    fi
fi

# Query balance
balance_output=$(curl "${CURL_TLS_OPTS[@]}" -sS --max-time 10 "$NODE_URL/wallet/balance?miner_id=$(urlencode "$WALLET")" 2>&1) || CURL_EXIT=$?

if [[ ${CURL_EXIT:-0} -ne 0 ]]; then
    # Network error
    echo "Error: Failed to query wallet '$WALLET' (curl exit ${CURL_EXIT})" >&2
    exit 2
fi

# Parse JSON response — handle multiple possible shapes
balance=$(echo "$balance_output" | python3 -c '
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
except json.JSONDecodeError as e:
    print("__MALFORMED_JSON__", file=sys.stderr)
    sys.exit(3)
except Exception:
    print("N/A")
' 2>&1)
PARSE_EXIT=$?

if [[ $PARSE_EXIT -eq 3 ]]; then
    echo "Error: Balance query returned malformed JSON" >&2
    exit 3
fi

# Check if balance is valid
if [[ "$balance" == "N/A" || "$balance" == "" ]]; then
    echo "Wallet: $WALLET"
    echo "Balance: N/A (wallet not found or node returned empty)" >&2
    exit 4
fi

# Query epoch info (non-fatal if it fails)
epoch_info=""
if epoch_raw=$(curl "${CURL_TLS_OPTS[@]}" -sS --max-time 10 "$NODE_URL/epoch" 2>&1); then
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

exit 0