#!/usr/bin/env python3
"""
RTC Auto-Pay — GitHub Actions script for automatic RTC payment on PR merge.

Scans PR comments for a payment directive from the repo owner, then calls
the RustChain VPS transfer API and posts a confirmation comment.

Payment directive format (in a PR comment by repo owner):
    **Payment: 75 RTC**
    Payment: 75 RTC

Environment variables (set by the GitHub Action):
    GITHUB_TOKEN    — GitHub token for API access
    PR_NUMBER       — Pull request number
    REPO            — Repository in "owner/repo" format
    PR_AUTHOR       — GitHub username of the PR author
    RTC_VPS_HOST    — RustChain VPS IP (e.g. 50.28.86.131)
    RTC_ADMIN_KEY   — Admin key for /wallet/transfer
    REPO_OWNER      — Repository owner username (e.g. Scottcjn)
"""

import json
import os
import re
import sys
import time

import requests

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------

GITHUB_API = "https://api.github.com"
VPS_PORT = 8099
FROM_WALLET = "founder_community"

# Payment directive pattern — matches both bold and plain variants:
#   **Payment: 75 RTC**
#   **Payment: 75.5 RTC**
#   Payment: 75 RTC
PAYMENT_RE = re.compile(
    r"\*{0,2}Payment:\s*([\d]+(?:\.[\d]+)?)\s*RTC\*{0,2}",
    re.IGNORECASE,
)

# Duplicate-detection: if this string appears in any comment, payment was
# already processed for this PR.
ALREADY_PAID_MARKER = "RTC-AutoPay-Confirmed"

# ---------------------------------------------------------------------------
# Conservative auto-tier (folded in from the former sophia-auto-approve.yml,
# PR #11536). When a merged PR has NO human `Payment:` directive, this single
# payer auto-awards a small, conservative amount ONLY for low-risk PRs.
# Everything else is left for a human directive. Crucially this lives in the
# ONE payer (this script, push:main) with a per-PR idempotency key, so there
# is no second workflow and no double-pay race.
# ---------------------------------------------------------------------------

# Auto-tier amount (env-overridable). Default kept at the Low/code-review
# bounty rate (3 RTC), NOT the original PR's flat 10, to avoid over-paying
# vs the explicit bounty system and discourage trivial-PR farming.
AUTO_TIER_RTC = float(os.environ.get("RTC_AUTO_TIER", "3"))

# Size ceiling for auto-approval; larger PRs need a human directive.
AUTO_MAX_CHANGED_LINES = int(os.environ.get("RTC_AUTO_MAX_LINES", "60"))

# Paths that must NEVER be auto-awarded — consensus / money / auth / CI code
# always needs a human in the loop regardless of diff size.
SENSITIVE_PREFIXES = (
    "node/",
    "rips/",
    "scripts/",
    ".github/",
    "BOUNTY_LEDGER.md",
)

# Marker recorded when the conservative auto-tier pays (distinct from the
# human-directive marker so logs/audits can tell them apart). The dedup
# check treats ANY occurrence of ALREADY_PAID_MARKER as "already paid".
AUTO_TIER_MARKER = "RTC-AutoPay-Confirmed (auto-tier)"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def env(name: str, required: bool = True) -> str:
    val = os.environ.get(name, "")
    if required and not val:
        print(f"::error::Missing required environment variable: {name}")
        sys.exit(1)
    return val


