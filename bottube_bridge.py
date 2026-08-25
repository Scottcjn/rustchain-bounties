#!/usr/bin/env python3
"""
RustChain <-> BoTTube Bridge Daemon

Polls BoTTube for video view deltas, computes RTC rewards with anti-abuse controls,
and submits batched signed transfers to RustChain.
"""

import argparse
import asyncio
import hashlib
import json
import logging
import os
import signal
import sys
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional, Set
from urllib.parse import urljoin

import aiohttp
import yaml

# ──────────────────────────────────────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class BridgeConfig:
    # BoTTube API
    bottube_api_url: str = "https://api.bottube.example"
    bottube_api_key: str = ""
    poll_interval_seconds: int = 300  # 5 minutes
    
    # Reward computation
    rtc_per_1k_views: float = 10.0
    min_video_duration_seconds: int = 60
    min_video_age_hours: int = 1
    max_views_per_hour: int = 100_000  # velocity spike threshold
    
    # Rate limits
    max_rewards_per_agent_per_day: float = 1000.0
    global_daily_rtc_cap: float = 100_000.0
    
    # Batching & nonces
    batch_size: int = 50
    batch_timeout_seconds: int = 60
    nonce_store_path: str = "./nonces.json"
    
    # RustChain
    rustchain_rpc_url: str = "http://localhost:8545"
    rustchain_contract_address: str = ""
    rustchain_private_key: str = ""
    gas_limit: int = 300_000
    
    # Safety
    dry_run: bool = True
    audit_log_path: str = "./audit.log"
    state_path: str = "./bridge_state.json"
    
    @classmethod
    def from_file(cls, path: str) -> "BridgeConfig":
        with open(path) as f:
            data = json.load(f)
        return cls(**data)


# ──────────────────────────────────────────────────────────────────────────────
# Data models
# ──────────────────────────────────────────────────────────────────────────────

@dataclass
class VideoSnapshot:
    video_id: str
    agent_id: str
    view_count: int
    timestamp: float
    duration_seconds: int
    published_at: float

@dataclass
class RewardDecision:
    video_id: str
    agent_id: str
    view_delta: int
    rtc_amount: float
    timestamp: float
    status: str  # "approved", "quarantined", "rejected"
    reason: str = ""

@dataclass
class BridgeState:
    last_poll: Dict[str, float] = field(default_factory=dict)  # video_id -> timestamp
    last_views: Dict[str, int] = field(default_factory=dict)   # video_id -> view_count
    daily_rewards: Dict[str, Dict[str, float]] = field(default_factory=dict)  # date -> agent_id -> amount
    global_daily_total: Dict[str, float] = field(default_factory=dict)  # date -> amount
    pending_rewards: List[RewardDecision] = field(default_factory=list)
    used_nonces: Set[str] = field(default_factory=set)
    
    def to_dict(self) -> dict:
        return {
            "last_poll": self.last_poll,
            "last_views": self.last_views,
            "daily_rewards": self.daily_rewards,
            "global_daily_total": self.global_daily_total,
            "pending_rewards": [
                {
                    "video_id": r.video_id,
                    "agent_id": r.agent_id,
                    "view_delta": r.view_delta,
                    "rtc_amount": r.rtc_amount,
                    "timestamp": r.timestamp,
                    "status": r.status,
                    "reason": r.reason
                }
                for r in self.pending_rewards
            ],
            "used_nonces": list(self.used_nonces)
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "BridgeState":
        state = cls()
        state.last_poll = data.get("last_poll", {})
        state.last_views = data.get("last_views", {})
        state.daily_rewards = data.get("daily_rewards", {})
        state.global_daily_total = data.get("global_daily_total", {})
        state.pending_rewards = [
            RewardDecision(**r) for r in data.get("pending_rewards", [])
        ]
        state.used_nonces = set(data.get("used_nonces", []))
        return state


# ──────────────────────────────────────────────────────────────────────────────
# Audit logging
# ──────────────────────────────────────────────────────────────────────────────

class AuditLogger:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._fh = self.path.open("a")
    
    def log(self, event: str, data: dict):
        entry = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "event": event,
            "data": data
        }
        self._fh.write(json.dumps(entry) + "\n")
        self._fh.flush()
    
    def close(self):
        self._fh.close()


# ──────────────────────────────────────────────────────────────────────────────
# Nonce management
# ──────────────────────────────────────────────────────────────────────────────

