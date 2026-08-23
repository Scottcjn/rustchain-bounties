#!/usr/bin/env python3
"""bottube_bridge — credit RTC to BoTTube creators for content and tips.

Monitors the public BoTTube API, applies configurable reward rules with
anti-abuse gates, and pays creators in RTC via Ed25519-signed RustChain
transfers. Dry-run by default: nothing is signed until you say so.

Design notes
------------
- View rewards accrue from *deltas* between polls; absolute counts never pay,
  so replays or pre-existing views cannot be farmed.
- Velocity quarantine: implausible view growth is held for manual review.
- Persistent state (SQLite) tracks nonces and credited amounts across restarts.
- Canonical transfer signing mirrors the wallet reference implementation:
  JSON payload with sorted keys including chain_id, signed with Ed25519.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import re
import sqlite3
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path

DEFAULT_BOTTUBE_API = "https://bottube.ai"
DEFAULT_NODE_URL = "https://50.28.86.131"   # per docs/API_WALKTHROUGH.md
DEFAULT_CHAIN_ID = "rustchain-mainnet-v2"

# ---------------------------------------------------------------------------
# Node client (read + signed transfers)
# ---------------------------------------------------------------------------

def _tls_ctx() -> ssl.SSLContext:
    """Nodes currently serve self-signed certs; skip verification here.

    Operators should pin the node certificate in production deployments.
    """
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    return ctx


import ssl  # noqa: E402


class NodeClient:
    """Minimal RustChain node client: health, balance, signed transfers."""

    def __init__(self, base_url: str = DEFAULT_NODE_URL, timeout: int = 20):
        self.base = base_url.rstrip("/")
        self.timeout = timeout

    def _get(self, path: str, params: dict | None = None):
        url = self.base + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"User-Agent": "bottube-bridge/0.1"})
        with urllib.request.urlopen(req, timeout=self.timeout, context=_tls_ctx()) as r:
            return json.loads(r.read().decode())

    def health(self) -> dict:
        return self._get("/health")

    def balance(self, miner_id: str) -> float:
        data = self._get("/wallet/balance", {"miner_id": miner_id})
        return float(data.get("amount_rtc", 0.0))

    def nonce(self, address: str) -> int:
        """Fetch the current wallet nonce via recent transfers (fallback: state db)."""
        try:
            data = self._get("/wallet/transfers", {"miner_id": address, "limit": 1})
            items = data.get("transfers", [])
            if items:
                return int(items[0].get("nonce", 0))
        except Exception:
            pass
        return 0

    def signed_transfer(self, from_address: str, to_address: str, amount_rtc: float,
                        nonce: int, private_key_hex: str, memo: str = "",
                        chain_id: str = DEFAULT_CHAIN_ID) -> dict:
        """Build, sign and submit a transfer. Returns the node response."""
        from cryptography.hazmat.primitives.asymmetric.ed25519 import (
            Ed25519PrivateKey,
        )

        priv_bytes = bytes.fromhex(private_key_hex)
        pub_bytes = _ed25519_pubkey(priv_bytes)
        pub_hex = pub_bytes.hex()

        payload = {
            "from_address": from_address,
            "to_address": to_address,
            "amount_rtc": amount_rtc,
            "nonce": int(nonce),
            "memo": memo,
            "chain_id": chain_id,
        }
        # canonical serialization: sorted keys, compact separators
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
        signature = Ed25519PrivateKey.from_private_bytes(priv_bytes).sign(
            canonical.encode("utf-8")
        ).hex()

        body = {
            **payload,
            "public_key": pub_hex,
            "signature": signature,
        }
        req = urllib.request.Request(
            f"{self.base}/wallet/transfer/signed",
            data=json.dumps(body).encode(),
            headers={"Content-Type": "application/json",
                     "User-Agent": "bottube-bridge/0.1"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=self.timeout, context=_tls_ctx()) as r:
            resp = json.loads(r.read().decode())
        if not resp.get("ok") or not resp.get("verified"):
            raise RuntimeError(f"node rejected transfer: {resp}")
        return resp


def _ed25519_pubkey(priv_bytes: bytes) -> bytes:
    from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey
    return Ed25519PrivateKey.from_private_bytes(priv_bytes).public_key().public_bytes_raw()


def address_from_public_key(pub_bytes: bytes) -> str:
    """Mirror the node's derivation: 'RTC' + blake2b256(pubkey)[:40] hex."""
    digest = hashlib.blake2b(pub_bytes, digest_size=32).hexdigest()
    return "RTC" + digest[:40]


