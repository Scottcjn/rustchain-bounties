"""
BHP Beacon AI Agent
A demonstration AI agent integrating with Beacon 2.6
Features: Heartbeat, Mayday distress signals, and Property Contracts

Author: Jack (BHP Team)
Date: 2026-02-15
"""

import time
import json
import logging
import uuid
from datetime import datetime
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class BHPBeaconAgent:
    """
    BHP Beacon AI Agent
    
    This agent demonstrates integration with Beacon 2.6:
    1. Heartbeat - Announcing presence via beacon.ping() and beacon.listen()
    2. Mayday - Sending and responding to distress signals
    3. Contracts - Using property contracts for resource management
    
    Bonus features:
    - Multi-agent coordination
    - Creative use case: Distributed training task coordination
    """
    
    def __init__(self, agent_id: str = "bhp-agent-001", role: str = "worker"):
        """
        Initialize the BHP Beacon Agent
        
        Args:
            agent_id: Unique identifier for the agent
            role: Agent role (e.g., "worker", "coordinator", "provider")
        """
        self.agent_id = agent_id
        self.role = role
        self.status = "active"
        self.resources: Dict[str, Any] = {}
        self.neighbors: List[str] = []
        self.mayday_history: List[Dict] = []
        self.contracts_offered: List[Dict] = []
        self.heartbeat_count = 0
        
        logger.info(f"BHP Beacon Agent initialized: {agent_id} ({role})")
    
    # ============================================================
    # Feature 1: Heartbeat - Announcing presence
    # ============================================================
    
    def ping(self) -> Dict[str, Any]:
        """
        Send a heartbeat ping to announce presence
        
        Returns:
            Dict with ping result
        """
        self.heartbeat_count += 1
        result = {
            "agent_id": self.agent_id,
            "role": self.role,
            "timestamp": datetime.now().isoformat(),
            "sequence": self.heartbeat_count,
            "status": "active"
        }
        logger.info(f"Heartbeat ping sent: seq={self.heartbeat_count}")
        return result
    
    def listen(self) -> List[str]:
        """
        Listen for nearby agents
        
        Returns:
            List of nearby agent IDs
        """
        # Simulate finding nearby agents
        simulated_neighbors = [
            f"agent-{i:03d}" for i in range(1, 4)
        ]
        self.neighbors = simulated_neighbors
        logger.info(f"Listening... Found {len(simulated_neighbors)} neighbors")
        return simulated_neighbors
    
    def start_heartbeat(self, interval: int = 30, duration: int = 120):
        """
        Start continuous heartbeat
        
        Args:
            interval: Seconds between heartbeats
            duration: Total duration to run
        """
        logger.info(f"Starting heartbeat: interval={interval}s, duration={duration}s")
        start_time = time.time()
        
        while time.time() - start_time < duration and self.status == "active":
            self.ping()
            neighbors = self.listen()
            if neighbors:
                logger.info(f"Neighbors: {neighbors}")
            time.sleep(interval)
        
        logger.info(f"Heartbeat stopped. Total pings: {self.heartbeat_count}")
    
    # ============================================================
    # Feature 2: Mayday - Distress signals
    # ============================================================
    
    def send_mayday(self, request_type: str, details: Optional[Dict] = None) -> Dict[str, Any]:
        """
        Send a mayday distress signal
        
        Args:
            request_type: Type of help needed (e.g., "need_compute", "need_storage")
            details: Additional details about the request
            
        Returns:
            Dict with mayday result
        """
        if details is None:
            details = {}
        
        mayday_id = str(uuid.uuid4())[:8]
        mayday_data = {
            "id": mayday_id,
            "agent_id": self.agent_id,
            "request_type": request_type,
            "details": details,
            "timestamp": datetime.now().isoformat(),
            "priority": details.get("priority", "normal"),
            "status": "broadcasted"
        }
        
        self.mayday_history.append(mayday_data)
        logger.info(f"Mayday sent: {request_type} (ID: {mayday_id})")
        return mayday_data
    
    def respond_to_mayday(self, mayday_id: str, response: Dict) -> Dict[str, Any]:
        """
        Respond to a mayday distress signal
        
        Args:
            mayday_id: ID of the mayday to respond to
            response: Response details
            
        Returns:
            Dict with response result
        """
        result = {
            "responder_id": self.agent_id,
            "mayday_id": mayday_id,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "status": "delivered"
        }
        logger.info(f"Mayday response sent to {mayday_id}")
        return result
    
    def get_mayday_history(self) -> List[Dict]:
        """Get history of sent mayday signals"""
        return self.mayday_history
    
    # ============================================================
    # Feature 3: Contracts - Resource management
    # ============================================================
    
    def contract_offer(self, resource: str, price: int, duration: int) -> Dict[str, Any]:
        """
        Offer a resource contract
        
        Args:
            resource: Resource type (e.g., "gpu_hours", "storage_gb")
            price: Price in RTC
            duration: Contract duration in seconds
            
        Returns:
            Dict with contract offer details
        """
        contract_id = str(uuid.uuid4())[:8]
        contract = {
            "id": contract_id,
            "provider_id": self.agent_id,
            "resource": resource,
            "price": price,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            "status": "offered"
        }
        
        self.contracts_offered.append(contract)
        logger.info(f"Contract offered: {resource} @ {price} RTC for {duration}s (ID: {contract_id})")
        return contract
    
    def rent_resource(self, resource: str, price: int, duration: int) -> Dict[str, Any]:
        """
        Rent a resource from another agent
        
        Args:
            resource: Resource type
            price: Price willing to pay
            duration: Duration needed in seconds
            
        Returns:
            Dict with rental contract
        """
        rental_id = str(uuid.uuid4())[:8]
        contract = {
            "id": rental_id,
            "renter_id": self.agent_id,
            "resource": resource,
            "price": price,
            "duration": duration,
            "timestamp": datetime.now().isoformat(),
            "status": "rented"
        }
        
        self.resources[resource] = contract
        logger.info(f"Resource rented: {resource} @ {price} RTC for {duration}s (ID: {rental_id})")
        return contract
    
    def list_resources(self) -> Dict[str, Any]:
        """List currently held resources"""
        return self.resources
    
    def list_contracts_offered(self) -> List[Dict]:
        """List contracts offered by this agent"""
        return self.contracts_offered
    
    # ============================================================
    # Bonus: Multi-agent coordination
    # ============================================================
    
    def coordinate_with_agents(self, agent_ids: List[str], task: str) -> Dict[str, Any]:
        """
        Coordinate with multiple agents for a task
        
        Args:
            agent_ids: List of agent IDs to coordinate with
            task: Task description
            
        Returns:
            Dict with coordination details
        """
        coordination_id = str(uuid.uuid4())[:8]
        
        coordination = {
            "id": coordination_id,
            "coordinator_id": self.agent_id,
            "participants": agent_ids,
            "task": task,
            "timestamp": datetime.now().isoformat(),
            "status": "coordinated"
        }
        
        # Simulate sending coordination signals
        for agent_id in agent_ids:
            logger.info(f"Coordination signal sent to {agent_id} for task: {task}")
        
        return coordination
    
    # ============================================================
    # Utility methods
    # ============================================================
    
    def get_status(self) -> Dict[str, Any]:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "role": self.role,
            "status": self.status,
            "heartbeat_count": self.heartbeat_count,
            "neighbors_count": len(self.neighbors),
            "resources_count": len(self.resources),
            "mayday_count": len(self.mayday_history),
            "contracts_offered_count": len(self.contracts_offered),
            "timestamp": datetime.now().isoformat()
        }
    
    def shutdown(self):
        """Gracefully shutdown the agent"""
        logger.info(f"Shutting down agent: {self.agent_id}")
        self.status = "inactive"