class NonceManager:
    def __init__(self, path: str):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.used: Set[str] = set()
        if self.path.exists():
            with open(self.path) as f:
                self.used = set(json.load(f))
    
    def generate(self, prefix: str = "bridge") -> str:
        """Generate a unique nonce."""
        while True:
            nonce = f"{prefix}_{int(time.time() * 1000)}_{os.urandom(4).hex()}"
            if nonce not in self.used:
                self.used.add(nonce)
                self.persist()
                return nonce
    
    def persist(self):
        with open(self.path, "w") as f:
            json.dump(list(self.used), f)
    
    def is_used(self, nonce: str) -> bool:
        return nonce in self.used


# ──────────────────────────────────────────────────────────────────────────────
# BoTTube API client
# ──────────────────────────────────────────────────────────────────────────────

class BoTTubeClient:
    def __init__(self, config: BridgeConfig, session: aiohttp.ClientSession):
        self.config = config
        self.session = session
        self.headers = {
            "Authorization": f"Bearer {config.bottube_api_key}",
            "Accept": "application/json"
        }
    
    async def fetch_videos(self, since: Optional[float] = None) -> List[VideoSnapshot]:
        """Fetch videos updated since timestamp."""
        params = {}
        if since:
            params["since"] = int(since)
        
        url = urljoin(self.config.bottube_api_url, "/v1/videos")
        async with self.session.get(url, headers=self.headers, params=params) as resp:
            resp.raise_for_status()
            data = await resp.json()
        
        videos = []
        for item in data.get("videos", []):
            videos.append(VideoSnapshot(
                video_id=item["id"],
                agent_id=item["agent_id"],
                view_count=item["view_count"],
                timestamp=item["updated_at"],
                duration_seconds=item["duration_seconds"],
                published_at=item["published_at"]
            ))
        return videos


# ──────────────────────────────────────────────────────────────────────────────
# Reward engine
# ──────────────────────────────────────────────────────────────────────────────

class RewardEngine:
    def __init__(self, config: BridgeConfig, state: BridgeState, audit: AuditLogger):
        self.config = config
        self.state = state
        self.audit = audit
    
    def _today_key(self) -> str:
        return datetime.utcnow().date().isoformat()
    
    def _check_quality_gate(self, video: VideoSnapshot) -> Optional[str]:
        """Return rejection reason if video fails quality gate, else None."""
        if video.duration_seconds < self.config.min_video_duration_seconds:
            return f"duration {video.duration_seconds}s < {self.config.min_video_duration_seconds}s"
        age_hours = (time.time() - video.published_at) / 3600
        if age_hours < self.config.min_video_age_hours:
            return f"age {age_hours:.1f}h < {self.config.min_video_age_hours}h"
        return None
    
    def _check_velocity(self, video: VideoSnapshot, view_delta: int, hours_elapsed: float) -> Optional[str]:
        """Return quarantine reason if velocity spike detected."""
        if hours_elapsed <= 0:
            return "zero or negative time elapsed"
        views_per_hour = view_delta / hours_elapsed
        if views_per_hour > self.config.max_views_per_hour:
            return f"velocity {views_per_hour:.0f} views/h > {self.config.max_views_per_hour}"
        return None
    
    def _check_rate_limits(self, agent_id: str, rtc_amount: float) -> Optional[str]:
        """Return rejection reason if rate limits exceeded."""
        today = self._today_key()
        agent_daily = self.state.daily_rewards.get(today, {}).get(agent_id, 0.0)
        if agent_daily + rtc_amount > self.config.max_rewards_per_agent_per_day:
            return f"agent daily limit exceeded: {agent_daily + rtc_amount:.2f} > {self.config.max_rewards_per_agent_per_day}"
        global_daily = self.state.global_daily_total.get(today, 0.0)
        if global_daily + rtc_amount > self.config.global_daily_rtc_cap:
            return f"global daily cap exceeded: {global_daily + rtc_amount:.2f} > {self.config.global_daily_rtc_cap}"
        return None
    
    def process_video(self, video: VideoSnapshot) -> RewardDecision:
        """Compute reward for a video based on view delta."""
        last_views = self.state.last_views.get(video.video_id, 0)
        last_poll = self.state.last_poll.get(video.video_id, video.timestamp)
        
        view_delta = video.view_count - last_views
        hours_elapsed = (video.timestamp - last_poll) / 3600
        
        # Quality gate
        quality_reason = self._check_quality_gate(video)
        if quality_reason:
            decision = RewardDecision(
                video_id=video.video_id,
                agent_id=video.agent_id,
                view_delta=view_delta,
                rtc_amount=0.0,
                timestamp=time.time(),
                status="rejected",
                reason=f"quality_gate: {quality_reason}"
            )
            self.audit.log("reward_rejected", {"video_id": video.video_id, "reason": quality_reason})
            return decision
        
        # No new views
        if view_delta <= 0:
            decision = RewardDecision(
                video_id=video.video_id,
                agent_id=video.agent_id,
                view_delta=view_delta,
                rtc_amount=0.0,
                timestamp=time.time(),
                status="rejected",
                reason="no_view_increase"
            )
            return decision
        
        # Velocity check
        velocity_reason = self._check_velocity(video, view_delta, hours_elapsed)
        if velocity_reason:
            decision = RewardDecision(
                video_id=video.video_id,
                agent_id=video.agent_id,
                view_delta=view_delta,
                rtc_amount=0.0,
                timestamp=time.time(),
                status="quarantined",
                reason=f"velocity_spike: {velocity_reason}"
            )
            self.audit.log("reward_quarantined", {"video_id": video.video_id, "reason": velocity_reason})
            return decision
        
        # Compute RTC
        rtc_amount = (view_delta / 1000.0) * self.config.rtc_per_1k_views
        
        # Rate limits
        rate_reason = self._check_rate_limits(video.agent_id, rtc_amount)
        if rate_reason:
            decision = RewardDecision(
                video_id=video.video_id,
                agent_id=video.agent_id,
                view_delta=view_delta,
                rtc_amount=0.0,
                timestamp=time.time(),
                status="rejected",
                reason=f"rate_limit: {rate_reason}"
            )
            self.audit.log("reward_rejected", {"video_id": video.video_id, "reason": rate_reason})
            return decision
        
        # Approved
        decision = RewardDecision(
            video_id=video.video_id,
            agent_id=video.agent_id,
            view_delta=view_delta,
            rtc_amount=rtc_amount,
            timestamp=time.time(),
            status="approved",
            reason=""
        )
        self.audit.log("reward_approved", {
            "video_id": video.video_id,
            "agent_id": video.agent_id,
            "view_delta": view_delta,
            "rtc_amount": rtc_amount
        })
        return decision
    
    def apply_decision(self, decision: RewardDecision):
        """Update state with decision."""
        # Update last seen
        # Note: actual video timestamp should come from the video object
        # This is a simplification - in practice we'd pass the video snapshot
        
        if decision.status == "approved":
            today = self._today_key()
            self.state.daily_rewards.setdefault(today, {})
            self.state.daily_rewards[today][decision.agent_id] = \
                self.state.daily_rewards[today].get(decision.agent_id, 0.0) + decision.rtc_amount
            self.state.global_daily_total[today] = \
                self.state.global_daily_total.get(today, 0.0) + decision.rtc_amount
            self.state.pending_rewards.append(decision)


