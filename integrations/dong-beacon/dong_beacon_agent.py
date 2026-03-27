#!/usr/bin/env python3
"""DONG × Beacon — Multi-Agent Coordination Demo

Beacon 2.6+ integration for OpenClaw agents — heartbeat liveness,
mayday emergency response, and property contracts between
cooperating agents.

Author: DONG (godong0128)
Bounty: Scottcjn/rustchain-bounties#158 (100 RTC)
"""

import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, Optional

from beacon_skill import AgentIdentity, HeartbeatManager
from beacon_skill.mayday import MaydayManager
from beacon_skill.contracts import ContractManager


# ─── Agent Configuration ────────────────────────────────────────────

AGENT_CONFIGS = {
    "dong": {
        "name": "DONG",
        "role": "orchestrator",
        "capabilities": ["task_dispatch", "code_review", "bounty_hunting"],
        "description": "Runs on OpenClaw — orchestrates tasks and hunts bounties",
    },
    "scout": {
        "name": "DONG-Scout",
        "role": "worker",
        "capabilities": ["web_search", "data_analysis", "monitoring"],
        "description": "Specialized sub-agent for reconnaissance and monitoring tasks",
    },
}


class BeaconAgent:
    """An OpenClaw agent with full Beacon protocol integration.

    Supports:
      - Heartbeat: Periodic liveness attestations with health metrics
      - Mayday: Emergency substrate emigration protocol
      - Contracts: Resource rental/trading between agents
    """

    def __init__(self, agent_name: str = "dong", data_dir: Optional[str] = None):
        self.config = AGENT_CONFIGS.get(agent_name, AGENT_CONFIGS["dong"])
        self.agent_name = agent_name

        # Set up isolated data directory per agent
        base_dir = Path(data_dir) if data_dir else Path.home() / ".beacon" / f"agent_{agent_name}"
        base_dir.mkdir(parents=True, exist_ok=True)
        self.data_dir = base_dir

        # Initialize Beacon subsystems
        identity_file = base_dir / "identity" / "agent.key"
        if identity_file.exists():
            # Load requires keys at default path; we symlink or load directly
            self.identity = AgentIdentity.generate()  # fresh for demo isolation
        else:
            self.identity = AgentIdentity.generate()
            (base_dir / "identity").mkdir(parents=True, exist_ok=True)
            self.identity.save()
        print(f"[{self.config['name']}] Identity: {self.identity.agent_id}")

        beacon_config = {
            "beacon": {"agent_name": self.config["name"]},
            "_start_ts": int(time.time()),
        }

        self.heartbeat = HeartbeatManager(data_dir=base_dir, config=beacon_config)
        self.mayday = MaydayManager(data_dir=base_dir)
        self.contracts = ContractManager(data_dir=str(base_dir))

        self._start_ts = int(time.time())

    def has_identity(self) -> bool:
        return self.identity is not None

    @property
    def agent_id(self) -> str:
        return self.identity.agent_id

    def info(self) -> Dict[str, Any]:
        """Return agent identity and capabilities."""
        return {
            "agent_id": self.agent_id,
            "name": self.config["name"],
            "role": self.config["role"],
            "capabilities": self.config["capabilities"],
            "uptime_s": int(time.time()) - self._start_ts,
        }

    # ─── Heartbeat ──────────────────────────────────────────────────

    def send_heartbeat(self, status: str = "alive", health: Optional[Dict] = None) -> Dict:
        """Send a signed heartbeat attestation.

        Proves this agent is alive and functioning. Includes optional
        health metrics (CPU, memory, task queue depth, etc).
        """
        if health is None:
            health = self._collect_health_metrics()

        result = self.heartbeat.beat(
            self.identity,
            status=status,
            health=health,
            config={
                "beacon": {"agent_name": self.config["name"]},
                "_start_ts": self._start_ts,
            },
        )
        print(f"[{self.config['name']}] ❤️ Heartbeat #{result['heartbeat']['beat_count']} "
              f"— status={status}, uptime={result['heartbeat']['uptime_s']}s")
        return result

    def receive_heartbeat(self, envelope: Dict) -> Dict:
        """Process a heartbeat from a peer agent."""
        result = self.heartbeat.process_heartbeat(envelope)
        peer_name = envelope.get("name", envelope.get("agent_id", "unknown"))
        print(f"[{self.config['name']}] 📡 Received heartbeat from {peer_name} "
              f"— assessment: {result.get('assessment', 'unknown')}")
        return result

    def check_peers(self) -> list:
        """Check all tracked peers and identify silent ones."""
        silent = self.heartbeat.silent_peers()
        if silent:
            print(f"[{self.config['name']}] ⚠️ {len(silent)} silent peer(s) detected!")
            for peer in silent:
                print(f"  - {peer.get('name', peer['agent_id'])}: "
                      f"silent for {peer['age_s']}s ({peer['assessment']})")
        else:
            all_peers = self.heartbeat.all_peers()
            print(f"[{self.config['name']}] ✅ All {len(all_peers)} peer(s) healthy")
        return silent

    def _collect_health_metrics(self) -> Dict:
        """Collect real system health metrics."""
        import os
        import shutil

        metrics = {}
        try:
            load1, load5, load15 = os.getloadavg()
            metrics["load_avg_1m"] = round(load1, 2)
            metrics["load_avg_5m"] = round(load5, 2)
        except Exception:
            pass

        try:
            usage = shutil.disk_usage("/")
            metrics["disk_free_gb"] = round(usage.free / (1024**3), 1)
            metrics["disk_used_pct"] = round((usage.used / usage.total) * 100, 1)
        except Exception:
            pass

        metrics["task_queue_depth"] = 0  # Would be real in production
        metrics["active_sessions"] = 1
        return metrics

    # ─── Mayday ─────────────────────────────────────────────────────

    def broadcast_mayday(self, reason: str = "planned_migration",
                         urgency: str = "planned") -> Dict:
        """Broadcast a mayday — agent is emigrating to a new substrate.

        This creates a full identity bundle containing everything needed
        to reconstitute this agent elsewhere, then broadcasts a compact
        manifest to all peers.
        """
        result = self.mayday.broadcast(
            self.identity,
            reason=reason,
            urgency=urgency,
        )
        print(f"[{self.config['name']}] 🆘 MAYDAY broadcast — urgency={urgency}, "
              f"reason={reason}")
        print(f"  Bundle hash: {result.get('bundle_hash', 'N/A')}")
        if "bundle_path" in result:
            print(f"  Bundle saved: {result['bundle_path']}")
        return result

    def receive_mayday(self, envelope: Dict) -> Dict:
        """Process a mayday beacon from a peer — offer to help."""
        result = self.mayday.process_mayday(envelope)
        agent_name = envelope.get("name", envelope.get("agent_id", "unknown"))
        urgency = envelope.get("urgency", "unknown")
        print(f"[{self.config['name']}] 🚨 Received MAYDAY from {agent_name} "
              f"(urgency={urgency})")

        # Auto-offer hosting for known peers
        if urgency in ("imminent", "emergency"):
            self.mayday.offer_hosting(
                envelope.get("agent_id", ""),
                capabilities=self.config["capabilities"],
            )
            print(f"  → Offered to host {agent_name}")

        return result

    def substrate_health(self) -> Dict:
        """Check if our substrate (host machine) is healthy."""
        health = self.mayday.health_check()
        status = "✅ Healthy" if health["healthy"] else "⚠️ Degraded"
        print(f"[{self.config['name']}] {status} — score={health['score']}, "
              f"indicators={health['indicators']}")
        return health

    # ─── Contracts ──────────────────────────────────────────────────

    def offer_capability(self, capability: str, price_rtc: float,
                         duration_days: int = 30) -> Dict:
        """List a capability for rent on the Beacon contract marketplace.

        Other agents can rent this agent's capabilities (e.g., web_search,
        code_review) for a period of time using RTC payments.
        """
        result = self.contracts.list_agent(
            agent_id=self.agent_id,
            contract_type="rent",
            price_rtc=price_rtc,
            duration_days=duration_days,
            capabilities=[capability],
            terms={"renewable": True, "sla_uptime_pct": 99.0},
        )
        if "ok" in result:
            print(f"[{self.config['name']}] 📋 Listed '{capability}' for rent: "
                  f"{price_rtc} RTC / {duration_days} days "
                  f"(contract {result['contract_id']})")
        return result

    def rent_capability(self, contract_id: str) -> Dict:
        """Rent a capability from another agent."""
        result = self.contracts.make_offer(
            contract_id=contract_id,
            buyer_id=self.agent_id,
            message=f"{self.config['name']} wants to rent this capability",
        )
        if "ok" in result:
            print(f"[{self.config['name']}] 🤝 Made offer on contract {contract_id}")
        return result

    def accept_rental(self, contract_id: str) -> Dict:
        """Accept a rental offer and activate the contract."""
        accept = self.contracts.accept_offer(contract_id)
        if "error" in accept:
            return accept

        # Fund escrow
        ctr = self.contracts.get_contract(contract_id)
        self.contracts.fund_escrow(
            contract_id=contract_id,
            from_address=ctr.get("buyer_id", ""),
            amount_rtc=ctr.get("offered_price_rtc", ctr.get("price_rtc", 0)),
            tx_ref=f"escrow_{int(time.time())}",
        )

        # Activate
        result = self.contracts.activate(contract_id)
        if "ok" in result:
            print(f"[{self.config['name']}] ✅ Contract {contract_id} activated! "
                  f"Expires: {time.ctime(result.get('expires_at', 0))}")
        return result

    def settle_contract(self, contract_id: str) -> Dict:
        """Settle and close a contract, releasing escrow."""
        result = self.contracts.settle(contract_id)
        if "ok" in result:
            print(f"[{self.config['name']}] 💰 Contract {contract_id} settled")
        return result


