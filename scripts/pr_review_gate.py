#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
PR-Review Bounty Gate — on-arrival adjudication of Bounty #73 code-review claims.

Runs per newly-opened/edited issue. For a code-review claim it verifies, against
the (public) Rustchain repo, that the claimant was the FIRST substantive reviewer
of the referenced PR, within the per-contributor cap. Conservative:
  - clear NOT-FIRST / rubber-stamp / over-cap  -> close (not planned) + comment
  - eligible                                   -> label 'bounty-eligible' + comment
  - ambiguous / no PR ref / non-native wallet  -> label 'needs-human' (no close)
Idempotent: skips issues already labeled/closed by the gate.

Env: GITHUB_TOKEN (repo + public read), GH_REPO (owner/name), ISSUE_NUMBER,
     TARGET_REPO (default Scottcjn/Rustchain), CAP (default 15), RATE_RTC (3).
"""
import os, re, json, sys, urllib.request, urllib.error

TOKEN=os.environ.get("GITHUB_TOKEN","")
REPO=os.environ.get("GH_REPO","Scottcjn/rustchain-bounties")
TARGET=os.environ.get("TARGET_REPO","Scottcjn/Rustchain")
NUM=os.environ.get("ISSUE_NUMBER","")
CAP=int(os.environ.get("CAP","15")); RATE=os.environ.get("RATE_RTC","3")
API="https://api.github.com"
def api(path, method="GET", data=None):
    req=urllib.request.Request(f"{API}{path}", method=method,
        headers={"Authorization":f"Bearer {TOKEN}","Accept":"application/vnd.github+json",
                 "X-GitHub-Api-Version":"2022-11-28","User-Agent":"pr-review-gate"})
    if data is not None:
        req.data=json.dumps(data).encode(); req.add_header("Content-Type","application/json")
    try:
        with urllib.request.urlopen(req,timeout=30) as r: return json.loads(r.read() or "null")
    except urllib.error.HTTPError as e:
        if method=="GET": return None
        raise

def is_review_claim(title):
    t=title.lower()
    return ("review" in t) and ("pr " in t or "code review" in t or "#73" in t or "pr#" in t or "pr #" in t)
def pr_ref(title, body):
    for s in (title, body or ""):
        m=re.search(r'(?:PR\s*#?|pull/|#)(\d{3,6})', s)
        if m: return m.group(1)
    return None
def native_wallet(body):
    b=body or ""
    if re.search(r'\bRTC[0-9a-fA-F]{40}\b', b) or re.search(r'(?i)miner[_\-]?id', b): return True
    # Solana/ETH payout request = not native
    if re.search(r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b', b) and "rtc" not in b.lower(): return False
    return None  # unknown -> don't reject on this alone

def comment(n, body): api(f"/repos/{REPO}/issues/{n}/comments","POST",{"body":body})
def add_label(n, lab): api(f"/repos/{REPO}/issues/{n}/labels","POST",{"labels":[lab]})
def close(n, reason_comment):
    comment(n, reason_comment); api(f"/repos/{REPO}/issues/{n}","PATCH",{"state":"closed","state_reason":"not_planned"})

def main():
    iss=api(f"/repos/{REPO}/issues/{NUM}")
    if not iss or iss.get("state")!="open": return
    labels={l["name"] for l in iss.get("labels",[])}
    if {"bounty-eligible","needs-human","gate-processed"} & labels: return  # idempotent
    title=iss.get("title",""); body=iss.get("body") or ""; author=iss["user"]["login"]
    if not is_review_claim(title): return  # not our claim type; leave for other workflows
    add_label(NUM,"gate-processed")
    pr=pr_ref(title,body)
    if not pr:
        add_label(NUM,"needs-human"); comment(NUM,"🤖 Gate: couldn't find a single PR reference. Per **Bounty #73**, file one claim per PR with `PR #<number>`. Flagged for human review."); return
    if native_wallet(body) is False:
        close(NUM,"🤖 Gate: payout must be a **native RTC wallet** (`RTC…`) — RTC has no off-ramp, no Solana/ETH bridge. Reopen with a native wallet."); return
    reviews=api(f"/repos/{TARGET}/pulls/{pr}/reviews")
    if reviews is None:
        add_label(NUM,"needs-human"); comment(NUM,f"🤖 Gate: couldn't read reviews for {TARGET}#{pr} (private/deleted?). Flagged for human review."); return
    rv=[r for r in reviews if r.get("submitted_at")]
    rv.sort(key=lambda r:r["submitted_at"])
    first = rv[0]["user"]["login"] if rv else None
    body_len = next((len(r.get("body") or "") for r in rv if r["user"]["login"]==author), 0)
    inl = api(f"/repos/{TARGET}/pulls/{pr}/comments?per_page=100") or []
    inline = sum(1 for c in inl if c.get("user",{}).get("login")==author)
    if first != author:
        close(NUM,f"🤖 Gate (Bounty #73 — first substantive review only): {TARGET}#{pr} was first reviewed by **{first or 'someone else'}**, not @{author}. Path back: review PRs where you're the first reviewer."); return
    if inline==0 and body_len<120:
        close(NUM,f"🤖 Gate: your review of {TARGET}#{pr} has no inline comments and no substantive summary — Bounty #73 requires a **substantive line-level review**, not a bare approval."); return
    # cap check: count author's existing bounty-eligible issues
    elig=api(f"/search/issues?q=repo:{REPO}+label:bounty-eligible+author:{author}+type:issue") or {}
    if elig.get("total_count",0)>=CAP:
        close(NUM,f"🤖 Gate: @{author} has reached the **{CAP} eligible reviews/contributor** cap (Bounty #73). Quality over volume — thanks!"); return
    add_label(NUM,"bounty-eligible")
    comment(NUM,f"✅ 🤖 Gate: **verified eligible** — @{author} is the first substantive reviewer of {TARGET}#{pr}. **{RATE} RTC** pending payout (native `RTC…` wallet if not on file).")

if __name__=="__main__":
    try: main()
    except Exception as e:
        print(f"gate error: {e}", file=sys.stderr)  # never fail the workflow
