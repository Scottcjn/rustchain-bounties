#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Org-wide maintenance triage: what is waiting on a maintainer, right now.

WHY
---
Two things made work invisible here.

1. **Two maintainer identities.** Activity surfaces under `sophiaeagent-beep`
   as well as `Scottcjn`. Anything that treats only one of them as "us" either
   miscounts a bot as a contributor or, worse, reads a bot's own reply as
   "someone answered this" and drops the thread.

2. **Nobody was watching the PR side.** On 2026-08-07, 287 of 412 open PRs
   across the org had zero comments. That is the same failure that collapsed
   bounty retention on the issue side: contributors act, hear nothing, leave.

This produces one ranked list of threads awaiting a maintainer, so the answer
to "what needs me today" is a command rather than an archaeology session.

BUCKETS (most urgent first)
  BALL_IN_OUR_COURT  a non-maintainer spoke last; we have not replied since
  NEVER_ANSWERED     open, external author, zero comments from anyone
  MOVED_RECENTLY     touched in the window but already has a maintainer reply

Ordering favours the longest wait, because the cost of silence compounds: the
issue-side median silent claim had been sitting 82 days.

Usage:
  python3 scripts/maintenance_sweep.py                 # PRs, all repos
  python3 scripts/maintenance_sweep.py --include-issues
  python3 scripts/maintenance_sweep.py --repo bottube --limit 50
"""
from __future__ import annotations

import argparse
import collections
import datetime
import json
import subprocess
import sys

ORG = "Scottcjn"
# Both maintainer identities, plus automation. Anything here speaking does NOT
# clear a thread from "waiting on us", and anything here authoring does not
# make a thread an external contribution.
MAINTAINERS = {"scottcjn", "sophiaeagent-beep"}
BOT_SUFFIX = "[bot]"
KNOWN_BOTS = {"github-actions", "dependabot", "renovate", "codecov", "copilot",
              "github-actions[bot]", "dependabot[bot]"}


def is_maintainer(login: str) -> bool:
    if not login:
        return False
    l = login.lower()
    return l in MAINTAINERS or l in KNOWN_BOTS or l.endswith(BOT_SUFFIX)


def gh_json(args, default):
    try:
        p = subprocess.run(["gh"] + args, capture_output=True, text=True, timeout=180)
        return json.loads(p.stdout or "null") or default
    except Exception as e:
        print(f"::warning::gh call failed: {e}", file=sys.stderr)
        return default


def search(q, limit):
    """Paginate the search API (it caps a single response at 100)."""
    out, page = [], 1
    while len(out) < limit:
        chunk = gh_json(["api", "-X", "GET", "search/issues",
                         "-f", f"q={q}", "-f", "per_page=100", "-f", f"page={page}"], {})
        items = chunk.get("items") or []
        if not items:
            break
        out.extend(items)
        if len(items) < 100 or page >= 10:   # API hard-stops at 1000 results
            break
        page += 1
    return out[:limit]


def _pr_path(item):
    """Return 'owner/repo/pulls/N' for a PR search result, else None."""
    if "pull_request" not in item:
        return None
    repo = item.get("repository_url", "").split("/repos/")[-1]
    return f"{repo}/pulls/{item['number']}" if repo else None


def _all_activity(item):
    """Every human utterance on a thread, oldest first.

    A PR carries THREE separate comment streams and the REST API keeps them
    apart:
      - issue comments      /issues/N/comments      (the main thread)
      - review comments     /pulls/N/comments       (inline, on a diff line)
      - reviews             /pulls/N/reviews        (approve / request-changes)

    Reading only the first is how a maintainer question gets lost. That is not
    hypothetical: an IBM LLVM reviewer asked a blocking question as an INLINE
    comment, it was never answered, and four months later he had to write
    "I think you might of missed my question/comment from above." A sweep that
    reads only issue comments would have called that thread answered.
    """
    events = []
    for c in gh_json(["api", item.get("comments_url", "") + "?per_page=100"], []) or []:
        events.append(((c.get("created_at") or ""), (c.get("user") or {}).get("login", "")))

    p = _pr_path(item)
    if p:
        for c in gh_json(["api", f"/repos/{p}/comments?per_page=100"], []) or []:
            events.append(((c.get("created_at") or ""), (c.get("user") or {}).get("login", "")))
        for r in gh_json(["api", f"/repos/{p}/reviews?per_page=100"], []) or []:
            # A review with no body still signals attention (APPROVED etc).
            events.append(((r.get("submitted_at") or ""), (r.get("user") or {}).get("login", "")))

    return sorted([e for e in events if e[0] and e[1]])


def classify(item, token_repo_cache):
    """Return (bucket, last_speaker, days_waiting)."""
    author = (item.get("user") or {}).get("login", "")
    created = item["created_at"][:10]

    events = _all_activity(item)
    if not events:
        if is_maintainer(author):
            return None, author, None          # our own untouched PR; not owed a reply
        return "NEVER_ANSWERED", author, created

    when, speaker = events[-1]
    when = when[:10]
    if is_maintainer(speaker):
        return "MOVED_RECENTLY", speaker, when
    return "BALL_IN_OUR_COURT", speaker, when


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=None, help="limit to one repo name")
    ap.add_argument("--limit", type=int, default=250)
    ap.add_argument("--include-issues", action="store_true")
    ap.add_argument("--today", default=None)
    a = ap.parse_args()

    today = (datetime.date.fromisoformat(a.today) if a.today
             else datetime.datetime.now(datetime.timezone.utc).date())
    scope = f"repo:{ORG}/{a.repo}" if a.repo else f"org:{ORG}"
    kinds = ["pr"] + (["issue"] if a.include_issues else [])

    rows = []
    for kind in kinds:
        items = search(f"{scope} is:{kind} is:open", a.limit)
        print(f"scanned {len(items)} open {kind}s", file=sys.stderr)
        for it in items:
            bucket, who, when = classify(it, {})
            if not bucket:
                continue
            days = (today - datetime.date.fromisoformat(when)).days if when else 0
            repo = it["repository_url"].rsplit("/", 1)[-1]
            rows.append({"bucket": bucket, "kind": kind, "repo": repo,
                         "number": it["number"], "title": it["title"][:70],
                         "author": (it.get("user") or {}).get("login", ""),
                         "last_speaker": who, "days": days,
                         "url": it["html_url"]})

    order = {"BALL_IN_OUR_COURT": 0, "NEVER_ANSWERED": 1, "MOVED_RECENTLY": 2}
    rows.sort(key=lambda r: (order[r["bucket"]], -r["days"]))

    counts = collections.Counter(r["bucket"] for r in rows)
    print(f"\n# Maintenance sweep — {today}\n")
    print(f"Maintainer identities treated as 'us': {', '.join(sorted(MAINTAINERS))} (+ bots)\n")
    for b in ("BALL_IN_OUR_COURT", "NEVER_ANSWERED", "MOVED_RECENTLY"):
        print(f"- **{b}**: {counts.get(b, 0)}")

    for b in ("BALL_IN_OUR_COURT", "NEVER_ANSWERED"):
        sel = [r for r in rows if r["bucket"] == b]
        if not sel:
            continue
        print(f"\n## {b} ({len(sel)})\n")
        print("| waiting | repo | # | author | last spoke | title |")
        print("|---:|---|---:|---|---|---|")
        for r in sel[:40]:
            print(f"| {r['days']}d | {r['repo']} | [{r['number']}]({r['url']}) | "
                  f"@{r['author']} | @{r['last_speaker']} | {r['title']} |")
        if len(sel) > 40:
            print(f"\n_{len(sel) - 40} more not shown._")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
