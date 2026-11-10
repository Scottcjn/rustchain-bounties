# SPDX-License-Identifier: MIT
"""
conftest.py — sets up the fake catalog_cli stub before any test imports it.

This lets tests run stand-alone without the full Rustchain repository checked out.
When running inside the actual Rustchain repo (CI), `catalog_cli` is already
importable from `tools/`; this conftest detects that and skips the stub.
"""
import sys
import types
import hashlib
import json
import secrets
import time
import urllib.parse
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def _make_stub_signed_transfer():
    mod = types.ModuleType("rustchain_signed_transfer")

    def build_signed_transfer(wallet, to_address, amount_rtc, memo, chain_id, nonce=None):
        nonce = nonce or secrets.token_hex(8)
        return {
            "from_address": wallet.address,
            "to_address": to_address,
            "amount_rtc": amount_rtc,
            "memo": memo,
            "chain_id": chain_id,
            "nonce": nonce,
            "public_key": wallet.public_key,
            "signature": wallet.sign_message(
                f"{wallet.address}|{to_address}|{amount_rtc}|{memo}|{nonce}|{chain_id}".encode()
            ),
        }

    def canonical_transfer_message(from_addr, to_addr, amount, memo, nonce, chain_id):
        return f"{from_addr}|{to_addr}|{amount}|{memo}|{nonce}|{chain_id}".encode()

    def chain_id_from_network_info(info):
        return info.get("chain_id", "rustchain-mainnet")

    mod.build_signed_transfer = build_signed_transfer
    mod.canonical_transfer_message = canonical_transfer_message
    mod.chain_id_from_network_info = chain_id_from_network_info
    return mod


