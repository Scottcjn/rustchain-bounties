#!/usr/bin/env python3
"""
Bounty #17184: Catalog Provider - Agent-to-Agent Flow
Inter-agent communication protocol for catalog providers.

This module implements an agent-to-agent flow for catalog providers
to discover, validate, and exchange miner/agent configurations.
"""

import json
import asyncio
import aiohttp
from typing import Dict, List, Any, Optional, AsyncGenerator
from dataclasses import dataclass, asdict


@dataclass
class CatalogEntry:
    """Represents a catalog entry for a miner or agent."""
    id: str
    name: str
    type: str  # "miner", "agent", "service"
    endpoint: str
    capabilities: List[str]
    status: str  # "active", "inactive", "offline"
    metadata: Dict[str, Any] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CatalogEntry":
        return cls(
            id=data.get("id", ""),
            name=data.get("name", ""),
            type=data.get("type", ""),
            endpoint=data.get("endpoint", ""),
            capabilities=data.get("capabilities", []),
            status=data.get("status", "inactive"),
            metadata=data.get("metadata", {}),
        )


@dataclass
class AgentRequest:
    """Request sent between agents."""
    request_id: str
    source_agent: str
    target_agent: str
    action: str  # "discover", "validate", "reconcile", "spend_rtc"
    payload: Dict[str, Any] = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = subprocess.check_output(
                ["date", "+%Y-%m-%dT%H:%M:%SZ"],
                text=True
            ).strip()
        if self.request_id is None:
            import uuid
            self.request_id = str(uuid.uuid4())


@dataclass  
class AgentResponse:
    """Response to an agent request."""
    request_id: str
    source_agent: str
    target_agent: str
    action: str
    success: bool
    payload: Dict[str, Any] = None
    error: str = None
    timestamp: str = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = subprocess.check_output(
                ["date", "+%Y-%m-%dT%H:%M:%SZ"],
                text=True
            ).strip()


