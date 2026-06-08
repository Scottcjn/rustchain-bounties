# SPDX-License-Identifier: MIT
import importlib.util
from pathlib import Path


def load_gate_module():
    script = Path(__file__).resolve().parents[1] / "scripts" / "pr_review_gate.py"
    spec = importlib.util.spec_from_file_location("pr_review_gate", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_pr_ref_uses_full_github_pull_url_repo():
    gate = load_gate_module()
    body = "Reviewed pull request: https://github.com/Scottcjn/bottube/pull/1327"

    assert gate.pr_ref("[CLAIM] Code review bounty #73", body) == (
        "Scottcjn/bottube",
        "1327",
    )


def test_pr_ref_prefers_explicit_repo_over_title_bare_pr():
    gate = load_gate_module()
    title = "[CLAIM] Code review bounty #73 for PR #1327"
    body = "Reviewed pull request: https://github.com/Scottcjn/bottube/pull/1327"

    assert gate.pr_ref(title, body) == ("Scottcjn/bottube", "1327")


def test_pr_ref_uses_owner_repo_shorthand():
    gate = load_gate_module()

    assert gate.pr_ref("Bounty #73 review for Scottcjn/ram-coffers#663", "") == (
        "Scottcjn/ram-coffers",
        "663",
    )


def test_pr_ref_falls_back_for_bare_pr_number():
    gate = load_gate_module()

    assert gate.pr_ref("Code review PR #7022", "", "Scottcjn/Rustchain") == (
        "Scottcjn/Rustchain",
        "7022",
    )
