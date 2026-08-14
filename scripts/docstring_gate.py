#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Adjudicate docstring bounty claims.

WHY THIS EXISTS
---------------
The #73 gate only recognises CODE-REVIEW claims -- `is_review_claim()` requires
"review" in the title. Every other bounty type falls straight through it, so
docstring, blog, star and bug claims had no automated adjudication at all and
simply accumulated unpaid. On 2026-08-10 that was 19 open docstring claims,
batches 31 to 49, none of them gate-processed.

Docstring claims are unusually verifiable, so they are worth gating properly
rather than paying on assertion. A claim states a PR, a file, a function count
and a rate, and the diff should be `+N/-0` where N is that count.

WHAT IT VERIFIES (all of it, before paying anything)
  1. The cited PR is **MERGED**. An open PR is not delivered work.
  2. The PR touches the claimed file.
  3. The added lines are **actually docstrings** -- lines opening with a quote
     triple. This is the check that matters: without it "I added 40 docstrings"
     pays out for 40 lines of anything.
  4. The claimed count matches what was really added.

PAYMENT IS COMPUTED FROM THE VERIFIED COUNT, NEVER THE CLAIMED ONE. A claim
that overstates is paid the true amount rather than rejected outright -- the
usual cause is miscounting, not fraud, and rejecting honest arithmetic errors
teaches people to stop claiming.

Sets `bounty-eligible` + `docstring-verified` and posts the arithmetic, so the
existing payout runner pays it on its next pass. Never moves RTC itself.

Env: GITHUB_TOKEN, GH_REPO, ISSUE_NUMBER, RATE_PER_FUNC (0.01), MAX_RTC (25).
"""
from __future__ import annotations

import datetime
import json
import os
import re
import subprocess
import sys

REPO = os.environ.get("GH_REPO", "Scottcjn/rustchain-bounties")
NUM = os.environ.get("ISSUE_NUMBER", "")
RATE = float(os.environ.get("RATE_PER_FUNC", "0.01"))
# A single claim asking for more than this is not auto-payable. Docstring work
# is small by nature; a very large claim is either a mistake or something that
# deserves a human read.
MAX_RTC = float(os.environ.get("MAX_RTC", "25"))
# Per-contributor rolling weekly ceiling on DOCSTRING earnings specifically.
#
# A per-claim ceiling bounds nothing here: each batch is ~5 RTC, so batch 50,
# 51 and 52 all sail under it. The unbounded axis is volume, not size -- there
# is always another file to document, which is the same faucet shape as the
# ONBOARD comparison bounty that had to be closed at 98% farm share.
#
# At 0.01 RTC/function the weekly cap is a soft backstop, not the constraint:
# a docstring is a one-line comment (often on a test stub), so the per-unit price
# sits at the top of what the strongest contributors earn across ALL bounty
# types in a week (measured 2026-08-10: typical top earners 20-50 RTC/week).
# It caps a faucet without punishing anyone doing real work.
#
# This applies ONLY to docstring claims. Large one-off bounties are untouched.
MAX_RTC_PER_WEEK = float(os.environ.get("MAX_RTC_PER_WEEK", "40"))

PR_RE = re.compile(r'github\.com/([\w.-]+/[\w.-]+)/pull/(\d+)')
COUNT_RE = re.compile(
    r'(?:functions?\s+documented|documented|added\s+docstrings?\s+to)\D{0,20}?(\d{1,3})',
    re.I)
FILE_RE = re.compile(r'(?:^|\s)((?:[\w.-]+/)*[\w.-]+\.py)\b')
DOCSTRING_OPEN = re.compile(r'^\s*[rRbBuU]{0,2}("""|\'\'\')')


class GhError(RuntimeError):
    """A `gh` invocation failed. Must never be mistaken for an empty result."""


def gh(args, default=None, strict=False):
    """Run `gh` and parse JSON.

    `strict=True` raises on failure instead of returning `default`. That matters
    wherever the result feeds a MONEY decision: the earnings lookup behind the
    weekly cap returned `{}` on any CLI/auth/rate-limit failure, which
    `docstring_rtc_this_week()` then reported as 0.0 RTC already earned. A
    contributor already over the 40 RTC/week ceiling was therefore treated as
    having earned nothing, and the cap failed OPEN. A failed lookup is not an
    authoritative zero.
    """
    try:
        p = subprocess.run(["gh"] + args, capture_output=True, text=True, timeout=120)
    except Exception as e:
        if strict:
            raise GhError(f"gh {' '.join(args[:3])} failed: {e}") from e
        return default
    if p.returncode != 0:
        if strict:
            raise GhError(f"gh {' '.join(args[:3])} exited {p.returncode}: "
                          f"{(p.stderr or '').strip()[:200]}")
        return default
    try:
        return json.loads(p.stdout) if p.stdout.strip() else default
    except json.JSONDecodeError as e:
        if strict:
            raise GhError(f"gh {' '.join(args[:3])} returned unparseable JSON: {e}") from e
        return default


