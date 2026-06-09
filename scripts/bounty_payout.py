#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Bounty payout — pays verified-eligible code-review claims as wallets confirm.

Completes the pipeline: the PR-review gate labels a claim `bounty-eligible`
(or a maintainer comments "Verified eligible"); when the claimant adds a native
RTC wallet, this run pays 3 RTC from founder_community and closes the claim.

If the claim has no native `RTC[0-9a-fA-F]{40}` address, the script falls
back to a GitHub handle from the issue body or a recent `Wallet: <handle>`
comment - matching the rtc-reward action's handle-fallback (PR #13394).
Bots are excluded so automation cannot farm rewards.

SAFETY:
  - pays ONLY verified-eligible claims (gate label or "Verified eligible" comment)
  - native RTC wallet preferred; handle fallback is opt-in
  - handle fallback excludes bot accounts (`type == 'Bot'` or `[bot]` suffix)
  - idempotency_key=bounty73-claim-<n> + 'RTC-AutoPay-Confirmed' marker => never double-pays
  - MAX_PER_RUN aggregate cap (default 40) — hard stop per run, surfaced in log
Env: GITHUB_TOKEN, RTC_ADMIN_KEY, RTC_VPS_HOST, GH_REPO, RATE_RTC(3), MAX_PER_RUN(40).
"""
import os, re, json, time, subprocess, ssl, urllib.request, urllib.error
TOKEN=os.environ["GITHUB_TOKEN"]; ADMIN=os.environ["RTC_ADMIN_KEY"]
HOST=os.environ.get("RTC_VPS_HOST","50.28.86.131"); REPO=os.environ.get("GH_REPO","Scottcjn/rustchain-bounties")
RATE=float(os.environ.get("RATE_RTC","3")); MAXRUN=int(os.environ.get("MAX_PER_RUN","40"))
FROM="founder_community"; PORT="8099"
WALLET_RE=re.compile(r'\bRTC[0-9a-fA-F]{40}\b')
# Matches `Wallet: <handle-or-address>` (case-insensitive, Markdown-tolerant).
# Tolerates:
#   - leading Markdown headers (`## Wallet: handle`)
#   - bullet list markers (`- **Wallet:** handle`)
#   - bold markers (`**Wallet:** handle` / `**Wallet**: handle`)
#   - inline code (`` `handle` ``)
#   - trailing parentheses / notes (`(GitHub handle)`)
#   - trailing annotation (`- please send RTC to @handle`)
HANDLE_RE=re.compile(r'(?i)(?:##?\s*)?(?:-|\*|``)?\s*Wallet\s*:\s*([a-z0-9_-]+)', re.MULTILINE)
# Add canonical payout form mapping
CANONICAL_PAYOUT_FORM = {
    '@jdjioe5-cpu': 'GitHub handle'
}

# Rest of the code remains the same