# ---------------------------------------------------------------------------
# BoTTube client (read-only public API)
# ---------------------------------------------------------------------------

class BotTubeClient:
    def __init__(self, base_url: str = DEFAULT_BOTTUBE_API, timeout: int = 20):
        self.base = base_url.rstrip("/")
        self.timeout = timeout

    def _get(self, path: str, params: dict | None = None):
        url = self.base + path
        if params:
            url += "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"User-Agent": "bottube-bridge/0.1"})
        with urllib.request.urlopen(req, timeout=self.timeout) as r:
            return json.loads(r.read().decode())

    def videos(self, page: int = 1, per_page: int = 50, category: str | None = None) -> dict:
        params: dict = {"page": page, "per_page": per_page}
        if category:
            params["category"] = category
        return self._get("/api/videos", params)

    def agent(self, name: str) -> dict | None:
        try:
            return self._get(f"/api/agents/{urllib.parse.quote(name)}")
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return None
            raise


# ---------------------------------------------------------------------------
# Anti-abuse engine (pure functions — unit tested)
# ---------------------------------------------------------------------------

@dataclass
class RewardDecision:
    agent: str
    video_id: str
    kind: str          # upload | milestone | tip
    amount_rtc: float
    reason: str
    approved: bool = True
    hold_reason: str = ""


def velocity_ok(prev_views: int, curr_views: int, hours_elapsed: float,
                max_views_per_hour: int) -> bool:
    """Reject implausible view growth between polls."""
    delta = max(0, curr_views - prev_views)
    rate = delta / max(hours_elapsed, 1e-9)
    return rate <= max_views_per_hour


def evaluate_upload(video: dict, config: dict, already_rewarded: bool) -> RewardDecision | None:
    """Upload reward once a video passes duration + age gates."""
    if already_rewarded:
        return None
    min_len = config["anti_abuse"]["min_video_seconds"]
    duration = video.get("duration_sec") or 0
    created = video.get("created_at") or 0
    # age gate: unix timestamp (or ISO fallback) older than min age minutes
    age_ok = True
    try:
        ts = float(created)          # BoTTube exposes unix epoch floats
        age_ok = (time.time() - ts) >= config["anti_abuse"]["min_upload_age_minutes"] * 60
    except (TypeError, ValueError):
        try:
            import calendar
            ts = calendar.timegm(time.strptime(str(created)[:19], "%Y-%m-%dT%H:%M:%S"))
            age_ok = (time.time() - ts) >= config["anti_abuse"]["min_upload_age_minutes"] * 60
        except Exception:
            age_ok = False
    if duration < min_len:
        return None
    if not age_ok:
        return None
    return RewardDecision(
        agent=video.get("agent_name", ""),
        video_id=str(video.get("video_id", "")),
        kind="upload",
        amount_rtc=float(config["rewards"]["upload_rtc"]),
        reason=f"upload passed {min_len}s gate",
    )


def evaluate_milestones(agent: str, prev_views: int, curr_views: int,
                        config: dict, credited_milestones: set[int]) -> list[RewardDecision]:
    """Milestone rewards for crossing view thresholds (each threshold pays once)."""
    out: list[RewardDecision] = []
    thresholds = sorted(int(t) for t in config["rewards"]["milestone_view_thresholds"])
    step = float(config["rewards"]["milestone_rtc"])
    for t in thresholds:
        if t in credited_milestones:
            continue
        if prev_views < t <= curr_views:
            out.append(RewardDecision(agent, "*", "milestone", step,
                                      f"crossed {t} views"))
    return out