def gh_raw(args):
    result = subprocess.run(["gh"] + args, capture_output=True, text=True, timeout=120)
    if result.returncode != 0:
        raise GhError(f"gh {' '.join(args[:3])} failed (exit {result.returncode}): {result.stderr.strip()}")
    return result.stdout


def add_labels(*names):
    """Apply labels via REST.

    `gh issue edit --add-label` goes through GraphQL and currently fails with a
    Projects-classic deprecation error -- and it fails SILENTLY, so the gate
    would post "verified" while never marking the claim eligible, and the payout
    runner would never see it. Verified by observing an adjudicated claim come
    back with `labels: []`.
    """
    ok = True
    for n in names:
        r = subprocess.run(["gh", "api", "-X", "POST",
                            f"/repos/{REPO}/issues/{NUM}/labels", "-f", f"labels[]={n}"],
                           capture_output=True, text=True, timeout=60)
        if r.returncode != 0:
            print(f"::warning::could not apply label {n}: {r.stderr.strip()[:120]}")
            ok = False
    return ok



def docstring_rtc_this_week(author):
    """RTC this author has already been granted for docstrings in 7 days.

    Summed from this gate's own `rtc-payout-amount` markers rather than from
    the chain, so the check works from Actions with no node access and no
    admin key. Only claims the gate itself verified are counted.
    """
    since = (datetime.datetime.now(datetime.timezone.utc)
             - datetime.timedelta(days=7)).strftime("%Y-%m-%d")
    q = (f"repo:{REPO} is:issue author:{author} label:docstring-verified "
         f"created:>{since}")
    res = gh(["api", "-X", "GET", "search/issues", "-f", f"q={q}", "-f", "per_page=100"], {}, strict=True)
    total = 0.0
    for it in (res.get("items") or []):
        if str(it.get("number")) == str(NUM):
            continue          # never count the claim being adjudicated
        body = it.get("body") or ""
        # The marker lives in a gate comment, not the issue body, so fetch them.
        cs = gh(["api", f"/repos/{REPO}/issues/{it['number']}/comments?per_page=100"], [], strict=True) or []
        for c in cs:
            m = re.search(r'<!--\s*rtc-payout-amount:\s*([\d.]+)\s*-->', c.get("body") or "")
            if m:
                total += float(m.group(1))
                break
    return round(total, 2)


def is_docstring_claim(title, body):
    t = (title or "").lower()
    if "docstring" in t or re.search(r'\bdocs?\s+batch\b', t):
        return True
    return "docstring" in (body or "").lower()[:400]


def count_added_docstrings(diff: str):
    """Return (docstring_lines, total_added, files_touched).

    Counts only ADDED lines that open a docstring. Continuation lines of a
    multi-line docstring are not counted, so one docstring is one unit however
    many lines it spans.
    """
    doc = total = 0
    files = []
    in_docstring = False
    for line in diff.splitlines():
        if line.startswith("+++ b/"):
            files.append(line[6:].strip())
            in_docstring = False
            continue
        if not line.startswith("+") or line.startswith("+++"):
            continue
        total += 1
        content = line[1:]
        if in_docstring:
            if '"""' in content or "'''" in content:
                in_docstring = False
            continue
        if DOCSTRING_OPEN.match(content):
            doc += 1
            stripped = content.strip()
            # One-liner if the closing quotes appear again on the same line.
            quote = '"""' if '"""' in stripped else "'''"
            if stripped.count(quote) < 2:
                in_docstring = True
    return doc, total, files


