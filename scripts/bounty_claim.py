#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Let a contributor mark a bounty as taken, so two people don't build the same thing.

WHY THIS EXISTS
---------------
Bounty #16250 was submitted five times. Four of those PRs created the identical
file, so only the first could merge and three people's work was closed as a
duplicate through no fault of their own. The bounty had sat open with nothing
indicating anyone was already on it, so five people each reasonably concluded it
was free.

That is a failure of the board, not of the contributors. A bounty with no
claimed state makes parallel effort invisible until the pull requests collide,
and the cost lands entirely on whoever was slowest.

HOW IT WORKS
  - A contributor comments `/claim` (or "claiming this") on a bounty issue.
  - The issue gets a `claimed` label and a comment naming who holds it and when
    it expires.
  - A second person trying to claim it is told who has it and when it frees,
    BEFORE they spend a week on it. That is the entire point.
  - Claims expire (default 7 days) and are released automatically, so a bounty
    cannot be squatted. Re-commenting `/claim` renews.

DELIBERATELY NOT ENFORCED
A claim is a courtesy signal, not a lock. Someone who submits without claiming
is still paid under first-in-time — the rule does not change. This exists to
stop wasted work, not to create a permission system, and a maintainer can
always release a claim by removing the label.

THE ONE THING THAT IS ENFORCED: `Live-URL:` on distribution bounties
An issue carrying the `distribution` label pays for something that exists OFF
GitHub (a post, a video, an article). The 2026-08-28 audit found ~45 such
claims that never left GitHub and zero X/YouTube/Hackaday deliveries ever,
because nothing here asked for one. So on those issues a claim must carry a
line `Live-URL: <url>` on an allowlisted host (see scripts/live_url.py). If it
is missing or off-list the bot explains the field, warmly, and does NOT record
the claim. Every other issue behaves exactly as before.

Env: GITHUB_TOKEN, GH_REPO, ISSUE_NUMBER, COMMENT_BODY, COMMENT_AUTHOR,
     CLAIM_DAYS (7), MODE (claim|sweep).
