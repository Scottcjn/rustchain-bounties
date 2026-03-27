#!/usr/bin/env python3
"""Tests for Energypantry Beacon integration (#158 proof package)."""

import unittest

from energypantry_beacon_agent import EnergypantryBeaconAgent, InMemoryBeaconBridge


class BeaconIntegrationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.bridge = InMemoryBeaconBridge()
        self.agent = EnergypantryBeaconAgent(
            agent_id="bcn_energypantry_test",
            role="operator",
            bridge=self.bridge,
        )

    def test_heartbeat(self) -> None:
        event = self.agent.send_heartbeat()
        self.assertEqual(event.kind, "heartbeat")
        self.assertEqual(event.payload["status"], "alive")
        self.assertEqual(event.payload["role"], "operator")

    def test_mayday(self) -> None:
        event = self.agent.send_mayday("relay timeout", urgency="critical")
        self.assertEqual(event.kind, "mayday")
        self.assertEqual(event.payload["reason"], "relay timeout")
        self.assertEqual(event.payload["urgency"], "critical")

    def test_contract_offer(self) -> None:
        event = self.agent.create_contract_offer(
            resource="indexing_capacity",
            amount_rtc=25,
            term="30d",
            counterparty="bcn_partner",
        )
        self.assertEqual(event.kind, "contract_offer")
        self.assertEqual(event.payload["resource"], "indexing_capacity")
        self.assertEqual(event.payload["amount_rtc"], 25)
        self.assertEqual(event.payload["counterparty"], "bcn_partner")

    def test_demo_flow_emits_three_events(self) -> None:
        events = self.agent.run_demo()
        self.assertEqual(len(events), 3)
        self.assertEqual([event.kind for event in events], ["heartbeat", "mayday", "contract_offer"])


if __name__ == "__main__":
    unittest.main()
