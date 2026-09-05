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
    """Resolve the claimed PR as (repo_fullname_or_None, number_str_or_None).

    Order matters: claim titles look like "Bounty #1009 claim: review of
    PR #1396", so a bare '#N' scan grabs the BOUNTY number, not the PR
    (2026-06-11 bug — 9 valid claims auto-rejected). Full PR URLs win,
    then explicit 'PR #N'/'pull/N', and bare '#N' only as a last resort
    with 'Bounty #N' references stripped first.
    """
    for s in (title, body or ""):
        m = re.search(r'github\.com/([\w.-]+/[\w.-]+)/pull/(\d{1,6})', s)
        if m: return m.group(1), m.group(2)
    for s in (title, body or ""):
        m = re.search(r'(?:\bPR\s*#?\s*|pull/)(\d{1,6})', s, re.IGNORECASE)
        if m: return None, m.group(1)
    for s in (title, body or ""):
        stripped = re.sub(r'(?i)bounty\s*#\s*\d{1,6}', '', s)
        m = re.search(r'#(\d{3,6})', stripped)
        if m: return None, m.group(1)
    return None, None

def prose_repo(title, body):
    """Candidate repo NAME when a claim names it in prose, not as a URL.

    Claims are routinely written as "Code review bounty #73 for
    rustchain-bounties PR #13434" or "Code Review - Scottcjn/rustchain-dialup
    PR #4". pr_ref() only extracts a repo from a full github.com/<o>/<r>/pull/N
    URL, so these resolve to (None, N) and the caller falls back to
    TARGET_REPO. It then looks up a number that belongs to a DIFFERENT repo,
    gets nothing, and files the claim as needs-human.

    That is not a fringe case: on 2026-08-07 it accounted for 7 of the 13
    unadjudicated claims that had to be paid out partially by hand.

    Returns a bare repo name (no owner) or None. Deliberately does NOT verify
    the repo exists -- the caller validates by attempting the lookup, so a
    false positive costs one extra API call and nothing else.
    """
    for s in (title, body or ""):
        if not s:
            continue
        # "owner/repo#123" or "owner/repo PR #123"
        m = re.search(r'\b[\w.-]+/([\w.-]+?)\s*(?:#|\bPR\s*#?\s*)(\d{1,6})\b', s, re.I)
        if m:
            return m.group(1)
        # "<repo-name> PR #123" -- require a hyphen or a known product prefix
        # so ordinary words ("the PR #12", "this PR #12") cannot match.
        m = re.search(r'\b((?:[\w.]+-[\w.-]+)|(?:rustchain|bottube|beacon|grazer)[\w.-]*)'
                      r'\s+PR\s*#?\s*(\d{1,6})\b', s, re.I)
        if m:
            return m.group(1)
    return None
def native_wallet(body):
    b=body or ""
    if re.search(r'\bRTC[0-9a-fA-F]{40}\b', b) or re.search(r'(?i)miner[_\-]?id', b): return True
    # Solana/ETH payout request = not native
    if re.search(r'\b[1-9A-HJ-NP-Za-km-z]{32,44}\b', b) and "rtc" not in b.lower(): return False
    return None  # unknown -> don't reject on this alone

# Rubber-stamp detector (Bounty #73: "LGTM", generic praise, or emoji
# reaction does not establish first-reviewer position). Bounty #73
# explicitly states terse praise with no line-level findings does not
# establish the first-reviewer slot. The helper logic lives in
# is_substantive_review() below; this block only defines the phrase list
# and the regex.
#
# Heuristic (intentionally narrow — only flags the obvious cases the
# 2026-06-06 clarification on issue #73 calls out):
#   1. Any review with >=1 inline comment is substantive (handled in
#      is_substantive_review).
#   2. Any review whose body is long enough to plausibly carry a finding
#      (>=80 chars after stripping whitespace) is substantive (handled
#      in is_substantive_review).
#   3. Any review whose body contains a file path, a line reference
#      like `L:NN`, a marker like "Ref:", "Finding", "Bug", "Issue:",
#      "Security", "Risk", "Guard", or a Markdown code fence, is
#      substantive (caught by _SUBSTANTIVE_MARKER_RE).
#   4. Emoji-only bodies are rubber-stamps (caught by _EMOJI_ONLY_RE).
#   5. Bodies that match the canonical "LGTM / great work / thanks"
#      pattern with no other content are rubber-stamps (caught by
#      _RUBBER_STAMP_RE). The pattern is anchored at the start (`^\s*`)
#      but the trailing class only allows whitespace, non-word chars,
#      and emoji, so a praise phrase that is immediately followed by
#      substantive text (e.g. "Great work, but the file path is
#      missing") will NOT match — _SUBSTANTIVE_MARKER_RE.search() will
#      catch the file path above.

