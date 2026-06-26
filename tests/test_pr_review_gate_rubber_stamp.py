# SPDX-License-Identifier: MIT
"""
Tests for the rubber-stamp chronological-first detection added in the v3
follow-up to PR #13429 (cross-repo parsing fix). Bounty #73's 2026-06-06
clarification explicitly states that "LGTM", generic praise, or emoji
reactions do not establish first-reviewer position.

The gate's `is_substantive_review` helper is the public seam. These tests
cover the four acceptance criteria from the AIjackgo CHANGES_REQUESTED
review on PR #13429:
  - emoji-only review is filtered
  - canonical "LGTM / great work / thanks" reviews are filtered
  - short generic praise with no findings is filtered
  - a real substantive review (file path, line ref, finding marker,
    or >= 80 chars) is kept
  - a review with >= 1 inline comment is always kept
  - a terse-but-real review (short but carries a finding marker) is kept
  - chronological ordering: substantive-second beats rubber-stamp-first
"""
import importlib.util
from pathlib import Path


def load_gate_module():
    script = Path(__file__).resolve().parents[1] / "scripts" / "pr_review_gate.py"
    spec = importlib.util.spec_from_file_location("pr_review_gate", script)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _review(login, body, state="COMMENTED"):
    return {
        "user": {"login": login},
        "body": body,
        "state": state,
        "submitted_at": "2026-06-08T00:00:00Z",
    }


# ---------------------------------------------------------------------------
# Per-review heuristic: is_substantive_review
# ---------------------------------------------------------------------------


def test_emoji_only_review_is_filtered():
    gate = load_gate_module()
    # Pure emoji + whitespace, short — classic rubber-stamp.
    assert gate.is_substantive_review(_review("jaxint", "🙌")) is False
    assert gate.is_substantive_review(_review("jaxint", "🚀 🎉 👍")) is False
    assert gate.is_substantive_review(_review("jaxint", "  🎉  ")) is False


def test_emoji_only_long_is_also_filtered():
    gate = load_gate_module()
    # Bounty #73 says emoji-only reviews do not establish first-reviewer
    # position regardless of length. A 60-char body of 30 🙌 is filtered.
    long_emoji = "🙌 " * 30
    assert gate.is_substantive_review(_review("jaxint", long_emoji)) is False


def test_long_body_with_text_is_substantive():
    gate = load_gate_module()
    # A 90-char body of pure text (no markers) is substantive per the
    # >= 80 char rule.
    body = "a" * 90
    assert gate.is_substantive_review(_review("reviewer", body)) is True


def test_lgtm_only_is_filtered():
    gate = load_gate_module()
    assert gate.is_substantive_review(_review("jaxint", "LGTM")) is False
    assert gate.is_substantive_review(_review("jaxint", "lgtm!")) is False
    assert gate.is_substantive_review(_review("jaxint", "LGTM 🚀")) is False


def test_great_work_phrases_are_filtered():
    gate = load_gate_module()
    assert gate.is_substantive_review(_review("jaxint", "Great work!")) is False
    assert gate.is_substantive_review(_review("jaxint", "Great work on this PR!")) is False
    assert gate.is_substantive_review(_review("jaxint", "Excellent contribution! Appreciate the work. 🙌")) is False
    assert gate.is_substantive_review(_review("jaxint", "Thanks for contributing to RustChain ecosystem. 🚀")) is False
    assert gate.is_substantive_review(_review("jaxint", "Looks good!")) is False
    assert gate.is_substantive_review(_review("jaxint", "Ship it")) is False
    assert gate.is_substantive_review(_review("jaxint", "Well done!")) is False


def test_short_generic_praise_is_filtered():
    gate = load_gate_module()
    # Short and contains "thanks" but no actual finding — filter.
    assert gate.is_substantive_review(_review("jaxint", "Nice!")) is False
    assert gate.is_substantive_review(_review("jaxint", "Awesome!")) is False
    assert gate.is_substantive_review(_review("jaxint", "Thank you")) is False
    assert gate.is_substantive_review(_review("jaxint", "thx!")) is False


def test_empty_body_is_filtered():
    gate = load_gate_module()
    assert gate.is_substantive_review(_review("jaxint", "")) is False
    assert gate.is_substantive_review(_review("jaxint", None)) is False
    assert gate.is_substantive_review(_review("jaxint", "   \n  ")) is False


def test_real_substantive_review_is_kept():
    gate = load_gate_module()
    # Long body (>= 80 chars) is always substantive.
    long = (
        "Reviewed the diff line by line. The new `get_wallet` constant "
        "introduces a hard-coded wallet field that duplicates the existing "
        "`register_wallet` constant. Recommend extracting to a shared module."
    )
    assert gate.is_substantive_review(_review("reviewer", long)) is True


def test_short_review_with_file_path_is_kept():
    gate = load_gate_module()
    # Short body, but contains a file path → substantive.
    assert gate.is_substantive_review(_review("reviewer", "See `app/mcp.py:520`")) is True
    assert gate.is_substantive_review(_review("reviewer", "scripts/pr_review_gate.py is missing the substantive filter")) is True