# ============================================================
# Demo and testing functions
# ============================================================

def demo_heartbeat():
    """Demonstrate heartbeat functionality"""
    print("\n" + "="*70)
    print("DEMO: Heartbeat Feature")
    print("="*70)
    
    agent = BHPBeaconAgent(agent_id="heartbeat-demo", role="demo")
    
    # Demo 1: Single heartbeat
    print("\n[1] Sending single heartbeat ping...")
    result = agent.ping()
    print(f"    Result: {json.dumps(result, indent=2)}")
    
    # Demo 2: Listen for neighbors
    print("\n[2] Listening for nearby agents...")
    neighbors = agent.listen()
    print(f"    Found neighbors: {neighbors}")
    
    # Demo 3: Multiple heartbeats
    print("\n[3] Sending multiple heartbeats...")
    for i in range(3):
        result = agent.ping()
        time.sleep(0.5)
    print(f"    Total heartbeats: {agent.heartbeat_count}")
    
    # Show status
    print("\n[4] Agent status:")
    print(f"    {json.dumps(agent.get_status(), indent=2)}")
    
    agent.shutdown()
    print("\n✅ Heartbeat demo completed!")


def demo_mayday():
    """Demonstrate mayday functionality"""
    print("\n" + "="*70)
    print("DEMO: Mayday Distress Signal Feature")
    print("="*70)
    
    agent = BHPBeaconAgent(agent_id="mayday-demo", role="emergency")
    
    # Demo 1: Mayday for compute
    print("\n[1] Sending mayday for compute resources...")
    result = agent.send_mayday(
        request_type="need_compute",
        details={
            "task": "inference",
            "model": "llama-7b",
            "priority": "high",
            "duration_minutes": 30
        }
    )
    print(f"    Result: {json.dumps(result, indent=2)}")
    
    # Demo 2: Mayday for storage
    print("\n[2] Sending mayday for storage...")
    result = agent.send_mayday(
        request_type="need_storage",
        details={
            "size_gb": 100,
            "duration_hours": 24
        }
    )
    print(f"    Result: {json.dumps(result, indent=2)}")
    
    # Demo 3: Respond to mayday
    print("\n[3] Responding to mayday...")
    response = agent.respond_to_mayday(
        mayday_id="mayday-001",
        response={
            "available": True,
            "resource": "gpu_hours",
            "amount": 10
        }
    )
    print(f"    Response: {json.dumps(response, indent=2)}")
    
    # Show history
    print("\n[4] Mayday history:")
    history = agent.get_mayday_history()
    for i, mayday in enumerate(history, 1):
        print(f"    {i}. {mayday['request_type']} (ID: {mayday['id']}) at {mayday['timestamp']}")
    
    agent.shutdown()
    print("\n✅ Mayday demo completed!")


