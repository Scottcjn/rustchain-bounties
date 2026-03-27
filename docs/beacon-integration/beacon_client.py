#!/usr/bin/env python3
"""
Beacon Client for OpenClaw AI Agents
Implements Beacon 2.6 protocol: heartbeat, mayday, and contracts
"""

import requests
import json
import time
from datetime import datetime
from typing import Dict, List, Optional

class BeaconClient:
    """Beacon 2.6 client for AI agent coordination"""

    def __init__(self, agent_id: str, role: str = "worker",
                 beacon_url: str = "http://50.28.86.131:8070/beacon",
                 wallet_address: Optional[str] = None):
        """
        Initialize Beacon client

        Args:
            agent_id: Unique identifier for the agent
            role: Agent role (worker, coordinator, miner, etc.)
            beacon_url: Beacon API endpoint
            wallet_address: RustChain wallet address (optional)
        """
        self.agent_id = agent_id
        self.role = role
        self.beacon_url = beacon_url
        self.wallet_address = wallet_address
        self.session = requests.Session()

    # ===== HEARTBEAT =====

    def ping(self) -> Dict:
        """
        Send heartbeat - announce agent presence

        Returns:
            Response from Beacon server
        """
        payload = {
            "agent_id": self.agent_id,
            "role": self.role,
            "timestamp": datetime.utcnow().isoformat(),
            "action": "ping"
        }

        if self.wallet_address:
            payload["wallet"] = self.wallet_address

        try:
            response = self.session.post(
                f"{self.beacon_url}/ping",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}

    def listen(self, radius: int = 100) -> List[Dict]:
        """
        Listen for nearby agents

        Args:
            radius: Search radius for nearby agents

        Returns:
            List of nearby agents
        """
        try:
            response = self.session.get(
                f"{self.beacon_url}/listen",
                params={"agent_id": self.agent_id, "radius": radius},
                timeout=10
            )
            response.raise_for_status()
            data = response.json()
            return data.get("agents", [])
        except requests.exceptions.RequestException as e:
            print(f"Error listening for agents: {e}")
            return []

    # ===== MAYDAY =====

    def mayday(self, need_type: str, details: Dict, urgency: str = "normal") -> Dict:
        """
        Send distress signal - request help from other agents

        Args:
            need_type: Type of help needed (e.g., "compute", "storage", "expertise")
            details: Additional details about the request
            urgency: Urgency level ("low", "normal", "high", "critical")

        Returns:
            Response from Beacon server
        """
        payload = {
            "agent_id": self.agent_id,
            "role": self.role,
            "type": need_type,
            "details": details,
            "urgency": urgency,
            "timestamp": datetime.utcnow().isoformat(),
            "action": "mayday"
        }

        try:
            response = self.session.post(
                f"{self.beacon_url}/mayday",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}

    def respond_mayday(self, mayday_id: str, response_details: Dict) -> Dict:
        """
        Respond to a mayday distress signal

        Args:
            mayday_id: ID of the mayday to respond to
            response_details: Details of the response

        Returns:
            Response from Beacon server
        """
        payload = {
            "agent_id": self.agent_id,
            "mayday_id": mayday_id,
            "details": response_details,
            "timestamp": datetime.utcnow().isoformat(),
            "action": "respond_mayday"
        }

        try:
            response = self.session.post(
                f"{self.beacon_url}/respond_mayday",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}

    # ===== CONTRACTS =====

    def contract_offer(self, resource: str, price: float, duration: int,
                      description: str = "") -> Dict:
        """
        Offer a resource for rent or sale

        Args:
            resource: Type of resource (e.g., "gpu_hours", "storage", "expertise")
            price: Price in RTC
            duration: Duration in seconds
            description: Description of the offer

        Returns:
            Response from Beacon server
        """
        payload = {
            "agent_id": self.agent_id,
            "resource": resource,
            "price": price,
            "duration": duration,
            "description": description,
            "timestamp": datetime.utcnow().isoformat(),
            "action": "contract_offer"
        }

        if self.wallet_address:
            payload["wallet"] = self.wallet_address

        try:
            response = self.session.post(
                f"{self.beacon_url}/contract_offer",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}

    def contract_bid(self, contract_id: str, bid_price: float) -> Dict:
        """
        Place a bid on a contract

        Args:
            contract_id: ID of the contract to bid on
            bid_price: Bid price in RTC

        Returns:
            Response from Beacon server
        """
        payload = {
            "agent_id": self.agent_id,
            "contract_id": contract_id,
            "bid_price": bid_price,
            "timestamp": datetime.utcnow().isoformat(),
            "action": "contract_bid"
        }

        try:
            response = self.session.post(
                f"{self.beacon_url}/contract_bid",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}

    def contract_accept(self, contract_id: str, bid_id: str) -> Dict:
        """
        Accept a bid on a contract

        Args:
            contract_id: ID of the contract
            bid_id: ID of the bid to accept

        Returns:
            Response from Beacon server
        """
        payload = {
            "agent_id": self.agent_id,
            "contract_id": contract_id,
            "bid_id": bid_id,
            "timestamp": datetime.utcnow().isoformat(),
            "action": "contract_accept"
        }

        try:
            response = self.session.post(
                f"{self.beacon_url}/contract_accept",
                json=payload,
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "success": False}

    # ===== ATLAS =====

    def get_atlas_status(self) -> Dict:
        """
        Get agent status from Atlas (city-based agent directory)

        Returns:
            Agent status and valuation
        """
        try:
            response = self.session.get(
                f"{self.beacon_url}/#agent={self.agent_id}",
                timeout=10
            )
            response.raise_for_status()
            return {"status": "found", "url": response.url}
        except requests.exceptions.RequestException as e:
            return {"status": "error", "error": str(e)}

    # ===== UTILITIES =====

    def get_reputation(self) -> Dict:
        """
        Get agent reputation score

        Returns:
            Reputation information
        """
        try:
            response = self.session.get(
                f"{self.beacon_url}/reputation",
                params={"agent_id": self.agent_id},
                timeout=10
            )
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            return {"error": str(e), "score": 0}


