#!/usr/bin/env python3
"""
Frogger Miner - RustChain Port Simulator
============================================

A conceptual demonstration of mining RustChain on Frogger arcade hardware (1981).

This simulator shows how the frog's journey across the river represents
mining rounds, with each successful crossing = 1 "hash" computed.

Author: OpenClaw Agent
Bounty Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
"""

import sys
import time
import random
import hashlib

# Set UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')
from dataclasses import dataclass
from typing import Optional
from enum import Enum


class LaneType(Enum):
    """Types of lanes in Frogger"""
    ROAD = "road"      # Cars - danger!
    RIVER = "river"    # Logs/turtles - need to ride
    SAFE = "safe"      # Starting/ending zone


class FrogState(Enum):
    """Frog states during mining"""
    WAITING = "waiting"
    HOPPING = "hopping"
    RIDING = "riding"  # On log/turtle
    SQUASHED = "squashed"  # Hit by car
    DROWNED = "drowned"  # Fell in water
    SUCCESS = "success"  # Reached home


@dataclass
class Block:
    """Simplified block structure for demonstration"""
    height: int
    previous_hash: str
    timestamp: float
    nonce: int
    miner: str  # Frog ID
    
    @property
    def hash(self) -> str:
        data = f"{self.height}{self.previous_hash}{self.timestamp}{self.nonce}{self.miner}"
        return hashlib.sha256(data.encode()).hexdigest()[:16]


@dataclass
class FrogMiner:
    """The Frogger Miner"""
    id: str
    position: int  # 0-10 (lanes)
    state: FrogState = FrogState.WAITING
    hashes_computed: int = 0
    blocks_found: int = 0
    lives: int = 3
    
    def hop(self) -> bool:
        """Attempt to hop to next lane"""
        if self.state in [FrogState.SQUASHED, FrogState.DROWNED]:
            return False
        self.position += 1
        self.state = FrogState.HOPPING
        self.hashes_computed += 1
        return True
    
    def reset(self):
        """Reset to starting position"""
        self.position = 0
        self.state = FrogState.WAITING


