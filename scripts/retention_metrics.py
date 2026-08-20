#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Measure contributor retention, and snapshot it so history survives.

WHY THIS EXISTS
---------------
On 2026-08-07 the bounty payout path was found broken in three places at once
(gate adjudicated a claim only at filing; payout skipped unlabelled claims;
payout could not see anything outside the 400 newest issues). Contributors
filed, heard nothing for a median of 82 days, and left: 30-day retention was
2% / 5% / 0% for the May / June / July cohorts.

Those fixes landed the same day, so NO post-fix cohort exists yet. The honest
next step is to measure whether fixing the plumbing alone moves retention
before layering another mechanism on top. This script is that measurement.

TWO THINGS IT GETS RIGHT THAT AD-HOC ANALYSIS DID NOT
-----------------------------------------------------
1. **Claims are not the metric; distinct humans are.** In one July week, 708
   claims came from 4 people. Any chart of claim volume shows a healthy repo
   and is a lie. Everything here is keyed on distinct authors.

2. **Farm accounts are reported separately, never silently mixed in.** ~73% of
   claim volume came from ~21 accounts. A blended retention number is dominated
   by bots that never churn, which flatters the figure precisely when it should
   alarm you. `--min-claims-for-farm` marks heavy accounts; totals are always
   emitted both ways.

Snapshots append to data/retention.jsonl. That matters: `gh issue list` caps
out (4,000 in practice), so early weeks fall out of reach as the tracker grows.
A snapshot taken today is the only way to still have today's numbers next year.

Usage:
  python3 scripts/retention_metrics.py                # print report
  python3 scripts/retention_metrics.py --snapshot     # also append to jsonl