def gh_headers() -> dict:
    return {
        "Authorization": f"token {env('GITHUB_TOKEN')}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }


def fetch_pr_comments(repo: str, pr_number: str) -> list:
    """Fetch all comments on a PR (issue comments endpoint)."""
    comments = []
    page = 1
    while True:
        url = f"{GITHUB_API}/repos/{repo}/issues/{pr_number}/comments"
        resp = requests.get(url, headers=gh_headers(), params={"per_page": 100, "page": page})
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        comments.extend(batch)
        page += 1
    return comments


def post_comment(repo: str, pr_number: str, body: str) -> None:
    """Post a comment on a PR."""
    url = f"{GITHUB_API}/repos/{repo}/issues/{pr_number}/comments"
    resp = requests.post(url, headers=gh_headers(), json={"body": body})
    resp.raise_for_status()
    print(f"Posted confirmation comment on PR #{pr_number}")


def transfer_rtc(vps_host: str, admin_key: str, to_wallet: str,
                 amount: float, memo: str, idempotency_key: str) -> dict:
    """Call the RustChain VPS transfer endpoint.

    The idempotency_key is per-PR, so the node de-duplicates any retry or
    concurrent run to a single transfer — the single serialization point
    that makes a double-pay impossible even if the workflow runs twice.
    """
    url = f"http://{vps_host}:{VPS_PORT}/wallet/transfer"
    payload = {
        "from_miner": FROM_WALLET,
        "to_miner": to_wallet,
        "amount_rtc": amount,
        "memo": memo,
        "idempotency_key": idempotency_key,
    }
    headers = {
        "Content-Type": "application/json",
        "X-Admin-Key": admin_key,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


def fetch_pr_files(repo: str, pr_number: str) -> list:
    """Fetch the changed-files list for a PR (paginated)."""
    files = []
    page = 1
    while True:
        url = f"{GITHUB_API}/repos/{repo}/pulls/{pr_number}/files"
        resp = requests.get(url, headers=gh_headers(), params={"per_page": 100, "page": page})
        resp.raise_for_status()
        batch = resp.json()
        if not batch:
            break
        files.extend(batch)
        if len(batch) < 100:
            break
        page += 1
    return files


def is_bot(author: str) -> bool:
    a = (author or "").lower()
    return a.endswith("[bot]") or a in {"dependabot", "github-actions", "renovate"}


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main() -> None:
    repo = env("REPO")
    pr_number = env("PR_NUMBER")
    pr_author = env("PR_AUTHOR")
    vps_host = env("RTC_VPS_HOST")
    admin_key = env("RTC_ADMIN_KEY")
    repo_owner = env("REPO_OWNER")

    print(f"Processing PR #{pr_number} in {repo} (author: {pr_author})")

    # --- Fetch comments ---------------------------------------------------
    comments = fetch_pr_comments(repo, pr_number)
    print(f"Found {len(comments)} comment(s) on PR #{pr_number}")

    # --- Check for duplicate run ------------------------------------------
    for c in comments:
        if ALREADY_PAID_MARKER in (c.get("body") or ""):
            print(f"Payment already processed (found {ALREADY_PAID_MARKER}). Skipping.")
            return

    # --- Find payment directive from repo owner ---------------------------
    payment_amount = None
    payment_comment_id = None

    for c in comments:
        author = (c.get("user") or {}).get("login", "")
        body = c.get("body") or ""

        # Only accept directives from the repo owner
        if author.lower() != repo_owner.lower():
            continue

        match = PAYMENT_RE.search(body)
        if match:
            payment_amount = float(match.group(1))
            payment_comment_id = c.get("id")
            print(f"Found payment directive: {payment_amount} RTC "
                  f"(comment {payment_comment_id} by {author})")
            # Use the LAST matching directive from the owner in case of updates
            # (don't break — keep scanning)

    # Pay kind drives the confirmation wording and the marker.
    pay_kind = "directive"

    if payment_amount is not None:
        # --- Human directive path -----------------------------------------
        if payment_amount <= 0:
            print(f"::warning::Payment amount is {payment_amount} RTC — skipping.")
            return
        if payment_amount > 10000:
            print(f"::error::Payment amount {payment_amount} RTC exceeds safety limit "
                  "of 10,000 RTC. Process manually.")
            sys.exit(1)
    else:
        # --- Conservative auto-tier path (no human directive) -------------
        # Folded in from the former sophia-auto-approve workflow so there is
        # exactly ONE payer. Auto-award only the low-risk tier; leave anything
        # larger/sensitive for a human `Payment:` directive.
        pay_kind = "auto-tier"

        if is_bot(pr_author):
            print(f"No directive; author {pr_author} is a bot — no auto-award.")
            return

        files = fetch_pr_files(repo, pr_number)
        total_changed = sum(f.get("additions", 0) + f.get("deletions", 0) for f in files)
        paths = [f.get("filename", "") for f in files]
        sensitive = [p for p in paths if p.startswith(SENSITIVE_PREFIXES)]

        if sensitive:
            print(f"No directive; PR touches sensitive paths {sensitive[:3]} — "
                  "not auto-awarding.")
            post_comment(
                repo, pr_number,
                "Sophia auto-tier: **skipped** — this PR touches "
                "consensus / money / CI code. It needs a maintainer "
                "`Payment: N RTC` directive rather than an automatic award.",
            )
            return

        if total_changed > AUTO_MAX_CHANGED_LINES:
            print(f"No directive; PR changes {total_changed} lines "
                  f"(> {AUTO_MAX_CHANGED_LINES}) — too large to auto-award.")
            post_comment(
                repo, pr_number,
                f"Sophia auto-tier: **skipped** — this PR changes {total_changed} "
                f"lines, above the {AUTO_MAX_CHANGED_LINES}-line conservative ceiling. "
                "It needs a maintainer `Payment: N RTC` directive.",
            )
            return

        payment_amount = AUTO_TIER_RTC
        print(f"No directive; eligible for conservative auto-tier "
              f"({total_changed} lines changed).")

    # --- Determine recipient wallet + per-PR idempotency key --------------
    # Wallet is the contributor's GitHub username.
    to_wallet = pr_author
    memo = f"PR #{pr_number} in {repo} — auto-pay ({pay_kind})"
    # Per-PR idempotency key: the node de-duplicates so this PR can be paid
    # at most once, no matter how many times the workflow fires.
    idem_key = f"autopay-{repo.replace('/', '-')}-pr-{pr_number}"

    print(f"Initiating transfer: {payment_amount} RTC from {FROM_WALLET} to "
          f"{to_wallet} ({pay_kind}, idem={idem_key})")

    # --- Call VPS transfer API --------------------------------------------
    try:
        result = transfer_rtc(vps_host, admin_key, to_wallet, payment_amount, memo, idem_key)
    except requests.exceptions.ConnectionError as e:
        print(f"::error::Cannot reach VPS at {vps_host}:{VPS_PORT} — {e}")
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        print(f"::error::VPS returned error: {e.response.status_code} — {e.response.text}")
        sys.exit(1)
    except requests.exceptions.Timeout:
        print(f"::error::VPS request timed out after 30s")
        sys.exit(1)

    ok = result.get("ok", False)
    pending_id = result.get("pending_id", result.get("tx_id", "n/a"))
    error = result.get("error", "")

    if not ok:
        print(f"::error::Transfer failed: {error}")
        # Post failure notice so humans know
        fail_body = (
            f"**RTC Auto-Pay Failed**\n\n"
            f"Attempted to pay **{payment_amount} RTC** to `{to_wallet}` "
            f"but the transfer was rejected:\n\n"
            f"```\n{error}\n```\n\n"
            f"Please process this payment manually.\n\n"
            f"<!-- {ALREADY_PAID_MARKER}:FAILED -->"
        )
        post_comment(repo, pr_number, fail_body)
        sys.exit(1)

    # --- Post confirmation comment ----------------------------------------
    if pay_kind == "auto-tier":
        title = f"## Sophia auto-tier — {payment_amount:g} RTC (conservative, no human directive)"
        tail = (
            f"\n**This is reversible.** The transfer is in the pending ledger with a "
            f"~24h void window. @{repo.split('/')[0]} — if this award is wrong, void "
            f"`pending_id {pending_id}` before it confirms. Larger or sensitive PRs are "
            f"not auto-awarded; they need a maintainer `Payment: N RTC` directive."
        )
    else:
        title = "**RTC Payment Sent**"
        tail = "Transfer confirmed on RustChain."

    confirm_body = (
        f"{title}\n\n"
        f"| Field | Value |\n"
        f"|-------|-------|\n"
        f"| Amount | **{payment_amount:g} RTC** |\n"
        f"| Recipient | `{to_wallet}` |\n"
        f"| From | `{FROM_WALLET}` |\n"
        f"| Memo | {memo} |\n"
        f"| pending_id | `{pending_id}` |\n\n"
        f"{tail}\n\n"
        f"<!-- {ALREADY_PAID_MARKER} kind={pay_kind} pending_id={pending_id} -->"
    )
    post_comment(repo, pr_number, confirm_body)

    print(f"Payment complete ({pay_kind}): {payment_amount} RTC to {to_wallet} "
          f"(pending_id={pending_id})")


if __name__ == "__main__":
    main()
