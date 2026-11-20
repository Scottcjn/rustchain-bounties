# RustChain RTC Balance — CLAUDE.md Snippet

Add this to any project `CLAUDE.md` to enable `/rtc-balance` as a Claude Code skill:

```markdown
## RustChain Wallet Balance Check

You can check any RustChain wallet balance directly from Claude Code.

### /rtc-balance <wallet-name>

Queries the RustChain public node (https://50.28.86.131) and returns:
- Wallet name
- RTC balance (with USD conversion at $0.10/RTC)
- Current epoch and online miners

### Setup (one-time)

```bash
# Clone the skill
git clone https://github.com/Scottcjn/rustchain-bounties.git \
  /tmp/rustchain-bounties

# Or copy the script to your PATH
cp /tmp/rustchain-bounties/tools/claude-code-rtc-balance/rtc_balance.sh \
  ~/bin/rtc-balance
chmod +x ~/bin/rtc-balance

# Test it
rtc-balance my-wallet-name
```

### Direct API calls

You can also query the RustChain node directly:

```bash
# Check balance
curl "https://50.28.86.131/wallet/balance?miner_id=<name>"

# Check epoch
curl "https://50.28.86.131/epoch"

# Node health
curl "https://50.28.86.131/health"
```

### Error handling

- `Wallet not found` — wallet doesn't exist on-chain
- `Node unreachable` — check internet or retry in 30s
- `Rate limited` — wait 5s before next query
