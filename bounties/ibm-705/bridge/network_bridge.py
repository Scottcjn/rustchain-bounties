"""
IBM 705 Network Bridge

This module provides the bridge between the IBM 705 simulator and the modern
RustChain network. Since the IBM 705 (1954) has no network capability,
we use a virtual tape interface for communication.

Architecture:
    ┌─────────────────┐    ┌─────────────────┐
    │  Modern Layer   │    │  IBM 705 Miner  │
    │  (Network I/O)  │◄──►│  (Computation)  │
    └─────────────────┘    └─────────────────┘
           │                       │
           └──── Virtual Tape ─────┘
"""

import json
import hashlib
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from pathlib import Path
import sys

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from ibm705_simulator import IBM705CPU, VirtualIO


@dataclass
class BlockHeader:
    """RustChain block header structure."""
    version: int
    previous_hash: str
    merkle_root: str
    timestamp: int
    difficulty: int
    nonce: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "previous_hash": self.previous_hash,
            "merkle_root": self.merkle_root,
            "timestamp": self.timestamp,
            "difficulty": self.difficulty,
            "nonce": self.nonce
        }
    
    def serialize(self) -> str:
        """Serialize block header for IBM 705 processing."""
        # Simplified: convert to numeric representation
        # In reality, would need to handle full hash
        hash_numeric = int(self.merkle_root[:10], 16) if len(self.merkle_root) >= 10 else 1234567890
        return f"{hash_numeric:010d}"


@dataclass
class MiningResult:
    """Result from IBM 705 mining operation."""
    hash_result: str
    nonce: int
    block_hash: str
    success: bool
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "hash_result": self.hash_result,
            "nonce": self.nonce,
            "block_hash": self.block_hash,
            "success": self.success
        }


class RustChainNetworkBridge:
    """
    Bridge between IBM 705 miner and RustChain network.
    
    Responsibilities:
    1. Fetch block headers from network
    2. Convert to IBM 705 format
    3. Load onto virtual tape
    4. Read results from 705
    5. Submit valid proofs to network
    """
    
    def __init__(self, network_url: str = "http://localhost:8080"):
        self.network_url = network_url
        self.cpu = IBM705CPU()
        self.io = self.cpu.io
        self.mining_program: Optional[str] = None
        self.current_block: Optional[BlockHeader] = None
    
    def load_mining_program(self, program_path: str) -> None:
        """Load IBM 705 assembly mining program."""
        with open(program_path, 'r') as f:
            self.mining_program = f.read()
        self.cpu.load_program(self.mining_program, start=200)
    
    def fetch_block(self) -> Optional[BlockHeader]:
        """
        Fetch current block from RustChain network.
        
        In production, this would make HTTP requests to RustChain nodes.
        For simulation, we generate a test block.
        """
        # TODO: Implement actual network call
        # response = requests.get(f"{self.network_url}/api/v1/block/current")
        
        # Simulated block for testing
        block = BlockHeader(
            version=1,
            previous_hash="0000000000000000000000000000000000000000000000000000000000000000",
            merkle_root="abcd1234567890abcd1234567890abcd1234567890abcd1234567890abcd1234",
            timestamp=int(time.time()),
            difficulty=9999999999,  # Easy difficulty for testing
            nonce=0
        )
        
        self.current_block = block
        return block
    
    def prepare_block_for_705(self, block: BlockHeader) -> None:
        """
        Prepare block data for IBM 705 processing.
        
        Memory layout:
        0100-0109: NONCE (starts at 0)
        0110-0119: BLOCK_DATA (block header hash)
        0120-0129: DIFFICULTY (target)
        """
        # Initialize nonce to 0
        self.cpu.memory.write_string(100, "0000000000")
        
        # Block data (simplified hash representation)
        block_data = block.serialize()
        self.cpu.memory.write_string(110, block_data)
        
        # Difficulty target
        difficulty_str = f"{block.difficulty:010d}"
        self.cpu.memory.write_string(120, difficulty_str)
        
        print(f"Block prepared for IBM 705:")
        print(f"  Block Data: {block_data}")
        print(f"  Difficulty: {difficulty_str}")
    
    def run_mining(self, max_instructions: int = 100000) -> MiningResult:
        """
        Run IBM 705 mining operation.
        
        Returns MiningResult with hash, nonce, and success status.
        """
        if not self.mining_program:
            raise ValueError("No mining program loaded")
        
        print(f"Starting IBM 705 mining operation...")
        print(f"Max instructions: {max_instructions}")
        
        # Run the CPU
        start_time = time.time()
        self.cpu.run(max_instructions=max_instructions)
        elapsed = time.time() - start_time
        
        # Read results
        hash_result = self.cpu.memory.read_string(140, 10)
        nonce_str = self.cpu.memory.read_string(100, 10)
        nonce = int(nonce_str.strip())
        
        # Check if solution was found (CPU halted)
        success = self.cpu.state.program_status == "HALT"
        
        # Compute actual block hash with found nonce
        block_hash = self._compute_block_hash(nonce)
        
        result = MiningResult(
            hash_result=hash_result.strip(),
            nonce=nonce,
            block_hash=block_hash,
            success=success
        )
        
        print(f"Mining complete in {elapsed:.2f}s")
        print(f"  Instructions executed: {self.cpu.state.instructions_executed}")
        print(f"  Nonce: {nonce}")
        print(f"  Hash: {hash_result.strip()}")
        print(f"  Success: {success}")
        
        return result
    
    def _compute_block_hash(self, nonce: int) -> str:
        """Compute actual block hash with nonce."""
        if not self.current_block:
            return "0" * 64
        
        # Create hash of block header + nonce
        header_data = json.dumps(self.current_block.to_dict(), sort_keys=True)
        full_hash = hashlib.sha256(f"{header_data}{nonce}".encode()).hexdigest()
        return full_hash
    
    def submit_result(self, result: MiningResult) -> bool:
        """
        Submit mining result to RustChain network.
        
        Returns True if submission accepted.
        """
        if not result.success:
            print("No valid solution to submit")
            return False
        
        # TODO: Implement actual network submission
        # response = requests.post(
        #     f"{self.network_url}/api/v1/mining/submit",
        #     json=result.to_dict()
        # )
        # return response.status_code == 200
        
        # Simulated submission
        print(f"Submitting result to network...")
        print(f"  Nonce: {result.nonce}")
        print(f"  Block Hash: {result.block_hash}")
        print("Submission accepted! (simulated)")
        return True
    
    def mine_block(self, max_instructions: int = 100000) -> Optional[MiningResult]:
        """
        Complete mining workflow: fetch, mine, submit.
        
        Returns MiningResult if successful, None otherwise.
        """
        # Step 1: Fetch block from network
        block = self.fetch_block()
        if not block:
            print("Failed to fetch block")
            return None
        
        # Step 2: Prepare for IBM 705
        self.prepare_block_for_705(block)
        
        # Step 3: Run mining
        result = self.run_mining(max_instructions)
        
        # Step 4: Submit if successful
        if result.success:
            self.submit_result(result)
        
        return result