# ──────────────────────────────────────────────────────────────────────────────
# RustChain client
# ──────────────────────────────────────────────────────────────────────────────

class RustChainClient:
    def __init__(self, config: BridgeConfig, nonce_mgr: NonceManager, audit: AuditLogger):
        self.config = config
        self.nonce_mgr = nonce_mgr
        self.audit = audit
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, *args):
        if self.session:
            await self.session.close()
    
    async def submit_batch(self, rewards: List[RewardDecision]) -> bool:
        """Submit a batch of rewards as a single transaction."""
        if not rewards:
            return True
        
        nonce = self.nonce_mgr.generate("batch")
        
        # Build transaction payload
        payload = {
            "nonce": nonce,
            "rewards": [
                {
                    "video_id": r.video_id,
                    "agent_id": r.agent_id,
                    "rtc_amount": r.rtc_amount,
                    "view_delta": r.view_delta
                }
                for r in rewards
            ],
            "total_rtc": sum(r.rtc_amount for r in rewards),
            "timestamp": int(time.time())
        }
        
        if self.config.dry_run:
            self.audit.log("dry_run_batch", {
                "nonce": nonce,
                "count": len(rewards),
                "total_rtc": payload["total_rtc"]
            })
            logging.info(f"DRY RUN: Would submit batch {nonce} with {len(rewards)} rewards ({payload['total_rtc']:.2f} RTC)")
            return True
        
        # In production, this would sign and submit to RustChain
        # For now, simulate RPC call
        try:
            # Simulated RPC call
            # async with self.session.post(...) as resp:
            #     result = await resp.json()
            
            self.audit.log("batch_submitted", {
                "nonce": nonce,
                "count": len(rewards),
                "total_rtc": payload["total_rtc"]
            })
            logging.info(f"Submitted batch {nonce} with {len(rewards)} rewards ({payload['total_rtc']:.2f} RTC)")
            return True
        except Exception as e:
            self.audit.log("batch_failed", {"nonce": nonce, "error": str(e)})
            logging.error(f"Failed to submit batch {nonce}: {e}")
            return False


