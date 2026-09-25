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
always release a claim by commenting `/unclaim` (or `/release`).

WHO CAN LOCK WHAT (hardening, 2026-09-25)
A brand-new account posted a bare `/claim` on eleven issues in ten minutes and
the bot granted seven 7-day locks -- one on a paid security bounty, four on
issues that were not bounties at all (contributor-opened "Claim: [BOUNTY...]"
submission trackers), because the only bounty check was "the title contains
the word bounty". So a claim is now recorded only when ALL of these hold:
  - the issue was opened by the repo owner or a maintainer (author_association
    OWNER/MEMBER/COLLABORATOR, or a login in CLAIM_MAINTAINERS) AND carries the
    `bounty` label. Titles starting "Claim:" are never lockable.
  - the claimant's GitHub account is at least CLAIM_MIN_ACCOUNT_AGE_DAYS old.
  - the claimant holds fewer than CLAIM_MAX_ACTIVE other active claims.
Lookups that fail (issue, account, claim search) REFUSE the claim with a
neutral note; they never grant it. Refusals are explained kindly -- anyone can
still submit work without claiming.

RELEASING A CLAIM
A maintainer (or the current holder) comments `/unclaim` or `/release`. The bot
posts a new marker whose expiry is already in the past -- so `active_claim`
reads the issue as unclaimed -- and removes the `claimed` label. No hand-editing
of bot comments.

THE ONE THING THAT IS ENFORCED: `Live-URL:` on distribution bounties
An issue carrying the `distribution` label pays for something that exists OFF
GitHub (a post, a video, an article). The 2026-08-28 audit found ~45 such
claims that never left GitHub and zero X/YouTube/Hackaday deliveries ever,
because nothing here asked for one. So on those issues a claim must carry a
line `Live-URL: <url>` on an allowlisted host (see scripts/live_url.py). If it
is missing or off-list the bot explains the field, warmly, and does NOT record
the claim. Every other issue behaves exactly as before.

Env: GITHUB_TOKEN, GH_REPO, ISSUE_NUMBER, COMMENT_BODY, COMMENT_AUTHOR,
     COMMENT_AUTHOR_ASSOCIATION, CLAIM_DAYS (7), CLAIM_MIN_ACCOUNT_AGE_DAYS (14),
     CLAIM_MAX_ACTIVE (2), CLAIM_MAINTAINERS (comma list), MODE (claim|sweep).
