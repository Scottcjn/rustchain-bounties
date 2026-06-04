#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Award RTC to a merged PR's contributor.

Resolves the recipient wallet from the PR body (an `RTC<40-hex>` address or a
`rtc-wallet: <addr>` line) or, failing that, a committed `.rtc-wallet` file.
Posts a confirmation comment and (unless --dry-run) asks the node to transfer.

Designed to run inside a GitHub Action; all inputs arrive via env vars so the
file stays import-clean and unit-testable. See action.yml.
"""
import json
import os
import re
import sys
import urllib.request
import urllib.error

RTC_ADDRESS_RE = re.compile(r"\bRTC[0-9a-fA-F]{40}\b")
# Explicit "rtc-wallet: <addr>" / "wallet: <addr>" lines win over a bare match.
RTC_LABELLED_RE = re.compile(
    r"(?im)^\s*(?:rtc[-_ ]?wallet|wallet)\s*[:=]\s*(RTC[0-9a-fA-F]{40})\b"
)


def extract_wallet(pr_body, rtc_wallet_file=None):
    """Return the recipient RTC address, or None.

    Precedence: a labelled `wallet:` line in the PR body, then the first bare
    RTC address in the body, then the `.rtc-wallet` file's first address.
    """
    for source in (pr_body or "",):
        m = RTC_LABELLED_RE.search(source)
        if m:
            return m.group(1)
    for source in (pr_body or "",):
        m = RTC_ADDRESS_RE.search(source)
        if m:
            return m.group(0)
    if rtc_wallet_file:
        m = RTC_ADDRESS_RE.search(rtc_wallet_file)
        if m:
            return m.group(0)
    return None


def _post_json(url, payload, headers, timeout=30):
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        raw = resp.read()
        return resp.status, (json.loads(raw) if raw else {})


def post_pr_comment(repo, pr_number, token, body):
    url = f"https://api.github.com/repos/{repo}/issues/{pr_number}/comments"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json",
        "User-Agent": "rtc-reward-action",
        "Content-Type": "application/json",
    }
    try:
        status, _ = _post_json(url, {"body": body}, headers)
        return status in (200, 201)
    except urllib.error.HTTPError as e:
        print(f"::warning::could not post PR comment: {e.code} {e.read()[:200]!r}")
        return False


def transfer_rtc(node_url, payload, timeout=30):
    """POST the transfer to the node. Returns (ok, response_dict)."""
    url = node_url.rstrip("/") + "/wallet/transfer"
    headers = {"Content-Type": "application/json", "User-Agent": "rtc-reward-action"}
    # Self-signed certs on some nodes; mirror the project's documented posture.
    import ssl
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    data = json.dumps(payload).encode()
    req = urllib.request.Request(url, data=data, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=timeout, context=ctx) as resp:
            raw = resp.read()
            return True, (json.loads(raw) if raw else {})
    except urllib.error.HTTPError as e:
        return False, {"error": e.code, "detail": e.read().decode("utf-8", "replace")[:300]}
    except Exception as e:  # noqa: BLE001 - surface any transport error to the log
        return False, {"error": str(e)}


def _bool(v):
    return str(v).strip().lower() in {"1", "true", "yes", "on"}


def main():
    repo = os.environ.get("INPUT_REPO") or os.environ.get("GITHUB_REPOSITORY", "")
    pr_number = os.environ.get("INPUT_PR_NUMBER", "")
    pr_body = os.environ.get("INPUT_PR_BODY", "")
    token = os.environ.get("INPUT_GITHUB_TOKEN", "")
    node_url = os.environ.get("INPUT_NODE_URL", "https://rustchain.org")
    amount = os.environ.get("INPUT_AMOUNT", "1")
    wallet_from = os.environ.get("INPUT_WALLET_FROM", "")
    admin_key = os.environ.get("INPUT_ADMIN_KEY", "")
    dry_run = _bool(os.environ.get("INPUT_DRY_RUN", "true"))

    rtc_wallet_file = None
    if os.path.exists(".rtc-wallet"):
        with open(".rtc-wallet", "r", encoding="utf-8", errors="replace") as fh:
            rtc_wallet_file = fh.read()

    wallet = extract_wallet(pr_body, rtc_wallet_file)
    if not wallet:
        print("::notice::no RTC wallet found in PR body or .rtc-wallet; nothing to award")
        _set_output("awarded", "false")
        _set_output("wallet", "")
        return 0

    try:
        amount_f = float(amount)
    except ValueError:
        print(f"::error::invalid amount: {amount!r}")
        return 1

    print(f"recipient wallet: {wallet}")
    print(f"amount: {amount_f} RTC  dry_run={dry_run}")

    if dry_run:
        msg = (f"\U0001F9EA **RTC reward (dry-run)** — would send **{amount_f} RTC** "
               f"to `{wallet}` for this merged PR. Set `dry-run: false` to enable real payouts.")
        if repo and pr_number and token:
            post_pr_comment(repo, pr_number, token, msg)
        _set_output("awarded", "false")
        _set_output("wallet", wallet)
        print("dry-run complete")
        return 0

    payload = {
        "from": wallet_from,
        "to": wallet,
        "amount_rtc": amount_f,
        "admin_key": admin_key,
        "memo": f"PR reward {repo}#{pr_number}",
    }
    ok, resp = transfer_rtc(node_url, payload)
    if ok and resp.get("ok", True):
        tx = resp.get("tx_hash") or resp.get("pending_id") or "(pending)"
        msg = (f"✅ **RTC reward sent** — **{amount_f} RTC** to `{wallet}` "
               f"for this merged PR. tx: `{tx}`")
        if repo and pr_number and token:
            post_pr_comment(repo, pr_number, token, msg)
        _set_output("awarded", "true")
        _set_output("wallet", wallet)
        _set_output("tx", str(tx))
        print(f"transfer ok: {tx}")
        return 0

    print(f"::error::transfer failed: {resp}")
    if repo and pr_number and token:
        post_pr_comment(repo, pr_number, token,
                        f"⚠️ RTC reward to `{wallet}` failed: `{resp}`")
    _set_output("awarded", "false")
    return 1


def _set_output(key, value):
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(f"{key}={value}\n")


if __name__ == "__main__":
    sys.exit(main())