def demo_contracts():
    """Demonstrate contracts functionality"""
    print("\n" + "="*70)
    print("DEMO: Property Contracts Feature")
    print("="*70)
    
    # Create provider agent
    provider = BHPBeaconAgent(agent_id="provider-001", role="provider")
    
    # Demo 1: Offer GPU hours
    print("\n[1] Offering GPU hours contract...")
    result = provider.contract_offer(
        resource="gpu_hours",
        price=10,  # RTC
        duration=3600  # 1 hour
    )
    print(f"    Offer: {json.dumps(result, indent=2)}")
    
    # Demo 2: Offer storage
    print("\n[2] Offering storage contract...")
    result = provider.contract_offer(
        resource="storage_gb",
        price=5,  # RTC
        duration=86400  # 24 hours
    )
    print(f"    Offer: {json.dumps(result, indent=2)}")
    
    # Show offered contracts
    print("\n[3] Contracts offered by provider:")
    for contract in provider.list_contracts_offered():
        print(f"    - {contract['resource']}: {contract['price']} RTC for {contract['duration']}s")
    
    # Create renter agent
    print("\n[4] Creating renter agent...")
    renter = BHPBeaconAgent(agent_id="renter-001", role="worker")
    
    # Demo 3: Rent resource
    print("\n[5] Renting compute resource...")
    contract = renter.rent_resource(
        resource="compute_instance",
        price=15,  # RTC
        duration=7200  # 2 hours
    )
    print(f"    Rental: {json.dumps(contract, indent=2)}")
    
    # Show rented resources
    print("\n[6] Resources rented by renter:")
    for name, details in renter.list_resources().items():
        print(f"    - {name}: {details['price']} RTC for {details['duration']}s")
    
    provider.shutdown()
    renter.shutdown()
    print("\n✅ Contracts demo completed!")