class CatalogProvider:
    """
    Catalog Provider - manages agent-to-agent interactions.
    
    Responsibilities:
    - Discover available agents/miners
    - Validate configurations
    - Reconcile path differences
    - Facilitate RTC spending
    - Maintain catalog state
    """
    
    def __init__(self, base_url: str = "http://localhost:8080", 
                 api_key: str = ""):
        self.base_url = base_url
        self.api_key = api_key
        self.catalog: Dict[str, CatalogEntry] = {}
        self.session = None
    
    async def get_session(self) -> aiohttp.ClientSession:
        """Get or create aiohttp session."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                headers={"Authorization": f"Bearer {self.api_key}"}
            )
        return self.session
    
    async def discover_agents(self, 
                             query: Optional[str] = None) -> List[CatalogEntry]:
        """
        Discover agents/miners in the catalog.
        
        Args:
            query: Optional search query for filtering
            
        Returns:
            List of CatalogEntry objects
        """
        session = await self.get_session()
        
        params = {}
        if query:
            params["query"] = query
        
        async with session.get(
            f"{self.base_url}/catalog/discover",
            params=params
        ) as response:
            if response.status == 200:
                data = await response.json()
                self.catalog = {
                    entry["id"]: CatalogEntry.from_dict(entry)
                    for entry in data.get("entries", [])
                }
                return list(self.catalog.values())
            else:
                raise Exception(
                    f"Discovery failed: {response.status} - {await response.text()}"
                )
    
    async def validate_catalog_entry(
        self, entry_id: str
    ) -> Dict[str, Any]:
        """
        Validate a catalog entry.
        
        Args:
            entry_id: ID of the catalog entry to validate
            
        Returns:
            Dict with validation results
        """
        session = await self.get_session()
        
        async with session.get(
            f"{self.base_url}/catalog/{entry_id}/validate"
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(
                    f"Validation failed: {response.status} - {await response.text()}"
                )
    
    async def reconcile_paths(
        self, 
        entry_id: str,
        source_platform: str,
        target_platform: str,
        paths: List[str]
    ) -> Dict[str, Any]:
        """
        Reconcile paths between different platforms for a catalog entry.
        
        Args:
            entry_id: Catalog entry ID
            source_platform: Source platform (e.g., "windows", "linux")
            target_platform: Target platform (e.g., "linux", "macos")
            paths: List of paths to reconcile
            
        Returns:
            Dict with reconciled paths
        """
        session = await self.get_session()
        
        payload = {
            "source_platform": source_platform,
            "target_platform": target_platform,
            "paths": paths,
        }
        
        async with session.post(
            f"{self.base_url}/catalog/{entry_id}/reconcile",
            json=payload
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(
                    f"Reconciliation failed: {response.status} - {await response.text()}"
                )
    
    async def spend_rtc_agent(
        self,
        from_agent: str,
        to_agent: str,
        amount: float,
        purpose: str,
    ) -> Dict[str, Any]:
        """
        Facilitate RTC spending between agents.
        
        Args:
            from_agent: Source agent ID
            to_agent: Target agent ID  
            amount: Amount of RTC to spend
            purpose: Purpose of the spending
            
        Returns:
            Dict with transaction result
        """
        session = await self.get_session()
        
        payload = {
            "from_agent": from_agent,
            "to_agent": to_agent,
            "amount": amount,
            "purpose": purpose,
        }
        
        async with session.post(
            f"{self.base_url}/rtc/spend",
            json=payload
        ) as response:
            if response.status == 200:
                return await response.json()
            else:
                raise Exception(
                    f"RTC spending failed: {response.status} - {await response.text()}"
                )
    
    async def stream_heartbeat(
        self, agent_id: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Stream heartbeats from an agent.
        
        Yields:
            Dict with heartbeat data at regular intervals
        """
        session = await self.get_session()
        
        async with session.get(
            f"{self.base_url}/agents/{agent_id}/heartbeat",
            headers={"Accept": "application/json-stream"},
            timeout=aiohttp.ClientTimeout(total=300)
        ) as response:
            async for line in response.content:
                line = line.decode("utf-8").strip()
                if line.startswith("data:"):
                    try:
                        data = json.loads(line[5:])
                        yield data
                    except json.JSONDecodeError:
                        continue
    
    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()


async def demo_agent_flow():
    """Demonstrate agent-to-agent flow."""
    provider = CatalogProvider(
        base_url="http://localhost:8080",
        api_key="demo-key"
    )
    
    try:
        # Step 1: Discover agents
        print("Step 1: Discovering agents...")
        agents = await provider.discover_agents()
        print(f"Found {len(agents)} agents")
        
        for agent in agents:
            print(f"  - {agent.name} ({agent.type}): {agent.status}")
        
        # Step 2: Validate a catalog entry
        if agents:
            print("\nStep 2: Validating first agent...")
            validation = await provider.validate_catalog_entry(agents[0].id)
            print(f"Validation result: {validation}")
        
        # Step 3: Reconcile paths
        print("\nStep 3: Reconciling paths...")
        if len(agents) >= 2:
            paths = ["C:/miners/data", "/opt/miners/data", "~/miners/data"]
            reconciled = await provider.reconcile_paths(
                agents[0].id,
                "windows",
                "linux",
                paths
            )
            print(f"Reconciled paths: {reconciled}")
        
        # Step 4: Spend RTC between agents
        print("\nStep 4: Spending RTC between agents...")
        if len(agents) >= 2:
            rtc_result = await provider.spend_rtc_agent(
                from_agent=agents[0].id,
                to_agent=agents[1].id,
                amount=100.0,
                purpose="miner_operation"
            )
            print(f"RTC transaction: {rtc_result}")
    
    finally:
        await provider.close()


if __name__ == "__main__":
    import subprocess
    import uuid
    asyncio.run(demo_agent_flow())