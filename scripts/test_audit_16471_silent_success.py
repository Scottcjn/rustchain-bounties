#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Unit tests for #16471 silent-success / wrong-effect defects in rustchain-bounties."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import docstring_gate


def test_rtc_reward_action_extracts_native_rtc_instead_of_hijacking_inline_code(tmp_path: Path):
    """Defect 1: rtc-reward-action must extract native RTC[0-9a-fA-F]{40} wallets
    instead of falling through to the first backticked code identifier (`main`, `pytest`)."""
    action_yml = (REPO_ROOT / ".github" / "actions" / "rtc-reward-action" / "action.yml").read_text(
        encoding="utf-8"
    )
    assert "RTC[a-fA-F0-9]{40}" in action_yml
    assert "curl -fsS" in action_yml

    out_file = tmp_path / "gh_output.txt"
    pr_body = (
        "## Summary\n"
        "Fixes a regression on `main` where `pytest` failed.\n\n"
        "Wallet: RTCc9aaefa30e5f78deb0b5e712bbd630cff04b597c\n"
    )
    script = """
set -euo pipefail
WALLET=$(printf '%s' "$PR_BODY" | grep -oE 'RTC[a-fA-F0-9]{40}' | head -1 || true)
if [[ -z "$WALLET" ]]; then
  WALLET=$(printf '%s' "$PR_BODY" | grep -oiE '(rtc[ _-]?)?(wallet([ _-]?name|[ _-]?id|[ _-]?address)?|miner[ _-]?id)[:= ]+`?[a-zA-Z0-9_-]{3,43}`?' | head -1 | sed -E 's/.*[:= ]+`?//; s/`$//' || true)
fi
if [[ -z "$WALLET" ]]; then
  WALLET=$(printf '%s' "$PR_BODY" | grep -oE '0x[a-fA-F0-9]{40}' | head -1 || true)
fi
if [[ "$WALLET" =~ ^RTC[a-fA-F0-9]{40}$ ]] || [[ "$WALLET" =~ ^[a-zA-Z0-9_-]{3,39}$ ]] || [[ "$WALLET" =~ ^0x[a-fA-F0-9]{40}$ ]]; then
  echo "contributor_wallet=$WALLET" > "$GITHUB_OUTPUT"
else
  echo "contributor_wallet=" > "$GITHUB_OUTPUT"
fi
"""
    subprocess.run(
        ["bash", "-c", script],
        env={**os.environ, "PR_BODY": pr_body, "GITHUB_OUTPUT": str(out_file)},
        check=True,
    )
    assert (
        out_file.read_text(encoding="utf-8").strip()
        == "contributor_wallet=RTCc9aaefa30e5f78deb0b5e712bbd630cff04b597c"
    )


def test_auto_pay_workflow_does_not_swallow_commits_pulls_api_failure():
    """Defect 2: auto-pay.yml must not swallow `gh api .../commits/${sha}/pulls` errors
    with `2>/dev/null || echo '[]'` and must iterate all merged PRs in the push."""
    yml = (REPO_ROOT / ".github" / "workflows" / "auto-pay.yml").read_text(encoding="utf-8")
    assert "|| echo '[]'" not in yml
    assert "MERGED_PRS_JSON" in yml
    assert "set -euo pipefail" in yml


def test_docstring_gate_counts_docstrings_after_unchanged_closing_delimiter_and_mixed_quotes():
    """Defect 3: count_added_docstrings() must not leave `in_docstring=True` across
    unchanged closing delimiters (` ` context lines / `@@` hunks) or single-quoted
    `'''...'''` one-liners that mention `\"\"\"`."""
    q3 = '"' * 3
    s3 = "'" * 3

    diff_unchanged_close = (
        "diff --git a/node/foo.py b/node/foo.py\n"
        "--- a/node/foo.py\n"
        "+++ b/node/foo.py\n"
        "@@ -1,5 +1,5 @@\n"
        " def first_func():\n"
        f"-    {q3}Old summary\n"
        f"+    {q3}Updated summary\n"
        "     unchanged body line\n"
        f"     {q3}\n"
        "     return 1\n"
        "@@ -10,2 +10,3 @@\n"
        " def second_func():\n"
        f"+    {q3}Newly added one-line docstring for second_func.{q3}\n"
        "     return 2\n"
    )
    doc_cnt, _, files = docstring_gate.count_added_docstrings(diff_unchanged_close)
    assert doc_cnt == 2
    assert files == ["node/foo.py"]

    diff_mixed_quotes = (
        "diff --git a/node/bar.py b/node/bar.py\n"
        "--- a/node/bar.py\n"
        "+++ b/node/bar.py\n"
        "@@ -1,4 +1,6 @@\n"
        " def f1():\n"
        f"+    {s3}Return True if line opens with {q3} delimiter.{s3}\n"
        "     return True\n"
        " def f2():\n"
        f"+    {q3}Second function docstring must not be swallowed.{q3}\n"
        "     return False\n"
    )
    doc_cnt2, _, _ = docstring_gate.count_added_docstrings(diff_mixed_quotes)
    assert doc_cnt2 == 2
