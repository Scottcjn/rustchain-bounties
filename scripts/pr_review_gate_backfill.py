#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Sweep un-adjudicated PR-review claims through the #73 gate.

WHY THIS EXISTS
---------------
`pr-review-gate.yml` fires on `issues: [opened, edited]`. That adjudicates a
claim exactly once, at the instant it is filed, and never again. Any claim
that missed that instant -- filed while the gate was failing, filed before the
gate existed, or edited in a way that did not re-trigger -- was invisible
forever. It sat open with no label, no verdict, and no reply.

That single trigger config produced a backlog of 104 silent claims with a
median age of 82 days, across 44 real contributors. `bounty_payout.py` only
pays claims the gate has labelled, so silence there meant no payout, which
meant contributors stopped showing up.

This sweep is the safety net: it re-drives the same gate over anything that
was never adjudicated, so a missed webhook costs a few hours instead of
forever.

SAFETY
------
  - The gate itself is idempotent: it skips issues it has already labelled or
    closed. Re-running is harmless.
  - Bounded per run (MAX_PER_RUN, default 60) so one sweep cannot exhaust the
    API budget. When the bound truncates the queue, the remainder is REPORTED,
    not silently dropped -- a silent cap reads as "everything is handled".
  - Only touches issues whose title is a review claim, per the gate's own
    `is_review_claim`, so it cannot wander into unrelated issues.

Env: GITHUB_TOKEN, GH_REPO, TARGET_REPO, CAP, RATE_RTC, MAX_PER_RUN,
     PROCESSED_LABEL.
"""
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = os.environ.get("GH_REPO", "Scottcjn/rustchain-bounties")
MAX_PER_RUN = int(os.environ.get("MAX_PER_RUN", "60"))
PROCESSED_LABEL = os.environ.get("PROCESSED_LABEL", "gate-processed")
SCRIPT_DIR = Path(__file__).resolve().parent


def _load_gate():
    """Import pr_review_gate for its is_review_claim() classifier only."""
    spec = importlib.util.spec_from_file_location(
        "pr_review_gate_mod", SCRIPT_DIR / "pr_review_gate.py"
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def list_unprocessed(gate):
    """Open review claims that carry neither the processed label nor a verdict."""
    out = subprocess.run(
        ["gh", "issue", "list", "-R", REPO, "--state", "open",
         "--limit", "1000", "--json", "number,title,labels"],
        capture_output=True, text=True, timeout=180,
    ).stdout
    try:
        issues = json.loads(out or "[]")
    except json.JSONDecodeError:
        print("::error::could not parse issue list", file=sys.stderr)
        return []

    never, stranded = [], []
    for i in issues:
        labels = {l["name"] for l in i.get("labels", [])}
        if not gate.is_review_claim(i.get("title") or ""):
            continue
        if "bounty-eligible" in labels:
            continue                       # adjudicated and payable; done
        if "needs-human" in labels:
            # Unresolved, not decided. These are stranded by construction:
            # once flagged, the gate's idempotency check skipped them forever,
            # so every later fix to the gate left its own past victims behind.
            # Re-adjudicating is how a fix reaches them. Retries stay silent
            # unless the verdict improves, so this costs no notification noise.
            stranded.append(i["number"])
        elif PROCESSED_LABEL not in labels:
            never.append(i["number"])
    # Oldest first: the longest-waiting contributor gets an answer first.
    # Never-adjudicated claims lead, since nobody has told those people
    # anything at all.
    return sorted(never), sorted(stranded)


def adjudicate(number, retry=False):
    env = {**os.environ, "ISSUE_NUMBER": str(number)}
    if retry:
        env["RETRY_NEEDS_HUMAN"] = "1"
    r = subprocess.run(
        [sys.executable, str(SCRIPT_DIR / "pr_review_gate.py")],
        capture_output=True, text=True, timeout=120, env=env,
    )
    ok = r.returncode == 0
    if not ok:
        print(f"::warning::gate failed on #{number}: {(r.stderr or '').strip()[:200]}")
    return ok


def main():
    gate = _load_gate()
    never, stranded = list_unprocessed(gate)
    total = len(never) + len(stranded)
    # Never-adjudicated claims get the budget first: those contributors have
    # heard nothing at all, whereas a stranded claim at least got a verdict.
    batch_new = never[:MAX_PER_RUN]
    batch_retry = stranded[:max(0, MAX_PER_RUN - len(batch_new))]
    print(f"gate-backfill: {len(never)} never-adjudicated, {len(stranded)} stranded "
          f"on needs-human; processing {len(batch_new)}+{len(batch_retry)}")

    done = 0
    for n in batch_new:
        if adjudicate(n):
            done += 1
    for n in batch_retry:
        if adjudicate(n, retry=True):
            done += 1

    processed = len(batch_new) + len(batch_retry)
    remaining = total - processed
    print(f"gate-backfill: adjudicated {done}/{processed}")
    if remaining > 0:
        # Never let a bound look like completion.
        print(f"::notice::{remaining} claims still pending "
              f"(MAX_PER_RUN={MAX_PER_RUN}); they process on the next run.")

    # Fail the run when adjudications failed.
    #
    # This used to `return 0` unconditionally, so all 60 claims in a batch could
    # fail and the workflow still went green. These are precisely the claims the
    # safety net exists to rescue from being stranded, so a green run reporting
    # "adjudicated 0/60" was the worst possible outcome: the backlog looked
    # handled while nothing had been. Reported by @AInoAKARI under #16471.
    failed = processed - done
    if failed:
        print(f"::error::{failed} of {processed} adjudications FAILED; "
              f"the claims they cover are still unresolved")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
