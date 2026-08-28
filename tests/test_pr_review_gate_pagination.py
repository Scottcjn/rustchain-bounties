# SPDX-License-Identifier: MIT
"""Regression tests for unpaginated review/comment inventory in pr_review_gate."""
import importlib.util
import re
from pathlib import Path


def load_gate_module():
    script = Path(__file__).resolve().parents[1] / "scripts" / "pr_review_gate.py"
    spec = importlib.util.spec_from_file_location("pr_review_gate_pagination", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_api_collect_follows_pages_until_short_page():
    gate = load_gate_module()
    pages = {
        1: [{"id": i} for i in range(30)],
        2: [{"id": 30}, {"id": 31}],
    }

    def fake_api(path, method="GET", data=None, strict=False):
        page = int(re.search(r"page=(\d+)", path).group(1))
        return pages.get(page, [])

    gate.api = fake_api
    items = gate.api_collect("/repos/o/r/pulls/1/reviews", per_page=30)
    assert len(items) == 32
    assert items[-1]["id"] == 31


def test_substantive_review_on_second_page_is_not_missed():
    gate = load_gate_module()
    substantive = {
        "user": {"login": "alice"},
        "body": "Ref: `app/foo.py:42` — missing null check on result",
        "submitted_at": "2026-06-08T11:00:00Z",
    }
    page1 = [
        {
            "user": {"login": f"bot{i}"},
            "body": "LGTM",
            "submitted_at": f"2026-06-08T10:{i:02d}:00Z",
        }
        for i in range(30)
    ]
    page2 = [substantive]

    def fake_api(path, method="GET", data=None, strict=False):
        if "/reviews" in path:
            page = int(re.search(r"page=(\d+)", path).group(1))
            return page1 if page == 1 else page2
        return []

    gate.api = fake_api
    reviews = gate.api_collect("/repos/o/r/pulls/9/reviews", per_page=30)
    rv = [r for r in reviews if r.get("submitted_at")]
    rv.sort(key=lambda r: r["submitted_at"])
    substantive_only = [r for r in rv if gate.is_substantive_review(r, inline_count=0)]
    assert substantive_only[0]["user"]["login"] == "alice"
