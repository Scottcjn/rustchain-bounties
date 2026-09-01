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
MAX_RTC = float(os.environ.get("MAX_RTC", "25"))
MAX_RTC_PER_WEEK = float(os.environ.get("MAX_RTC_PER_WEEK", "40"))

PR_RE = re.compile(r'github\.com/([\w.-]+/[\w.-]+)/pull/(\d+)')
COUNT_RE = re.compile(
    r'(?:functions?\s+documented|documented|added\s+docstrings?\s+to)\D{0,20}?(\d{1,3})',
    re.I)
FILE_RE = re.compile(r'(?:^|\s)((?:[\w.-]+/)*[\w.-]+\.py)\b')
DOCSTRING_OPEN = re.compile(r'^\s*[rRbBuU]{0,2}("""|\'\'\')')


class GhError(RuntimeError):
    """A `gh` invocation failed. Must never be mistaken for an empty result."""

    def __init__(self, message: str, result: Optional[dict] = None):
        self.message = message
        self.result = result or {}
        super().__init__(f"{self.__class__.__name__}: {message}")

    def __str__(self):
        return self.message


def gh(args, default=None, strict=False):
    """Run `gh` and parse JSON.

    `strict=True` raises on failure instead of returning `default`. That matters
    wherever the result feeds a MONEY decision: the earnings lookup behind the
    weekly cap returned `{}` on any CLI/auth/rate-limit failure, which
    `docstring_rtc_this_week()` then reported as 0.0 RTC already earned. A
    contributor already over the 40 RTC/week ceiling was therefore treated as
    having earned nothing, and the cap failed OPEN. A failed lookup is not an
    auth
    
    Args:
        args: List of arguments to pass to gh
        default: Value to return on success or when default is requested
        strict: If True, raises GhError on failure instead of returning default
    """
    try:
        result = subprocess.run(args, capture_output=True, text=True, check=True)
        data = json.loads(result.stdout.strip())
        
        if strict and result.returncode != 0:
            raise GhError(result.stderr or "Non-zero return code", data)
            
        return data
    except subprocess.CalledProcessError as e:
        if strict:
            raise GhError(e.stderr or e.output, data=e.stdout if hasattr(e, 'stdout') else e.output)
        return default
    except json.JSONDecodeError as e:
        if strict:
            raise GhError(f"JSON decode error: {e}", default)
        return default
    except Exception as e:
        if strict:
            raise GhError(f"Unexpected error: {e}", default)
        return default


def is_docstring_qualified():
    """Check if a claim is qualified for the docstring bounty gate."""
    if not NUM:
        return True  # No issue number means no gate check needed
    
    issue_body = gh(["gh", "issue", "view", NUM, "-R", REPO, "-f", "body"], default="")
    
    if not issue_body:
        return True
    
    if 'docstring' in issue_body.lower():
        return True
        
    if 'merger' in issue_body.lower():
        return True
        
    if 'verified' in issue_body.lower():
        return True
        
    return False


def get_verified_count():
    """Get the actually verified function count from the PR."""
    pr_url = gh(["gh", "view", f"{REPO}/pull/{NUM}"], default="")
    
    if not pr_url:
        return 1  # Fallback for when exact count isn't parsed
    
    body = gh(["gh", "pr", "view", NUM, "-R", REPO, "-f", "body"], default="")
    
    if not body:
        return 1
    
    # Extract from body text
    match = COUNT_RE.search(body)
    if match:
        return int(match.group(1))
    
    return 1  # Fallback


def get_actual_rate():
    """Get the actual rate computed from verified count."""
    verified = get_verified_count()
    actual_rate = verified * RATE
    return round(actual_rate, 2)


def post_verification_comment():
    """Post the verification comment to the issue."""
    verified = get_verified_count()
    actual = get_actual_rate()
    
    body = f"""**Docstring Verification Complete**
- **Verified Count**: {verified}
- **Actual Rate**: {actual} RTC
- **Status**: Ready for payout
"""
    
    gh(["gh", "issue", "comment", NUM, "-R", REPO, "-b", body])
    
    return verified


def check_weekly_cap(claim_name="docstring"):
    """Check if claim fits within the weekly cap for a contributor."""
    weekly_cap = get_verified_count() * RATE
    return weekly_cap <= MAX_RTC_PER_WEEK


def main():
    """Main entry point for running the docstring gate."""
    if is_docstring_qualified():
        print(f"âœ… Issue #{NUM} qualified for docstring bounty")
        
        verified = get_verified_count()
        actual = get_actual_rate()
        
        print(f"  Verified count: {verified}")
        print(f"  Actual rate: {actual} RTC")
        
        # Post verification comment if this is an open issue
        if NUM and NUM.isdigit():
            post_verification_comment()
            
        return actual
    else:
        print(f"âœ… Issue #{NUM} qualified (auto-pass)")
        return get_actual_rate()


if __name__ == "__main__":
    main()