"""
from __future__ import annotations

import datetime
import json
import os
import re
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from live_url import ALLOWED_HOSTS_HUMAN, CUSTOM_DOMAIN, classify_for_review, deny_reason, find_live_url  # noqa: E402

REPO = os.environ.get("GH_REPO", "Scottcjn/rustchain-bounties")
CLAIM_DAYS = int(os.environ.get("CLAIM_DAYS", "7"))
CLAIM_MIN_ACCOUNT_AGE_DAYS = int(os.environ.get("CLAIM_MIN_ACCOUNT_AGE_DAYS", "14"))
CLAIM_MAX_ACTIVE = int(os.environ.get("CLAIM_MAX_ACTIVE", "2"))
LABEL = "claimed"
BOUNTY_LABEL = "bounty"
DISTRIBUTION_LABEL = "distribution"
MARKER = "<!-- bounty-claim -->"

# Maintainer identity: GitHub's author_association on the issue/comment
# payload, plus an explicit allowlist (the owner, and the maintenance bot
# account) so a maintainer is never mis-classified if GitHub reports NONE.
MAINTAINER_ASSOCIATIONS = {"OWNER", "MEMBER", "COLLABORATOR"}
MAINTAINERS = {m.strip().lower() for m in os.environ.get(
    "CLAIM_MAINTAINERS", "Scottcjn,AutomatedJanitor").split(",") if m.strip()}

CLAIM_RE = re.compile(
    r'(^|\s)(/claim\b|claiming this|i(?:\'| a)?m taking this|taking this one|i will take this)',
    re.I)
# Only an explicit `/claim` earns a refusal reply on a non-lockable issue; the
# natural phrasings ("taking this one") are too common in ordinary discussion
# to answer on every issue.
EXPLICIT_CLAIM_RE = re.compile(r'(^|\s)/claim\b', re.I)
UNCLAIM_RE = re.compile(r'(^|\s)/(unclaim|release)\b', re.I)
# "/claim" inside a quote block is someone quoting the instructions, not claiming.
QUOTE_RE = re.compile(r'^\s*>')


def gh(args, default=None):
    try:
        p = subprocess.run(["gh"] + args, capture_output=True, text=True, timeout=90)
        return json.loads(p.stdout) if p.stdout.strip() else default
    except Exception:
        return default


def gh_strict(args):
    """Like gh(), but returns None on ANY failure, including a non-zero exit.

    `gh api` prints the error body (e.g. {"message": "Not Found"}) to stdout
    and exits non-zero, which gh() would happily parse and return as if it
    were data. Every lookup that gates a claim goes through here so that an
    error can only ever refuse, never grant.
    """
    try:
        p = subprocess.run(["gh"] + args, capture_output=True, text=True, timeout=90)
        if p.returncode != 0 or not p.stdout.strip():
            print(f"[WARN] gh {' '.join(args[:3])} failed (exit {p.returncode}): "
                  f"{p.stderr.strip()}", file=sys.stderr)
            return None
        return json.loads(p.stdout)
    except Exception as exc:  # timeout, bad JSON, gh missing
        print(f"[WARN] gh {' '.join(args[:3])} failed: {exc}", file=sys.stderr)
        return None


def comment(num, body):
    return gh(["issue", "comment", str(num), "-R", REPO, "--body", body], None)


def is_maintainer(login, association="") -> bool:
    return ((association or "").upper() in MAINTAINER_ASSOCIATIONS
            or (login or "").lower() in MAINTAINERS)


def _unquoted(body: str) -> str:
    return "\n".join(line for line in (body or "").splitlines() if not QUOTE_RE.match(line))


def is_unclaim_request(body: str) -> bool:
    return bool(body) and bool(UNCLAIM_RE.search(_unquoted(body)))


def fetch_issue(num):
    """REST issue payload (title, state, labels, user, author_association) or None."""
    iss = gh_strict(["api", f"/repos/{REPO}/issues/{num}"])
    if not isinstance(iss, dict) or "state" not in iss:
        return None
    return iss


def issue_labels(iss) -> set:
    return {(lab.get("name") or "").lower() for lab in (iss.get("labels") or [])
            if isinstance(lab, dict)}


def lockable_reason(iss):
    """None if this issue is a real bounty that may be claimed, else why not."""
    title = (iss.get("title") or "").strip()
    if title.lower().startswith("claim:"):
        return "submission_tracker"
    author = (iss.get("user") or {}).get("login", "")
    if not is_maintainer(author, iss.get("author_association", "")):
        return "not_maintainer_issue"
    if BOUNTY_LABEL not in issue_labels(iss):
        return "no_bounty_label"
    return None


def account_age_days(login):
    """Whole days since the account was created, or None if it cannot be read."""
    if not login:
        return None
    user = gh_strict(["api", f"users/{login}"])
    created = (user or {}).get("created_at") if isinstance(user, dict) else None
    if not created:
        return None
    try:
        ts = datetime.datetime.fromisoformat(created.replace("Z", "+00:00"))
    except ValueError:
        return None
    return (datetime.datetime.now(datetime.timezone.utc) - ts).days


def claimed_issue_numbers():
    """Open issues carrying the `claimed` label, or None if the search failed."""
    nums = []
    for page in range(1, 11):
        res = gh_strict(["api", "-X", "GET", "search/issues",
                         "-f", f"q=repo:{REPO} is:issue is:open label:{LABEL}",
                         "-f", "per_page=100", "-f", f"page={page}"])
        if not isinstance(res, dict) or not isinstance(res.get("items"), list):
            return None
        nums.extend(it["number"] for it in res["items"] if "number" in it)
        if len(res["items"]) < 100:
            break
    return nums


def active_claims_held_by(author, exclude=None):
    """How many OTHER issues `author` currently holds, or None on lookup failure."""
    nums = claimed_issue_numbers()
    if nums is None:
        return None
    count = 0
    for n in nums:
        if exclude is not None and str(n) == str(exclude):
            continue
        held = active_claim(n)
        if held and held[0].lower() == (author or "").lower():
            count += 1
    return count


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
    return bool(CLAIM_RE.search(_unquoted(body)))


def active_claim(num):
    """Return (holder, expiry_date) for the newest unexpired claim, else None."""
    page = 1
    comments = []
    while page <= 50:
        chunk = gh(["api", f"/repos/{REPO}/issues/{num}/comments?per_page=100&page={page}"], []) or []
        if not isinstance(chunk, list) or not chunk:
            break
        comments.extend(chunk)
        if len(chunk) < 100:
            break
        page += 1
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
    elif classify_for_review(url) == CUSTOM_DOMAIN:
        # A blog on the claimant's own domain: not auto-verifiable, not denied.
        # Record nothing yet, but say so plainly and tag it for one manual look.
        gh(["issue", "comment", str(num), "-R", REPO, "--body",
            f"@{author} — `{url}` looks like your own site rather than one of the "
            f"platforms the bot can verify on its own, so I have flagged it for a "
            f"maintainer to confirm the byline and that the page is indexed. No "
            f"action needed from you unless we ask; that check happens once."], None)
        gh(["issue", "edit", str(num), "-R", REPO, "--add-label", "live-url-manual-review"], None)
        print(f"live-url custom-domain; held for manual review: {url}")
        return False
    else:
        why = deny_reason(url)
        if why:
            lead = (f"thank you for including a link — but `{url}` cannot count as the "
                    f"published piece: {why}. It is welcome as a supporting link *inside* "
                    "the article; the Live-URL has to be where readers find it.")
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


NEUTRAL_REFUSAL = (
    "I could not verify the details needed to record this claim right now, so "
    "I have not recorded it. Nothing is wrong with your comment -- please try "
    "`/claim` again a little later. You can also simply submit your work: a "
    "claim is optional, and payment is always first-in-time.")

NOT_LOCKABLE_REPLY = (
    "`/claim` is only for bounty issues posted by the maintainers (they carry the "
    "`bounty` label). It marks a bounty as being worked on so nobody else builds the "
    "same thing in parallel. This issue is not one of those{extra}, so there is "
    "nothing to claim here -- no action needed. If you are working on a bounty, "
    "comment `/claim` on the bounty issue itself; if you have already done the "
    "work, just link your PR or submission.")


def do_claim(num, author, body="", explicit=None):
    if explicit is None:
        explicit = bool(EXPLICIT_CLAIM_RE.search(_unquoted(body)))

    iss = fetch_issue(num)
    if iss is None:
        comment(num, f"@{author} — {NEUTRAL_REFUSAL}")
        print("issue lookup failed; claim refused")
        return 0
    if (iss.get("state") or "").lower() != "open":
        print("issue not open; ignoring")
        return 0

    why = lockable_reason(iss)
    if why:
        # Natural phrasings ("taking this one") on ordinary issues are just
        # conversation; only an explicit /claim gets an explanation.
        if explicit:
            extra = (" (it tracks a submission, not an open bounty)"
                     if why == "submission_tracker" else "")
            comment(num, f"@{author} — thanks for the enthusiasm! "
                         + NOT_LOCKABLE_REPLY.format(extra=extra))
        print(f"not a lockable bounty ({why}); claim not recorded")
        return 0

    age = account_age_days(author)
    if age is None:
        comment(num, f"@{author} — {NEUTRAL_REFUSAL}")
        print("account-age lookup failed; claim refused")
        return 0
    if age < CLAIM_MIN_ACCOUNT_AGE_DAYS:
        comment(num,
                f"@{author} — welcome, and thank you for your interest! Claims (the "
                f"{CLAIM_DAYS}-day \"I'm working on this\" marker) are available to GitHub "
                f"accounts at least {CLAIM_MIN_ACCOUNT_AGE_DAYS} days old, so I have "
                f"not recorded one here. That does **not** stop you working on this "
                f"bounty: you can submit your work directly without claiming, and "
                f"payment is first-in-time either way. Once your account is "
                f"{CLAIM_MIN_ACCOUNT_AGE_DAYS} days old, `/claim` will work normally.")
        print(f"account {age}d old < {CLAIM_MIN_ACCOUNT_AGE_DAYS}d; claim refused")
        return 0

    labels = issue_labels(iss)
    if not live_url_gate(num, author, body, labels):
        return 0

    held = active_claim(num)
    expiry = datetime.date.today() + datetime.timedelta(days=CLAIM_DAYS)

    if held and held[0].lower() != (author or "").lower():
        comment(num,
            f"@{author} — this one is already claimed by **@{held[0]}** until "
            f"**{held[1].isoformat()}**.\n\n"
            f"Telling you now so you do not spend a week on something that is already "
            f"being built. Bounty #16250 was submitted five times because nothing showed "
            f"it was taken, and three people had their work closed as duplicates.\n\n"
            f"If @{held[0]} has not delivered by {held[1].isoformat()} the claim lapses "
            f"automatically and you can take it. You are also still free to submit anyway — "
            f"claims are a courtesy, not a lock, and payment is still first-in-time. But "
            f"now you are choosing that with your eyes open.")
        print(f"already claimed by {held[0]}")
        return 0

    if not held:  # a renewal by the current holder is not a new claim
        others = active_claims_held_by(author, exclude=num)
        if others is None:
            comment(num, f"@{author} — {NEUTRAL_REFUSAL}")
            print("active-claim count lookup failed; claim refused")
            return 0
        if others >= CLAIM_MAX_ACTIVE:
            comment(num,
                f"@{author} — you already hold {others} active claims, and each "
                f"account can hold at most {CLAIM_MAX_ACTIVE} at a time so bounties "
                f"stay open for everyone. Nothing is wrong — finish or release one "
                f"(comment `/unclaim` on it) and then `/claim` this one. You are also "
                f"free to submit work here without claiming; payment is first-in-time.")
            print(f"{author} holds {others} claims >= cap {CLAIM_MAX_ACTIVE}; refused")
            return 0

    add_label(num, LABEL)
    renew = " (renewed)" if held else ""
    comment(num,
        f"{MARKER}\n🔒 **Claimed{renew}.** holder: @{author} · expires: {expiry.isoformat()}\n\n"
        f"This bounty now shows as taken so nobody else duplicates your work. The claim "
        f"lapses automatically on **{expiry.isoformat()}** — comment `/claim` again to renew "
        f"if you need longer, no explanation needed.\n\n"
        f"A claim is a courtesy signal, not a lock: it does not reserve payment, and anyone "
        f"who submits first is still paid first. It exists so people can see what is already "
        f"being worked on.")
    print(f"claimed #{num} by {author} until {expiry}")
    return 0


def do_unclaim(num, author, association=""):
    """Release a claim properly: a new marker with a past expiry + drop the label.

    Allowed for maintainers and for the current holder releasing their own.
    """
    held = active_claim(num)
    maintainer = is_maintainer(author, association)
    if not maintainer and not (held and held[0].lower() == (author or "").lower()):
        comment(num, f"@{author} — only a maintainer or the current claim holder can "
                     f"release a claim. If you think this claim is stale, mention a "
                     f"maintainer here and they can release it.")
        print(f"{author} ({association}) may not release #{num}")
        return 0

    iss = fetch_issue(num)
    has_label = iss is None or LABEL in issue_labels(iss)  # unknown -> try removal
    if not held and not has_label:
        print(f"#{num} has no active claim; nothing to release")
        return 0

    past = (datetime.date.today() - datetime.timedelta(days=1)).isoformat()
    prior = held[0] if held else "none"
    comment(num,
        f"{MARKER}\n🔓 **Claim released** by @{author}. holder: @{prior} · expires: {past}\n\n"
        f"This bounty is open again — anyone can take it by commenting `/claim`.")
    if has_label:
        remove_label(num, LABEL)
    print(f"released #{num} (was {prior}) by {author}")
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
    association = os.environ.get("COMMENT_AUTHOR_ASSOCIATION", "")
    if not num:
        print("ISSUE_NUMBER not set", file=sys.stderr)
        return 1
    if is_unclaim_request(body):
        return do_unclaim(num, author, association)
    if not is_claim_request(body):
        print("comment is not a claim request; ignoring")
        return 0
    return do_claim(num, author, body)


if __name__ == "__main__":
    raise SystemExit(main())
