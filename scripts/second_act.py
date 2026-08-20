#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Second-act hook: turn a payout comment into a reason to come back.

WHY THIS AND NOT A TENURE MULTIPLIER
------------------------------------
The original proposal was "Contributor Antiquity": a pay multiplier that grows
with continuous weeks active, mirroring the chain's Proof-of-Antiquity thesis.
An adversarial panel (GPT-5.6-sol, Grok, qwen2.5-14b) independently killed it
with the same objection, so it is recorded here to stop it being reinvented:

    Hardware antiquity resists forgery because physical serials and silicon
    fingerprints are SCARCE. Contributor tenure is a GitHub/wallet timestamp,
    which is software-cheap. A human ages one identity serially over 52 weeks;
    a farm ages 200 in parallel for the same calendar cost. With ~73% of claim
    volume already farm-controlled, a tenure multiplier is a loyalty program
    for the farms -- and it rewards them for SLOWING DOWN, which is exactly how
    they evade the existing claim-velocity heuristics.

    "Same word, opposite scarcity. Design for the scarcity you actually have."

The scarcity we actually have is human attention. So this module spends
nothing extra and instead uses the one moment of guaranteed attention we get:
the payout notification. It supplies two things for that comment.

  1. REPUTATION ANTIQUITY, with no payout multiplier. The contributor's
     first-paid date and accepted-contribution count are shown as standing.
     Theme preserved, economic attack surface ~zero: a farm can age an account
     but gains no RTC for it.

  2. A SECOND ACT: one concrete, currently-open bounty to do next, chosen to
     match what they just completed. A closing comment that says only "thanks"
     wastes the moment; ending on a named next task is the cheapest retention
     step available.

Both are advisory strings. This module never moves RTC and never writes to the
chain. If anything here fails it returns empty and the caller posts the plain
payout comment -- a broken hook must never block a payment.
"""
from __future__ import annotations

import json
import re
import subprocess

BOUNTY_TITLE_RE = re.compile(r"\[BOUNTY:?\s*([\d.]+)(?:\s*-\s*[\d.]+)?\s*RTC\]", re.I)
# Task families, so the suggested next act resembles the work just accepted.
# Matched with word boundaries, NOT substrings. Naive `"review" in title` also
# matches "Rich Link PREVIEWs", which suggested a BoTTube embed task to a code
# reviewer. Anchor every key so a family cannot be claimed by a coincidence.
FAMILIES = {
    "review": (r"reviews?", r"code[- ]review", r"pr[- ]review"),
    "writing": (r"blogs?", r"posts?", r"explainers?", r"tutorials?", r"docs?", r"documentation"),
    "security": (r"security", r"vulnerabilit\w*", r"audit\w*", r"harden\w*", r"exploit\w*"),
    "mining": (r"miners?", r"mining", r"hardware", r"attestation\w*", r"fingerprint\w*"),
}
FAMILY_RE = {
    fam: re.compile(r"\b(?:" + "|".join(keys) + r")\b", re.I)
    for fam, keys in FAMILIES.items()
}


def _gh_json(args, default):
    try:
        out = subprocess.run(["gh"] + args, capture_output=True, text=True, timeout=60).stdout
        return json.loads(out or "null") or default
    except Exception:
        return default


def classify(title: str) -> str:
    t = title or ""
    for fam, rx in FAMILY_RE.items():
        if rx.search(t):
            return fam
    return "general"


def standing(handle: str, repo: str) -> str:
    """Reputation antiquity: how long they have been here, and how much landed.

    Deliberately NOT a multiplier. Status only.
    """
    if not handle:
        return ""
    closed = _gh_json(
        ["search", "issues", "--repo", repo, "--author", handle, "--state", "closed",
         "--limit", "100", "--json", "number,createdAt", "--match", "title"], [])
    if not closed:
        return ""
    first = min(i["createdAt"][:10] for i in closed if i.get("createdAt"))
    n = len(closed)
    if n <= 1:
        return f"First accepted contribution here. Welcome aboard."
    return f"Contributor since **{first}** · **{n}** accepted contributions."


def next_act(handle: str, repo: str, just_did: str) -> str:
    """One open bounty to do next, preferring the family they just worked in."""
    issues = _gh_json(
        ["issue", "list", "-R", repo, "--state", "open", "--author", "Scottcjn",
         "--limit", "200", "--json", "number,title"], [])
    offers = [i for i in issues if BOUNTY_TITLE_RE.search(i.get("title") or "")]
    if not offers:
        return ""
    fam = classify(just_did)
    same = [i for i in offers if classify(i["title"]) == fam]
    matched = bool(same) and fam != "general"
    pool = same or offers
    # Stable per-contributor pick, so re-running does not shuffle the suggestion
    # and two contributors are not both pushed at the same bounty.
    pick = pool[sum(ord(c) for c in (handle or "x")) % len(pool)]
    title = re.sub(r"^\[BOUNTY:?[^\]]*\]\s*", "", pick["title"]).strip()
    amt = BOUNTY_TITLE_RE.search(pick["title"])
    amt = f" ({amt.group(1)} RTC)" if amt else ""
    # Only claim a family match when one actually exists. Saying "since you just
    # did review work" above an unrelated task reads as automated and wrong,
    # which is worse than a neutral lead.
    lead = f"More {fam} work, since that is your lane" if matched else "Next, if you want it"
    return f"{lead}: **#{pick['number']}** {title}{amt}"


def build(handle: str, repo: str, just_did: str) -> str:
    """Return the trailing block for a payout comment. Never raises."""
    try:
        parts = [p for p in (standing(handle, repo), next_act(handle, repo, just_did)) if p]
        return ("\n\n---\n" + "\n\n".join(parts)) if parts else ""
    except Exception:
        return ""


if __name__ == "__main__":
    import sys
    h = sys.argv[1] if len(sys.argv) > 1 else "octocat"
    t = sys.argv[2] if len(sys.argv) > 2 else "PR Review - Bounty #73"
    print(build(h, "Scottcjn/rustchain-bounties", t) or "(no hook produced)")
