import json
import os
import sys
from unittest.mock import MagicMock, patch


SCRIPTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "scripts")
if SCRIPTS_DIR not in sys.path:
    sys.path.insert(0, SCRIPTS_DIR)

import node_miner_weekly_scan as weekly_scan
import prometheus_exporter
import sophia_scheduler


def _json_response(payload):
    response = MagicMock()
    response.read.return_value = json.dumps(payload).encode("utf-8")
    response.__enter__ = MagicMock(return_value=response)
    response.__exit__ = MagicMock(return_value=False)
    return response


def test_prometheus_exporter_verifies_tls_by_default():
    default_ctx = object()
    with patch("prometheus_exporter.ssl.create_default_context", return_value=default_ctx) as create_ctx, \
         patch("prometheus_exporter.ssl._create_unverified_context") as insecure_ctx, \
         patch("prometheus_exporter.urllib.request.urlopen", return_value=_json_response({"ok": True})) as urlopen:
        data, err, _elapsed = prometheus_exporter._request_json("https://example.test/health")

    assert data == {"ok": True}
    assert err is None
    create_ctx.assert_called_once_with()
    insecure_ctx.assert_not_called()
    assert urlopen.call_args.kwargs["context"] is default_ctx


def test_weekly_scan_verifies_tls_by_default():
    default_ctx = object()
    with patch("node_miner_weekly_scan.ssl.create_default_context", return_value=default_ctx) as create_ctx, \
         patch("node_miner_weekly_scan.ssl._create_unverified_context") as insecure_ctx, \
         patch("node_miner_weekly_scan.urllib.request.urlopen", return_value=_json_response({"ok": True})) as urlopen:
        data, err = weekly_scan._request_json("https://example.test/health")

    assert data == {"ok": True}
    assert err is None
    create_ctx.assert_called_once_with()
    insecure_ctx.assert_not_called()
    assert urlopen.call_args.kwargs["context"] is default_ctx


def test_sophia_scheduler_verifies_tls_by_default():
    default_ctx = object()
    with patch("sophia_scheduler.ssl.create_default_context", return_value=default_ctx) as create_ctx, \
         patch("sophia_scheduler.ssl._create_unverified_context") as insecure_ctx, \
         patch("sophia_scheduler.urllib.request.urlopen", return_value=_json_response({"epoch": 1})) as urlopen:
        data = sophia_scheduler.fetch_node_json("https://example.test", "/epoch")

    assert data == {"epoch": 1}
    create_ctx.assert_called_once_with()
    insecure_ctx.assert_not_called()
    assert urlopen.call_args.kwargs["context"] is default_ctx


def test_cli_verify_tls_flags_remain_accepted():
    assert prometheus_exporter.parse_args([]).verify_tls is True
    assert prometheus_exporter.parse_args(["--verify-tls"]).verify_tls is True
    with patch.object(sys, "argv", ["node_miner_weekly_scan.py"]):
        assert weekly_scan.parse_args().verify_tls is True
    with patch.object(sys, "argv", ["node_miner_weekly_scan.py", "--verify-tls"]):
        assert weekly_scan.parse_args().verify_tls is True
