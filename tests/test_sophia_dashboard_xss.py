"""XSS regression tests for scripts/sophia_dashboard.py (RIP-306).

These tests load the actual <script> source from the dashboard file and assert:
  * No inline onclick handler that interpolates unsanitized JSON.
  * Every API-controlled value going into innerHTML passes through esc().
  * Click delegation uses data-record-idx (not inline onclick).
  * The esc() helper escapes the five HTML-significant characters.

Run with: pytest -q tests/test_sophia_dashboard_xss.py
"""

import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "sophia_dashboard.py"


def _load_script_source() -> str:
    # NOTE: comments inside the script body reference "</script>" literally as
    # part of the threat-model write-up. Use the LAST </script> so we capture
    # the entire script body rather than stopping at a comment.
    text = SCRIPT.read_text(encoding="utf-8")
    start = text.index("<script>") + len("<script>")
    end = text.rindex("</script>")
    assert end > start, "could not locate <script>...</script> block"
    return text[start:end]


SCRIPT_SRC = _load_script_source()

def _strip_line_comments(src: str) -> str:
    """Strip // ... \n comments so we can grep for code patterns, not docs."""
    return re.sub(r"//[^\n]*", "", src)


SCRIPT_CODE = _strip_line_comments(SCRIPT_SRC)


# ---------- Source-pattern regression tests ----------

def test_no_inline_onclick_with_json_stringify():
    """The per-row onclick with JSON.stringify pattern must be gone."""
    # Use SCRIPT_CODE (line comments stripped) so we don't trip on the threat-model
    # write-up that describes the very pattern we removed.
    assert "onclick='showDetail(" not in SCRIPT_CODE, (
        "inline onclick with JSON.stringify still present -- unsafe single-quoted JS interpolation"
    )
    assert "JSON.stringify(r).replace(/" not in SCRIPT_CODE, (
        "JSON.stringify-then-replace-single-quote pattern is still in the source"
    )

def test_esc_helper_present_and_complete():
    """esc() must escape all five HTML-significant characters and coerce nullish."""
    m = re.search(r"function esc\(v\)\s*\{(.*?)\n\}", SCRIPT_SRC, flags=re.DOTALL)
    assert m, "esc() function not found"
    body = m.group(1)
    assert "v == null" in body, "esc() does not coerce nullish to empty string"
    for c in ("&", "<", ">", '"', "\'"):
        token = ".replace(/" + c + "/g,"
        assert token in body, "esc() does not replace " + repr(c)
    for ent in ("&amp;", "&lt;", "&gt;", "&quot;", "&#39;"):
        assert ent in SCRIPT_SRC, "esc() does not emit " + ent

def test_delegated_click_handler_present():
    """A single delegated click listener replaces the inline onclick pattern."""
    assert "addEventListener('click'" in SCRIPT_SRC
    assert "data-record-idx" in SCRIPT_SRC
    assert "currentFilteredRecords" in SCRIPT_SRC
    assert "closest('tr[data-record-idx]')" in SCRIPT_SRC
    assert "currentFilteredRecords[idx]" in SCRIPT_SRC

def test_tbody_rows_use_data_record_idx():
    """Every row must carry data-record-idx so the listener can find the record."""
    assert 'data-record-idx="${idx}"' in SCRIPT_SRC, (
        "tbody rows must carry data-record-idx for delegated clicks"
    )

def _interpolations(block):
    """Yield the inner expression of every ${...} interpolation in the block."""
    out = []
    i = 0
    while True:
        j = block.find("${", i)
        if j == -1:
            break
        k = block.find("}", j + 2)
        if k == -1:
            break
        out.append(block[j + 2 : k])
        i = k + 1
    return out

def test_tbody_innerHTML_all_api_values_escaped():
    """Every interpolation inside tbody.innerHTML that came from API must go through esc()."""
    m = re.search(
        r"tbody\.innerHTML = filtered\.map\(.*?\)\.join\(''\);",
        SCRIPT_SRC, flags=re.DOTALL,
    )
    assert m, "tbody.innerHTML map block not found"
    block = m.group(0)

    must_escape_substrings = (
        "esc(r.id)", "esc(truncated)", "esc(r.verdict)", "esc(conf)",
        "esc(flags)", "esc(r.model_version", "esc(r.latency_ms",
        "esc(r.created_at", "esc(r.override_verdict)",
    )
    for sub in must_escape_substrings:
        assert sub in block, "missing esc() for: " + sub

    safe = {"idx", "confColor", "override"}
    seen = set(_interpolations(block))
    safe_emoji_starts = ("EMOJI[",)
    for v in seen:
        is_safe = v in safe or v.startswith("esc(") or v.startswith(safe_emoji_starts)
        assert is_safe, "un-escaped interpolation in tbody block: " + v

def test_history_innerHTML_all_api_values_escaped():
    m = re.search(
        r"const rows = \(hist\.inspections \|\| \[\]\)\.map\(.*?\)\.join\(''\);",
        SCRIPT_SRC, flags=re.DOTALL,
    )
    assert m, "history rows map block not found"
    block = m.group(0)
    must_escape_substrings = (
        "esc(h.verdict)", "esc(h.created_at)", "esc(h.override_verdict)",
    )
    for sub in must_escape_substrings:
        assert sub in block, "missing esc() for: " + sub

    seen = set(_interpolations(block))
    # The history block contains a nested ternary ${h.override_verdict ? `... ${esc(h.override_verdict)}...` : ''}
    # which our simple _interpolations() helper will treat as ONE giant interpolation. Accept it as long as it
    # contains esc() somewhere inside.
    safe_emoji_starts = ("EMOJI[",)
    for v in seen:
        # Accept: esc()-wrapped, EMOJI[...] lookup, numeric toFixed() expression, or anything containing esc()
        is_safe = (v.startswith("esc(") or v.startswith(safe_emoji_starts)
                   or "esc(" in v or "toFixed" in v)
        assert is_safe, "un-escaped interpolation in history block: " + v

def test_detail_verdict_uses_esc():
    """The detail-verdict innerHTML must escape record.verdict."""
    m = re.search(
        r"detail-verdict.*?Confidence:.*?%",
        SCRIPT_SRC, flags=re.DOTALL,
    )
    assert m, "detail-verdict line not found"
    block = m.group(0)
    assert "esc(record.verdict)" in block, "detail-verdict must escape record.verdict"

def test_detail_title_uses_textContent():
    """The detail-title uses textContent, which is inherently safe."""
    assert "getElementById('detail-title').textContent" in SCRIPT_SRC
    assert "getElementById('detail-title').innerHTML" not in SCRIPT_SRC

def test_history_inspections_array_filtered():
    """Defensive: history must default to [] when missing, not error."""
    assert "hist.inspections || []" in SCRIPT_SRC

if __name__ == '__main__':
    sys.exit(pytest.main([__file__, "-v"]))