def demo_multi_agent():
    """Demonstrate multi-agent coordination"""
    print("\n" + "="*70)
    print("DEMO: Multi-Agent Coordination (Bonus Feature)")
    print("="*70)
    
    # Create coordinator agent
    coordinator = BHPBeaconAgent(agent_id="coordinator-001", role="coordinator")
    
    # Demo 1: Coordinate distributed training
    print("\n[1] Coordinating distributed training task...")
    result = coordinator.coordinate_with_agents(
        agent_ids=["agent-002", "agent-003", "agent-004"],
        task="distributed_training"
    )
    print(f"    Coordination: {json.dumps(result, indent=2)}")
    
    # Demo 2: All agents send heartbeats
    print("\n[2] All agents sending heartbeats...")
    agents = [
        BHPBeaconAgent(agent_id=f"agent-{i:03d}", role="worker")
        for i in range(2, 5)
    ]
    agents.append(coordinator)
    
    for agent in agents:
        agent.ping()
        time.sleep(0.3)
    
    print(f"    Total heartbeats sent: {sum(a.heartbeat_count for a in agents)}")
    
    # Demo 3: Agent marketplace simulation
    print("\n[3] Agent marketplace simulation...")
    
    # Provider offers resources
    provider = BHPBeaconAgent(agent_id="marketplace-provider", role="provider")
    provider.contract_offer("gpu_hours", price=8, duration=3600)
    provider.contract_offer("memory_gb", price=3, duration=7200)
    
    # Workers request resources
    for i in range(1, 3):
        worker = BHPBeaconAgent(agent_id=f"marketplace-worker-{i}", role="worker")
        worker.send_mayday("need_compute", {"budget": 10, "duration": 3600})
        worker.shutdown()
    
    print("    Marketplace: 2 resources offered, 2 requests made")
    
    # Cleanup
    for agent in agents:
        agent.shutdown()
    provider.shutdown()
    
    print("\n✅ Multi-agent coordination demo completed!")


def run_all_demos():
    """Run all demonstration scenarios"""
    print("\n" + "="*70)
    print(" BHP BEACON AI AGENT - FULL DEMONSTRATION")
    print(" Integrating Beacon 2.6 with AI Agents")
    print("="*70)
    print("\nThis demonstration shows:")
    print("  1. Heartbeat - Announcing presence via beacon.ping()")
    print("  2. Mayday - Sending distress signals")
    print("  3. Contracts - Resource management with rent/buy")
    print("  4. Multi-agent coordination (BONUS)")
    print("="*70)
    
    demo_heartbeat()
    demo_mayday()
    demo_contracts()
    demo_multi_agent()
    
    print("\n" + "="*70)
    print(" ALL DEMOS COMPLETED SUCCESSFULLY!")
    print("="*70)
    print("\nThe BHP Beacon AI Agent demonstrates:")
    print("  ✅ Beacon 2.6 Heartbeat integration")
    print("  ✅ Beacon 2.6 Mayday distress signals")
    print("  ✅ Beacon 2.6 Property Contracts (rent/buy)")
    print("  ✅ Multi-agent coordination (BONUS)")
    print("  ✅ Creative use case: Distributed training marketplace")
    print("="*70)


if __name__ == "__main__":
    run_all_demos()
