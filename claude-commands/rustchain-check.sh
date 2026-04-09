#!/bin/bash
# RustChain Check — Claude Code Slash Command
# Usage: /rustchain-check [wallet-address]

API="https://api.rustchain.io/v1"
WALLET="${1:-$RUSTCHAIN_WALLET}"

if [ -z "$WALLET" ]; then
    echo "❌ Usage: /rustchain-check <wallet-address>"
    echo "   Or set RUSTCHAIN_WALLET env var"
    exit 1
fi

echo "🦀 RustChain Status"
echo "━━━━━━━━━━━━━━━━━━"

# Balance
BALANCE=$(curl -s "$API/balance/$WALLET" 2>/dev/null)
RTC=$(echo "$BALANCE" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d.get('amount_rtc','?'))" 2>/dev/null || echo "?")
echo "💰 Balance: $RTC RTC"

# Miner status
MINER=$(curl -s "$API/miner/$WALLET/status" 2>/dev/null)
ATTESTING=$(echo "$MINER" | python3 -c "import json,sys;d=json.load(sys.stdin);print('🟢 Attesting' if d.get('attesting') else '🔴 Offline')" 2>/dev/null || echo "❓ Unknown")
echo "⛏️  Miner: $ATTESTING"

# Bounties
BOUNTIES=$(curl -s "$API/bounties?limit=5" 2>/dev/null)
COUNT=$(echo "$BOUNTIES" | python3 -c "import json,sys;d=json.load(sys.stdin);print(len(d.get('bounties',[])))" 2>/dev/null || echo "?")
echo "📋 Open Bounties: $COUNT"

# Health
HEALTH=$(curl -s "$API/health" 2>/dev/null)
STATUS=$(echo "$HEALTH" | python3 -c "import json,sys;d=json.load(sys.stdin);v=d.get('version','?');print(f'Online (v{v})' if d.get('ok') else 'Offline')" 2>/dev/null || echo "❌ Unreachable")
echo "❤️  Node: $STATUS"