def test_short_review_with_line_ref_is_kept():
    gate = load_gate_module()
    assert gate.is_substantive_review(_review("reviewer", "L:520 missing the guard")) is True
    assert gate.is_substantive_review(_review("reviewer", "line 75 — off-by-one")) is True


def test_short_review_with_finding_marker_is_kept():
    gate = load_gate_module()
    assert gate.is_substantive_review(_review("reviewer", "Ref: missing input validation")) is True
    assert gate.is_substantive_review(_review("reviewer", "Bug: race in the timeout handler")) is True
    assert gate.is_substantive_review(_review("reviewer", "Security: unprotected eval path")) is True
    assert gate.is_substantive_review(_review("reviewer", "Guard needed on the response path")) is True
    assert gate.is_substantive_review(_review("reviewer", "Regression in the diff for issue #946")) is True


def test_short_review_with_code_fence_is_kept():
    gate = load_gate_module()
    # Even a 3-char `~~~` fence is enough — Markdown code is a finding format.
    assert gate.is_substantive_review(_review("reviewer", "see ``` for the bug")) is True


def test_inline_comments_make_review_substantive():
    gate = load_gate_module()
    # Even an empty body, with 1+ inline comments, is substantive.
    assert gate.is_substantive_review(_review("reviewer", ""), inline_count=1) is True
    assert gate.is_substantive_review(_review("reviewer", "LGTM"), inline_count=3) is True


def test_terse_but_real_review_with_marker_is_NOT_filtered():
    gate = load_gate_module()
    # Short review that carries an explicit file path or finding marker.
    assert gate.is_substantive_review(_review("reviewer", "Add a `scripts/docs_smoke.py` to the validation suite")) is True


def test_terse_real_review_without_marker_is_filtered():
    gate = load_gate_module()
    # A 41-char review with NO marker, no praise phrase, no emoji.
    # Default to rubber-stamp per Bounty #73. Reviewers with terse-but-
    # real feedback should add a `Ref:` prefix or a file path to be sure.
    assert gate.is_substantive_review(_review("reviewer", "Move this constant to a module-level enum")) is False
    assert gate.is_substantive_review(_review("reviewer", "Consider using a deque here for clarity")) is False


# ---------------------------------------------------------------------------
# End-to-end: chronological ordering with rubber-stamp filter
# ---------------------------------------------------------------------------


def test_substantive_second_beats_rubber_stamp_first():
    gate = load_gate_module()
    # Rubber-stamp at 13:47, real substantive review at 14:00. Without the
    # filter, the gate would set `first = jaxint` and reject the real
    # reviewer. With the filter, `first` should be the substantive one.
    reviews = [
        _review("jaxint", "Excellent contribution! Appreciate the work. 🙌",
                state="COMMENTED"),
        _review("reviewer", (
            "Ref: the `get_wallet` constant in `app/mcp.py:520` is duplicated "
            "from `register_wallet`; recommend extracting to a shared module."
        ), state="APPROVED"),
    ]
    inline_by_login = {"jaxint": 0, "reviewer": 0}
    substantive = [r for r in reviews if gate.is_substantive_review(
        r, inline_count=inline_by_login.get(r["user"]["login"], 0)
    )]
    assert len(substantive) == 1
    assert substantive[0]["user"]["login"] == "reviewer"


def test_all_rubber_stamps_vacuous_first():
    gate = load_gate_module()
    # All three are rubber-stamps. With the filter, no review qualifies and
    # `first` is None — the claimant vacuously becomes the first substantive
    # reviewer.
    reviews = [
        _review("a", "LGTM"),
        _review("b", "Great work!"),
        _review("c", "🚀"),
    ]
    substantive = [r for r in reviews if gate.is_substantive_review(r, inline_count=0)]
    assert substantive == []


def test_substantive_first_with_rubber_stamp_later_still_keeps_substantive():
    gate = load_gate_module()
    # Substantive first, then a rubber-stamp later. Substantive reviewer
    # correctly holds the slot — no regression for the canonical case.
    reviews = [
        _review("first", "Ref: `app/foo.py:42` — missing null check on result"),
        _review("later", "LGTM!"),
    ]
    substantive = [r for r in reviews if gate.is_substantive_review(r, inline_count=0)]
    assert len(substantive) == 1
    assert substantive[0]["user"]["login"] == "first"


# ---------------------------------------------------------------------------
# Cross-cutting: belt-and-suspenders with the existing inline>=1 OR body>=120
# guard. The new filter should NOT regress that path.
# ---------------------------------------------------------------------------


def test_existing_120_char_threshold_still_triggers():
    gate = load_gate_module()
    # 119 chars, no markers, no inline → short, generic, but does NOT match
    # any rubber-stamp pattern (it has substantive-sounding text). Default
    # to keeping it via the >= 80 char threshold.
    body = "a" * 79 + "b"  # 80 chars, no markers
    assert gate.is_substantive_review(_review("reviewer", body)) is True


def test_short_but_specifically_about_a_bug_is_kept():
    gate = load_gate_module()
    # 25 chars, has a finding marker → kept.
    assert gate.is_substantive_review(_review("reviewer", "Bug: race in timeout")) is True
