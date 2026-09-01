#!/usr/bin/env python3
"""Smoke tests for plaintext-HTTP default fixes in health-check.py and scripts/auto-pay.py.

We don't actually call the network; we import each module with stubs so we
can read the URL it would have built.
"""
import importlib.util
import os
import sys
from unittest import mock


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def _load(name, rel):
    sys.modules.setdefault("tabulate", mock.MagicMock())
    spec = importlib.util.spec_from_file_location(name, os.path.join(REPO_ROOT, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_health_check_default_uses_https():
    captured = {}
    hc = _load("hc1", "health-check.py")
    os.environ.pop("RUSTCHAIN_HEALTH_INSECURE", None)
    fake_resp = mock.MagicMock()
    fake_resp.raise_for_status = lambda: None
    fake_resp.json = lambda: {"version": "x", "uptime": 1, "db_rw": True, "tip_age": 0}
    with mock.patch.object(hc.requests, "get", return_value=fake_resp) as mp:
        def _capture(url, **kw):
            captured["url"] = url
            return fake_resp
        mp.side_effect = _capture
        hc.query_node("1.2.3.4:9999")
    assert captured["url"].startswith("https://"), f"expected https://, got {captured['url']}"


def test_health_check_force_http_via_env():
    captured = {}
    hc = _load("hc2", "health-check.py")
    fake_resp = mock.MagicMock()
    fake_resp.raise_for_status = lambda: None
    fake_resp.json = lambda: {"version": "x", "uptime": 1, "db_rw": True, "tip_age": 0}
    with mock.patch.dict(os.environ, {"RUSTCHAIN_HEALTH_INSECURE": "1"}):
        with mock.patch.object(hc.requests, "get", return_value=fake_resp) as mp:
            def _capture(url, **kw):
                captured["url"] = url
                return fake_resp
            mp.side_effect = _capture
            hc.query_node("1.2.3.4:9999")
    assert captured["url"].startswith("http://"), f"expected http://, got {captured['url']}"


def test_auto_pay_transfer_default_uses_https():
    captured = {}
    ap = _load("ap1", "scripts/auto-pay.py")
    os.environ.pop("RUSTCHAIN_PAYOUT_INSECURE", None)
    fake_resp = mock.MagicMock()
    fake_resp.raise_for_status = lambda: None
    fake_resp.json = lambda: {"ok": True}
    with mock.patch.object(ap.requests, "post", return_value=fake_resp) as mp:
        def _capture(url, **kw):
            captured["url"] = url
            return fake_resp
        mp.side_effect = _capture
        ap.transfer_rtc("vps.example", "adminkey", "to-wallet", 1.0, "memo", "idem")
    assert captured["url"].startswith("https://"), f"expected https://, got {captured['url']}"


def test_auto_pay_transfer_force_http_via_env():
    captured = {}
    ap = _load("ap2", "scripts/auto-pay.py")
    fake_resp = mock.MagicMock()
    fake_resp.raise_for_status = lambda: None
    fake_resp.json = lambda: {"ok": True}
    with mock.patch.dict(os.environ, {"RUSTCHAIN_PAYOUT_INSECURE": "1"}):
        with mock.patch.object(ap.requests, "post", return_value=fake_resp) as mp:
            def _capture(url, **kw):
                captured["url"] = url
                return fake_resp
            mp.side_effect = _capture
            ap.transfer_rtc("vps.example", "adminkey", "to-wallet", 1.0, "memo", "idem")
    assert captured["url"].startswith("http://"), f"expected http://, got {captured['url']}"


if __name__ == "__main__":
    test_health_check_default_uses_https()
    test_health_check_force_http_via_env()
    test_auto_pay_transfer_default_uses_https()
    test_auto_pay_transfer_force_http_via_env()
    print("OK: 4/4 plaintext-http default tests passed")