# Substantive-marker regex. Used to detect file paths, line refs, and
# finding keywords. Defined BEFORE the rubber-stamp regex so the
# is_substantive_review helper can short-circuit: a body that contains
# a marker is never rubber-stamp, even if it also starts with a praise
# phrase.
_SUBSTANTIVE_MARKER_RE = re.compile(
    r"(?:"
    r"\b(?:ref|refs|reference|finding|findings|bug|issue|risk|guard|"
    r"security|vuln|vulnerability|regression|edge case|missing|broken|"
    r"leak|panic|null|deref|injection|xss|csrf|race|deadlock|overflow)\b"
    r"|"
    r"`[^`]*\.[a-zA-Z0-9]{1,5}`"          # `path.ext`
    r"|"
    r"\b[a-zA-Z0-9_./-]+\.(?:py|js|ts|go|rs|java|kt|swift|c|cpp|h|hpp|"
    r"md|yaml|yml|json|toml|sh|bash)\b"  # bare file path
    r"|"
    r"\bL:?\s*\d{1,4}\b"                  # L:123 or L 123 line ref
    r"|"
    r"\bline\s*\d{1,4}\b"                 # line 123
    r"|"
    r"```"                                # markdown code fence
    r")",
    re.IGNORECASE,
)

# A review body is rubber-stamp iff:
#   (a) it is short (under 80 chars stripped), AND
#   (b) it does NOT contain a substantive marker, AND
#   (c) it starts with (or fully is) one of the canonical praise phrases.
# This is the helper logic; see is_substantive_review() below. The
# phrase list is small on purpose: a real review that starts with "Risk:"
# or "Bug:" is filtered upstream by the substantive-marker check, not by
# this list. The phrases here are the canonical "LGTM / great work /
# thanks / appreciate" patterns plus the universal praise emoji.
_RUBBER_STAMP_PHRASES = (
    "lgtm", "lgtm!", "great work", "great contribution", "great work on this",
    "nice work", "nice!", "nice job", "awesome", "awesome!",
    "looks good", "looks great", "ship it", "shipit", "approved!",
    "excellent", "excellent contribution", "appreciate", "appreciated",
    "appreciate the work", "thanks", "thanks!", "thanks for", "thank you",
    "thx", "thnx", "great pr", "great review", "great catch", "great find",
    "good work", "good job", "well done", "wonderful", "fantastic", "amazing",
)
# Regex for "body is essentially just praise." The pattern matches if the
# body STARTS with a praise phrase and is short enough that the rest of
# the body cannot contain a substantive marker. Concretely: the body
# must be <= 100 chars AND consist of (whitespace + praise phrase +
# trailing punctuation/emoji/whitespace).
_RUBBER_STAMP_RE = re.compile(
    r"^\s*(?:" + "|".join(re.escape(p) for p in _RUBBER_STAMP_PHRASES) + r")"
    r"[\s\W"
    r"\U0001F300-\U0001FAFF"
    r"\U0001F600-\U0001F64F"
    r"\U0001F680-\U0001F6FF"
    r"\U0001F1E0-\U0001F1FF"
    r"\u2600-\u27BF"
    r"]*$",
    re.IGNORECASE | re.UNICODE,
)
# Emoji-only detector: any body that is purely emoji + whitespace +
# non-word punctuation is a rubber-stamp, regardless of length. The
# Bounty #73 source explicitly calls out "an emoji reaction" as not
# establishing first-reviewer position.
_EMOJI_ONLY_RE = re.compile(
    r"^[\s\W"
    r"\U0001F300-\U0001FAFF"                  # symbols + pictographs
    r"\U0001F600-\U0001F64F"                  # emoticons
    r"\U0001F680-\U0001F6FF"                  # transport
    r"\U0001F1E0-\U0001F1FF"                  # flags
    r"\u2600-\u27BF"                          # misc symbols + dingbats
    r"]+$",
    re.UNICODE,
)