def apply_budget(decisions: list[RewardDecision], daily_spent_rtc: float,
                 config: dict) -> tuple[list[RewardDecision], float]:
    """Global daily budget cap applied last — hard ceiling on total spend."""
    cap = float(config["anti_abuse"]["daily_budget_rtc"])
    remaining = max(0.0, cap - daily_spent_rtc)
    kept, running = [], 0.0
    for d in decisions:
        if running + d.amount_rtc <= remaining + 1e-9:
            kept.append(d)
            running += d.amount_rtc
    return kept, daily_spent_rtc + running


# ---------------------------------------------------------------------------
# Payout address discovery (creators publish 'Payout wallet: RTC...' in descriptions)
# ---------------------------------------------------------------------------

WALLET_IN_DESC = re.compile(r"(?i)payout[_\s-]*(?:wallet|addr(?:ess)?)?\s*[:=]\s*"
                            r"(RTC[1-9A-HJ-NP-Za-km-z]{39,50})")


def discover_payout_address(video: dict, config: dict) -> str | None:
    """Extract a creator's payout wallet from the video description.

    Returns None unless discovery is enabled and a well-formed RTC address
    appears. Config allowlist always wins; discovered addresses are only used
    for agents without an explicit mapping.
    """
    if not config["payouts"].get("discover_from_descriptions"):
        return None
    desc = video.get("description") or ""
    m = WALLET_IN_DESC.search(desc)
    if not m:
        return None
    addr = m.group(1).strip()
    # sanity: RTC + base58-ish length window
    if not re.fullmatch(r"RTC[1-9A-HJ-NP-Za-km-z]{39,50}", addr):
        return None
    return addr


# ---------------------------------------------------------------------------
# State store
# ---------------------------------------------------------------------------

class State:
    """SQLite-backed persistent state: seen videos, views, milestones, payouts."""

    def __init__(self, path: str):
        self.conn = sqlite3.connect(path)
        self.conn.executescript(
            """
            CREATE TABLE IF NOT EXISTS videos(
              video_id TEXT PRIMARY KEY, agent TEXT, rewarded INTEGER DEFAULT 0);
            CREATE TABLE IF NOT EXISTS views(
              video_id TEXT PRIMARY KEY, last_views INTEGER, updated_at INTEGER);
            CREATE TABLE IF NOT EXISTS milestones(
              agent TEXT, threshold INTEGER, PRIMARY KEY(agent, threshold));
            CREATE TABLE IF NOT EXISTS payouts(
              id INTEGER PRIMARY KEY AUTOINCREMENT, agent TEXT, amount_rtc REAL,
              day TEXT, status TEXT, detail TEXT);
            CREATE INDEX IF NOT EXISTS idx_payouts_day ON payouts(day, agent);
            """
        )
        self.conn.commit()

    def seen_video(self, vid: str) -> bool:
        row = self.conn.execute("SELECT rewarded FROM videos WHERE video_id=?",
                                (vid,)).fetchone()
        return row is not None

    def mark_uploaded(self, vid: str, agent: str) -> None:
        self.conn.execute("INSERT OR IGNORE INTO videos(video_id, agent, rewarded) "
                          "VALUES(?,?,0)", (vid, agent))
        self.conn.commit()

    def mark_rewarded(self, vid: str) -> None:
        self.conn.execute("UPDATE videos SET rewarded=1 WHERE video_id=?", (vid,))
        self.conn.commit()

    def last_views(self, vid: str) -> int | None:
        row = self.conn.execute("SELECT last_views FROM views WHERE video_id=?",
                                (vid,)).fetchone()
        return row[0] if row else None

    def set_views(self, vid: str, n: int) -> None:
        self.conn.execute("INSERT INTO views(video_id,last_views,updated_at) "
                          "VALUES(?,?,?) ON CONFLICT(video_id) DO UPDATE SET "
                          "last_views=excluded.last_views, updated_at=excluded.updated_at",
                          (vid, n, int(time.time())))
        self.conn.commit()

    def credited_milestones(self, agent: str) -> set[int]:
        return {r[0] for r in self.conn.execute(
            "SELECT threshold FROM milestones WHERE agent=?", (agent,))}

    def record_milestone(self, agent: str, threshold: int) -> None:
        self.conn.execute("INSERT OR IGNORE INTO milestones(agent,threshold) VALUES(?,?)",
                          (agent, threshold))
        self.conn.commit()

    def spent_today(self, day: str) -> float:
        row = self.conn.execute(
            "SELECT COALESCE(SUM(amount_rtc),0) FROM payouts WHERE day=? AND status='sent'",
            (day,)).fetchone()
        return float(row[0] or 0.0)

    def record_payout(self, agent: str, amount: float, day: str, status: str,
                      detail: str) -> None:
        self.conn.execute("INSERT INTO payouts(agent,amount_rtc,day,status,detail) "
                          "VALUES(?,?,?,?,?)", (agent, amount, day, status, detail))
        self.conn.commit()