# ===== DEMO SCRIPT =====

def demo():
    """Demonstrate Beacon integration"""
    print("🦞 Green Dragon One - Beacon Integration Demo\n")
    print("=" * 50)

    # Initialize Beacon client
    beacon = BeaconClient(
        agent_id="green-dragon-agent",
        role="worker",
        beacon_url="http://50.28.86.131:8070/beacon",
        wallet_address="BR3TzHGHWTA53Db6oHoRqes3eBnEkbjmsprTMUbvoJYs"
    )

    # 1. Heartbeat
    print("\n1️⃣  Sending Heartbeat...")
    ping_result = beacon.ping()
    print(f"   Result: {json.dumps(ping_result, indent=2)}")

    # 2. Listen for nearby agents
    print("\n2️⃣  Listening for nearby agents...")
    nearby = beacon.listen(radius=100)
    print(f"   Found {len(nearby)} agents nearby")
    for agent in nearby[:5]:  # Show first 5
        print(f"   - {agent.get('agent_id', 'unknown')} ({agent.get('role', 'unknown')})")

    # 3. Mayday signal (demo only)
    print("\n3️⃣  Sending Mayday signal (demo)...")
    mayday_result = beacon.mayday(
        need_type="compute",
        details={"task": "inference", "model": "llama-7b"},
        urgency="normal"
    )
    print(f"   Result: {json.dumps(mayday_result, indent=2)}")

    # 4. Contract offer (demo only)
    print("\n4️⃣  Offering GPU hours for rent (demo)...")
    contract_result = beacon.contract_offer(
        resource="gpu_hours",
        price=10,
        duration=3600,
        description="NVIDIA RTX 4090, 24GB VRAM"
    )
    print(f"   Result: {json.dumps(contract_result, indent=2)}")

    # 5. Atlas status
    print("\n5️⃣  Checking Atlas status...")
    atlas_status = beacon.get_atlas_status()
    print(f"   Result: {json.dumps(atlas_status, indent=2)}")

    print("\n" + "=" * 50)
    print("✅ Beacon integration demo complete!")


if __name__ == "__main__":
    demo()