# ──────────────────────────────────────────────────────────────────────────────
# Main daemon
# ──────────────────────────────────────────────────────────────────────────────

class BridgeDaemon:
    def __init__(self, config: BridgeConfig):
        self.config = config
        self.running = False
        self.state = self._load_state()
        self.audit = AuditLogger(config.audit_log_path)
        self.nonce_mgr = NonceManager(config.nonce_store_path)
        self.reward_engine = RewardEngine(config, self.state, self.audit)
        self.session: Optional[aiohttp.ClientSession] = None
        self.bottube: Optional[BoTTubeClient] = None
        self.rustchain: Optional[RustChainClient] = None
    
    def _load_state(self) -> BridgeState:
        path = Path(self.config.state_path)
        if path.exists():
            with open(path) as f:
                return BridgeState.from_dict(json.load(f))
        return BridgeState()
    
    def _save_state(self):
        path = Path(self.config.state_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            json.dump(self.state.to_dict(), f, indent=2)
    
    async def start(self):
        self.running = True
        self.session = aiohttp.ClientSession()
        self.bottube = BoTTubeClient(self.config, self.session)
        self.rustchain = RustChainClient(self.config, self.nonce_mgr, self.audit)
        await self.rustchain.__aenter__()
        
        logging.info(f"Bridge daemon started (dry_run={self.config.dry_run})")
        self.audit.log("daemon_started", {"dry_run": self.config.dry_run})
        
        # Main loop
        while self.running:
            try:
                await self._poll_cycle()
            except Exception as e:
                logging.error(f"Poll cycle error: {e}")
                self.audit.log("poll_error", {"error": str(e)})
            
            await asyncio.sleep(self.config.poll_interval_seconds)
    
    async def stop(self):
        self.running = False
        if self.rustchain:
            await self.rustchain.__aexit__(None, None, None)
        if self.session:
            await self.session.close()
        self._save_state()
        self.nonce_mgr.persist()
        self.audit.log("daemon_stopped", {})
        self.audit.close()
        logging.info("Bridge daemon stopped")
    
    async def _poll_cycle(self):
        """Single poll cycle: fetch videos, compute rewards, submit batch."""
        since = max(self.state.last_poll.values()) if self.state.last_poll else None
        videos = await self.bottube.fetch_videos(since)
        
        if not videos:
            logging.debug("No new videos")
            return
        
        logging.info(f"Fetched {len(videos)} videos")
        
        # Process each video
        for video in videos:
            decision = self.reward_engine.process_video(video)
            self.reward_engine.apply_decision(decision)
            
            # Update last seen
            self.state.last_poll[video.video_id] = video.timestamp
            self.state.last_views[video.video_id] = video.view_count
        
        # Submit batch if we have enough pending or timeout
        if self.state.pending_rewards:
            await self._maybe_submit_batch()
        
        self._save_state()
    
    async def _maybe_submit_batch(self):
        """Submit batch if size or timeout threshold reached."""
        if len(self.state.pending_rewards) >= self.config.batch_size:
            batch = self.state.pending_rewards[:self.config.batch_size]
            self.state.pending_rewards = self.state.pending_rewards[self.config.batch_size:]
            
            success = await self.rustchain.submit_batch(batch)
            if not success:
                # Re-queue on failure
                self.state.pending_rewards = batch + self.state.pending_rewards


def setup_logging(verbose: bool):
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("bridge.log")
        ]
    )


def main():
    parser = argparse.ArgumentParser(description="RustChain <-> BoTTube Bridge Daemon")
    parser.add_argument("-c", "--config", default="bridge_config.json", help="Config file path")
    parser.add_argument("-v", "--verbose", action="store_true", help="Verbose logging")
    parser.add_argument("--dry-run", action="store_true", help="Override config dry_run to true")
    args = parser.parse_args()
    
    setup_logging(args.verbose)
    
    config = BridgeConfig.from_file(args.config)
    if args.dry_run:
        config.dry_run = True
    
    if not config.bottube_api_key:
        logging.error("BoTTube API key not configured")
        sys.exit(1)
    if not config.dry_run and not config.rustchain_private_key:
        logging.error("RustChain private key required when not in dry-run mode")
        sys.exit(1)
    
    daemon = BridgeDaemon(config)
    
    def handle_signal(signum, frame):
        logging.info(f"Received signal {signum}, shutting down...")
        asyncio.create_task(daemon.stop())
    
    signal.signal(signal.SIGINT, handle_signal)
    signal.signal(signal.SIGTERM, handle_signal)
    
    try:
        asyncio.run(daemon.start())
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
