"""Tests for elyan-staking-sdk C-1 fix: real on-chain verification via the gate
endpoint. Covers the three blockers flagged on #16787:

  1. The poll URL must be a real template literal that embeds the validated
     txId, not a bare ${this.gateEndpoint}/poll/ string.
  2. The Authorization header must use a real template literal, not the
     escaped literal backslash-Bearer-backslash.
  3. The fail-closed path must reject malformed txIds up front, before
     the network call.

A Python http.server mock stands in for the RustChain gate endpoint so the
compiled JS can be exercised end-to-end against a recorded request.
"""
from __future__ import annotations

import contextlib
import http.server
import json
import os
import socket
import subprocess
import threading
import time
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[1]
SDK_DIR = REPO_ROOT / "elyan-staking-sdk"
INDEX_TS = SDK_DIR / "index.ts"


def _start_mock_gate(responses):
    captured = []
    queue = list(responses)

    class _Handler(http.server.BaseHTTPRequestHandler):
        def log_message(self, *_args):
            pass

        def do_GET(self):
            captured.append({
                "method": "GET",
                "path": self.path,
                "headers": {k.lower(): v for k, v in self.headers.items()},
            })
            if not queue:
                self.send_response(500)
                self.end_headers()
                return
            body = queue.pop(0)
            payload = json.dumps(body).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("127.0.0.1", 0))
    port = sock.getsockname()[1]
    sock.close()
    server = http.server.HTTPServer(("127.0.0.1", port), _Handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return f"http://127.0.0.1:{port}", captured, server


@contextlib.contextmanager
def mock_gate(responses):
    base_url, captured, server = _start_mock_gate(responses)
    try:
        yield base_url, captured
    finally:
        server.shutdown()


@pytest.fixture(scope="module")
def compiled_sdk(tmp_path_factory):
    tsc_candidates = [
        SDK_DIR / "node_modules" / ".bin" / "tsc.cmd",
        SDK_DIR / "node_modules" / ".bin" / "tsc.ps1",
        SDK_DIR / "node_modules" / ".bin" / "tsc",
    ]
    tsc = next((p for p in tsc_candidates if p.exists()), None)
    if tsc is None:
        pytest.skip("tsc not installed in elyan-staking-sdk/node_modules")
    out_dir = tmp_path_factory.mktemp("elyan-sdk-out")
    result = subprocess.run(
        [str(tsc), "-p", str(SDK_DIR), "--outDir", str(out_dir)],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        pytest.fail("tsc failed:\n" + result.stdout + "\n" + result.stderr)
    js_path = out_dir / "index.js"
    if not js_path.exists():
        pytest.skip("tsc did not emit index.js")
    return js_path


def _run_node(js_path, gate_url, tx_id_expr, call_expr):
    node_modules = SDK_DIR / "node_modules"
    if not (node_modules / "axios").exists():
        pytest.skip("axios not installed in elyan-staking-sdk/node_modules")
    nm_str = json.dumps(str(node_modules))
    js_str = json.dumps(str(js_path))
    gate_str = json.dumps(gate_url)
    full_script = (
        "const Module = require('module');\n"
        f"Module.globalPaths.push({nm_str});\n"
        f"const {{ StakingClient }} = require({js_str});\n"
        f"const client = new StakingClient('apikey-test', '00', {gate_str});\n"
        f"client.{call_expr}.then(r => console.log('RESULT:' + r)).catch(e => console.log('ERROR:' + e.message));\n"
    )
    env = os.environ.copy()
    env["NODE_PATH"] = str(node_modules)
    proc = subprocess.run(
        ["node", "-e", full_script],
        capture_output=True,
        text=True,
        env=env,
        timeout=20,
    )
    return (proc.stdout or "") + ("\n--- STDERR ---\n" + proc.stderr if proc.stderr else "")


VALID_TX = "deadbeef" + "00" * 30  # 64-hex, matches /^[0-9a-fA-F]{8,128}$/


# Source-level regression checks

def test_source_has_no_bare_gate_endpoint_poll():
    """The old buggy line `${this.gateEndpoint}/poll/,` (bare $-expression,
    no backticks) must not exist anywhere in index.ts."""
    src = INDEX_TS.read_text(encoding="utf-8")
    assert "${this.gateEndpoint}/poll/," not in src, (
        "bare un-backticked `${this.gateEndpoint}/poll/,` still in source; "
        "this is the syntax error flagged by the reviewer."
    )


def test_source_has_no_literal_backslash_bearer():
    """The old buggy header `Authorization: \\Bearer \\` (literal backslashes)
    must not exist anywhere in index.ts."""
    src = INDEX_TS.read_text(encoding="utf-8")
    assert "\\Bearer \\" not in src, (
        "literal `\\Bearer \\` still in source; header template is broken."
    )


def test_poll_url_embeds_txid_in_template_literal():
    """pollImpl must fetch a backtick-enclosed URL that interpolates the
    validated txId; this is the gate that the validated variable is
    actually placed into the request path."""
    src = INDEX_TS.read_text(encoding="utf-8")
    needle = "${this.gateEndpoint}/poll/${txId}"
    assert needle in src, (
        f"expected pollImpl to fetch `${{this.gateEndpoint}}/poll/${{txId}}` "
        f"(inside backticks), but did not find it in source."
    )


def test_authorization_header_is_template_literal():
    """The Authorization header must be a backtick template literal that
    interpolates this.apiKey, not the escaped literal."""
    src = INDEX_TS.read_text(encoding="utf-8")
    needle = "Authorization: `Bearer ${this.apiKey}`"
    assert needle in src, (
        f"expected `Authorization: \\`Bearer ${{this.apiKey}}\\``, "
        f"but did not find it."
    )


def test_pollImpl_url_compiles_as_real_template(compiled_sdk):
    """The compiled JS must contain the runtime URL with the txId
    interpolated into the path component."""
    js = compiled_sdk.read_text(encoding="utf-8")
    assert "`${this.gateEndpoint}/poll/${txId}`" in js, (
        "compiled JS does not embed txId into the poll URL; reviewer blocker."
    )


# End-to-end: hit a mock gate endpoint

def test_pollImpl_calls_mock_gate_with_txid_in_path(compiled_sdk):
    with mock_gate([{"status": "finalized"}]) as (base_url, captured):
        call = f"pollImpl({json.dumps(VALID_TX)})"
        _ = _run_node(compiled_sdk, base_url, VALID_TX, call)
        time.sleep(0.3)
    assert captured, "mock gate received no requests"
    req = captured[0]
    assert req["method"] == "GET"
    assert req["path"].endswith("/poll/" + VALID_TX), (
        f"expected mock gate path to end with /poll/{VALID_TX}, "
        f"got {req['path']!r}"
    )
    auth = req["headers"].get("authorization", "")
    assert auth.startswith("Bearer "), (
        f"expected Authorization: Bearer <key>, got {auth!r}"
    )


def test_pollImpl_returns_true_on_finalized(compiled_sdk):
    with mock_gate([{"status": "finalized"}]) as (base_url, _):
        out = _run_node(compiled_sdk, base_url, VALID_TX, f"pollImpl({json.dumps(VALID_TX)})")
        time.sleep(0.3)
    assert "RESULT:true" in out, f"expected finalized->true, got:\n{out}"


def test_pollImpl_returns_false_on_unknown_status(compiled_sdk):
    with mock_gate([{"status": "pending"}]) as (base_url, _):
        out = _run_node(compiled_sdk, base_url, VALID_TX, f"pollImpl({json.dumps(VALID_TX)})")
        time.sleep(0.3)
    assert "RESULT:false" in out, f"expected pending->false, got:\n{out}"


def test_pollImpl_rejects_invalid_txid_without_calling_gate(compiled_sdk):
    with mock_gate([]) as (base_url, captured):
        out = _run_node(compiled_sdk, base_url, "../etc/passwd",
                        "pollImpl('../etc/passwd')")
        time.sleep(0.3)
    assert captured == [], (
        f"mock gate should not have been hit for an invalid txId; got {captured}"
    )
    assert "ERROR:Invalid txId format" in out, (
        f"expected fail-closed 'Invalid txId format', got:\n{out}"
    )