class MockRustChainNode:
    """
    Mock RustChain node for testing.
    
    Simulates network responses without actual network calls.
    """
    
    def __init__(self):
        self.blocks_mined = 0
        self.submissions = []
    
    def get_current_block(self) -> Dict[str, Any]:
        """Return mock block data."""
        return {
            "version": 1,
            "previous_hash": "0" * 64,
            "merkle_root": "abcd1234" * 8,
            "timestamp": int(time.time()),
            "difficulty": 9999999999
        }
    
    def submit_mining_result(self, result: Dict[str, Any]) -> bool:
        """Accept mining submission."""
        self.submissions.append(result)
        self.blocks_mined += 1
        return True
    
    def get_stats(self) -> Dict[str, Any]:
        """Get node statistics."""
        return {
            "blocks_mined": self.blocks_mined,
            "submissions": len(self.submissions)
        }


def demo_mining():
    """Demonstrate IBM 705 mining workflow."""
    print("=" * 60)
    print("IBM 705 RustChain Miner - Demo")
    print("=" * 60)
    
    # Create bridge
    bridge = RustChainNetworkBridge()
    
    # Load mining program
    mining_program_path = Path(__file__).parent.parent / "mining_code.asm"
    if mining_program_path.exists():
        bridge.load_mining_program(str(mining_program_path))
        print(f"Loaded mining program: {mining_program_path}")
    else:
        print("Using built-in mining program")
    
    # Mine a block
    result = bridge.mine_block(max_instructions=10000)
    
    if result:
        print("\n" + "=" * 60)
        print("Mining Results:")
        print(f"  Nonce: {result.nonce}")
        print(f"  Hash: {result.hash_result}")
        print(f"  Block Hash: {result.block_hash}")
        print(f"  Success: {result.success}")
        print("=" * 60)
    
    return result


if __name__ == "__main__":
    demo_mining()