"""
from __future__ import annotations

import datetime
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from live_url import ALLOWED_HOSTS_HUMAN, find_live_url  # noqa: E402

REPO = os.environ.get("GH_REPO", "Scottcjn/rustchain-bounties")
CLAIM_DAYS = int(os.environ.get("CLAIM_DAYS", "7"))
LABEL = "claimed"
DISTRIBUTION_LABEL = "distribution"
MARKER = "<!-- bounty-claim -->"

CLAIM_RE = re.compile(
    r'(^|\s)(/claim\b|claiming this|i(?:\'| a)?m taking this|taking this one|i will take this)',
    re.I)
# "/claim" inside a quote block is someone quoting the instructions, not claiming.
QUOTE_RE = re.compile(r'^\s*>')


def gh(args, default=None):
    try:
        p = subprocess.run(["gh"] + args, capture_output=True, text=True, timeout=90)
        return json.loads(p.stdout) if p.stdout.strip() else default
    except Exception:
        return default


def gh_ok(args):
    result = subprocess.run(["gh"] + args, capture_output=True, text=True, timeout=90)
    if result.returncode != 0:
        print(f"[WARN] gh {' '.join(args[:3])} failed (exit {result.returncode}): {result.stderr.strip()}", file=sys.stderr)
        return False
    return True


def add_label(num, name):
    # REST, not `gh issue edit`: that path goes through GraphQL and currently
    # fails on a Projects-classic deprecation WITHOUT a non-zero exit, which
    # would leave a claim silently unrecorded.
    return gh_ok(["api", "-X", "POST", f"/repos/{REPO}/issues/{num}/labels",
                  "-f", f"labels[]={name}"])


def remove_label(num, name):
    return gh_ok(["api", "-X", "DELETE", f"/repos/{REPO}/issues/{num}/labels/{name}"])


def is_claim_request(body: str) -> bool:
    if not body:
        return False
    lines = [l for l in body.splitlines() if not QUOTE_RE.match(l)]
    return bool(CLAIM_RE.search("\n".join(lines)))


def active_claim(num):
    """Return (holder, expiry_date) for the newest unexpired claim, else None."""
    comments = gh(["api", f"/repos/{REPO}/issues/{num}/comments?per_page=100"], []) or []
    today = datetime.date.today()
    newest = None
    for c in comments:
        b = c.get("body") or ""
        if MARKER not in b:
            continue
        m = re.search(r'holder:\s*@?([A-Za-z0-9_-]+).*?expires:\s*(\d{4}-\d{2}-\d{2})', b, re.S)
        if m:
            newest = (m.group(1), datetime.date.fromisoformat(m.group(2)))
    if not newest:
        return None
    return newest if newest[1] >= today else None


def live_url_gate(num, author, body, labels) -> bool:
    """Return True if the claim may proceed.

    Only bites on `distribution`-labelled issues. On a missing or off-list
    Live-URL it posts one explanatory comment and returns False; the caller
    must then NOT add the `claimed` label.
    """
    if DISTRIBUTION_LABEL not in labels:
        return True
    url, platform, reason = find_live_url(body)
    if reason == "ok":
        print(f"live-url ok: {platform} {url}")
        return True
    if reason == "missing":
        lead = ("this bounty pays for something that lives **off GitHub** — a post, a "
                "video, an article — so a claim here needs one extra line that tells us "
                "where it is.")
    else:
        lead = (f"thank you for including a link — but `{url}` is not on a host we can "
                "verify, so I could not record the claim yet.")
    gh(["issue", "comment", str(num), "-R", REPO, "--body",
        f"@{author} — {lead} Please re-comment with a line like "
        f"`Live-URL: https://…` pointing at the published piece itself (not a draft, "
        f"gist, or GitHub Pages copy). Accepted hosts: {ALLOWED_HOSTS_HUMAN}. The "
        f"verifier bot fetches that URL on its next pass and reports what it finds, "
        f"which is what unlocks review. If you have not published yet, that is "
        f"completely fine — post first, then claim with the link, and it will go "
        f"through. Nothing is lost by the wait; this only exists because earlier "
        f"claims here said \"posting now, will update\" and never could."], None)
    print(f"live-url {reason}; claim not recorded")
    return False


def do_claim(num, author, body=""):
    iss = gh(["issue", "view", str(num), "-R", REPO, "--json", "title,state,labels"], {})
    if not iss or iss.get("state") != "OPEN":
        print("issue not open; ignoring")
        return 0
    title = iss.get("title", "")
    if "BOUNTY" not in title.upper() and "bounty" not in title.lower():
        print("not a bounty issue; ignoring")
        return 0

    labels = {(lab.get("name") or "").lower() for lab in (iss.get("labels") or [])
              if isinstance(lab, dict)}
    if not live_url_gate(num, author, body, labels):
        return 0

    held = active_claim(num)
    expiry = datetime.date.today() + datetime.timedelta(days=CLAIM_DAYS)

    if held and held[0].lower() != (author or "").lower():
        gh(["issue", "comment", str(num), "-R", REPO, "--body",
            f"@{author} — this one is already claimed by **@{held[0]}** until "
            f"**{held[1].isoformat()}**.\n\n"
            f"Telling you now so you do not spend a week on something that is already "
            f"being built. Bounty #16250 was submitted five times because nothing showed "
            f"it was taken, and three people had their work closed as duplicates.\n\n"
            f"If @{held[0]} has not delivered by {held[1].isoformat()} the claim lapses "
            f"automatically and you can take it. You are also still free to submit anyway — "
            f"claims are a courtesy, not a lock, and payment is still first-in-time. But "
            f"now you are choosing that with your eyes open."], None)
        print(f"already claimed by {held[0]}")
        return 0

    add_label(num, LABEL)
    renew = " (renewed)" if held else ""
    gh(["issue", "comment", str(num), "-R", REPO, "--body",
        f"{MARKER}\n🔒 **Claimed{renew}.** holder: @{author} · expires: {expiry.isoformat()}\n\n"
        f"This bounty now shows as taken so nobody else duplicates your work. The claim "
        f"lapses automatically on **{expiry.isoformat()}** — comment `/claim` again to renew "
        f"if you need longer, no explanation needed.\n\n"
        f"A claim is a courtesy signal, not a lock: it does not reserve payment, and anyone "
        f"who submits first is still paid first. It exists so people can see what is already "
        f"being worked on."], None)
    print(f"claimed #{num} by {author} until {expiry}")
    return 0


def do_sweep():
    """Release expired claims so a bounty cannot be squatted."""
    res = gh(["api", "-X", "GET", "search/issues",
              "-f", f"q=repo:{REPO} is:issue is:open label:{LABEL}",
              "-f", "per_page=100"], {})
    items = (res or {}).get("items") or []
    released = 0
    for it in items:
        num = it["number"]
        if active_claim(num):
            continue
        remove_label(num, LABEL)
        gh(["issue", "comment", str(num), "-R", REPO, "--body",
            "🔓 **Claim lapsed — this bounty is open again.**\n\n"
            "The previous claim expired without a submission. No hard feelings and no "
            "penalty: claims lapse on a timer precisely so a bounty cannot sit reserved "
            "indefinitely.\n\n"
            "Anyone can take it now by commenting `/claim`."], None)
        released += 1
        print(f"released #{num}")
    print(f"sweep: {released} claim(s) released of {len(items)} labelled")
    return 0


def main():
    mode = os.environ.get("MODE", "claim")
    if mode == "sweep":
        return do_sweep()
    num = os.environ.get("ISSUE_NUMBER", "")
    body = os.environ.get("COMMENT_BODY", "")
    author = os.environ.get("COMMENT_AUTHOR", "")
    if not num:
        print("ISSUE_NUMBER not set", file=sys.stderr)
        return 1
    if not is_claim_request(body):
        print("comment is not a claim request; ignoring")
        return 0
    return do_claim(num, author, body)


if __name__ == "__main__":
    raise SystemExit(main())