def main():
    if not NUM:
        print("ISSUE_NUMBER not set", file=sys.stderr)
        return 1
    iss = gh(["issue", "view", NUM, "-R", REPO,
              "--json", "title,body,labels,author,state"], {})
    if not iss:
        print(f"could not read {REPO}#{NUM}", file=sys.stderr)
        return 1
    labels = {l["name"] for l in iss.get("labels", [])}
    if {"bounty-eligible", "docstring-verified", "gate-processed"} & labels:
        print("already adjudicated; skipping")
        return 0
    title, body = iss.get("title", ""), iss.get("body") or ""
    if not is_docstring_claim(title, body):
        print("not a docstring claim; leaving for another gate")
        return 0

    m = PR_RE.search(body) or PR_RE.search(title)
    if not m:
        gh(["issue", "comment", NUM, "-R", REPO, "--body",
            "🤖 Docstring gate: no pull request URL found in this claim. Add the full "
            "`https://github.com/<owner>/<repo>/pull/<n>` link and it will be re-checked."], None)
        add_labels("needs-human")
        return 0
    pr_repo, pr_num = m.group(1), m.group(2)

    pr = gh(["pr", "view", pr_num, "-R", pr_repo,
             "--json", "state,additions,deletions,files,author,mergedAt"], {})
    if not pr:
        gh(["issue", "comment", NUM, "-R", REPO, "--body",
            f"🤖 Docstring gate: could not read {pr_repo}#{pr_num}. Flagged for a human."], None)
        add_labels("needs-human")
        return 0

    if pr.get("state") != "MERGED":
        gh(["issue", "comment", NUM, "-R", REPO, "--body",
            f"🤖 Docstring gate: {pr_repo}#{pr_num} is **{pr.get('state','OPEN').lower()}**, not merged.\n\n"
            f"Docstring bounties pay on merge, because until then the documentation is not in the "
            f"codebase. This claim is not closed — it will be re-checked automatically once the PR "
            f"lands, and you do not need to re-file it."], None)
        add_labels("awaiting-merge")
        print(f"{pr_repo}#{pr_num} not merged ({pr.get('state')}); waiting")
        return 0

    diff = gh_raw(["pr", "diff", pr_num, "-R", pr_repo])
    doc_count, total_added, files = count_added_docstrings(diff)
    claimed = None
    cm = COUNT_RE.search(body) or COUNT_RE.search(title)
    if cm:
        claimed = int(cm.group(1))

    amount = round(doc_count * RATE, 2)
    if doc_count == 0:
        gh(["issue", "comment", NUM, "-R", REPO, "--body",
            f"🤖 Docstring gate: {pr_repo}#{pr_num} is merged, but no added lines in it open a "
            f"docstring ({total_added} lines added in total). If the work is real and the gate has "
            f"misread it, say so here and a human will look."], None)
        add_labels("needs-human")
        return 0

    author = (iss.get("author") or {}).get("login", "")
    try:
        already = docstring_rtc_this_week(author) if author else 0.0
    except GhError as e:
        # Cannot establish prior earnings => cannot honour the cap => do not pay.
        # Failing closed is the whole point; the previous behaviour approved the
        # claim as though the contributor had earned nothing this week.
        gh(["issue", "comment", NUM, "-R", REPO, "--body",
            f"🤖 Docstring gate: verified **{doc_count} docstrings** in {pr_repo}#{pr_num}, but the "
            f"weekly-earnings lookup failed, so the {MAX_RTC_PER_WEEK:g} RTC/week cap cannot be "
            f"checked right now.\n\nHolding rather than approving — a failed lookup is not proof "
            f"that you have earned nothing. This retries automatically on the next sweep; you do "
            f"not need to do anything."], None)
        add_labels("needs-human")
        print(f"::error::earnings lookup failed, refusing to approve: {e}")
        return 0
    if already + amount > MAX_RTC_PER_WEEK:
        add_labels("weekly-cap-reached")
        gh(["issue", "comment", NUM, "-R", REPO, "--body",
            f"🤖 Docstring gate: verified **{doc_count} docstrings** in {pr_repo}#{pr_num} "
            f"(**{amount} RTC**), but this would take you to "
            f"**{round(already + amount, 2)} RTC** of docstring earnings in a rolling 7 days, "
            f"over the **{MAX_RTC_PER_WEEK:g} RTC/week** ceiling for this bounty type.\n\n"
            f"**The work is accepted and this claim is not closed.** It becomes payable again as "
            f"soon as the rolling window clears, and it will be picked up automatically. You do "
            f"not need to re-file it or do anything.\n\n"
            f"Why the ceiling exists: documentation bounties are unbounded by nature, since there "
            f"is always another file. The cap keeps one bounty type from consuming the pool, and "
            f"40 RTC/week is roughly the top of what any contributor earns across all bounty types. "
            f"It is not a judgement on the quality of your work, which has been consistently fine.\n\n"
            f"If you want higher-value work, the bounty board has open items at 7 to 35 RTC each "
            f"that are not rate-limited."], None)
        print(f"weekly cap: {author} at {already} + {amount} > {MAX_RTC_PER_WEEK}")
        return 0

    if amount > MAX_RTC:
        gh(["issue", "comment", NUM, "-R", REPO, "--body",
            f"🤖 Docstring gate: verified **{doc_count} docstrings** in {pr_repo}#{pr_num}, which at "
            f"{RATE} RTC each comes to {amount} RTC. That is above the {MAX_RTC} RTC auto-pay ceiling, "
            f"so it needs a human to release it. Nothing is wrong with the claim."], None)
        add_labels("needs-human")
        return 0

    note = ""
    if claimed is not None and claimed != doc_count:
        note = (f"\n\nYou claimed **{claimed}**; the diff contains **{doc_count}**. "
                f"Paying the verified number. If you think the gate has miscounted, say so and a "
                f"human will check — miscounts are usually arithmetic, not bad faith.")

    verified_comment = (
        f"✅ 🤖 **Docstring gate: verified.**\n\n"
        f"- PR {pr_repo}#{pr_num} is **merged**\n"
        f"- Files: `{', '.join(files[:4]) or 'n/a'}`\n"
        f"- Added lines opening a docstring: **{doc_count}** (of {total_added} added lines)\n"
        f"- Rate {RATE} RTC each → **{amount} RTC**{note}\n\n"
        f"<!-- rtc-payout-amount: {amount} -->\n"
        f"Queued for payout. The balance moves after the standard confirmation window, not on this "
        f"comment."
    )
    gh_raw(["issue", "comment", NUM, "-R", REPO, "--body", verified_comment])
    if not add_labels("bounty-eligible", "docstring-verified"):
        print("::error::verified amount marker posted, but labels were not applied")
        return 1
    print(f"verified {doc_count} docstrings -> {amount} RTC on {REPO}#{NUM}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
