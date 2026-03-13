#!/usr/bin/env python3
"""RustChain weekly node/miner scan for payout and upgrade outreach.

This script is intended for maintainer ops:
- Scan registered nodes and determine weekly node-host payout candidates.
- Scan attesting miners visible from public node APIs.
- Flag expected miners that are missing (likely outdated client/offline/wrong node).

Default scan source is the public primary node:
  https://50.28.86.131
  https://52.55.255.216
  https://3.141.215.213
"""

from __future__ import annotations

import argparse
import json
import ssl
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple
from urllib.error import HTTPError, URLError

DEFAULT_SEED_NODE = "https://50.28.86.131"
DEFAULT_TIMEOUT_SECONDS = 20


def now_utc_ts() -> int:
    return int(datetime.now(timezone.utc).timestamp())


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def ts_to_utc(ts: Optional[int]) -> str:
    if not ts:
        return "-"
    return datetime.fromtimestamp(int(ts), tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def normalize_base_url(raw: str) -> str:
    text = (raw or "").strip()
    if not text:
        return ""
    if "://" not in text:
        text = f"https://{text}"
    parsed = urllib.parse.urlparse(text)
    scheme = parsed.scheme or "https"
    netloc = parsed.netloc or parsed.path
    return f"{scheme}://{netloc}".rstrip("/")


def node_identity(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    host = parsed.hostname or parsed.netloc or url
    port = parsed.port
    if port is None:
        port = 443 if parsed.scheme == "https" else 80
    return f"{host}:{port}"


def _request_json(
    url: str,
    timeout_s: int = DEFAULT_TIMEOUT_SECONDS,
    headers: Optional[Dict[str, str]] = None,
    verify_tls: bool = False,
) -> Tuple[Optional[Any], Optional[str]]:
    req = urllib.request.Request(url)
    req.add_header("Accept", "application/json")
    req.add_header("User-Agent", "rustchain-weekly-scan/1.0")
    for k, v in (headers or {}).items():
        if v:
            req.add_header(k, v)

    context = None
    if url.startswith("https://") and not verify_tls:
        context = ssl._create_unverified_context()

    try:
        with urllib.request.urlopen(req, timeout=timeout_s, context=context) as resp:
            raw = resp.read().decode("utf-8")
        try:
            return json.loads(raw), None
        except json.JSONDecodeError:
            return None, "invalid_json"
    except HTTPError as e:
        return None, f"http_{e.code}"
    except URLError as e:
        return None, f"url_error:{e.reason}"
    except TimeoutError:
        return None, "timeout"
    except Exception as e:  # pragma: no cover - defensive catch for ops script
        return None, f"error:{type(e).__name__}"


def fetch_json(
    base_url: str,
    path: str,
    timeout_s: int = DEFAULT_TIMEOUT_SECONDS,
    headers: Optional[Dict[str, str]] = None,
    verify_tls: bool = False,
) -> Tuple[Optional[Any], Optional[str]]:
    url = f"{base_url.rstrip('/')}{path}"
    return _request_json(url, timeout_s=timeout_s, headers=headers, verify_tls=verify_tls)


def classify_node_host(
    is_active: bool,
    online: bool,
    node_version: str,
    network_version: str,
) -> Tuple[bool, str]:
    """Classify node host payout eligibility and action.

    Rule of thumb:
    - Active + online => eligible for weekly host payout.
    - Version mismatch still pays, but includes upgrade action.
    """
    if not is_active:
        return False, "inactive_no_payout"
    if not online:
        return False, "investigate_offline"
    if network_version and node_version and node_version != network_version:
        return True, "pay_weekly_and_upgrade_node"
    return True, "pay_weekly"


def classify_miner_age(
    last_attest_ts: Optional[int],
    now_ts: int,
    active_window_h: float,
    weekly_window_h: float,
) -> Dict[str, Any]:
    if not last_attest_ts:
        return {
            "age_h": None,
            "state": "unknown",
            "weekly_eligible": False,
            "suggested_action": "request_status_or_upgrade",
        }

    age_h = max(0.0, (now_ts - int(last_attest_ts)) / 3600.0)
    if age_h <= active_window_h:
        return {
            "age_h": age_h,
            "state": "active",
            "weekly_eligible": True,
            "suggested_action": "pay_weekly",
        }
    if age_h <= weekly_window_h:
        return {
            "age_h": age_h,
            "state": "stale_but_weekly_eligible",
            "weekly_eligible": True,
            "suggested_action": "pay_weekly_and_ping_health_check",
        }
    return {
        "age_h": age_h,
        "state": "inactive",
        "weekly_eligible": False,
        "suggested_action": "restart_or_upgrade_miner",
    }


def load_expected_miners(path: str) -> Set[str]:
    expected: Set[str] = set()
    if not path:
        return expected

    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"expected miners file not found: {path}")

    for line in p.read_text(encoding="utf-8").splitlines():
        text = line.strip()
        if not text or text.startswith("#"):
            continue
        if "#" in text:
            text = text.split("#", 1)[0].strip()
        for token in text.replace(",", " ").split():
            cleaned = token.strip()
            if cleaned:
                expected.add(cleaned)
    return expected


def _dedupe_preserve(values: Iterable[str]) -> List[str]:
    out: List[str] = []
    seen: Set[str] = set()
    for v in values:
        norm = normalize_base_url(v)
        if not norm:
            continue
        key = node_identity(norm)
        if key in seen:
            continue
        seen.add(key)
        out.append(norm)
    return out


def _registry_rows_to_map(nodes_payload: Any) -> Tuple[Dict[str, Dict[str, Any]], List[Dict[str, Any]]]:
    rows: List[Dict[str, Any]] = []
    if isinstance(nodes_payload, dict):
        raw_rows = nodes_payload.get("nodes", [])
        if isinstance(raw_rows, list):
            rows = [r for r in raw_rows if isinstance(r, dict)]
    elif isinstance(nodes_payload, list):
        rows = [r for r in nodes_payload if isinstance(r, dict)]

    mapped: Dict[str, Dict[str, Any]] = {}
    for row in rows:
        key = node_identity(normalize_base_url(str(row.get("url", ""))))
        if key:
            mapped[key] = row
    return mapped, rows


def _aggregate_miners(node_miners: Dict[str, List[Dict[str, Any]]]) -> Dict[str, Dict[str, Any]]:
    aggregate: Dict[str, Dict[str, Any]] = {}
    for node_url, rows in node_miners.items():
        for row in rows:
            miner_id = str(row.get("miner", "")).strip()
            if not miner_id:
                continue
            last_attest = int(row.get("last_attest") or 0)
            existing = aggregate.get(miner_id)
            if not existing:
                aggregate[miner_id] = {
                    "miner": miner_id,
                    "last_attest": last_attest if last_attest > 0 else None,
                    "first_attest": row.get("first_attest"),
                    "device_family": row.get("device_family"),
                    "device_arch": row.get("device_arch"),
                    "hardware_type": row.get("hardware_type"),
                    "entropy_score": row.get("entropy_score"),
                    "antiquity_multiplier": row.get("antiquity_multiplier"),
                    "nodes_seen": [node_url],
                }
            else:
                if last_attest and (existing.get("last_attest") or 0) < last_attest:
                    existing["last_attest"] = last_attest
                if node_url not in existing["nodes_seen"]:
                    existing["nodes_seen"].append(node_url)
    return aggregate


def build_report(args: argparse.Namespace) -> Dict[str, Any]:
    now_ts = now_utc_ts()
    generated_at = now_utc_iso()

    seed = normalize_base_url(args.seed_node)
    headers: Dict[str, str] = {}
    if args.admin_key:
        headers["X-Admin-Key"] = args.admin_key
        headers["X-API-Key"] = args.admin_key

    seed_health, seed_health_err = fetch_json(
        seed, "/health", timeout_s=args.timeout, headers=headers, verify_tls=args.verify_tls
    )
    network_version = seed_health.get("version", "") if isinstance(seed_health,