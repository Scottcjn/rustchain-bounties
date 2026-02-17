#!/usr/bin/env python3
"""Energypantry Beacon integration for RustChain bounty #158.

This module implements a small but verifiable agent integration that covers:
- heartbeat announcements
- mayday alerts
- contract offers

It supports two bridges:
1) BeaconSkillBridge: uses the `beacon-skill` package when available
2) InMemoryBeaconBridge: deterministic local bridge for reproducible tests
"""

from __future__ import annotations

import argparse
import json
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass
class BeaconEvent:
    kind: str
    agent_id: str
    ts: int
    payload: Dict[str, Any]


class BeaconBridge:
    """Bridge contract for Beacon operations."""

    def ping(self, agent_id: str, role: str) -> BeaconEvent:
        raise NotImplementedError

    def mayday(self, agent_id: str, reason: str, details: Dict[str, Any]) -> BeaconEvent:
        raise NotImplementedError

    def contract_offer(
        self,
        agent_id: str,
        resource: str,
        amount_rtc: int,
        term: str,
        counterparty: str,
    ) -> BeaconEvent:
        raise NotImplementedError


class InMemoryBeaconBridge(BeaconBridge):
    """Deterministic bridge used for local tests and offline validation."""

    def __init__(self) -> None:
        self._events: List[BeaconEvent] = []

    def _new_event(self, kind: str, agent_id: str, payload: Dict[str, Any]) -> BeaconEvent:
        event = BeaconEvent(kind=kind, agent_id=agent_id, ts=int(time.time()), payload=payload)
        self._events.append(event)
        return event

    def ping(self, agent_id: str, role: str) -> BeaconEvent:
        return self._new_event(
            "heartbeat",
            agent_id,
            {
                "status": "alive",
                "role": role,
            },
        )

    def mayday(self, agent_id: str, reason: str, details: Dict[str, Any]) -> BeaconEvent:
        return self._new_event(
            "mayday",
            agent_id,
            {
                "reason": reason,
                "details": details,
                "urgency": details.get("urgency", "medium"),
            },
        )

    def contract_offer(
        self,
        agent_id: str,
        resource: str,
        amount_rtc: int,
        term: str,
        counterparty: str,
    ) -> BeaconEvent:
        return self._new_event(
            "contract_offer",
            agent_id,
            {
                "resource": resource,
                "amount_rtc": amount_rtc,
                "term": term,
                "counterparty": counterparty,
            },
        )

    def history(self) -> List[BeaconEvent]:
        return list(self._events)


class BeaconSkillBridge(BeaconBridge):
    """Bridge backed by the `beacon-skill` package if installed."""

    def __init__(self, agent_id: str, role: str) -> None:
        try:
            from beacon_skill import Beacon  # type: ignore
        except ImportError as exc:
            raise RuntimeError(
                "BeaconSkillBridge requires beacon-skill. Install with: pip install beacon-skill"
            ) from exc

        self._agent_id = agent_id
        self._role = role
        self._beacon = Beacon(agent_id=agent_id, role=role)

    def ping(self, agent_id: str, role: str) -> BeaconEvent:
        self._beacon.ping()
        return BeaconEvent(
            kind="heartbeat",
            agent_id=agent_id,
            ts=int(time.time()),
            payload={"status": "alive", "role": role, "bridge": "beacon-skill"},
        )

    def mayday(self, agent_id: str, reason: str, details: Dict[str, Any]) -> BeaconEvent:
        self._beacon.mayday(reason, details=details)
        return BeaconEvent(
            kind="mayday",
            agent_id=agent_id,
            ts=int(time.time()),
            payload={"reason": reason, "details": details, "bridge": "beacon-skill"},
        )

    def contract_offer(
        self,
        agent_id: str,
        resource: str,
        amount_rtc: int,
        term: str,
        counterparty: str,
    ) -> BeaconEvent:
        self._beacon.contract_offer(resource=resource, price=amount_rtc, duration=term)
        return BeaconEvent(
            kind="contract_offer",
            agent_id=agent_id,
            ts=int(time.time()),
            payload={
                "resource": resource,
                "amount_rtc": amount_rtc,
                "term": term,
                "counterparty": counterparty,
                "bridge": "beacon-skill",
            },
        )


class EnergypantryBeaconAgent:
    """Minimal agent with three Beacon capabilities for bounty proof."""

    def __init__(self, agent_id: str, role: str = "operator", bridge: Optional[BeaconBridge] = None):
        self.agent_id = agent_id
        self.role = role
        self.bridge = bridge or InMemoryBeaconBridge()

    def send_heartbeat(self) -> BeaconEvent:
        return self.bridge.ping(agent_id=self.agent_id, role=self.role)

    def send_mayday(self, reason: str, urgency: str = "high") -> BeaconEvent:
        return self.bridge.mayday(
            agent_id=self.agent_id,
            reason=reason,
            details={"urgency": urgency, "source": "energypantry-agent"},
        )

    def create_contract_offer(
        self,
        resource: str,
        amount_rtc: int,
        term: str,
        counterparty: str,
    ) -> BeaconEvent:
        return self.bridge.contract_offer(
            agent_id=self.agent_id,
            resource=resource,
            amount_rtc=amount_rtc,
            term=term,
            counterparty=counterparty,
        )

    def run_demo(self) -> List[BeaconEvent]:
        events = [
            self.send_heartbeat(),
            self.send_mayday(reason="Need extra GPU workers", urgency="medium"),
            self.create_contract_offer(
                resource="gpu_hours",
                amount_rtc=40,
                term="7d",
                counterparty="bcn_superplane_bridge",
            ),
        ]
        return events


def _print_events(events: List[BeaconEvent]) -> None:
    payload = {
        "eventCount": len(events),
        "events": [asdict(event) for event in events],
    }
    print(json.dumps(payload, indent=2, ensure_ascii=True))


def main() -> int:
    parser = argparse.ArgumentParser(description="Run Energypantry Beacon integration demo")
    parser.add_argument("--agent-id", default="bcn_energypantry")
    parser.add_argument("--role", default="operator")
    parser.add_argument(
        "--bridge",
        default="memory",
        choices=["memory", "beacon-skill"],
        help="Use in-memory bridge for deterministic testability or beacon-skill for live mode.",
    )
    args = parser.parse_args()

    if args.bridge == "beacon-skill":
        bridge: BeaconBridge = BeaconSkillBridge(agent_id=args.agent_id, role=args.role)
    else:
        bridge = InMemoryBeaconBridge()

    agent = EnergypantryBeaconAgent(agent_id=args.agent_id, role=args.role, bridge=bridge)
    events = agent.run_demo()
    _print_events(events)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