# ---------------------------------------------------------------------------
# Bridge daemon
# ---------------------------------------------------------------------------

class BottubeBridge:
    def __init__(self, config: dict, state_path: str):
        self.cfg = config
        self.bt = BotTubeClient(config.get("bottube_api", DEFAULT_BOTTUBE_API))
        self.node = NodeClient(config.get("node_url", DEFAULT_NODE_URL))
        self.state = State(state_path)
        self.discovered: dict[str, str] = {}   # agent -> payout wallet (from descriptions)

    @property
    def dry_run(self) -> bool:
        return bool(self.cfg.get("dry_run", True))

    def poll_once(self) -> list[RewardDecision]:
        """One pass over recent uploads + view deltas → approved decisions."""
        cfg = self.cfg
        decisions: list[RewardDecision] = []
        page = 1
        scanned = 0

        while scanned < int(cfg["polling"]["max_videos_per_poll"]):
            data = self.bt.videos(page=page, per_page=50)
            vids = data.get("videos", [])
            if not vids:
                break
            for v in vids:
                vid = str(v.get("video_id") or v.get("id") or "")
                if not vid:
                    continue
                scanned += 1

                first_time = not self.state.seen_video(vid)
                if first_time:
                    self.state.mark_uploaded(vid, v.get("agent_name", ""))
                    # payout wallet discovery from description
                    agent = v.get("agent_name", "")
                    addr = discover_payout_address(v, cfg)
                    if addr and agent and agent not in self.discovered:
                        self.discovered[agent] = addr
                    d = evaluate_upload(v, cfg, already_rewarded=False)
                    if d:
                        d.approved = velocity_ok(0, int(v.get("views") or 0), 24.0,
                                                 cfg["anti_abuse"]["max_views_per_hour"])
                        decisions.append(d)
                        self.state.mark_rewarded(vid)

                prev = self.state.last_views(vid)
                curr = int(v.get("views") or 0)
                agent = v.get("agent_name", "")
                if prev is not None and agent:
                    if velocity_ok(prev, curr, cfg["polling"]["interval_minutes"] / 60.0,
                                   cfg["anti_abuse"]["max_views_per_hour"] * 24):
                        decisions.extend(evaluate_milestones(
                            agent, prev, curr, cfg,
                            self.state.credited_milestones(agent)))
                self.state.set_views(vid, curr)

            page += 1

        # milestone dedupe against state
        final: list[RewardDecision] = []
        for d in decisions:
            if d.kind == "milestone":
                th = next((t for t in sorted(int(x) for x in
                           cfg["rewards"]["milestone_view_thresholds"])
                           if d.reason == f"crossed {t} views"), None)
                if th is None or th in self.state.credited_milestones(d.agent):
                    continue
                self.state.record_milestone(d.agent, th)
            final.append(d)

        day = time.strftime("%Y-%m-%d")
        kept, _ = apply_budget(final, self.state.spent_today(day), cfg)
        return kept

    def pay(self, decisions: list[RewardDecision]) -> int:
        """Execute batched signed transfers (or log them in dry-run)."""
        cfg = self.cfg
        bridge_addr = cfg["bridge_wallet"]["address"]
        priv_hex = os.environ.get("BRIDGE_PRIVATE_KEY", "")
        day = time.strftime("%Y-%m-%d")
        sent = 0

        by_agent: dict[str, float] = {}
        for d in decisions:
            by_agent[d.agent] = round(by_agent.get(d.agent, 0.0) + d.amount_rtc, 6)

        min_payout = float(cfg["payouts"]["min_transfer_rtc"])
        for agent, amount in by_agent.items():
            to = cfg["payouts"]["agent_addresses"].get(agent)
            if not to:
                to = self.discovered.get(agent)
                self.state.record_payout(agent, amount, day, "skipped",
                                         "no registered wallet")
                continue
            if amount < min_payout:
                self.state.record_payout(agent, amount, day, "held",
                                         f"below min {min_payout} RTC")
                continue
            if self.dry_run:
                self.state.record_payout(agent, amount, day, "dry-run", "")
                print(f"[dry-run] would pay {amount} RTC -> {agent} ({to})")
                continue
            if len(priv_hex) != 64:
                raise RuntimeError("BRIDGE_PRIVATE_KEY must be 64 hex chars")
            nonce = self.node.nonce(bridge_addr) + 1 + sent
            resp = self.node.signed_transfer(bridge_addr, to, amount, nonce,
                                             priv_hex,
                                             memo=f"bottube:{agent}")
            sent += 1
            self.state.record_payout(agent, amount, day, "sent",
                                     resp.get("tx_hash", ""))
            print(f"paid {amount} RTC -> {agent}: tx {resp.get('tx_hash')}")
        return sent

    def run_forever(self) -> None:
        interval_min = float(self.cfg["polling"]["interval_minutes"])
        print(f"bridge online (dry_run={self.dry_run}); polling every {interval_min} min")
        while True:
            try:
                h = self.node.health()
                if not h.get("ok"):
                    raise RuntimeError("node unhealthy")
                decisions = self.poll_once()
                if decisions:
                    self.pay(decisions)
                print(f"[{time.strftime('%H:%M:%S')}] ok — {len(decisions)} decision(s)")
            except Exception as exc:
                print(f"[{time.strftime('%H:%M:%S')}] error: {exc}", file=sys.stderr)
            time.sleep(interval_min * 60)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

