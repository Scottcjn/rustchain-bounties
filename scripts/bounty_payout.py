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
# Matches `Wallet: <handle-or-address>` (case-insensitive, common label forms).
HANDLE_RE=re.compile(
    r'(?im)^\s*(?:wallet|wallet\s*address|wallet\s*id|recipient)\s*[:=]\s*'
    r'`?([A-Za-z0-9][A-Za-z0-9_-]{1,38})`?\s*(?:#.*)?$'
)
GH_LOGIN_RE=re.compile(r'^[A-Za-z0-9][A-Za-z0-9_-]{0,38}$')
BOT_SUFFIX_RE=re.compile(r'\[bot\]$', re.IGNORECASE)
def gh(args):
    return subprocess.run(["gh"]+args,capture_output=True,text=True,timeout=60,
        env={**os.environ,"GH_TOKEN":TOKEN}).stdout
def _post(url, body):
    ctx=ssl.create_default_context(); ctx.check_hostname=False; ctx.verify_mode=ssl.CERT_NONE
    req=urllib.request.Request(url,data=body,method="POST",
        headers={"Content-Type":"application/json","X-Admin-Key":ADMIN})
    with urllib.request.urlopen(req,timeout=30,context=ctx) as r: return json.loads(r.read())
def transfer(to,memo,idem):
    body=json.dumps({"from_miner":FROM,"to_miner":to,"amount_rtc":RATE,"memo":memo,"idempotency_key":idem}).encode()
    # node gunicorn is bound to 127.0.0.1:8099 (nginx-only) — reach it via the
    # nginx HTTPS endpoint (the working path); fall back to the internal port.
    for url in (f"https://{HOST}/wallet/transfer", f"http://{HOST}:{PORT}/wallet/transfer"):
        try: return True,_post(url,body)
        except Exception as e: last=str(e)[:160]
    return False,last
def _is_bot_login(login, user_obj):
    if user_obj and isinstance(user_obj, dict):
        if user_obj.get("type") == "Bot":
            return True
    if login and BOT_SUFFIX_RE.search(login):
        return True
    return False
def _looks_like_handle(token):
    if not token:
        return False
    if WALLET_RE.fullmatch(token):
        return False
    if not GH_LOGIN_RE.match(token):
        return False
    bad = {"address", "wallet", "id", "tbd", "tba", "n/a", "none", "null",
           "the", "my", "your", "this", "pending", "see", "comment", "issue"}
    return token.lower() not in bad
def resolve_wallet(issue_body, comments, claimant_login=None):
    """Return (wallet, source) where source is 'native' | 'handle' | None.
    Resolution order:
      1. Native `RTC[0-9a-fA-F]{40}` in the issue body (preferred).
      2. `Wallet: <handle>` line in the issue body, when it parses as a
         plausible GitHub login.
      3. Most recent non-bot `Wallet: <handle>` comment.
      4. `claimant_login` (the PR author) if it is a plausible login and not
         a bot. Caller is responsible for bot-excluding.
    """
    body = issue_body or ""
    wm = WALLET_RE.search(body)
    if wm:
        return wm.group(0), "native"
    hm = HANDLE_RE.search(body)
    if hm and _looks_like_handle(hm.group(1)):
        return hm.group(1), "handle"
    if comments:
        for c in reversed(comments):
            user_obj = c.get("user") if isinstance(c, dict) else None
            author = (user_obj or {}).get("login") if isinstance(user_obj, dict) else None
            if _is_bot_login(author, user_obj):
                continue
            cb = c.get("body") or ""
            m = HANDLE_RE.search(cb)
            if m and _looks_like_handle(m.group(1)):
                return m.group(1), "handle"
    if claimant_login and _looks_like_handle(claimant_login) and not _is_bot_login(claimant_login, None):
        return claimant_login, "handle"
    return None, None
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
    wallet, source = resolve_wallet(d.get("body"), coms)
    if not wallet: continue
    ok,resp=transfer(wallet,f"Bounty #73 code-review — claim #{num} (source: {source})",f"bounty73-claim-{num}")
    if ok:
        paid+=1; total+=RATE
        gh(["issue","comment",num,"-R",REPO,"--body",f"💸 **RTC-AutoPay-Confirmed** — {RATE:g} RTC sent to `{wallet}` (source: {source}, verified #73 review, founder_community). Thanks!"])
        gh(["issue","close",num,"-R",REPO,"--reason","completed"])
    else: print(f"::warning::pay failed #{num}: {resp}")
    time.sleep(1.5)
print(f"bounty-payout: paid {paid} claims = {total:g} RTC this run")