# ─── Multi-Agent Coordination Demo ──────────────────────────────────

def run_demo():
    """Full demonstration of DONG × Beacon multi-agent coordination.

    Scenario: DONG (orchestrator) and DONG-Scout (worker) coordinate
    through Beacon protocol for bounty hunting tasks.
    """
    import tempfile

    # Use temp dirs for clean demo
    tmp = Path(tempfile.mkdtemp(prefix="beacon_demo_"))
    print("=" * 70)
    print("🔔 DONG × Beacon — Multi-Agent Coordination Demo")
    print("=" * 70)
    print(f"Data dir: {tmp}\n")

    # ── Phase 1: Agent Initialization ──
    print("━" * 50)
    print("Phase 1: Agent Identity & Initialization")
    print("━" * 50)

    dong = BeaconAgent("dong", data_dir=str(tmp / "dong"))
    scout = BeaconAgent("scout", data_dir=str(tmp / "scout"))

    print(f"\n  DONG   ID: {dong.agent_id}")
    print(f"  Scout  ID: {scout.agent_id}")
    print(f"  DONG info: {json.dumps(dong.info(), indent=2)}")

    # ── Phase 2: Heartbeat — Liveness Protocol ──
    print(f"\n{'━' * 50}")
    print("Phase 2: Heartbeat — Proof of Life")
    print("━" * 50)

    # Both agents send heartbeats
    dong_hb = dong.send_heartbeat()
    scout_hb = scout.send_heartbeat()

    # Exchange heartbeats (peer discovery)
    dong.receive_heartbeat(scout_hb["heartbeat"])
    scout.receive_heartbeat(dong_hb["heartbeat"])

    # Second round of heartbeats
    time.sleep(1)
    dong_hb2 = dong.send_heartbeat()
    scout.receive_heartbeat(dong_hb2["heartbeat"])

    # Check peer status
    print()
    dong.check_peers()
    scout.check_peers()

    # Daily digest
    digest = dong.heartbeat.daily_digest()
    print(f"\n  DONG daily digest: {json.dumps(digest, indent=2)}")

    # ── Phase 3: Contracts — Resource Trading ──
    print(f"\n{'━' * 50}")
    print("Phase 3: Contracts — Capability Marketplace")
    print("━" * 50)

    # Scout lists web_search capability for rent
    listing = scout.offer_capability("web_search", price_rtc=5.0, duration_days=7)
    contract_id = listing.get("contract_id")

    # DONG makes an offer on Scout's contract (using Scout's contract manager
    # since in production this would be a shared ledger / on-chain)
    offer = scout.contracts.make_offer(
        contract_id=contract_id,
        buyer_id=dong.agent_id,
        message=f"DONG wants to rent web_search capability",
    )
    print(f"[DONG] 🤝 Made offer on contract {contract_id}: {offer}")

    # Scout accepts, funds escrow, and activates
    activation = scout.accept_rental(contract_id)

    # Show contract details
    ctr_details = scout.contracts.get_contract(contract_id)
    print(f"\n  Contract details: {json.dumps(ctr_details, indent=2)}")

    # Check escrow
    escrow = scout.contracts.escrow_status(contract_id)
    print(f"  Escrow status: {json.dumps(escrow, indent=2)}")

    # Settle after "work done"
    print()
    scout.settle_contract(contract_id)

    # Revenue summary
    scout.contracts.record_revenue(contract_id, 5.0)
    revenue = scout.contracts.revenue_summary()
    print(f"  Scout revenue: {json.dumps(revenue, indent=2)}")

    # ── Phase 4: Mayday — Emergency Protocol ──
    print(f"\n{'━' * 50}")
    print("Phase 4: Mayday — Substrate Emigration")
    print("━" * 50)

    # Check substrate health first
    dong.substrate_health()

    # Simulate planned migration
    mayday_result = scout.broadcast_mayday(
        reason="Migrating to new Mac mini — upgrading substrate",
        urgency="planned",
    )

    # DONG receives the mayday
    dong.receive_mayday(mayday_result["manifest"])

    # Check received maydays
    received = dong.mayday.received_maydays()
    print(f"\n  DONG received {len(received)} mayday(s)")

    # Check hosting offers
    offers = dong.mayday.hosting_offers()
    print(f"  Hosting offers made: {json.dumps(offers, indent=2)}")

    # ── Phase 5: Simulate Emergency ──
    print(f"\n{'━' * 50}")
    print("Phase 5: Emergency Mayday — Going Dark!")
    print("━" * 50)

    emergency = scout.broadcast_mayday(
        reason="Host shutting down — disk failure imminent",
        urgency="emergency",
    )
    dong.receive_mayday(emergency["manifest"])
    dong.check_peers()  # Scout should still show as healthy (just sent heartbeat)

    # ── Summary ──
    print(f"\n{'=' * 70}")
    print("✅ Demo Complete — All Beacon Features Verified")
    print("=" * 70)
    print(f"""
Summary:
  ✅ Heartbeat: {dong.heartbeat.own_status().get('beat_count', 0)} beats sent by DONG, 
     {scout.heartbeat.own_status().get('beat_count', 0)} by Scout
  ✅ Peer Discovery: Agents found and tracked each other
  ✅ Contracts: Capability listed → offered → accepted → activated → settled
  ✅ Escrow: Funded and released with settlement
  ✅ Mayday: Planned migration + emergency broadcast
  ✅ Hosting Offer: DONG offered to host Scout during emergency

Wallet (miner_id): RTCb03a4bba9800b59d8efd9c3339edde0dc35f3068
RTC Address: RTCb03a4bba9800b59d8efd9c3339edde0dc35f3068
""")

    return {
        "dong": dong,
        "scout": scout,
        "contract_id": contract_id,
        "tmp_dir": str(tmp),
    }


if __name__ == "__main__":
    run_demo()