def is_substantive_review(review, inline_count=0):
    """Return True iff the review carries actionable, line-level findings.

    Order of checks matters. Bounty #73's 2026-06-06 clarification says
    "LGTM", generic praise, and emoji reactions do not establish
    first-reviewer position. A real review names a file/line and a
    concrete issue or risk. The helper returns False (rubber-stamp) for
    any review that fails every positive signal:

      1. >= 1 inline (line-level) review comment          -> substantive
      2. non-empty body whose first non-blank word is a
         substantive marker (file path, line ref, "Ref:", "Bug:",
         "Risk:", "Security", etc.)                      -> substantive
      3. body length (stripped) >= 80 chars AND the body
         is not pure emoji                                -> substantive
      4. short body that is just praise + emoji           -> rubber-stamp
      5. short body with no marker                        -> rubber-stamp
         (Bounty #73 explicitly says terse praise without findings
         is not substantive; default-deny matches the spec.)
      6. empty body                                        -> rubber-stamp
    """
    if inline_count and inline_count > 0:
        return True
    body = (review.get("body") or "").strip()
    if not body:
        return False
    # Substantive marker short-circuit: a body that names a file, line, or
    # finding keyword is never a rubber-stamp, even if it ALSO starts with
    # a praise phrase (e.g. "Great catch on the file path bug in
    # `app/foo.py`" — kept).
    if _SUBSTANTIVE_MARKER_RE.search(body):
        return True
    # Emoji-only body is always a rubber-stamp, regardless of length.
    if _EMOJI_ONLY_RE.match(body):
        return False
    # Body starts with a praise phrase and is short: rubber-stamp.
    # The regex's trailing class allows only whitespace, non-word chars,
    # and emoji, so a praise phrase that is immediately followed by
    # substantive text (e.g. "Great work, but the file path is missing")
    # will NOT match this regex — `_SUBSTANTIVE_MARKER_RE.search` already
    # caught the "file path" marker above.
    if _RUBBER_STAMP_RE.match(body):
        return False
    # Long body without an explicit marker: presumed substantive (a
    # real review with line-level findings usually exceeds 80 chars and
    # the marker regex is intentionally narrow).
    if len(body) >= 80:
        return True
    # Short body, no marker, not a praise phrase, not emoji-only. Default
    # to rubber-stamp because Bounty #73 explicitly excludes terse
    # praise. A borderline case like "Move this constant to a
    # module-level enum" (30 chars, no marker) is also a rubber-stamp by
    # this rule; reviewers with terse-but-real feedback should add a
    # `Ref:` prefix or a file path to be sure.
    return False


def comment(n, body): api(f"/repos/{REPO}/issues/{n}/comments","POST",{"body":body})
def add_label(n, lab): api(f"/repos/{REPO}/issues/{n}/labels","POST",{"labels":[lab]})
def close(n, reason_comment):
    comment(n, reason_comment); api(f"/repos/{REPO}/issues/{n}","PATCH",{"state":"closed","state_reason":"not_planned"})

def _unresolved(msg, quiet):
    """Flag a claim the gate could not decide.

    On a RETRY_NEEDS_HUMAN pass the claim is ALREADY labelled and the claimant
    has already been told. Re-commenting the same verdict every sweep would
    turn a helpful retry into notification spam, so a retry that fails to
    improve on the previous outcome exits without speaking.
    """
    if quiet:
        return
    add_label(NUM, "needs-human")
    comment(NUM, msg)

