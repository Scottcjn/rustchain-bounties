"""XSS regression tests for otc-bridge/templates/index.html alert + modal.

Companion to the esc() patches in PR #16818. These three patches (alertDiv, button
onclick, openTradeModal) close the residual XSS surface that PR #16818 missed:
  * result.error and result.order.id interpolated into alertDiv.innerHTML.
  * openTradeModal(order.id) inlined into an onclick attribute.
  * order.order_type interpolated into the trade-modal innerHTML.

Run with: pytest -q tests/test_otc_bridge_alert_modal_xss.py
"""

import pathlib
import re
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parents[1]
TPL = REPO / "otc-bridge" / "templates" / "index.html"


def _load_script() -> str:
    text = TPL.read_text(encoding="utf-8")
    s = text.index("<script>") + len("<script>")
    e = text.rindex("</script>")
    assert e > s
    return text[s:e]


SCRIPT = _load_script()

def _strip_comments(src):
    return re.sub(r"//[^\n]*", "", src)


SCRIPT_CODE = _strip_comments(SCRIPT)


PAT_ERR = "alertDiv\\.innerHTML\\s*=\\s*\\`<div class=\"alert alert-error\">\\${([^}]+)}</div>\\`"
PAT_OK = "alertDiv\\.innerHTML\\s*=\\s*\\`<div class=\"alert alert-success\">Order created! ID:\\s*\\${([^}]+)}</div>\\`"
PAT_BTN = "onclick=\"openTradeModal\\('\\${([^}]+)}','\\${([^}]+)}'\\)\""
PAT_SIG = "function openTradeModal\\(([^)]+)\\)\\s*\\{"
PAT_BODY = "function openTradeModal\\(orderId, orderType\\)\\s*\\{(.*?)\\n        \\}"

def test_esc_helper_present():
    assert "function esc(v)" in SCRIPT, "esc() helper missing from otc-bridge index.html"

def test_alertDiv_result_error_escaped():
    m = re.search(PAT_ERR, SCRIPT_CODE)
    assert m, "alertDiv error block not found"
    interp = m.group(1)
    assert "esc(" in interp, "alertDiv error interpolation must call esc(): " + interp

def test_alertDiv_order_id_escaped():
    m = re.search(PAT_OK, SCRIPT_CODE)
    assert m, "alertDiv success block not found"
    interp = m.group(1)
    assert "esc(" in interp, "alertDiv order.id interpolation must call esc(): " + interp

def test_button_onclick_passes_escaped_order_type():
    m = re.search(PAT_BTN, SCRIPT_CODE)
    assert m, "openTradeModal button onclick pattern not found"
    for grp in m.groups():
        assert "esc(" in grp, "openTradeModal arg must be esc()-wrapped: " + grp

def test_openTradeModal_signature_accepts_orderType():
    m = re.search(PAT_SIG, SCRIPT_CODE)
    assert m, "openTradeModal function not found"
    sig = m.group(1)
    assert "orderId" in sig and "orderType" in sig, (
        "openTradeModal signature must accept both args: " + sig
    )

def test_openTradeModal_does_not_reference_undefined_order():
    m = re.search(PAT_BODY, SCRIPT_CODE, flags=re.DOTALL)
    assert m, "openTradeModal body not found"
    body = m.group(1)
    assert "order.order_type" not in body, (
        "openTradeModal still references the bare `order.` identifier (undefined when called by name)"
    )

def test_openTradeModal_uses_safe_deposit_instr():
    m = re.search(PAT_BODY, SCRIPT_CODE, flags=re.DOTALL)
    assert m
    body = m.group(1)
    assert "safeType" in body, "openTradeModal must compute a safeType from esc(orderType)"
    assert "depositInstr" in body, "openTradeModal must derive depositInstr from safeType"

if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
