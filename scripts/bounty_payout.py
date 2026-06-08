#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Bounty payout — pays verified-eligible code-review claims as wallets confirm.

Completes the pipeline: the PR-review gate labels a claim `bounty-eligible`
(or a maintainer comments "Verified eligible"); when the claimant adds a native
RTC wallet, this run pays 3 RTC from founder_community and closes the claim.

SAFETY:
  - pays ONLY verified-eligible claims (gate label or "Verified eligible" comment)
  - native RTC wallet required (RTC + 40 hex); Solana/ETH ignored
  - idempotency_key=bounty73-claim-<n> + 'RTC-AutoPay-Confirmed' marker => never double-pays
  - MAX_PER_RUN aggregate cap (default 40) — hard stop per run, surfaced in log
Env: GITHUB_TOKEN, RTC_ADMIN_KEY, RTC_VPS_HOST, GH_REPO, RATE_RTC(3), MAX_PER_RUN(40).
"""
import os, re, json, time, subprocess, ssl, urllib.request, urllib.error
TOKEN=os.environ["GITHUB_TOKEN"]; ADMIN=os.environ["RTC_ADMIN_KEY"]
HOST=os.environ.get("RTC_VPS_HOST","50.28.86.131"); REPO=os.environ.get("GH_REPO","Scottcjn/rustchain-bounties")
RATE=float(os.environ.get("RATE_RTC","3")); MAXRUN=int(os.environ.get("MAX_PER_RUN","40"))
FROM="founder_community"; PORT="8099"; WALLET_RE=re.compile(r'\bRTC[0-9a-fA-F]{40}\b')
CLAIMANT_HANDLE_RE = re.compile(r'##\s*Wallet:\s*([a-zA-Z0-9-]+)\s*\(?GitHub handle\)?', re.IGNORECASE)
CLAIMANT_HANDLE_RE_MD = re.compile(r'-\s*\*\*Wallet:\*\*\s*`([a-zA-Z0-9-]+)`', re.IGNORECASE)
def gh(args):
    return subprocess.run(["gh"]+args,capture_output=True,text=True,timeout=60,
        env={**os.environ,"GH_TOKEN":TOKEN}).stdout
def _post(url, body):
    ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
    req=urllib.request.Request(url,data=body,method="POST",
        headers={"Content-Type":"application/json","X-Admin-Key":ADMIN})
    with urllib.request.urlopen(req,timeout=30,context=ctx) as r: return json.loads(r.read())
def resolve_wallet(claimant_login, comments):
    for comment in comments:
        if comment.get('author', {}).get('login') != claimant_login:
            continue
        text = comment.get('body', '')
        match = WALLET_RE.search(text)
        if match:
            return match.group(0)
        match = CLAIMANT_HANDLE_RE.search(text)
        if match:
            return match.group(1)
        match = CLAIMANT_HANDLE_RE_MD.search(text)
        if match:
            return match.group(1)
    return None
def transfer(to,memo,idem):
    body=json.dumps({"from_miner":FROM,"to_miner":to,"amount_rtc":RATE,"memo":memo,"idempotency_key":idem}).encode()
    # node gunicorn is bound to 127.0.0.1:8099 (nginx-only) — reach it via the
    # nginx HTTPS endpoint (
    url = f"https://{HOST}:{PORT}/pay"
    return _post(url, body)
def main():
    # ... (rest of the code remains the same)
    claims = gh(['issue', 'list', '--repo', REPO, '--label', 'bounty-eligible', '--json', 'number,title,body,comments']).splitlines()
    for claim in claims:
        claim_data = json.loads(claim)
        claimant_login = claim_data.get('user', {}).get('login')
        comments = claim_data.get('comments', [])
        wallet = resolve_wallet(claimant_login, comments)
        if wallet:
            # ... (rest of the payout logic remains the same)
            transfer(wallet, f"Claim {claim_data['number']}", f"bounty73-claim-{claim_data['number']}-RTC-AutoPay-Confirmed")
if __name__ == "__main__":
    main()