def main():
    iss=api(f"/repos/{REPO}/issues/{NUM}")
    if not iss or iss.get("state")!="open": return
    labels={l["name"] for l in iss.get("labels",[])}
    # Idempotency, with one deliberate exception.
    #
    # `bounty-eligible` means adjudicated and payable -- never touch it again.
    # `gate-processed` alone means adjudicated cleanly -- likewise.
    #
    # `needs-human` means the OPPOSITE: the gate could not decide. Treating it
    # as final made it a permanent dead end, so every later fix to this script
    # stranded its own past victims. That is exactly what happened: claims
    # gated before the 2026-06-11 pr_ref fix were told "couldn't read reviews
    # for Scottcjn/Rustchain#<n>" because full PR URLs were not yet preferred,
    # and they were never revisited after the fix landed. Seven such claims had
    # to be settled by hand on 2026-08-07; at least three resolve cleanly
    # against current code.
    #
    # With RETRY_NEEDS_HUMAN set, an unresolved claim is re-adjudicated. To
    # avoid re-notifying people when nothing has changed, a retry that still
    # cannot resolve exits SILENTLY (see `quiet` below) -- it comments only
    # when the verdict actually improves.
    retry = os.environ.get("RETRY_NEEDS_HUMAN", "") == "1"
    quiet = False
    if "bounty-eligible" in labels:
        return
    if "needs-human" in labels:
        if not retry:
            return
        quiet = True            # only speak up if the outcome improves
    elif "gate-processed" in labels:
        return
    title=iss.get("title",""); body=iss.get("body") or ""; author=iss["user"]["login"]
    if not is_review_claim(title): return  # not our claim type; leave for other workflows
    add_label(NUM,"gate-processed")
    claim_repo, pr = pr_ref(title, body)
    if not pr:
        _unresolved("🤖 Gate: couldn't find a single PR reference. Per **Bounty #73**, file one claim per PR with `PR #<number>` (a full PR URL is best). Flagged for human review.", quiet); return
    # Cross-repo claims: trust an explicit PR URL if it points at one of
    # the maintainer's repos; anything else goes to a human.
    target = TARGET
    if claim_repo:
        if claim_repo.lower().startswith(TARGET.split("/")[0].lower() + "/"):
            target = claim_repo
        else:
            _unresolved(f"🤖 Gate: claim references a PR outside the maintainer's repos ({claim_repo}#{pr}). Flagged for human review.", quiet); return
    if native_wallet(body) is False:
        close(NUM,"🤖 Gate: payout must be a **native RTC wallet** (`RTC…`) — RTC has no off-ramp, no Solana/ETH bridge. Reopen with a native wallet."); return
    reviews=api(f"/repos/{target}/pulls/{pr}/reviews")
    if reviews is None and not claim_repo:
        # The default target was an assumption, not a statement by the
        # claimant. Before giving up, honour a repo named in prose
        # ("... for rustchain-bounties PR #13434"). Only reached when the
        # assumed lookup already failed, so this can rescue a claim but can
        # never redirect one that was resolving correctly.
        cand = prose_repo(title, body)
        if cand and cand.lower() != target.split("/")[1].lower():
            owner = TARGET.split("/")[0]
            alt = f"{owner}/{cand}"
            alt_reviews = api(f"/repos/{alt}/pulls/{pr}/reviews")
            if alt_reviews is not None:
                target, reviews = alt, alt_reviews
    if reviews is None:
        _unresolved(f"🤖 Gate: couldn't read reviews for {target}#{pr} (private/deleted?). Flagged for human review.", quiet); return
    rv=[r for r in reviews if r.get("submitted_at")]
    rv.sort(key=lambda r:r["submitted_at"])
    inl = api(f"/repos/{target}/pulls/{pr}/comments?per_page=100") or []
    # Per-author inline counts (so the rubber-stamp filter is per-review).
    author_inline = {}
    for c in inl:
        login = (c.get("user") or {}).get("login")
        if login:
            author_inline[login] = author_inline.get(login, 0) + 1
    # Filter out rubber-stamp reviews before picking the first substantive
    # reviewer. If a review has no inline comments, run it through
    # is_substantive_review(); if it has any inline comments, it is
    # substantive by definition.
    substantive = [r for r in rv if is_substantive_review(
        r, inline_count=author_inline.get(r["user"]["login"], 0)
    )]
    first = substantive[0]["user"]["login"] if substantive else None
    body_len = next((len(r.get("body") or "") for r in rv if r["user"]["login"]==author), 0)
    inline = author_inline.get(author, 0)
    if first != author:
        close(NUM,f"🤖 Gate (Bounty #73 — first substantive review only): {target}#{pr} was first reviewed by **{first or 'someone else'}** (after filtering rubber-stamps), not @{author}. Path back: review PRs where you're the first reviewer."); return
    if inline==0 and body_len<120:
        close(NUM,f"🤖 Gate: your review of {target}#{pr} has no inline comments and no substantive summary — Bounty #73 requires a **substantive line-level review**, not a bare approval."); return
    # cap check: count author's existing bounty-eligible issues ORG-WIDE
    # (user:Scottcjn spans every repo, so the per-contributor cap stays global
    # even though the gate now runs in both rustchain-bounties and Rustchain).
    elig=api(f"/search/issues?q=user:Scottcjn+label:bounty-eligible+author:{author}+type:issue") or {}
    if elig.get("total_count",0)>=CAP:
        close(NUM,f"🤖 Gate: @{author} has reached the **{CAP} eligible reviews/contributor** cap (Bounty #73). Quality over volume — thanks!"); return
    add_label(NUM,"bounty-eligible")
    comment(NUM,f"✅ 🤖 Gate: **verified eligible** — @{author} is the first substantive reviewer of {target}#{pr}. **{RATE} RTC** pending payout (native `RTC…` wallet if not on file).")

if __name__=="__main__":
    try: main()
    except Exception as e:
        print(f"gate error: {e}", file=sys.stderr)  # never fail the workflow
