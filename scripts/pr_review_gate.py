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
    m=re.search(r'#(\d+)', title+body)
    return m and m.group(1)

def is_substantive_review(review):
    body = review.get('body', '')
    return len(body.split()) > 10 and not body.startswith(('Thanks', 'Great', 'Excellent', 'Good'))

def get_first_substantive_review(reviews):
    substantive_reviews = [review for review in reviews if is_substantive_review(review)]
    return substantive_reviews and substantive_reviews[0] or None

def main():
    # ... (rest of the code remains the same)

    # Get the reviews for the PR
    reviews = api(f'/repos/{TARGET}/pulls/{pr_ref}/reviews')

    # Get the first substantive review
    first_substantive_review = get_first_substantive_review(reviews)

    # ... (rest of the code remains the same)

if __name__ == '__main__':
    main()