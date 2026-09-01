#!/usr/bin/env python3
"""
Smoke tests for integrations/luisalias007-cmyk/mcp_server.py

We do not start the MCP stdio transport here. Instead we exercise the
module-level constants and the URL/SSL guards directly so we can run
the test without mcp.server installed.
"""
import importlib
import os
import sys
import warnings
from unittest import mock


REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
SERVER_PATH = os.path.join(
    REPO_ROOT, "integrations", "luisalias007-cmyk", "mcp_server.py"
)


def _load_with_stub():
    """Import the server module after stubbing mcp.server so we can run without it."""
    fake_server = mock.MagicMock()
    fake_app = mock.MagicMock()
    fake_server.Server.return_value = fake_app
    sys.modules.setdefault("mcp", mock.MagicMock())
    sys.modules.setdefault("mcp.server", mock.MagicMock())
    sys.modules["mcp.server"].Server = fake_server.Server
    sys.modules.setdefault("mcp.server.stdio", mock.MagicMock())
    sys.modules["mcp.server.stdio"].stdio_server = mock.MagicMock()
    fake_types = mock.MagicMock()
    sys.modules.setdefault("mcp.types", fake_types)
    fake_types.TextContent = mock.MagicMock()
    fake_types.Tool = mock.MagicMock()
    spec = importlib.util.spec_from_file_location("luis_mcp_server", SERVER_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module, fake_server


def test_warns_on_plaintext_http_default():
    env = {"RUSTCHAIN_BASE_URL": "http://example.invalid:8088"}
    with mock.patch.dict(os.environ, env, clear=True):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _load_with_stub()
    msgs = [str(w.message) for w in caught if issubclass(w.category, RuntimeWarning)]
    assert any("plaintext HTTP" in m for m in msgs), f"expected plaintext warning, got: {msgs}"


def test_no_warning_on_https_default():
    env = {"RUSTCHAIN_BASE_URL": "https://example.invalid:8443"}
    with mock.patch.dict(os.environ, env, clear=True):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _load_with_stub()
    msgs = [str(w.message) for w in caught if issubclass(w.category, RuntimeWarning)]
    assert not any("plaintext HTTP" in m for m in msgs), f"unexpected HTTP warning: {msgs}"


def test_warns_when_insure_skip_tls_set():
    env = {
        "RUSTCHAIN_BASE_URL": "https://example.invalid:8443",
        "RUSTCHAIN_INSECURE_SKIP_TLS": "1",
    }
    with mock.patch.dict(os.environ, env, clear=True):
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            _load_with_stub()
    msgs = [str(w.message) for w in caught if issubclass(w.category, RuntimeWarning)]
    assert any("RUSTCHAIN_INSECURE_SKIP_TLS=1" in m for m in msgs), f"expected skip-tls warning, got: {msgs}"


if __name__ == "__main__":
    test_warns_on_plaintext_http_default()
    test_no_warning_on_https_default()
    test_warns_when_insure_skip_tls_set()
    print("OK: 3/3 mcp_server.py security tests passed")
