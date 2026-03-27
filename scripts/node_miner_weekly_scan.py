#!/usr/bin/env python3
"""RustChain weekly node/miner scan for payout and upgrade outreach.

This script is intended for maintainer ops:
- Scan registered nodes and determine weekly node-host payout candidates.
- Scan attesting miners visible from public node APIs.
- Flag expected miners that are missing (likely outdated client/offline/wrong node).

Default scan source is the public primary node:
  https://50.28.86.131
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
    network_version = seed_health.get("version", "") if isinstance(seed_health, dict) else ""

    epoch_payload, epoch_err = fetch_json(
        seed, "/epoch", timeout_s=args.timeout, headers=headers, verify_tls=args.verify_tls
    )
    nodes_payload, nodes_err = fetch_json(
        seed, "/api/nodes", timeout_s=args.timeout, headers=headers, verify_tls=args.verify_tls
    )

    registry_map, registry_rows = _registry_rows_to_map(nodes_payload)
    discovered_urls = [seed]
    discovered_urls.extend([str(r.get("url", "")).strip() for r in registry_rows if r.get("url")])
    for extra in args.node_url:
        discovered_urls.append(extra)
    node_urls = _dedupe_preserve(discovered_urls)

    node_rows: List[Dict[str, Any]] = []
    node_miners: Dict[str, List[Dict[str, Any]]] = {}
    version_mismatch: List[Dict[str, Any]] = []

    for node_url in node_urls:
        key = node_identity(node_url)
        registry = registry_map.get(key, {})

        health_payload, health_err = fetch_json(
            node_url, "/health", timeout_s=args.timeout, headers=headers, verify_tls=args.verify_tls
        )
        miners_payload, miners_err = fetch_json(
            node_url, "/api/miners", timeout_s=args.timeout, headers=headers, verify_tls=args.verify_tls
        )

        online = isinstance(health_payload, dict) and health_err is None
        node_version = ""
        uptime_s = None
        if isinstance(health_payload, dict):
            node_version = str(health_payload.get("version", ""))
            uptime_s = health_payload.get("uptime_s")

        is_active = bool(registry.get("is_active", True if node_url == seed else False))
        payout_eligible, action = classify_node_host(
            is_active=is_active,
            online=online,
            node_version=node_version,
            network_version=network_version,
        )

        if action == "pay_weekly_and_upgrade_node":
            version_mismatch.append(
                {
                    "node_url": node_url,
                    "node_id": registry.get("node_id"),
                    "node_version": node_version,
                    "network_version": network_version,
                }
            )

        node_rows.append(
            {
                "node_id": registry.get("node_id") or key,
                "name": registry.get("name") or key,
                "wallet": registry.get("wallet"),
                "url": node_url,
                "is_active": is_active,
                "online": online,
                "health_ok": bool(health_payload.get("ok")) if isinstance(health_payload, dict) else False,
                "version": node_version,
                "uptime_s": uptime_s,
                "payout_eligible": payout_eligible,
                "suggested_action": action,
                "health_error": health_err,
                "miners_error": miners_err,
            }
        )

        miners_list: List[Dict[str, Any]] = []
        if isinstance(miners_payload, list):
            miners_list = [m for m in miners_payload if isinstance(m, dict)]
        node_miners[node_url] = miners_list

    # Include registered nodes that have no public URL (redacted/missing) so they are
    # visible in payout review output instead of silently disappearing.
    scanned_keys = {node_identity(n["url"]) for n in node_rows if n.get("url")}
    for row in registry_rows:
        raw_url = normalize_base_url(str(row.get("url", "")))
        key = node_identity(raw_url) if raw_url else ""
        if raw_url and key in scanned_keys:
            continue
        if not raw_url:
            node_rows.append(
                {
                    "node_id": row.get("node_id") or "unknown_node",
                    "name": row.get("name") or "unknown_node",
                    "wallet": row.get("wallet"),
                    "url": "-",
                    "is_active": bool(row.get("is_active", False)),
                    "online": False,
                    "health_ok": False,
                    "version": "-",
                    "uptime_s": None,
                    "payout_eligible": False,
                    "suggested_action": "missing_url_or_redacted",
                    "health_error": "missing_url",
                    "miners_error": "missing_url",
                }
            )

    aggregate = _aggregate_miners(node_miners)
    miner_rows: List[Dict[str, Any]] = []
    for miner_id, data in aggregate.items():
        classification = classify_miner_age(
            data.get("last_attest"),
            now_ts=now_ts,
            active_window_h=args.active_window_hours,
            weekly_window_h=args.weekly_window_hours,
        )
        miner_rows.append(
            {
                "miner": miner_id,
                "last_attest": data.get("last_attest"),
                "last_attest_utc": ts_to_utc(data.get("last_attest")),
                "age_h": classification.get("age_h"),
                "state": classification["state"],
                "weekly_eligible": classification["weekly_eligible"],
                "suggested_action": classification["suggested_action"],
                "device_family": data.get("device_family"),
                "device_arch": data.get("device_arch"),
                "antiquity_multiplier": data.get("antiquity_multiplier"),
                "nodes_seen": sorted(data.get("nodes_seen", [])),
                "node_count": len(data.get("nodes_seen", [])),
            }
        )
    miner_rows.sort(key=lambda m: (m["age_h"] is None, m["age_h"] if m["age_h"] is not None else 999999, m["miner"]))

    expected = set(args.expected_miner)
    if args.expected_miners_file:
        expected.update(load_expected_miners(args.expected_miners_file))

    observed_miners = {m["miner"] for m in miner_rows}
    missing_expected = sorted(expected - observed_miners)
    missing_expected_rows: List[Dict[str, Any]] = []
    for miner_id in missing_expected:
        missing_expected_rows.append(
            {
                "miner": miner_id,
                "state": "not_visible_in_public_api",
                "weekly_eligible": False,
                "suggested_action": "check_node_url_then_upgrade_miner",
            }
        )

    node_payout_count = sum(1 for n in node_rows if n["payout_eligible"])
    miner_payout_count = sum(1 for m in miner_rows if m["weekly_eligible"])
    offline_node_count = sum(1 for n in node_rows if n["is_active"] and not n["online"])

    return {
        "generated_at": generated_at,
        "seed_node": seed,
        "query_errors": {
            "seed_health": seed_health_err,
            "seed_epoch": epoch_err,
            "seed_nodes": nodes_err,
        },
        "network": {
            "version": network_version,
            "epoch": epoch_payload if isinstance(epoch_payload, dict) else None,
            "health": seed_health if isinstance(seed_health, dict) else None,
        },
        "summary": {
            "nodes_scanned": len(node_rows),
            "active_nodes_online": sum(1 for n in node_rows if n["is_active"] and n["online"]),
            "active_nodes_offline": offline_node_count,
            "node_hosts_weekly_payout_eligible": node_payout_count,
            "miners_observed": len(miner_rows),
            "miners_weekly_payout_eligible": miner_payout_count,
            "expected_miners_missing": len(missing_expected_rows),
            "version_mismatch_nodes": len(version_mismatch),
        },
        "nodes": node_rows,
        "miners": miner_rows,
        "expected_miners_missing_rows": missing_expected_rows,
        "version_mismatch_nodes": version_mismatch,
    }


def _fmt_age(age_h: Optional[float]) -> str:
    if age_h is None:
        return "-"
    return f"{age_h:.2f}"


def _fmt_bool(value: bool) -> str:
    return "yes" if value else "no"


def render_markdown(report: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("# RustChain Weekly Node + Miner Scan")
    lines.append("")
    lines.append(f"- Generated: {report['generated_at']}")
    lines.append(f"- Seed node: {report['seed_node']}")
    lines.append(f"- Network version: {report.get('network', {}).get('version') or '-'}")
    lines.append("")

    summary = report.get("summary", {})
    lines.append("## Summary")
    lines.append("")
    lines.append(f"- Nodes scanned: {summary.get('nodes_scanned', 0)}")
    lines.append(f"- Node hosts weekly payout eligible: {summary.get('node_hosts_weekly_payout_eligible', 0)}")
    lines.append(f"- Active nodes offline: {summary.get('active_nodes_offline', 0)}")
    lines.append(f"- Miners observed: {summary.get('miners_observed', 0)}")
    lines.append(f"- Miners weekly payout eligible: {summary.get('miners_weekly_payout_eligible', 0)}")
    lines.append(f"- Expected miners missing: {summary.get('expected_miners_missing', 0)}")
    lines.append(f"- Version mismatch nodes: {summary.get('version_mismatch_nodes', 0)}")
    lines.append("")

    lines.append("## Node Hosts")
    lines.append("")
    lines.append("| Node | Active | Online | Version | Payout | Action |")
    lines.append("|---|---|---|---|---|---|")
    for n in report.get("nodes", []):
        lines.append(
            f"| {n.get('name') or n.get('node_id')} "
            f"| {_fmt_bool(bool(n.get('is_active')))} "
            f"| {_fmt_bool(bool(n.get('online')))} "
            f"| {n.get('version') or '-'} "
            f"| {_fmt_bool(bool(n.get('payout_eligible')))} "
            f"| {n.get('suggested_action') or '-'} |"
        )
    lines.append("")

    lines.append("## Miners (Observed)")
    lines.append("")
    lines.append("| Miner | Last Attest (UTC) | Age(h) | Mult | Weekly Eligible | Action |")
    lines.append("|---|---|---|---|---|---|")
    for m in report.get("miners", []):
        lines.append(
            f"| {m.get('miner')} "
            f"| {m.get('last_attest_utc')} "
            f"| {_fmt_age(m.get('age_h'))} "
            f"| {m.get('antiquity_multiplier') if m.get('antiquity_multiplier') is not None else '-'} "
            f"| {_fmt_bool(bool(m.get('weekly_eligible')))} "
            f"| {m.get('suggested_action')} |"
        )
    lines.append("")

    missing = report.get("expected_miners_missing_rows", [])
    if missing:
        lines.append("## Expected Miners Missing")
        lines.append("")
        lines.append("| Miner | State | Action |")
        lines.append("|---|---|---|")
        for row in missing:
            lines.append(f"| {row.get('miner')} | {row.get('state')} | {row.get('suggested_action')} |")
        lines.append("")

    mismatch = report.get("version_mismatch_nodes", [])
    if mismatch:
        lines.append("## Version Mismatch Nodes")
        lines.append("")
        lines.append("| Node | Node Version | Network Version |")
        lines.append("|---|---|---|")
        for row in mismatch:
            lines.append(
                f"| {row.get('node_id') or row.get('node_url')} "
                f"| {row.get('node_version') or '-'} "
                f"| {row.get('network_version') or '-'} |"
            )
        lines.append("")

    lines.append("## Recommended Next Steps")
    lines.append("")
    lines.append("1. Queue weekly payouts for all rows marked `pay_weekly` or `pay_weekly_and_upgrade_node`.")
    lines.append("2. DM missing miners with a restart + latest miner update check.")
    lines.append("3. Ask version-mismatch node hosts to upgrade, then re-run this scan.")
    lines.append("")
    return "\n".join(lines)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Weekly RustChain node/miner payout + upgrade scan")
    p.add_argument("--seed-node", default=DEFAULT_SEED_NODE, help="Seed node URL (default: %(default)s)")
    p.add_argument("--node-url", action="append", default=[], help="Additional node URL(s) to scan")
    p.add_argument("--expected-miners-file", default="", help="Path to newline-delimited expected miner IDs")
    p.add_argument(
        "--expected-miner",
        action="append",
        default=[],
        help="Expected miner ID (repeatable). Missing IDs are flagged for outreach.",
    )
    p.add_argument("--active-window-hours", type=float, default=2.0, help="Hours considered actively attesting")
    p.add_argument(
        "--weekly-window-hours",
        type=float,
        default=168.0,
        help="Hours considered weekly payout eligible",
    )
    p.add_argument("--timeout", type=int, default=DEFAULT_TIMEOUT_SECONDS, help="HTTP timeout per request in seconds")
    p.add_argument(
        "--verify-tls",
        action="store_true",
        help="Verify TLS certs (off by default because official node uses self-signed TLS)",
    )
    p.add_argument(
        "--admin-key",
        default="",
        help="Optional admin key. Passed as X-Admin-Key/X-API-Key where required.",
    )
    p.add_argument("--out-json", default="", help="Write machine-readable JSON report to this path")
    p.add_argument("--out-md", default="", help="Write markdown report to this path")
    return p.parse_args()


def main() -> int:
    args = parse_args()
    report = build_report(args)
    markdown = render_markdown(report)

    if args.out_json:
        Path(args.out_json).write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")
    if args.out_md:
        Path(args.out_md).write_text(markdown + "\n", encoding="utf-8")

    if not args.out_md:
        print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
