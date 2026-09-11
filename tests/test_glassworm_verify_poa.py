#!/usr/bin/env python3
"""Smoke tests for glassworm-protocol/src/main.py.

We stub requests.post and load the module with PyGithub mocked so the
imports succeed without network access. The tests cover the new
fail-closed paths and the new RPC-based verify_poa implementation.
"""
import importlib.util
import json
import os
import sys
from unittest import mock


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))


def _load():
    """Load the glassworm module with PyGithub stubbed out."""
    fake_github_module = mock.MagicMock()
    fake_github_module.Github = mock.MagicMock()
    sys.modules.setdefault("github", fake_github_module)
    spec = importlib.util.spec_from_file_location(
        "glassworm_main_under_test",
        os.path.join(REPO_ROOT, "glassworm-protocol", "src", "main.py"),
    )
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_verify_poa_real_rpc_returns_true_only_on_ok_and_verified():
    """verify_poa must return True only when the RPC says ok=true AND verified=true."""
    mod = _load()
    fake = mock.MagicMock()
    fake.status_code = 200
    fake.json.return_value = {"ok": True, "verified": True}
    with mock.patch.object(mod.requests, "post", return_value=fake):
        assert mod.verify_poa("abc", "poa_xyz", "https://rpc.example") is True


def test_verify_poa_real_rpc_rejects_partial():
    """ok=true but verified=false must return False."""
    mod = _load()
    fake = mock.MagicMock()
    fake.status_code = 200
    fake.json.return_value = {"ok": True, "verified": False}
    with mock.patch.object(mod.requests, "post", return_value=fake):
        assert mod.verify_poa("abc", "poa_xyz", "https://rpc.example") is False


def test_verify_poa_real_rpc_rejects_non_200():
    """A 4xx/5xx must return False (fail-closed)."""
    mod = _load()
    fake = mock.MagicMock()
    fake.status_code = 503
    with mock.patch.object(mod.requests, "post", return_value=fake):
        assert mod.verify_poa("abc", "poa_xyz", "https://rpc.example") is False


def test_verify_poa_real_rpc_rejects_connection_error():
    """ConnectionError / Timeout / SSLError must return False (fail-closed)."""
    mod = _load()
    with mock.patch.object(
        mod.requests,
        "post",
        side_effect=mod.requests.exceptions.ConnectionError("nope"),
    ):
        assert mod.verify_poa("abc", "poa_xyz", "https://rpc.example") is False


def test_verify_poa_rejects_missing_inputs():
    """An empty rpc_url or empty poa_hash must return False, never None."""
    mod = _load()
    assert mod.verify_poa("abc", None, "https://rpc.example") is False
    assert mod.verify_poa("abc", "", "https://rpc.example") is False
    assert mod.verify_poa("abc", "poa_xyz", "") is False
    assert mod.verify_poa("abc", "poa_xyz", None) is False


def test_verify_poa_default_uses_tls_verify_true():
    """By default the post() call must be invoked with verify=True."""
    mod = _load()
    captured = {}
    def _capture(url, **kw):
        captured.update(kw)
        fake = mock.MagicMock()
        fake.status_code = 200
        fake.json.return_value = {"ok": True, "verified": True}
        return fake
    with mock.patch.dict(os.environ, {}, clear=False),          mock.patch.object(mod.requests, "post", side_effect=_capture):
        os.environ.pop("RUSTCHAIN_INSECURE_SKIP_TLS_VERIFY", None)
        mod.verify_poa("abc", "poa_xyz", "https://rpc.example")
    assert captured.get("verify") is True, f"expected verify=True, got {captured.get('verify')}"


def test_verify_poa_tls_skip_opt_in():
    """RUSTCHAIN_INSECURE_SKIP_TLS_VERIFY=1 must propagate verify=False to requests."""
    mod = _load()
    captured = {}
    def _capture(url, **kw):
        captured.update(kw)
        fake = mock.MagicMock()
        fake.status_code = 200
        fake.json.return_value = {"ok": True, "verified": True}
        return fake
    with mock.patch.dict(os.environ, {"RUSTCHAIN_INSECURE_SKIP_TLS_VERIFY": "1"}),          mock.patch.object(mod.requests, "post", side_effect=_capture):
        mod.verify_poa("abc", "poa_xyz", "https://rpc.example")
    assert captured.get("verify") is False, f"expected verify=False, got {captured.get('verify')}"


if __name__ == "__main__":
    test_verify_poa_real_rpc_returns_true_only_on_ok_and_verified()
    test_verify_poa_real_rpc_rejects_partial()
    test_verify_poa_real_rpc_rejects_non_200()
    test_verify_poa_real_rpc_rejects_connection_error()
    test_verify_poa_rejects_missing_inputs()
    test_verify_poa_default_uses_tls_verify_true()
    test_verify_poa_tls_skip_opt_in()
    print("OK: 7/7 glassworm verify_poa tests passed")