"""
from __future__ import annotations

import argparse
import collections
import datetime
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = os.environ.get("GH_REPO", "Scottcjn/rustchain-bounties")
DATA = Path(__file__).resolve().parent.parent / "data" / "retention.jsonl"
# Accounts that post bounties rather than claim them. Counting them as
# "contributors" would invent retention that does not exist.
MAINTAINERS = {"scottcjn", "sophiaeagent-beep", "github-actions[bot]"}


def fetch(limit: int):
    out = subprocess.run(
        ["gh", "issue", "list", "-R", REPO, "--state", "all", "--limit", str(limit),
         "--json", "number,author,createdAt"],
        capture_output=True, text=True, timeout=600,
    ).stdout
    try:
        issues = json.loads(out or "[]")
    except json.JSONDecodeError:
        print("::error::could not parse issue list", file=sys.stderr)
        return []
    rows = []
    for i in issues:
        a = (i.get("author") or {}).get("login")
        if not a or a.lower() in MAINTAINERS:
            continue
        rows.append((i["createdAt"][:10], a))
    rows.sort()
    return rows


def week_of(day: str) -> str:
    d = datetime.date.fromisoformat(day)
    return (d - datetime.timedelta(days=d.weekday())).isoformat()


def analyse(rows, farm_threshold: int, today: datetime.date):
    per = collections.Counter(a for _, a in rows)
    farms = {a for a, n in per.items() if n >= farm_threshold}

    first, last, count = {}, {}, collections.Counter()
    for day, a in rows:
        first.setdefault(a, day)
        last[a] = day
        count[a] += 1

    # Weekly distinct humans, split new vs returning.
    seen, weeks = set(), collections.OrderedDict()
    for day, a in rows:
        if a in farms:
            continue
        w = weeks.setdefault(week_of(day), {"claims": 0, "people": set(), "new": set()})
        w["claims"] += 1
        w["people"].add(a)
        if a not in seen:
            w["new"].add(a)
            seen.add(a)

    weekly = [
        {"week": w, "claims": e["claims"], "people": len(e["people"]),
         "new": len(e["new"]), "returning": len(e["people"]) - len(e["new"])}
        for w, e in weeks.items()
    ]

    # Cohort retention. A cohort is only meaningful once every member has had a
    # full 30 days to come back, so young cohorts are marked immature rather
    # than reported as 0% -- an immature cohort looks like catastrophic churn.
    cohorts = collections.defaultdict(list)
    for a in first:
        if a in farms:
            continue
        cohorts[first[a][:7]].append(a)

    out_cohorts = []
    for m in sorted(cohorts):
        ppl = cohorts[m]
        mature = [a for a in ppl
                  if (today - datetime.date.fromisoformat(first[a])).days >= 30]
        retained = [a for a in mature
                    if (datetime.date.fromisoformat(last[a])
                        - datetime.date.fromisoformat(first[a])).days > 30]
        one_shot = sum(1 for a in ppl if count[a] == 1)
        out_cohorts.append({
            "cohort": m,
            "people": len(ppl),
            "one_and_done": one_shot,
            "mature": len(mature),
            "retained_30d": len(retained),
            "retention_pct": (round(100 * len(retained) / len(mature), 1)
                              if mature else None),
        })

    return {
        "generated": today.isoformat(),
        "window_first_claim": rows[0][0] if rows else None,
        "window_last_claim": rows[-1][0] if rows else None,
        "truncated": None,  # set by caller
        "farm_threshold": farm_threshold,
        "farm_accounts": len(farms),
        "farm_claims": sum(per[a] for a in farms),
        "human_accounts": len(per) - len(farms),
        "human_claims": sum(per[a] for a in per if a not in farms),
        "weekly": weekly,
        "cohorts": out_cohorts,
    }


def report(r):
    L = []
    L.append(f"# Contributor retention — {r['generated']}")
    L.append(f"\nWindow: {r['window_first_claim']} .. {r['window_last_claim']}")
    if r["truncated"]:
        L.append("\n> **Window truncated by the API cap.** Weeks before the window "
                 "start are not visible here; earlier snapshots in data/retention.jsonl "
                 "hold them.")
    L.append(f"\nHumans: **{r['human_accounts']}** accounts / {r['human_claims']} claims")
    L.append(f"Farms (>= {r['farm_threshold']} claims): **{r['farm_accounts']}** accounts "
             f"/ {r['farm_claims']} claims — excluded from every figure below")
    L.append("\n## Weekly distinct humans\n")
    L.append("| week | claims | people | new | returning |")
    L.append("|---|---:|---:|---:|---:|")
    for w in r["weekly"][-16:]:
        L.append(f"| {w['week']} | {w['claims']} | {w['people']} | {w['new']} | {w['returning']} |")
    L.append("\n## 30-day retention by cohort\n")
    L.append("| cohort | people | 1-and-done | mature | retained | retention |")
    L.append("|---|---:|---:|---:|---:|---:|")
    for c in r["cohorts"][-8:]:
        pct = "immature" if c["retention_pct"] is None else f"{c['retention_pct']}%"
        L.append(f"| {c['cohort']} | {c['people']} | {c['one_and_done']} | "
                 f"{c['mature']} | {c['retained_30d']} | {pct} |")
    return "\n".join(L)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=4000)
    ap.add_argument("--min-claims-for-farm", type=int, default=21,
                    help="accounts at/above this claim count are treated as farms")
    ap.add_argument("--snapshot", action="store_true",
                    help="append the result to data/retention.jsonl")
    ap.add_argument("--today", default=None, help="override today (YYYY-MM-DD), for tests")
    a = ap.parse_args()

    rows = fetch(a.limit)
    if not rows:
        print("no claims found", file=sys.stderr)
        return 1
    today = (datetime.date.fromisoformat(a.today) if a.today
             else datetime.datetime.now(datetime.timezone.utc).date())
    r = analyse(rows, a.min_claims_for_farm, today)
    # If we came back with exactly the cap, the oldest data was cut off.
    r["truncated"] = len(rows) >= a.limit
    print(report(r))

    if a.snapshot:
        DATA.parent.mkdir(parents=True, exist_ok=True)
        with DATA.open("a", encoding="utf-8") as f:
            f.write(json.dumps(r, separators=(",", ":")) + "\n")
        print(f"\nsnapshot appended -> {DATA}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
