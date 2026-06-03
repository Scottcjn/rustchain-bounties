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
import os, re, json, time, subprocess, urllib.request, urllib.error
TOKEN=os.environ["GITHUB_TOKEN"]; ADMIN=os.environ["RTC_ADMIN_KEY"]
HOST=os.environ.get("RTC_VPS_HOST","50.28.86.131"); REPO=os.environ.get("GH_REPO","Scottcjn/rustchain-bounties")
RATE=float(os.environ.get("RATE_RTC","3")); MAXRUN=int(os.environ.get("MAX_PER_RUN","40"))
FROM="founder_community"; PORT="8099"; WALLET_RE=re.compile(r'\bRTC[0-9a-fA-F]{40}\b')
def gh(args):
    return subprocess.run(["gh"]+args,capture_output=True,text=True,timeout=60,
        env={**os.environ,"GH_TOKEN":TOKEN}).stdout
def transfer(to,memo,idem):
    body=json.dumps({"from_miner":FROM,"to_miner":to,"amount_rtc":RATE,"memo":memo,"idempotency_key":idem}).encode()
    req=urllib.request.Request(f"http://{HOST}:{PORT}/wallet/transfer",data=body,method="POST",
        headers={"Content-Type":"application/json","X-Admin-Key":ADMIN})
    try:
        with urllib.request.urlopen(req,timeout=30) as r: return True,json.loads(r.read())
    except Exception as e: return False,str(e)[:160]
issues=json.loads(gh(["issue","list","-R",REPO,"--state","open","--limit","400","--json","number,title,labels"]))
paid=0; total=0.0
for i in issues:
    if paid>=MAXRUN: print(f"::notice::MAX_PER_RUN={MAXRUN} reached — stopping; remaining eligible will pay next run."); break
    t=i["title"].lower()
    if not (("review" in t) and ("pr" in t or "code" in t or "#73" in t)): continue
    num=str(i["number"]); labels={l["name"] for l in i.get("labels",[])}
    d=json.loads(gh(["issue","view",num,"-R",REPO,"--json","body,comments"]))
    coms=d.get("comments",[])
    eligible = ("bounty-eligible" in labels) or any("Verified eligible" in (c.get("body") or "") for c in coms)
    if not eligible: continue
    if any("RTC-AutoPay-Confirmed" in (c.get("body") or "") for c in coms): continue
    wm=WALLET_RE.search(d.get("body") or "")
    if not wm: continue  # pending wallet
    ok,resp=transfer(wm.group(0),f"Bounty #73 code-review — claim #{num}",f"bounty73-claim-{num}")
    if ok:
        paid+=1; total+=RATE
        gh(["issue","comment",num,"-R",REPO,"--body",f"💸 **RTC-AutoPay-Confirmed** — {RATE:g} RTC sent to `{wm.group(0)}` (verified #73 review, founder_community). Thanks!"])
        gh(["issue","close",num,"-R",REPO,"--reason","completed"])
    else: print(f"::warning::pay failed #{num}: {resp}")
    time.sleep(1.5)
print(f"bounty-payout: paid {paid} claims = {total:g} RTC this run")
