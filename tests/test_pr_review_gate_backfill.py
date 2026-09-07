# SPDX-License-Identifier: MIT
"""The PR-review-gate backfill sweep must fail CLOSED on issue enumeration.

`list_unprocessed()` used to read `subprocess.run(...).stdout` and discard the
return code, so a failed `gh issue list` (auth, rate-limit, 5xx, network) or
truncated JSON on a zero exit became an empty list -> "zero open claims" -> a
green run that adjudicated nothing while every unprocessed claim stayed
stranded. That is this project's signature failure shape: reports success while
doing nothing. Reported by @bgrubbs1 under #16471.

These tests pin that authoritative enumeration failure exits non-zero, while a
genuine empty result on a successful exit is still treated as a real zero.
"""
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest


def load_backfill():
    script = (
        Path(__file__).resolve().parents[1] / "scripts" / "pr_review_gate_backfill.py"
    )
    spec = importlib.util.spec_from_file_location("pr_review_gate_backfill_test", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FakeGate:
    """Minimal stand-in for the gate module's is_review_claim() classifier."""

    @staticmethod
    def is_review_claim(title):
        return title.startswith("Bounty #73 claim")


def _completed(returncode, stdout="", stderr=""):
    return subprocess.CompletedProcess(
        args=["gh", "issue", "list"],
        returncode=returncode,
        stdout=stdout,
        stderr=stderr,
    )


def test_gh_nonzero_exit_fails_closed(monkeypatch):
    """gh issue list failing with empty stdout must NOT read as zero claims."""
    mod = load_backfill()
    monkeypatch.setattr(
        mod.subprocess, "run", lambda *a, **k: _completed(1, stdout="", stderr="HTTP 503")
    )
    with pytest.raises(SystemExit) as exc:
        mod.list_unprocessed(FakeGate())
    assert exc.value.code == 1


def test_malformed_json_on_success_fails_closed(monkeypatch):
    """Exit 0 with truncated/garbage JSON must NOT read as zero claims."""
    mod = load_backfill()
    monkeypatch.setattr(mod.subprocess, "run", lambda *a, **k: _completed(0, stdout="{"))
    with pytest.raises(SystemExit) as exc:
        mod.list_unprocessed(FakeGate())
    assert exc.value.code == 1


def test_empty_issue_list_on_success_is_a_real_zero(monkeypatch):
    """A genuine empty list on a zero exit is a real zero, not a failure."""
    mod = load_backfill()
    monkeypatch.setattr(mod.subprocess, "run", lambda *a, **k: _completed(0, stdout="[]"))
    never, stranded = mod.list_unprocessed(FakeGate())
    assert never == []
    assert stranded == []


def test_normal_path_partitions_claims(monkeypatch):
    """The fix must not break normal classification of open claims."""
    mod = load_backfill()
    issues = [
        {"number": 5, "title": "Bounty #73 claim: review of PR #100", "labels": []},
        {"number": 6, "title": "Bounty #73 claim: review of PR #101",
         "labels": [{"name": "needs-human"}]},
        {"number": 7, "title": "Bounty #73 claim: review of PR #102",
         "labels": [{"name": "bounty-eligible"}]},
        {"number": 8, "title": "unrelated issue", "labels": []},
    ]
    monkeypatch.setattr(
        mod.subprocess, "run", lambda *a, **k: _completed(0, stdout=json.dumps(issues))
    )
    never, stranded = mod.list_unprocessed(FakeGate())
    assert never == [5]        # unlabeled review claim -> never adjudicated
    assert stranded == [6]     # needs-human -> re-drive
    # #7 (bounty-eligible) is done; #8 is not a review claim -> both excluded
