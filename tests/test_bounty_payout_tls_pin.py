#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""The admin-key transfer must authenticate the node before sending the key.

scripts/bounty_payout.py used `ssl.CERT_NONE` + `check_hostname=False` on the
HTTPS leg, so anyone on-path could terminate TLS with ANY certificate and read
X-Admin-Key. Removing the plaintext fallback (the earlier fix) only stopped
passive sniffing. These tests run a real local TLS server with a self-signed
certificate and check that:

  - with RUSTCHAIN_TLS_PIN_SHA256 matching the cert, the request goes through;
  - with a different pin, the connection is dropped after the handshake and
    NOT ONE BYTE of the request (so not the admin key) reaches the server, and
    transfer() does not then fall back to plaintext even with INSECURE=1;
  - with no pin and no opt-in, the self-signed cert fails CA verification and
    nothing is sent (fail closed);
  - a malformed pin is rejected.
"""
import hashlib
import importlib.util
import os
import shutil
import socket
import ssl
import subprocess
import tempfile
import threading
import unittest
from pathlib import Path
from unittest import mock

os.environ.setdefault("GITHUB_TOKEN", "dummy")
os.environ.setdefault("RTC_ADMIN_KEY", "dummy")
os.environ.setdefault("RTC_VPS_HOST", "127.0.0.1")
os.environ.setdefault("GH_REPO", "owner/repo")

_orig_run = subprocess.run


def _stub_run(*a, **kw):
    class _R:
        stdout = "[]"
        stderr = ""
        returncode = 0
    return _R()


subprocess.run = _stub_run
try:
    SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "bounty_payout.py"
    spec = importlib.util.spec_from_file_location("bounty_payout_tls_pin_test", SCRIPT)
    bp = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bp)
finally:
    subprocess.run = _orig_run


def _make_cert(tmp):
    key, crt = os.path.join(tmp, "k.pem"), os.path.join(tmp, "c.pem")
    _orig_run(["openssl", "req", "-x509", "-newkey", "rsa:2048", "-nodes", "-keyout", key,
               "-out", crt, "-days", "2", "-subj", "/CN=rustchain-test-node"],
              check=True, capture_output=True)
    return key, crt


class _TlsServer:
    """One-connection TLS server that records every byte the client sends."""

    def __init__(self, key, crt):
        self.ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        self.ctx.load_cert_chain(crt, key)
        self.sock = socket.socket()
        self.sock.bind(("127.0.0.1", 0))
        self.sock.listen(1)
        self.port = self.sock.getsockname()[1]
        self.received = b""
        self.t = threading.Thread(target=self._serve, daemon=True)
        self.t.start()

    def _serve(self):
        self.sock.settimeout(10)
        try:
            raw, _ = self.sock.accept()
        except OSError:
            return
        try:
            conn = self.ctx.wrap_socket(raw, server_side=True)
        except (ssl.SSLError, OSError):
            raw.close()
            return
        conn.settimeout(5)
        try:
            while b"\r\n\r\n" not in self.received:
                chunk = conn.recv(65536)
                if not chunk:
                    return
                self.received += chunk
            head, _, rest = self.received.partition(b"\r\n\r\n")
            length = 0
            for line in head.split(b"\r\n"):
                if line.lower().startswith(b"content-length:"):
                    length = int(line.split(b":", 1)[1])
            while len(rest) < length:
                chunk = conn.recv(65536)
                if not chunk:
                    break
                rest += chunk
                self.received += chunk
            payload = b'{"ok": true, "tx_hash": "t1"}'
            conn.sendall(b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\n"
                         b"Content-Length: " + str(len(payload)).encode() +
                         b"\r\nConnection: close\r\n\r\n" + payload)
        except (ssl.SSLError, OSError):
            pass
        finally:
            conn.close()

    def close(self):
        self.t.join(timeout=10)
        self.sock.close()


@unittest.skipUnless(shutil.which("openssl"), "openssl CLI needed to mint a test cert")
class TlsPinTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tmp = tempfile.mkdtemp()
        cls.key, cls.crt = _make_cert(cls.tmp)
        der = ssl.PEM_cert_to_DER_cert(Path(cls.crt).read_text())
        cls.pin = hashlib.sha256(der).hexdigest()

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.tmp, ignore_errors=True)

    def setUp(self):
        self.srv = _TlsServer(self.key, self.crt)
        self.url = f"https://127.0.0.1:{self.srv.port}/wallet/transfer"
        self.env = mock.patch.dict(os.environ, {"RTC_ADMIN_KEY": "dummy"})
        self.env.start()
        for k in ("RUSTCHAIN_TLS_PIN_SHA256", "RUSTCHAIN_PAYOUT_INSECURE", "RUSTCHAIN_CA_BUNDLE"):
            os.environ.pop(k, None)

    def tearDown(self):
        self.srv.close()
        self.env.stop()

    def test_matching_pin_sends_request(self):
        os.environ["RUSTCHAIN_TLS_PIN_SHA256"] = self.pin
        resp = bp._post(self.url, b'{"x": 1}')
        self.srv.close()
        self.assertEqual(resp, {"ok": True, "tx_hash": "t1"})
        self.assertIn(b"POST /wallet/transfer", self.srv.received)
        self.assertIn(b"X-Admin-Key", self.srv.received)

    def test_openssl_fingerprint_format_is_accepted(self):
        pretty = ":".join(self.pin[i:i + 2] for i in range(0, 64, 2)).upper()
        os.environ["RUSTCHAIN_TLS_PIN_SHA256"] = f"SHA256 Fingerprint={pretty}"
        self.assertEqual(bp._post(self.url, b"{}")["ok"], True)

    def test_wrong_pin_sends_nothing(self):
        os.environ["RUSTCHAIN_TLS_PIN_SHA256"] = "0" * 64
        with self.assertRaises(bp.TlsPinMismatch):
            bp._post(self.url, b'{"x": 1}')
        self.srv.close()
        self.assertEqual(self.srv.received, b"", "admin key request reached an unpinned server")

    def test_self_signed_without_pin_fails_closed(self):
        with self.assertRaises(ssl.SSLCertVerificationError):
            bp._post(self.url, b'{"x": 1}')
        self.srv.close()
        self.assertEqual(self.srv.received, b"")

    def test_pin_mismatch_never_falls_back_to_plaintext(self):
        calls = []
        real_post = bp._post

        def spy(url, body):
            calls.append(url)
            return real_post(url, body)

        os.environ["RUSTCHAIN_TLS_PIN_SHA256"] = "1" * 64
        os.environ["RUSTCHAIN_PAYOUT_INSECURE"] = "1"
        with mock.patch.object(bp, "_post", spy), \
                mock.patch.object(bp, "HOST", f"127.0.0.1:{self.srv.port}"):
            ok, resp = bp.transfer("alice", "memo", "idem-pin")
        self.assertFalse(ok)
        self.assertIn("tls_pin_mismatch", resp)
        self.assertEqual(len(calls), 1, calls)
        self.assertTrue(calls[0].startswith("https://"))



class PinFormatTests(unittest.TestCase):
    def test_malformed_pin_is_rejected(self):
        with mock.patch.dict(os.environ, {"RUSTCHAIN_TLS_PIN_SHA256": "not-a-hash"}):
            with self.assertRaises(ValueError):
                bp._tls_pin()

    def test_unset_pin_is_empty(self):
        with mock.patch.dict(os.environ, {}):
            os.environ.pop("RUSTCHAIN_TLS_PIN_SHA256", None)
            self.assertEqual(bp._tls_pin(), "")


if __name__ == "__main__":
    unittest.main()
