#!/usr/bin/env python3
"""Test suite for DONG × Beacon integration.

Validates all three Beacon features: Heartbeat, Mayday, and Contracts.
Run with: python3 test_beacon_integration.py
"""

import json
import sys
import tempfile
import time
from pathlib import Path

# Track test results
PASSED = 0
FAILED = 0
TOTAL = 0


def test(name: str, condition: bool, detail: str = ""):
    global PASSED, FAILED, TOTAL
    TOTAL += 1
    if condition:
        PASSED += 1
        print(f"  ✅ {name}")
    else:
        FAILED += 1
        print(f"  ❌ {name}" + (f" — {detail}" if detail else ""))


def main():
    global PASSED, FAILED, TOTAL

    from dong_beacon_agent import BeaconAgent

    tmp = Path(tempfile.mkdtemp(prefix="beacon_test_"))

    print("=" * 60)
    print("🧪 DONG × Beacon Integration Tests")
    print("=" * 60)

    # ── Test 1: Identity Creation ──
    print("\n📌 1. Agent Identity")
    dong = BeaconAgent("dong", data_dir=str(tmp / "dong"))
    scout = BeaconAgent("scout", data_dir=str(tmp / "scout"))

    test("DONG identity created", dong.has_identity())
    test("Scout identity created", scout.has_identity())
    test("Agent IDs are unique", dong.agent_id != scout.agent_id)
    test("Agent ID format valid (bcn_*)", dong.agent_id.startswith("bcn_"))
    test("Agent info returns correct name", dong.info()["name"] == "DONG")
    test("Agent info returns capabilities", len(dong.info()["capabilities"]) > 0)

    # ── Test 2: Heartbeat ──
    print("\n📌 2. Heartbeat Protocol")
    hb1 = dong.send_heartbeat()
    test("Heartbeat returns payload", "heartbeat" in hb1)
    test("Heartbeat has agent_id", hb1["heartbeat"]["agent_id"] == dong.agent_id)
    test("Heartbeat count increments", hb1["heartbeat"]["beat_count"] == 1)
    test("Heartbeat has timestamp", hb1["heartbeat"]["ts"] > 0)
    test("Heartbeat includes status", hb1["heartbeat"]["status"] == "alive")

    hb2 = dong.send_heartbeat()
    test("Beat count increments to 2", hb2["heartbeat"]["beat_count"] == 2)

    # Health metrics
    test("Health metrics included", "health" in hb2["heartbeat"])

    # Peer tracking
    scout_hb = scout.send_heartbeat()
    recv = dong.receive_heartbeat(scout_hb["heartbeat"])
    test("Peer heartbeat processed", "agent_id" in recv)
    test("Peer assessment is healthy", recv.get("assessment") == "healthy")

    peers = dong.heartbeat.all_peers()
    test("Peer tracked in peer list", len(peers) == 1)
    test("Tracked peer is Scout", peers[0]["agent_id"] == scout.agent_id)

    # Silence detection
    silent = dong.check_peers()
    test("No silent peers detected", len(silent) == 0)

    # Daily digest
    digest = dong.heartbeat.daily_digest()
    test("Daily digest has beat count", digest["own_beat_count"] == 2)
    test("Daily digest has peers_seen", digest["peers_seen"] >= 1)

    # Degraded status
    hb_degraded = dong.send_heartbeat(status="degraded")
    test("Degraded status accepted", hb_degraded["heartbeat"]["status"] == "degraded")

    # ── Test 3: Mayday ──
    print("\n📌 3. Mayday Protocol")

    # Substrate health check
    health = scout.substrate_health()
    test("Health check returns score", "score" in health)
    test("Health check returns indicators", "indicators" in health)

    # Planned migration
    mayday = scout.broadcast_mayday(
        reason="Upgrading to new substrate",
        urgency="planned",
    )
    test("Mayday broadcast returns manifest", "manifest" in mayday)
    test("Mayday has bundle hash", len(mayday.get("bundle_hash", "")) > 0)
    test("Mayday bundle saved to disk", "bundle_path" in mayday)
    test("Bundle file exists", Path(mayday["bundle_path"]).exists())

    # Receive mayday
    recv_mayday = dong.receive_mayday(mayday["manifest"])
    test("Mayday received and logged", "received_at" in recv_mayday)

    # Emergency mayday
    emergency = scout.broadcast_mayday(
        reason="Disk failure imminent",
        urgency="emergency",
    )
    dong.receive_mayday(emergency["manifest"])
    received = dong.mayday.received_maydays()
    test("Multiple maydays tracked", len(received) >= 2)

    # Hosting offers
    offers = dong.mayday.hosting_offers()
    test("Hosting offer made for emergency", len(offers) > 0)

    # ── Test 4: Contracts ──
    print("\n📌 4. Contract Protocol")

    # List capability
    listing = scout.offer_capability("web_search", price_rtc=5.0, duration_days=7)
    test("Capability listed successfully", "ok" in listing)
    cid = listing.get("contract_id", "")
    test("Contract ID generated", len(cid) > 0)

    # Check listing
    available = scout.contracts.list_available()
    test("Contract appears in available list", len(available) == 1)
    test("Listed price correct", available[0]["price_rtc"] == 5.0)
    test("Contract type is rent", available[0]["type"] == "rent")

    # Make offer (buyer calls seller's contract manager in shared-state scenario)
    offer = scout.contracts.make_offer(
        contract_id=cid,
        buyer_id=dong.agent_id,
        message="DONG wants to rent web_search",
    )
    test("Offer made successfully", "ok" in offer)

    # Accept and activate
    activation = scout.accept_rental(cid)
    test("Contract activated", "ok" in activation)
    test("Contract has expiry", activation.get("expires_at", 0) > 0)

    # Verify active contract
    active = scout.contracts.active_contracts()
    test("Contract is active", len(active) == 1)
    test("Active contract matches ID", active[0]["id"] == cid)

    # Escrow funded
    escrow = scout.contracts.escrow_status(cid)
    test("Escrow funded", escrow.get("amount_rtc", 0) == 5.0)
    test("Escrow not yet released", escrow.get("released") == False)

    # Contract history
    history = scout.contracts.contract_history(cid)
    test("Contract has event history", len(history) >= 4)  # listed, offered, accepted, active

    # Settle
    settlement = scout.settle_contract(cid)
    test("Contract settled", "ok" in settlement)

    # Verify escrow released
    escrow_after = scout.contracts.escrow_status(cid)
    test("Escrow released after settlement", escrow_after.get("released") == True)

    # Revenue tracking
    scout.contracts.record_revenue(cid, 5.0)
    revenue = scout.contracts.revenue_summary()
    test("Revenue recorded", revenue["total_rtc"] == 5.0)

    # ── Test 5: Multi-Agent Coordination ──
    print("\n📌 5. Multi-Agent Coordination")

    # Full coordination flow
    dong_hb = dong.send_heartbeat(health={"task": "bounty_hunting", "active": True})
    scout_hb = scout.send_heartbeat(health={"task": "web_scanning", "active": True})

    dong.receive_heartbeat(scout_hb["heartbeat"])
    scout.receive_heartbeat(dong_hb["heartbeat"])

    dong_peers = dong.heartbeat.all_peers()
    scout_peers = scout.heartbeat.all_peers()
    test("DONG tracks Scout", any(p["agent_id"] == scout.agent_id for p in dong_peers))
    test("Scout tracks DONG", any(p["agent_id"] == dong.agent_id for p in scout_peers))

    # Both agents healthy
    test("DONG peer assessment: healthy",
         dong.heartbeat.peer_status(scout.agent_id)["assessment"] == "healthy")
    test("Scout peer assessment: healthy",
         scout.heartbeat.peer_status(dong.agent_id)["assessment"] == "healthy")

    # ── Results ──
    print(f"\n{'=' * 60}")
    print(f"Results: {PASSED}/{TOTAL} passed, {FAILED} failed")
    print("=" * 60)

    if FAILED == 0:
        print("🎉 ALL TESTS PASSED!")
    else:
        print(f"⚠️ {FAILED} test(s) failed")

    return FAILED == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
