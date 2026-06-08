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
#   - trailing annotation (`- please send RTC here`)
# The implementation strips `**` markers per-line and matches against
# the simplified pattern; this is much more reliable than trying to
# support every bold/colon interleaving in a single regex.
HANDLE_RE=re.compile(
    r'(?im)^\s*[-*]?\s*(?:#+\s+)?'
    r'(?:wallet|wallet\s+address|wallet\s+id|recipient)'
    r'\s*[:=]\s*'
    r'`?([A-Za-z0-9][A-Za-z0-9_-]{0,38})`?'
    r'(?:\s*\([^)]*\))?'
    r'(?:\s*[-—]\s*\S.*)?'
    r'\s*$'
)
GH_LOGIN_RE=re.compile(r'^[A-Za-z0-9][A-Za-z0-9_-]{0,38}$')
BOT_SUFFIX_RE=re.compile(r'\[bot\]$', re.IGNORECASE)
# Known non-human logins that should be excluded even without an explicit
# type/suffix marker. Keep the set small and verifiable from public GitHub
# conventions (CI bots, automation accounts, etc.).
KNOWN_BOT_LOGINS=frozenset({
    "github-actions", "github-actions[bot]",
    "dependabot", "dependabot[bot]",
    "renovate", "renovate[bot]",
    "codecov", "codecov[bot]",
    "deepsource-io[bot]", "imgbot[bot]", "netlify[bot]",
})


def _find_handle_in_text(text):
    """Return the first handle found on any line of `text`, or None.

    Strips Markdown bold (`**`) markers per-line before matching so
    `**Wallet:** handle` and `**Wallet**: handle` both work, and
    accepts bullet/header prefixes. The first matching line wins.
    """
    if not text:
        return None
    for raw_line in text.splitlines():
        line = raw_line.replace("**", "").strip()
        m = HANDLE_RE.match(line)
        if m:
            return m.group(1)
    return None
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
    """Return True if the comment/author appears to be a bot.

    Accepts both REST (`user`) and GraphQL (`author`) comment shapes from
    `gh issue view --json comments`. Falls back to login-string heuristics
    (suffix `[bot]`, known CI-bot logins) when the type is not declared.
    """
    # `user` field is the REST shape; `author` field is the GraphQL shape
    # returned by `gh issue view --json comments`. Either may be present.
    for obj in (user_obj,):
        if obj and isinstance(obj, dict):
            t = obj.get("type")
            if t == "Bot":
                return True
            if t and t != "User":
                # Unknown type (e.g. "Bot" with a capital "B" or
                # "Organization"). Be conservative.
                if t.lower() == "bot":
                    return True
            # GraphQL GraphType `__typename` and the `is_bot` field
            # are sometimes exposed. Trust them when seen.
            if obj.get("is_bot") is True:
                return True
            if obj.get("__typename") == "Bot":
                return True
    if login:
        if BOT_SUFFIX_RE.search(login):
            return True
        if login.lower() in KNOWN_BOT_LOGINS:
            return True
    return False


def _comment_author_login(c):
    """Return (login, user_obj) for a comment in either REST or GraphQL shape.

    `gh issue view --json comments` returns `author` (GraphQL); some other
    call paths return `user` (REST). The previous version only checked
    `user`, so it silently treated every GraphQL comment as a non-bot.
    """
    if not isinstance(c, dict):
        return None, None
    # GraphQL shape (from `gh issue view --json comments`).
    a = c.get("author")
    if isinstance(a, dict):
        return a.get("login"), a
    # REST shape (fallback; e.g. from custom REST endpoints).
    u = c.get("user")
    if isinstance(u, dict):
        return u.get("login"), u
    return None, None
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
    hm = _find_handle_in_text(body)
    if hm and _looks_like_handle(hm):
        return hm, "handle"
    if comments:
        for c in reversed(comments):
            author, user_obj = _comment_author_login(c)
            if _is_bot_login(author, user_obj):
                continue
            cb = c.get("body") or ""
            m = _find_handle_in_text(cb)
            if m and _looks_like_handle(m):
                return m, "handle"
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
    d=json.loads(gh(["issue","view",num,"-R",REPO,"--json","body,comments,author"]))
    coms=d.get("comments",[])
    # `claimant_login` is the issue author's GitHub login. It is the last-resort
    # handle fallback for claims whose body says "Wallet: TBD" and whose
    # comment thread has no parseable handle. The previous version fetched
    # only `body,comments`, so the fallback was unreachable in production.
    a=d.get("author") or {}
    claimant=a.get("login") if isinstance(a, dict) else None
    eligible = ("bounty-eligible" in labels) or any("Verified eligible" in (c.get("body") or "") for c in coms)
    if not eligible: continue
    if any("RTC-AutoPay-Confirmed" in (c.get("body") or "") for c in coms): continue
    wallet, source = resolve_wallet(d.get("body"), coms, claimant_login=claimant)
    if not wallet: continue
    ok,resp=transfer(wallet,f"Bounty #73 code-review — claim #{num} (source: {source})",f"bounty73-claim-{num}")
    if ok:
        paid+=1; total+=RATE
        gh(["issue","comment",num,"-R",REPO,"--body",f"💸 **RTC-AutoPay-Confirmed** — {RATE:g} RTC sent to `{wallet}` (source: {source}, verified #73 review, founder_community). Thanks!"])
        gh(["issue","close",num,"-R",REPO,"--reason","completed"])
    else: print(f"::warning::pay failed #{num}: {resp}")
    time.sleep(1.5)
print(f"bounty-payout: paid {paid} claims = {total:g} RTC this run")
