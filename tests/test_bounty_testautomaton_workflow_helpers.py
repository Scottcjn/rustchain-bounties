# SPDX-License-Identifier: MIT
import importlib.util
import json
import sys
from pathlib import Path


MODULE_DIR = Path(__file__).resolve().parents[1] / "bounty-hunter-testautomaton"


def load_module(name: str):
    module_path = MODULE_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


scanner = load_module("scanner")
submitter = load_module("submitter")
tracker = load_module("tracker")
implementer = load_module("implementer")


def make_bounty(**overrides):
    data = {
        "number": 1589,
        "title": "[EASY BOUNTY: 2 RTC] Write tests",
        "body": "Cover untested functions.",
        "labels": ["bounty", "easy"],
        "reward_rtc": 2.0,
        "is_multi_claim": False,
        "url": "https://github.com/Scottcjn/rustchain-bounties/issues/1589",
    }
    data.update(overrides)
    return scanner.Bounty(**data)


def test_tracker_records_submission_and_sums_pending_rewards(tmp_path, monkeypatch):
    log_path = tmp_path / "earnings.json"
    monkeypatch.setattr(tracker, "LOG_PATH", log_path)

    assert tracker._load() == []

    tracker.record_submission(
        bounty_number=1589,
        title="Write tests",
        reward_rtc=2.0,
        pr_url="https://github.com/Scottcjn/rustchain-bounties/pull/1",
        wallet="0xabc",
    )
    records = json.loads(log_path.read_text())
    records.append(
        {
            "timestamp": "2026-05-13T00:00:00+00:00",
            "bounty": 1590,
            "title": "Paid bounty",
            "reward_rtc": 10.0,
            "pr_url": "https://example.com/pr",
            "wallet": "0xabc",
            "status": "paid",
        }
    )
    log_path.write_text(json.dumps(records))

    assert tracker.total_pending_rtc() == 2.0
    assert records[0]["status"] == "pending"
    assert records[0]["wallet"] == "0xabc"


def test_template_files_include_expected_submission_readme():
    bounty = make_bounty(number=42, title="Add focused tests", reward_rtc=3.5)

    files = implementer._template_files(bounty)

    assert list(files) == ["submissions/bounty-42/README.md"]
    content = files["submissions/bounty-42/README.md"]
    assert "# Bounty #42" in content
    assert "Add focused tests" in content
    assert "Reward: 3.5 RTC" in content


def test_submit_pr_pushes_branch_and_creates_claim_body(monkeypatch):
    bounty = make_bounty(
        number=1589,
        title="Write tests for TestAutomaton",
        reward_rtc=2.0,
    )
    git_calls = []
    gh_calls = []

    def fake_git(*args, cwd):
        git_calls.append((args, cwd))
        return ""

    def fake_gh(*args):
        gh_calls.append(args)
        return "https://github.com/Scottcjn/rustchain-bounties/pull/9272\n"

    monkeypatch.setattr(submitter, "_git", fake_git)
    monkeypatch.setattr(submitter, "_gh", fake_gh)
    monkeypatch.setattr(submitter, "_get_fork_owner", lambda: "agent-fork")

    pr_url = submitter.submit_pr(
        bounty=bounty,
        workdir="/tmp/workdir",
        branch="bounty-1589-agent-fork",
        wallet="0xabc",
    )

    assert pr_url == "https://github.com/Scottcjn/rustchain-bounties/pull/9272"
    assert git_calls == [(("push", "origin", "bounty-1589-agent-fork"), "/tmp/workdir")]
    gh_args = gh_calls[0]
    assert gh_args[:3] == ("pr", "create", "--repo")
    assert "Scottcjn/rustchain-bounties" in gh_args
    assert "--head" in gh_args
    assert "agent-fork:bounty-1589-agent-fork" in gh_args
    body = gh_args[gh_args.index("--body") + 1]
    assert "Bounty Claim: #1589" in body
    assert "**Reward:** 2.0 RTC" in body
    assert "**Wallet:** `0xabc`" in body
    assert "Closes #1589" in body