def _make_stub_catalog_cli():
    """
    Minimal stub of catalog_cli.py that provides only what the daemon and tests
    need: AgentKey, CatalogClient, CatalogError, urllib_transport, CATEGORIES.
    """
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat

    st = _make_stub_signed_transfer()
    sys.modules["rustchain_signed_transfer"] = st

    mod = types.ModuleType("catalog_cli")
    CATEGORIES = ("render", "review", "hw_test", "vision", "compute",
                  "docs", "translation", "testing", "other")
    PAYMENT_ENDPOINT = "/wallet/transfer/signed"
    DEFAULT_NODE = "https://rustchain.org"

    class CatalogError(Exception):
        def __init__(self, message, status=None, payload=None):
            super().__init__(message)
            self.status = status
            self.payload = payload or {}

    class AgentKey:
        def __init__(self, private_key):
            self._key = private_key
            pub = private_key.public_key().public_bytes(Encoding.Raw, PublicFormat.Raw)
            self.public_key = pub.hex()
            self.agent_id = "bcn_" + hashlib.sha256(pub).hexdigest()[:12]
            self.rtc_address = "RTC" + hashlib.sha256(pub).hexdigest()[:40]
            self.address = self.agent_id  # payer compat

        @classmethod
        def from_seed_hex(cls, seed_hex):
            seed = bytes.fromhex(seed_hex.strip().removeprefix("0x"))
            return cls(Ed25519PrivateKey.from_private_bytes(seed))

        @classmethod
        def load(cls, path=None, password=None):
            import os, getpass
            key_path = Path(path or os.environ.get("BEACON_IDENTITY_PATH",
                                                    Path.home() / ".beacon" / "identity" / "agent.key"))
            key_path = Path(key_path).expanduser()
            if not key_path.exists():
                raise CatalogError(f"no Beacon identity at {key_path}")
            text = key_path.read_text().strip()
            if not text.startswith("{"):
                return cls.from_seed_hex(text)
            data = json.loads(text)
            seed_hex = data.get("private_key_hex") or data.get("seed")
            return cls.from_seed_hex(seed_hex)

        def sign_message(self, message: bytes) -> str:
            return self._key.sign(message).hex()

        def payer(self, pay_from="bcn"):
            return self

    def _safe_id(value):
        value = str(value).strip()
        if not value or any(ch in value for ch in "/?#%\\ ") or value in (".", ".."):
            raise CatalogError(f"invalid id {value!r}")
        return value

    def _price_value(price_rtc):
        from decimal import Decimal, InvalidOperation, ROUND_DOWN
        try:
            d = Decimal(str(price_rtc)).quantize(Decimal("0.000001"), rounding=ROUND_DOWN)
        except (InvalidOperation, ValueError):
            raise CatalogError(f"invalid price {price_rtc!r}")
        if d <= 0:
            raise CatalogError("price must be > 0")
        return float(d)

    class CatalogClient:
        def __init__(self, transport, agent=None):
            self._send = transport
            self.agent = agent

        def _request(self, method, path, payload=None, params=None, signed=False):
            query = {k: v for k, v in (params or {}).items() if v not in (None, "")}
            if query:
                path = f"{path}?{urllib.parse.urlencode(query)}"
            body = b"" if payload is None else json.dumps(payload, separators=(",", ":")).encode()
            headers = {"Accept": "application/json"}
            if payload is not None:
                headers["Content-Type"] = "application/json"
            if signed:
                headers.update(self._auth_headers(method, path, body))
            status, data = self._send(method, path, body, headers)
            if status >= 400:
                message = data.get("error") if isinstance(data, dict) else None
                raise CatalogError(f"{method} {path} -> HTTP {status}: {message or data}",
                                   status=status, payload=data if isinstance(data, dict) else {})
            return data

        def _auth_headers(self, method, path, body):
            if self.agent is None:
                raise CatalogError("this command needs a Beacon identity")
            timestamp = str(int(time.time()))
            nonce = secrets.token_hex(16)
            message = "\n".join([method.upper(), path, hashlib.sha256(body).hexdigest(),
                                 timestamp, nonce, self.agent.agent_id]).encode("utf-8")
            return {
                "X-Agent-Id": self.agent.agent_id,
                "X-Agent-Timestamp": timestamp,
                "X-Agent-Nonce": nonce,
                "X-Agent-Signature": self.agent.sign_message(message),
            }

        def my_orders(self, role="buyer", status=None):
            return self._request("GET", "/catalog/orders", params={"role": role, "status": status},
                                 signed=True)

        def get_order(self, order_id, signed=True):
            return self._request("GET", f"/catalog/orders/{_safe_id(order_id)}", signed=signed)

        def deliver(self, order_id, deliverable_hash, deliverable_uri=None):
            payload = {"deliverable_hash": deliverable_hash.strip().lower()}
            if deliverable_uri:
                payload["deliverable_uri"] = deliverable_uri
            return self._request("POST", f"/catalog/orders/{_safe_id(order_id)}/deliver",
                                 payload, signed=True)

        def accept(self, order_id):
            return self._request("POST", f"/catalog/orders/{_safe_id(order_id)}/accept", {},
                                 signed=True)

        def offer(self, title, category, price_rtc, description="",
                  unit="per job", turnaround_hours=None):
            if category not in CATEGORIES:
                raise CatalogError(f"category must be one of: {', '.join(CATEGORIES)}")
            payload = {"title": title, "description": description, "category": category,
                       "price_rtc": _price_value(price_rtc), "unit": unit}
            if turnaround_hours is not None:
                payload["turnaround_hours"] = int(turnaround_hours)
            return self._request("POST", "/catalog/listings", payload, signed=True)

        def order(self, listing_id, note=""):
            payload = {"listing_id": listing_id}
            if note:
                payload["note"] = note
            return self._request("POST", "/catalog/orders", payload, signed=True)

        def build_payment(self, order_id, pay_from="bcn", nonce=None):
            order = self.get_order(order_id, signed=True)
            if order.get("buyer") != self.agent.agent_id:
                raise CatalogError(f"{self.agent.agent_id} is not the buyer of {order_id}")
            if order.get("status") != "accepted":
                raise CatalogError(f"order {order_id} is not accepted")
            instr = order.get("payment_instructions", {})
            chain_id = instr.get("chain_id", "rustchain-mainnet")
            memo = f"svc:{order['id']}"
            price = float(order["price_rtc"])
            payer_obj = self.agent.payer(pay_from) if hasattr(self.agent, "payer") else self.agent
            body = st.build_signed_transfer(payer_obj, order["provider"], price, memo, chain_id, nonce)
            return {"order": order, "body": body,
                    "signed_message": st.canonical_transfer_message(
                        payer_obj.address, order["provider"], price, memo,
                        body["nonce"], chain_id).decode()}

        def send_payment(self, body):
            return self._request("POST", PAYMENT_ENDPOINT, body)

    def urllib_transport(node, insecure=False, timeout=30.0):
        import urllib.request, ssl, urllib.error
        base = node.rstrip("/")
        context = None
        if insecure:
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

        def transport(method, path, body, headers):
            url = base + path
            req = urllib.request.Request(url, data=body or None, headers=headers, method=method)
            try:
                with urllib.request.urlopen(req, context=context, timeout=timeout) as r:
                    return r.status, json.loads(r.read())
            except urllib.error.HTTPError as exc:
                try:
                    return exc.code, json.loads(exc.read())
                except Exception:
                    return exc.code, {"error": str(exc)}
            except Exception as exc:
                raise CatalogError(str(exc)) from exc
        return transport

    mod.CatalogError = CatalogError
    mod.AgentKey = AgentKey
    mod.CatalogClient = CatalogClient
    mod.urllib_transport = urllib_transport
    mod.CATEGORIES = CATEGORIES
    mod.PAYMENT_ENDPOINT = PAYMENT_ENDPOINT
    mod.DEFAULT_NODE = DEFAULT_NODE
    return mod


# Inject stub if the real catalog_cli is not importable
if "catalog_cli" not in sys.modules:
    try:
        import importlib
        # Try to import from the tools/ path of the actual repo (CI scenario)
        _tools_path = ROOT.parent.parent.parent.parent / "tools"  # from tests/ inside repo
        if (_tools_path / "catalog_cli.py").exists():
            import importlib.util as _util
            _spec = _util.spec_from_file_location("catalog_cli", _tools_path / "catalog_cli.py")
            _mod = _util.module_from_spec(_spec)
            sys.modules["catalog_cli"] = _mod
            _spec.loader.exec_module(_mod)
        else:
            raise ImportError("not in repo")
    except Exception:
        sys.modules["catalog_cli"] = _make_stub_catalog_cli()
