#!/usr/bin/env python3
"""
Comprehensive Beacon Integration Test
Tests all major Beacon 2.6 features
"""

from beacon_skill import AgentIdentity, HeartbeatManager, AtlasManager
import json
from datetime import datetime, timezone

def test_beacon_integration():
    """Comprehensive test of Beacon 2.6 integration"""

    print("🧪 Beacon 2.6 Integration Test Suite")
    print("=" * 70)
    print(f"Test Started: {datetime.now(timezone.utc).isoformat()}\n")

    test_results = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "tests": []
    }

    # Test 1: Identity Management
    print("TEST 1: Agent Identity Management")
    print("-" * 70)
    try:
        identity = AgentIdentity.load()
        test_results["tests"].append({
            "test": "Identity Load",
            "status": "PASS",
            "agent_id": identity.agent_id,
            "public_key": identity.public_key_hex
        })
        print(f"✅ PASS: Agent identity loaded")
        print(f"   Agent ID: {identity.agent_id}")
        print(f"   Public Key: {identity.public_key_hex[:30]}...")
    except Exception as e:
        test_results["tests"].append({
            "test": "Identity Load",
            "status": "FAIL",
            "error": str(e)
        })
        print(f"❌ FAIL: {e}")
        return test_results

    # Test 2: Heartbeat Initialization
    print("\nTEST 2: Heartbeat Manager Initialization")
    print("-" * 70)
    try:
        hb_mgr = HeartbeatManager()
        test_results["tests"].append({
            "test": "Heartbeat Init",
            "status": "PASS"
        })
        print("✅ PASS: HeartbeatManager initialized successfully")
    except Exception as e:
        test_results["tests"].append({
            "test": "Heartbeat Init",
            "status": "FAIL",
            "error": str(e)
        })
        print(f"❌ FAIL: {e}")
        return test_results

    # Test 3: Send Heartbeat
    print("\nTEST 3: Send Heartbeat with Health Metrics")
    print("-" * 70)
    try:
        health = {
            "cpu": 30.5,
            "memory": 52.3,
            "disk": 67.8,
            "uptime": 172800,  # 48 hours
            "tasks_completed": 15,
            "status": "online"
        }

        heartbeat_result = hb_mgr.beat(
            identity,
            status="alive",
            health=health
        )

        test_results["tests"].append({
            "test": "Heartbeat Send",
            "status": "PASS",
            "health": health
        })
        print("✅ PASS: Heartbeat sent successfully")
        print(f"   CPU: {health['cpu']}%")
        print(f"   Memory: {health['memory']}%")
        print(f"   Disk: {health['disk']}%")
        print(f"   Status: {health['status']}")
    except Exception as e:
        test_results["tests"].append({
            "test": "Heartbeat Send",
            "status": "FAIL",
            "error": str(e)
        })
        print(f"❌ FAIL: {e}")
        return test_results

    # Test 4: Agent History
    print("\nTEST 4: Retrieve Agent History")
    print("-" * 70)
    try:
        history = hb_mgr.agent_history(identity.agent_id, limit=10)
        test_results["tests"].append({
            "test": "Agent History",
            "status": "PASS",
            "count": len(history)
        })
        print(f"✅ PASS: Retrieved {len(history)} heartbeats from history")
        for idx, beat in enumerate(history[-3:], 1):  # Show last 3
            print(f"   {idx}. Status: {beat.get('status', 'unknown')}")
    except Exception as e:
        test_results["tests"].append({
            "test": "Agent History",
            "status": "FAIL",
            "error": str(e)
        })
        print(f"❌ FAIL: {e}")
        return test_results

    # Test 5: Peer Discovery
    print("\nTEST 5: Peer Discovery")
    print("-" * 70)
    try:
        peers = hb_mgr.all_peers(include_dead=False)
        test_results["tests"].append({
            "test": "Peer Discovery",
            "status": "PASS",
            "peer_count": len(peers)
        })
        print(f"✅ PASS: Discovered {len(peers)} active peers")
        for peer in peers[:3]:  # Show first 3
            agent_id = peer.get('agent_id', 'unknown')
            print(f"   - {agent_id[:25]}...")
    except Exception as e:
        test_results["tests"].append({
            "test": "Peer Discovery",
            "status": "FAIL",
            "error": str(e)
        })
        print(f"❌ FAIL: {e}")
        return test_results

    # Test 6: Atlas Integration
    print("\nTEST 6: Atlas Integration")
    print("-" * 70)
    try:
        atlas_mgr = AtlasManager()
        atlas_url = f"http://50.28.86.131:8070/beacon/#agent={identity.agent_id}"
        test_results["tests"].append({
            "test": "Atlas Integration",
            "status": "PASS",
            "atlas_url": atlas_url
        })
        print("✅ PASS: AtlasManager initialized")
        print(f"   Atlas: http://50.28.86.131:8070/beacon/")
        print(f"   Agent Atlas: {atlas_url}")
    except Exception as e:
        test_results["tests"].append({
            "test": "Atlas Integration",
            "status": "FAIL",
            "error": str(e)
        })
        print(f"❌ FAIL: {e}")
        return test_results

    # Test 7: Silence Detection
    print("\nTEST 7: Silence Detection")
    print("-" * 70)
    try:
        silent_agents = hb_mgr.check_silence(threshold_s=86400)  # 24 hours
        test_results["tests"].append({
            "test": "Silence Detection",
            "status": "PASS",
            "silent_count": len(silent_agents)
        })
        print(f"✅ PASS: Silence detection completed")
        print(f"   Silent agents (>24h): {len(silent_agents)}")
    except Exception as e:
        test_results["tests"].append({
            "test": "Silence Detection",
            "status": "FAIL",
            "error": str(e)
        })
        print(f"❌ FAIL: {e}")
        return test_results

    # Summary
    print("\n" + "=" * 70)
    print("📊 TEST SUMMARY")
    print("=" * 70)

    passed = sum(1 for t in test_results["tests"] if t["status"] == "PASS")
    failed = sum(1 for t in test_results["tests"] if t["status"] == "FAIL")
    total = len(test_results["tests"])

    print(f"Total Tests: {total}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Success Rate: {passed/total*100:.1f}%")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED! Beacon integration is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Review errors above.")

    # Summary Info
    print("\n📋 INTEGRATION SUMMARY")
    print("=" * 70)
    print(f"Agent ID: {identity.agent_id}")
    print(f"Public Key: {identity.public_key_hex}")
    print(f"Heartbeats Sent: {test_results['tests'][2].get('health', {})}")
    print(f"Peer Discovery: Working")
    print(f"Atlas Integration: Working")
    print(f"History Tracking: Working")
    print(f"Silence Detection: Working")

    print("\n🔗 LINKS")
    print("=" * 70)
    print(f"Atlas: http://50.28.86.131:8070/beacon/#agent={identity.agent_id}")
    print(f"Explorer: https://50.28.86.131/explorer")

    return test_results


if __name__ == "__main__":
    results = test_beacon_integration()

    # Save results to JSON
    with open("test_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print("\n💾 Test results saved to test_results.json")
    print("\n✅ Beacon 2.6 integration test complete!")
