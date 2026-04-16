#!/usr/bin/env python3
"""
RTC Reward Action — Reusable GitHub Action script for automatic RTC payment on PR merge.

This script is called by .github/workflows/rtc-reward.yml (a reusable workflow).
It supports configurable amount, source wallet, and dry-run mode.

Payment directive format (in a PR comment by repo owner):
    **Payment: 75 RTC**
    Payment: 75 RTC

Environment variables (set by the GitHub Action):
    PR_NUMBER          — Pull request number
    REPO               — Repository in "owner/repo" format
    PR_AUTHOR          — GitHub username of the PR author
    RTC_VPS_HOST       — RustChain VPS IP (from secrets)
    RTC_ADMIN_KEY      — Admin key for /wallet/transfer (from secrets)
    REPO_OWNER         — Repository owner username
    AMOUNT             — Configured RTC amount per merge
    FROM_WALLET        — Source wallet name on RustChain VPS
    DRY_RUN            — "true" to simulate transfer without sending
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
DEFAULT_AMOUNT = 5
DEFAULT_FROM_WALLET = "founder_community"

# Payment directive pattern
PAYMENT_RE = re.compile(
    r"\*{0,2}Payment:\s*([\d]+(?:\.[\d]+)?)\s*RTC\*{0,2}",
    re.IGNORECASE,
)

ALREADY_PAID_MARKER = "RTC-Reward-Confirmed"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def env(name: str, required: bool = True, default: str = "") -> str:
    val = os.environ.get(name, default)
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
                 amount: float, from_wallet: str, memo: str) -> dict:
    """Call the RustChain VPS transfer endpoint."""
    url = f"http://{vps_host}:{VPS_PORT}/wallet/transfer"
    payload = {
        "from_miner": from_wallet,
        "to_miner": to_wallet,
        "amount_rtc": amount,
        "memo": memo,
    }
    headers = {
        "Content-Type": "application/json",
        "X-Admin-Key": admin_key,
    }
    resp = requests.post(url, headers=headers, json=payload, timeout=30)
    resp.raise_for_status()
    return resp.json()


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
    from_wallet = env("FROM_WALLET", required=False, default=DEFAULT_FROM_WALLET)
    configured_amount = env("AMOUNT", required=False, default=str(DEFAULT_AMOUNT))
    dry_run = env("DRY_RUN", required=False, default="false").lower() == "true"

    print(f"[RTC Reward] Processing PR #{pr_number} in {repo} (author: {pr_author})")
    print(f"[RTC Reward] Configured amount: {configured_amount} RTC, from wallet: {from_wallet}")

    # --- Dry-run mode --------------------------------------------------------
    if dry_run:
        print(f"::notice::DRY-RUN MODE: Would pay {configured_amount} RTC to {pr_author}")
        dry_body = (
            f"**RTC Reward (Dry Run)**\n\n"
            f"This PR qualifies for a **{configured_amount} RTC** reward.\n\n"
            f"| Field | Value |\n"
            f"|-------|-------|\n"
            f"| Amount | **{configured_amount} RTC** |\n"
            f"| Recipient | `{pr_author}` |\n"
            f"| From | `{from_wallet}` |\n"
            f"| Status | 🟡 Dry run — no actual transfer |\n\n"
            f"<!-- {ALREADY_PAID_MARKER}:DRY-RUN -->"
        )
        post_comment(repo, pr_number, dry_body)
        print("Dry run complete.")
        return

    # --- Fetch comments ------------------------------------------------------
    try:
        comments = fetch_pr_comments(repo, pr_number)
        print(f"[RTC Reward] Found {len(comments)} comment(s) on PR #{pr_number}")
    except Exception as e:
        print(f"::warning::Could not fetch comments: {e} — proceeding with configured amount")

    # --- Check for duplicate run ---------------------------------------------
    for c in comments:
        if ALREADY_PAID_MARKER in (c.get("body") or ""):
            print(f"[RTC Reward] Payment already processed. Skipping.")
            return

    # --- Determine payment amount ---------------------------------------------
    payment_amount = None

    # First: check configured amount from workflow
    try:
        payment_amount = float(configured_amount)
        print(f"[RTC Reward] Using configured amount: {payment_amount} RTC")
    except ValueError:
        pass

    # Second: look for a payment directive override in comments from repo owner
    for c in comments:
        author = (c.get("user") or {}).get("login", "")
        body = c.get("body") or ""

        if author.lower() != repo_owner.lower():
            continue

        match = PAYMENT_RE.search(body)
        if match:
            payment_amount = float(match.group(1))
            print(f"[RTC Reward] Found payment directive override: {payment_amount} RTC "
                  f"(from comment by {author})")

    if payment_amount is None:
        print("[RTC Reward] No configured amount and no directive found. Nothing to do.")
        return

    if payment_amount <= 0:
        print(f"::warning::Payment amount is {payment_amount} RTC — skipping.")
        return

    if payment_amount > 10000:
        print(f"::error::Payment amount {payment_amount} RTC exceeds safety limit of 10,000 RTC.")
        sys.exit(1)

    # --- Determine recipient wallet ------------------------------------------
    # Read .rtc-wallet file from repo root if it exists
    to_wallet = pr_author
    rtc_wallet_file = Path(".rtc-wallet")
    if rtc_wallet_file.exists():
        to_wallet = rtc_wallet_file.read_text().strip()
        print(f"[RTC Reward] Read recipient wallet '{to_wallet}' from .rtc-wallet file")

    memo = f"PR #{pr_number} in {repo} — RTC reward"

    print(f"[RTC Reward] Initiating transfer: {payment_amount} RTC "
          f"from {from_wallet} to {to_wallet}")

    # --- Call VPS transfer API -----------------------------------------------
    try:
        result = transfer_rtc(vps_host, admin_key, to_wallet,
                              payment_amount, from_wallet, memo)
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
        fail_body = (
            f"**RTC Reward Failed**\n\n"
            f"Attempted to pay **{payment_amount} RTC** to `{to_wallet}` "
            f"but the transfer was rejected:\n\n"
            f"```\n{error}\n```\n\n"
            f"Please process this payment manually.\n\n"
            f"<!-- {ALREADY_PAID_MARKER}:FAILED -->"
        )
        post_comment(repo, pr_number, fail_body)
        sys.exit(1)

    # --- Post confirmation comment -------------------------------------------
    confirm_body = (
        f"**RTC Payment Sent**\n\n"
        f"| Field | Value |\n"
        f"|-------|-------|\n"
        f"| Amount | **{payment_amount} RTC** |\n"
        f"| Recipient | `{to_wallet}` |\n"
        f"| From | `{from_wallet}` |\n"
        f"| Memo | {memo} |\n"
        f"| pending_id | `{pending_id}` |\n\n"
        f"Transfer confirmed on RustChain.\n\n"
        f"<!-- {ALREADY_PAID_MARKER} pending_id={pending_id} -->"
    )
    post_comment(repo, pr_number, confirm_body)

    print(f"[RTC Reward] Payment complete: {payment_amount} RTC to {to_wallet} "
          f"(pending_id={pending_id})")


if __name__ == "__main__":
    from pathlib import Path
    main()