class FroggerMinerSimulator:
    """
    Simulates mining RustChain on Frogger arcade hardware.
    
    The game board has 13 lanes:
    - Lane 0: Starting safe zone
    - Lanes 1-5: Roads with cars (danger!)
    - Lanes 6-10: River with logs (need to ride)
    - Lanes 11-12: Home safe zone + bonus
    
    Each successful crossing = 1 hash
    Reaching home = potential block found
    """
    
    LANES = 13
    DIFFICULTY = 4  # Number of leading zeros needed
    
    def __init__(self, wallet_address: str):
        self.wallet = wallet_address
        self.frog = FrogMiner(id="FROG-001", position=0)
        self.current_block_height = 0
        self.previous_hash = "0" * 64
        self.total_hashes = 0
        self.blocks_mined = 0
        self.start_time = time.time()
        
        # Initialize lanes
        self.lanes = self._generate_lanes()
        
    def _generate_lanes(self) -> list:
        """Generate the game board lanes"""
        lanes = []
        for i in range(self.LANES):
            if i == 0:
                lanes.append(LaneType.SAFE)
            elif i <= 5:
                lanes.append(LaneType.ROAD)
            elif i <= 10:
                lanes.append(LaneType.RIVER)
            else:
                lanes.append(LaneType.SAFE)
        return lanes
    
    def _check_collision(self, lane: int) -> bool:
        """Check if frog hits obstacle (70% chance on roads/river)"""
        if self.lanes[lane] == LaneType.SAFE:
            return False
        # Simulate random obstacle
        return random.random() < 0.3  # 30% safe passage
    
    def _mine_block(self) -> Optional[Block]:
        """Attempt to mine a block when reaching home"""
        # Simplified mining: random chance based on "difficulty"
        hash_result = hashlib.sha256(
            f"{self.current_block_height}{time.time()}{random.random()}".encode()
        ).hexdigest()
        
        if hash_result.startswith("0" * self.DIFFICULTY):
            block = Block(
                height=self.current_block_height,
                previous_hash=self.previous_hash,
                timestamp=time.time(),
                nonce=random.randint(0, 1000000),
                miner=self.frog.id
            )
            self.blocks_mined += 1
            self.current_block_height += 1
            self.previous_hash = block.hash
            return block
        return None
    
    def play_turn(self) -> str:
        """Execute one mining turn (frog hop)"""
        if self.frog.lives <= 0:
            return "GAME OVER - No lives remaining"
        
        if self.frog.position >= self.LANES - 1:
            # Reached home!
            self.frog.state = FrogState.SUCCESS
            block = self._mine_block()
            result = f"🎉 FROG REACHED HOME! "
            if block:
                result += f"⛏️ BLOCK FOUND! Hash: {block.hash}"
                self.frog.blocks_found += 1
            else:
                result += f"💎 Hash computed (no block)"
            self.frog.reset()
            return result
        
        # Attempt to hop
        self.frog.hop()
        current_lane = self.frog.position
        
        # Check for collision
        if not self._check_collision(current_lane):
            lane_type = self.lanes[current_lane]
            if lane_type == LaneType.ROAD:
                self.frog.state = FrogState.SQUASHED
                self.frog.lives -= 1
                self.frog.reset()
                return f"💀 SQUASHED by car at lane {current_lane}! Lives: {self.frog.lives}"
            elif lane_type == LaneType.RIVER:
                self.frog.state = FrogState.DROWNED
                self.frog.lives -= 1
                self.frog.reset()
                return f"🌊 DROWNED in river at lane {current_lane}! Lives: {self.frog.lives}"
        
        self.total_hashes += 1
        return f"🐸 HOP to lane {current_lane} ({self.lanes[current_lane].value}) - Hash #{self.total_hashes}"
    
    def get_stats(self) -> dict:
        """Get mining statistics"""
        elapsed = time.time() - self.start_time
        return {
            "wallet": self.wallet,
            "total_hashes": self.total_hashes,
            "blocks_mined": self.blocks_mined,
            "current_height": self.current_block_height,
            "lives_remaining": self.frog.lives,
            "elapsed_seconds": elapsed,
            "hash_rate": self.total_hashes / max(elapsed, 1),
            "frog_position": self.frog.position,
        }
    
    def run_simulation(self, turns: int = 50, delay: float = 0.5):
        """Run the mining simulation"""
        print("=" * 60)
        print("🐸 FROGGER MINER - RustChain Port Simulator 🎮")
        print("=" * 60)
        print(f"Wallet: {self.wallet}")
        print(f"Lanes: {self.LANES} (SAFE → ROAD×5 → RIVER×5 → SAFE×2)")
        print(f"Difficulty: {self.DIFFICULTY} leading zeros")
        print("=" * 60)
        print()
        
        for turn in range(turns):
            if self.frog.lives <= 0:
                print("💀 GAME OVER!")
                break
            
            result = self.play_turn()
            print(f"Turn {turn + 1:3d}: {result}")
            
            if delay > 0:
                time.sleep(delay)
        
        print()
        print("=" * 60)
        print("📊 MINING STATISTICS")
        print("=" * 60)
        
        stats = self.get_stats()
        for key, value in stats.items():
            if isinstance(value, float):
                print(f"{key}: {value:.4f}")
            else:
                print(f"{key}: {value}")
        
        print("=" * 60)
        print(f"⛏️ Total Hashes: {stats['total_hashes']}")
        print(f"🏆 Blocks Found: {stats['blocks_mined']}")
        print(f"💰 Wallet: {stats['wallet']}")
        print("=" * 60)


def main():
    """Main entry point"""
    wallet = "RTC4325af95d26d59c3ef025963656d22af638bb96b"
    simulator = FroggerMinerSimulator(wallet)
    
    # Run 50 turns with 0.3s delay
    simulator.run_simulation(turns=50, delay=0.3)
    
    print()
    print("🎮 Simulation complete!")
    print("📝 This demonstrates the CONCEPTUAL port of RustChain miner to Frogger.")
    print("🕹️ Actual Z80 hardware would be ~1 trillion times slower.")
    print()


if __name__ == "__main__":
    main()
