#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Recognise a TRUSTED record that an RTC payout was already made.

Both payers -- scripts/auto-pay.py (merged PRs) and scripts/bounty_payout.py
(claim issues) -- skip anything that already carries a payment record. That
skip is the only thing standing between "paid once" and "paid twice", but it
is also a way to CANCEL a payment: whatever counts as a record makes the run
print "already processed" and exit green without paying.

The old check was a bare substring test for ``RTC-AutoPay-Confirmed`` in any
comment by anyone. That let:

  * any GitHub user cancel a payout by commenting the string;
  * a trusted bot cancel one by echoing attacker-controlled text -- e.g.
    guard-bounty-pr posts as github-actions[bot] and lists changed file
    paths, so a PR adding ``scripts/RTC-AutoPay-Confirmed.py`` produced a
    "trusted" marker;
  * a maintainer cancel one by quoting the marker name in review prose.

A comment now records a payment only when BOTH hold:

  1. its author is a paying identity (TRUSTED_MARKER_AUTHORS, plus the repo
     owner passed by the caller); and
  2. the marker appears in the exact structured form the payers emit, on a
     line of its own, outside fenced code:
       - ``<!-- RTC-AutoPay-Confirmed[ key=value ...] -->``  (auto-pay; also
         the only form it has ever emitted, since 7634c70), or
       - a line starting ``💸 **RTC-AutoPay-Confirmed** — payout ``
         (bounty_payout's visible confirmation).

The legacy failure notice ``<!-- RTC-AutoPay-Confirmed:FAILED -->`` does not
match form (1) -- the ``:`` is not allowed after the marker -- so an old
failed attempt never reads as a payment.

Tightening the dedup cannot cause a double payment on its own: every transfer
carries a per-PR / per-claim idempotency key, which the node de-duplicates.
"""
import re

MARKER = "RTC-AutoPay-Confirmed"

# Identities whose comment can record a payment: the workflow token that posts
# confirmations, the maintainer and the Sophia agent account (which have posted
# confirmations by hand). Mirrors TRUSTED_AUTHORS in scripts/bounty_payout.py.
TRUSTED_MARKER_AUTHORS = frozenset({
    "scottcjn", "sophiaeagent-beep", "github-actions[bot]", "github-actions"})

_HTML_MARKER_RE = re.compile(
    r"^[ \t]*<!--[ \t]*" + re.escape(MARKER)
    + r"(?:[ \t]+[A-Za-z_][A-Za-z0-9_-]*=[^\s<>]*)*[ \t]*-->[ \t]*$",
    re.MULTILINE,
)
_PAYOUT_LINE_RE = re.compile(
    r"^💸 \*\*" + re.escape(MARKER) + r"\*\* — payout ", re.MULTILINE)
# Fenced code (``` or ~~~). A marker quoted inside a code block is a quotation,
# not a record. An unterminated fence runs to the end of the body, as it
# renders on GitHub.
_FENCE_RE = re.compile(r"^[ \t]*(```|~~~).*?(?:^[ \t]*\1[^\n]*$|\Z)",
                       re.MULTILINE | re.DOTALL)


# A Markdown blockquote line (`> ...`, nested `>> ...` included).
_QUOTE_LINE_RE = re.compile(r"^[ \t]*>[^\n]*$", re.MULTILINE)
# An inline code span: a run of N backticks closed by a run of exactly N.
_INLINE_CODE_RE = re.compile(r"(?<!`)(`+)(?!`).+?(?<!`)\1(?!`)", re.DOTALL)


def strip_quoted_and_code(body) -> str:
    """`body` with everything the author did not say in their own voice removed.

    Drops fenced code blocks (``` / ~~~, unterminated ones run to the end),
    blockquote lines (`> ...`) and inline code spans. What is left is the
    author's own prose, which is the only place an instruction (e.g. a
    `Payment: N RTC` directive) may come from -- quoting someone else's text
    or showing an example of the syntax must not act on it.
    """
    if not isinstance(body, str):
        return ""
    text = _FENCE_RE.sub("", body.replace("\r\n", "\n"))
    text = _QUOTE_LINE_RE.sub("", text)
    return _INLINE_CODE_RE.sub("", text)


def body_records_payment(body) -> bool:
    """True if `body` carries a structured payment marker (author NOT checked)."""
    if not isinstance(body, str) or MARKER not in body:
        return False
    text = _FENCE_RE.sub("", body.replace("\r\n", "\n"))
    return bool(_HTML_MARKER_RE.search(text) or _PAYOUT_LINE_RE.search(text))


def comment_login(comment) -> str:
    """Author login of a GraphQL (`author`) or REST (`user`) comment, lowercased.

    Same precedence as the other payout helpers (`_comment_login` in
    docstring_gate.py, `_comment_author_login` in bounty_payout.py): `author`
    first, and if it is a dict its login is final.
    """
    if not isinstance(comment, dict):
        return ""
    for key in ("author", "user"):
        obj = comment.get(key)
        if isinstance(obj, dict):
            return str(obj.get("login") or "").lower()
    return ""


def comment_records_payment(comment, repo_owner: str = "") -> bool:
    """True if `comment` is a TRUSTED, structured record of a completed payment."""
    if not isinstance(comment, dict):
        return False
    trusted = TRUSTED_MARKER_AUTHORS | ({repo_owner.lower()} if repo_owner else set())
    if comment_login(comment) not in trusted:
        return False
    return body_records_payment(comment.get("body"))