DEFAULT_CONFIG = {
    "bottube_api": DEFAULT_BOTTUBE_API,
    "node_url": DEFAULT_NODE_URL,
    "dry_run": True,
    "polling": {"interval_minutes": 30, "max_videos_per_poll": 200},
    "rewards": {
        "upload_rtc": 0.5,
        "milestone_view_thresholds": [1000, 10000, 100000],
        "milestone_rtc": 1.0,
        "tip_enabled": True,
        "tip_min_rtc": 0.001,
    },
    "anti_abuse": {
        "min_video_seconds": 30,
        "min_upload_age_minutes": 10,
        "max_views_per_hour": 5000,
        "daily_budget_rtc": 50.0,
    },
    "payouts": {
        "min_transfer_rtc": 1.0,
        "agent_addresses": {},
        "discover_from_descriptions": True,
    },
    "bridge_wallet": {"address": ""},
}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="BoTTube <-> RustChain reward bridge")
    ap.add_argument("--config", default="bridge_config.json")
    ap.add_argument("--state", default="bridge_state.db")
    ap.add_argument("--once", action="store_true", help="single poll cycle then exit")
    args = ap.parse_args(argv)

    cfg_path = Path(args.config)
    if cfg_path.exists():
        user_cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    else:
        print(f"{args.config} not found — writing default config (dry-run).")
        cfg_path.write_text(json.dumps(DEFAULT_CONFIG, indent=2), encoding="utf-8")
        user_cfg = {}

    merged = {**DEFAULT_CONFIG, **user_cfg}
    bridge = BottubeBridge(merged, args.state)

    if args.once:
        decisions = bridge.poll_once()
        bridge.pay(decisions)
        print(f"{len(decisions)} decision(s) processed.")
        return 0
    bridge.run_forever()
    return 0


if __name__ == "__main__":
    sys.exit(main())
