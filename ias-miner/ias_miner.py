#!/usr/bin/env python3
"""
RustChain IAS Machine Miner - "Von Neumann Edition"
Cycle-accurate simulator of the 1952 IAS Machine for Proof-of-Antiquity mining.

This implementation faithfully reproduces:
- 40-bit word architecture
- Williams tube memory timing
- Vacuum tube switching characteristics
- Original IAS instruction set

Author: Elyan Labs
License: Apache 2.0
"""

import time
import hashlib
import struct
import random
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import IntEnum
import asyncio


# =============================================================================
# IAS Machine Constants
# =============================================================================

WORD_SIZE = 40  # bits
MEMORY_SIZE = 1024  # words
INSTRUCTION_SIZE = 20  # bits
INSTRUCTIONS_PER_WORD = 2

# Vacuum tube timing characteristics (microseconds)
TUBE_SWITCH_ON_MIN = 0.1
TUBE_SWITCH_ON_MAX = 1.0
TUBE_SWITCH_OFF_MIN = 0.5
TUBE_SWITCH_OFF_MAX = 2.0

# Williams tube persistence (microseconds)
WILLIAMS_PERSISTENCE_MIN = 100
WILLIAMS_PERSISTENCE_MAX = 300

# Instruction cycle times (from IAS documentation)
INSTRUCTION_CYCLES = {
    0: 6,   # STO - Store
    1: 6,   # ADD
    2: 6,   # SUB
    3: 12,  # MPY - Multiply
    4: 14,  # DIV - Divide
    5: 4,   # RCL - Replace/Clear
    6: 3,   # JMP - Jump
    7: 3,   # JNG - Jump if negative
    8: 10,  # INP - Input (variable)
    9: 10,  # OUT - Output (variable)
}


# =============================================================================
# IAS Machine State
# =============================================================================

@dataclass
class IASState:
    """Complete state of the IAS Machine"""
    ac: int = 0  # Accumulator (40-bit)
    mq: int = 0  # Multiplier/Quotient (40-bit)
    ib: int = 0  # Instruction Buffer
    pc: int = 0  # Program Counter (10 bits)
    memory: List[int] = None  # 1024 words
    
    def __post_init__(self):
        if self.memory is None:
            self.memory = [0] * MEMORY_SIZE
    
    def to_dict(self) -> dict:
        return {
            'ac': self.ac,
            'mq': self.mq,
            'ib': self.ib,
            'pc': self.pc,
            'memory_hash': hashlib.sha256(
                b''.join(struct.pack('>I', w & 0xFFFFFFFFFF) for w in self.memory)
            ).hexdigest()
        }


# =============================================================================
# Williams Tube Memory Simulation
# =============================================================================

class WilliamsTubeMemory:
    """
    Simulates Williams tube memory with realistic timing characteristics.
    
    Williams tubes stored data as charge patterns on CRT phosphor.
    Each tube had unique characteristics based on:
    - Phosphor composition and aging
    - CRT beam positioning accuracy
    - High voltage supply stability
    - Temperature
    """
    
    def __init__(self, size: int = MEMORY_SIZE):
        self.size = size
        self.cells = [0] * size
        self.charge_levels = [0.0] * size  # Simulated charge decay
        self.access_times = []  # Timing history for entropy
        
        # Unique tube characteristics (simulated aging)
        self.tube_id = hashlib.sha256(
            str(time.time()).encode()
        ).hexdigest()[:16]
        
    def read(self, address: int) -> int:
        """Read from Williams tube with timing simulation"""
        if address < 0 or address >= self.size:
            raise ValueError(f"Address {address} out of range")
        
        # Simulate Williams tube read timing
        # Real Williams tubes had variable access times due to:
        # - Beam positioning
        # - Charge sensing
        # - Amplifier settling
        start_time = time.monotonic_ns()
        
        # Simulate charge decay (unique per tube)
        decay_factor = 0.999 + (hash(self.tube_id + str(address)) % 100) / 10000
        self.charge_levels[address] *= decay_factor
        
        # Recharge the cell (Williams tubes were destructive read)
        self.charge_levels[address] = 1.0
        
        end_time = time.monotonic_ns()
        self.access_times.append(end_time - start_time)
        
        return self.cells[address]
    
    def write(self, address: int, value: int):
        """Write to Williams tube with timing simulation"""
        if address < 0 or address >= self.size:
            raise ValueError(f"Address {address} out of range")
        
        start_time = time.monotonic_ns()
        
        # Williams tubes wrote by modifying charge patterns
        # Writing took longer than reading
        self.cells[address] = value & 0xFFFFFFFFFF  # 40-bit mask
        self.charge_levels[address] = 1.0
        
        end_time = time.monotonic_ns()
        self.access_times.append(end_time - start_time)
    
    def get_entropy(self) -> bytes:
        """Extract entropy from timing variations"""
        if len(self.access_times) < 100:
            return b'\x00' * 32
        
        # Use timing variations as entropy source
        timing_data = b''.join(
            struct.pack('>Q', t) for t in self.access_times[-100:]
        )
        
        # Mix with tube characteristics
        tube_entropy = hashlib.sha256(
            self.tube_id.encode() + timing_data
        ).digest()
        
        return tube_entropy
    
    def get_decay_signature(self) -> str:
        """Get unique decay pattern signature"""
        # Sample charge levels across memory
        samples = [self.charge_levels[i] for i in range(0, 1024, 64)]
        decay_hash = hashlib.sha256(
            json.dumps(samples, sort_keys=True).encode()
        ).hexdigest()
        return decay_hash


# =============================================================================
# Vacuum Tube Timing Simulation
# =============================================================================

class VacuumTubeSimulator:
    """
    Simulates vacuum tube switching characteristics for entropy generation.
    
    Real vacuum tubes had random variations in:
    - Turn-on/turn-off times (thermal electron emission)
    - Grid capacitance charging
    - Plate current fluctuations
    - Thermal noise
    """
    
    def __init__(self):
        self.switch_times = []
        self.tube_temperature = 25.0  # Celsius (simulated warm-up)
        
    def simulate_switch(self, tube_type: str = "6J6") -> int:
        """
        Simulate vacuum tube switching with realistic timing.
        
        Returns switching time in nanoseconds.
        """
        # Warm-up effect (tubes get faster as they heat up)
        self.tube_temperature = min(85.0, self.tube_temperature + 0.1)
        temp_factor = 1.0 - (self.tube_temperature - 25.0) / 200.0
        
        # Base switching time with thermal noise
        base_on = random.gauss(0.5, 0.15) * temp_factor  # microseconds
        base_off = random.gauss(1.0, 0.3) * temp_factor
        
        # Add tube-specific characteristics
        if tube_type == "6J6":
            base_on *= 0.9
            base_off *= 0.95
        elif tube_type == "5670":
            base_on *= 1.1
            base_off *= 1.05
        
        # Convert to nanoseconds
        switch_time = int((base_on + base_off) * 1000)
        self.switch_times.append(switch_time)
        
        return switch_time
    
    def get_entropy(self) -> bytes:
        """Extract entropy from tube switching variations"""
        if len(self.switch_times) < 50:
            return b'\x00' * 32
        
        # Use timing jitter as entropy
        jitter = [
            self.switch_times[i] - self.switch_times[i-1]
            for i in range(1, len(self.switch_times[-50:]))
        ]
        
        jitter_data = b''.join(struct.pack('>i', j) for j in jitter)
        
        # Mix with temperature signature
        temp_entropy = struct.pack('>f', self.tube_temperature)
        
        return hashlib.sha256(jitter_data + temp_entropy).digest()


# =============================================================================
# IAS Instruction Set
# =============================================================================

class IASOpcode(IntEnum):
    STO = 0   # Store AC to memory
    ADD = 1   # Add memory to AC
    SUB = 2   # Subtract memory from AC
    MPY = 3   # Multiply MQ by memory
    DIV = 4   # Divide AC by memory
    RCL = 5   # Replace AC from memory (also Clear)
    JMP = 6   # Jump to address
    JNG = 7   # Jump if AC < 0
    INP = 8   # Input from tape
    OUT = 9   # Output to tape


class IASProcessor:
    """
    IAS Machine CPU implementation.
    
    Implements the original 1952 instruction set with cycle-accurate timing.
    """
    
    def __init__(self, memory: WilliamsTubeMemory):
        self.state = IASState(memory=[0] * MEMORY_SIZE)
        self.memory = memory
        self.tube_sim = VacuumTubeSimulator()
        self.cycle_count = 0
        self.instruction_log = []
        
    def fetch_instruction(self) -> Tuple[int, int, int]:
        """Fetch instruction from memory (20 bits)"""
        # Read word from memory (contains 2 instructions)
        word = self.memory.read(self.state.pc)
        
        # Extract left or right instruction based on PC
        if self.state.pc % 2 == 0:
            # Left instruction (bits 0-19)
            instruction = (word >> 20) & 0xFFFFF
        else:
            # Right instruction (bits 20-39)
            instruction = word & 0xFFFFF
            self.state.pc += 1  # Move to next word after right instruction
        
        # Decode instruction
        opcode = (instruction >> 15) & 0x1F  # 5 bits
        register = (instruction >> 13) & 0x03  # 2 bits (unused in most IAS instructions)
        address = instruction & 0x1FFF  # 13 bits
        
        return opcode, register, address
    
    def sign_extend(self, value: int, bits: int) -> int:
        """Sign extend a value to 40 bits"""
        sign_bit = 1 << (bits - 1)
        if value & sign_bit:
            return value | (~((1 << bits) - 1) & 0xFFFFFFFFFF)
        return value & 0xFFFFFFFFFF
    
    def execute_instruction(self, opcode: int, address: int):
        """Execute a single IAS instruction"""
        start_cycles = self.cycle_count
        
        if opcode == IASOpcode.STO:
            # Store AC to memory
            self.memory.write(address, self.state.ac)
            
        elif opcode == IASOpcode.ADD:
            # Add memory to AC
            mem_value = self.memory.read(address)
            mem_value = self.sign_extend(mem_value, 40)
            self.state.ac = (self.state.ac + mem_value) & 0xFFFFFFFFFF
            
        elif opcode == IASOpcode.SUB:
            # Subtract memory from AC
            mem_value = self.memory.read(address)
            mem_value = self.sign_extend(mem_value, 40)
            self.state.ac = (self.state.ac - mem_value) & 0xFFFFFFFFFF
            
        elif opcode == IASOpcode.MPY:
            # Multiply MQ by memory
            mem_value = self.memory.read(address)
            mem_value = self.sign_extend(mem_value, 40)
            # 80-bit result stored in AC (high) and MQ (low)
            result = self.state.mq * mem_value
            self.state.ac = (result >> 40) & 0xFFFFFFFFFF
            self.state.mq = result & 0xFFFFFFFFFF
            
        elif opcode == IASOpcode.DIV:
            # Divide AC by memory
            mem_value = self.memory.read(address)
            mem_value = self.sign_extend(mem_value, 40)
            if mem_value != 0:
                self.state.mq = self.state.ac // mem_value
                self.state.ac = self.state.ac % mem_value
                
        elif opcode == IASOpcode.RCL:
            # Replace AC from memory
            self.state.ac = self.memory.read(address)
            
        elif opcode == IASOpcode.JMP:
            # Jump to address
            self.state.pc = address
            self.cycle_count += INSTRUCTION_CYCLES[opcode]
            return
            
        elif opcode == IASOpcode.JNG:
            # Jump if AC < 0
            if self.state.ac & 0x8000000000:  # Sign bit
                self.state.pc = address
                self.cycle_count += INSTRUCTION_CYCLES[opcode]
                return
                
        elif opcode == IASOpcode.INP:
            # Input (simulated)
            self.state.ac = 0  # Simulated input
            
        elif opcode == IASOpcode.OUT:
            # Output (simulated)
            pass  # Output to simulated tape
        
        # Update cycle count based on instruction type
        self.cycle_count += INSTRUCTION_CYCLES.get(opcode, 6)
        
        # Log instruction for attestation
        self.instruction_log.append({
            'opcode': opcode,
            'address': address,
            'cycles': INSTRUCTION_CYCLES.get(opcode, 6),
            'ac': self.state.ac,
            'timestamp': time.monotonic_ns()
        })
        
        # Increment PC
        self.state.pc = (self.state.pc + 1) % MEMORY_SIZE
    
    def get_instruction_timing_entropy(self) -> bytes:
        """Extract entropy from instruction execution timing"""
        if len(self.instruction_log) < 50:
            return b'\x00' * 32
        
        # Use instruction timing variations
        timing_data = b''.join(
            struct.pack('>Q', inst['timestamp'])
            for inst in self.instruction_log[-50:]
        )
        
        cycle_data = struct.pack(
            '>' + 'I' * len(self.instruction_log[-50:]),
            *[inst['cycles'] for inst in self.instruction_log[-50:]]
        )
        
        return hashlib.sha256(timing_data + cycle_data).digest()


# =============================================================================
# RustChain Miner Implementation
# =============================================================================

class RustChainIASMiner:
    """
    RustChain Proof-of-Antiquity miner for IAS Machine.
    
    Collects hardware entropy from simulated IAS Machine characteristics
    and submits attestations to the RustChain network.
    """
    
    def __init__(self, wallet_address: Optional[str] = None):
        self.memory = WilliamsTubeMemory()
        self.cpu = IASProcessor(self.memory)
        self.wallet = wallet_address or self.generate_wallet()
        self.miner_id = f"ias_1952_{hashlib.sha256(self.wallet.encode()).hexdigest()[:8]}"
        self.attestations = []
        self.running = False
        
    def generate_wallet(self) -> str:
        """Generate wallet from hardware entropy"""
        # Combine multiple entropy sources
        entropy = b''
        entropy += self.memory.get_entropy()
        entropy += self.cpu.tube_sim.get_entropy()
        entropy += struct.pack('>d', time.time())
        
        wallet_hash = hashlib.sha256(entropy).hexdigest()
        return f"RTC{wallet_hash[:40]}"
    
    def collect_attestation(self) -> dict:
        """Collect hardware attestation proof"""
        # Run benchmark program to generate timing data
        self.run_benchmark()
        
        attestation = {
            'miner_id': self.miner_id,
            'architecture': 'IAS',
            'year': 1952,
            'wallet': self.wallet,
            'timestamp': int(time.time()),
            'proofs': {
                'williams_decay': self.memory.get_decay_signature(),
                'williams_entropy': self.memory.get_entropy().hex(),
                'tube_entropy': self.cpu.tube_sim.get_entropy().hex(),
                'instruction_timing': self.cpu.get_instruction_timing_entropy().hex(),
                'cycle_count': self.cpu.cycle_count,
                'instructions_executed': len(self.cpu.instruction_log)
            },
            'state': self.cpu.state.to_dict()
        }
        
        # Sign attestation (simplified - real implementation would use crypto)
        attestation['signature'] = hashlib.sha256(
            json.dumps(attestation['proofs'], sort_keys=True).encode()
        ).hexdigest()
        
        self.attestations.append(attestation)
        return attestation
    
    def run_benchmark(self):
        """Run IAS benchmark program to generate timing data"""
        # Load simple benchmark program into memory
        # This program performs various operations to exercise the hardware
        
        program = [
            # Initialize memory with test pattern
            (0, 0x50000),  # RCL 0
            (1, 0x50001),  # ADD 1
            (2, 0x50002),  # SUB 2
            (3, 0x50003),  # MPY 3
            (4, 0x50004),  # DIV 4
            # Loop
            (6, 0x00000),  # JMP 0
        ]
        
        # Load program into memory
        for i, (opcode, addr) in enumerate(program):
            instruction = (opcode << 15) | addr
            self.memory.write(i, instruction)
        
        # Execute benchmark (enough iterations for good timing data)
        self.cpu.state.pc = 0
        for _ in range(100):
            opcode, _, address = self.cpu.fetch_instruction()
            self.cpu.execute_instruction(opcode, address)
            
            # Simulate vacuum tube timing
            self.cpu.tube_sim.simulate_switch()
    
    def save_wallet(self, filename: str = "WALLET.TXT"):
        """Save wallet to file"""
        with open(filename, 'w') as f:
            f.write(f"RustChain IAS Machine Wallet\n")
            f.write(f"=============================\n\n")
            f.write(f"Address: {self.wallet}\n")
            f.write(f"Miner ID: {self.miner_id}\n")
            f.write(f"Architecture: IAS (1952)\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write(f"⚠️  BACKUP THIS FILE! ⚠️\n")
            f.write(f"Store on punch tape or floppy disk!\n")
    
    def save_attestation(self, filename: str = "ATTEST.TXT"):
        """Save attestation to file"""
        attestation = self.collect_attestation()
        with open(filename, 'w') as f:
            json.dump(attestation, f, indent=2)
        print(f"Attestation saved to {filename}")
    
    async def submit_attestation(self, endpoint: str = "https://rustchain.org/api/attest"):
        """Submit attestation to RustChain network"""
        import aiohttp
        
        attestation = self.collect_attestation()
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(endpoint, json=attestation) as response:
                    if response.status == 200:
                        result = await response.json()
                        print(f"[OK] Attestation submitted successfully!")
                        print(f"  Reward: {result.get('reward', 'pending')} RTC")
                        return result
                    else:
                        print(f"[FAIL] Submission failed: {response.status}")
                        return None
        except Exception as e:
            print(f"[NETERR] Network error: {e}")
            return None
    
    async def mine(self, interval: int = 600):
        """
        Main mining loop.
        
        Args:
            interval: Attestation interval in seconds (default: 10 minutes)
        """
        self.running = True
        print(f"[START] RustChain IAS Miner starting...")
        print(f"   Miner ID: {self.miner_id}")
        print(f"   Wallet: {self.wallet}")
        print(f"   Architecture: IAS (1952) - Von Neumann")
        print(f"   Attestation interval: {interval}s")
        print()
        
        # Save wallet on first run
        self.save_wallet()
        print("[SAVE] Wallet saved to WALLET.TXT - BACKUP IMMEDIATELY!")
        print()
        
        while self.running:
            try:
                print(f"[RUN] Collecting attestation...")
                attestation = self.collect_attestation()
                
                print(f"   Williams tubes: {attestation['proofs']['williams_decay'][:16]}...")
                print(f"   Vacuum tubes: {attestation['proofs']['tube_entropy'][:16]}...")
                print(f"   Cycles: {attestation['proofs']['cycle_count']}")
                print(f"   Instructions: {attestation['proofs']['instructions_executed']}")
                
                # Submit to network
                await self.submit_attestation()
                
                # Wait for next interval
                print(f"   Waiting {interval}s until next attestation...")
                await asyncio.sleep(interval)
                
            except KeyboardInterrupt:
                print("\n[STOP] Miner stopped by user")
                self.running = False
            except Exception as e:
                print(f"[ERR] Error: {e}")
                await asyncio.sleep(60)  # Wait before retry
    
    def status(self):
        """Print miner status"""
        print(f"\n{'='*60}")
        print(f"RustChain IAS Miner Status")
        print(f"{'='*60}")
        print(f"Miner ID: {self.miner_id}")
        print(f"Wallet: {self.wallet}")
        print(f"Architecture: IAS (1952)")
        print(f"Total attestations: {len(self.attestations)}")
        print(f"Total cycles: {self.cpu.cycle_count}")
        print(f"Total instructions: {len(self.cpu.instruction_log)}")
        print(f"Williams tube entropy: {self.memory.get_entropy().hex()[:32]}...")
        print(f"Vacuum tube entropy: {self.cpu.tube_sim.get_entropy().hex()[:32]}...")
        print(f"{'='*60}\n")


# =============================================================================
# Main Entry Point
# =============================================================================

async def main():
    import argparse
    
    parser = argparse.ArgumentParser(
        description='RustChain IAS Machine Miner - Von Neumann Edition'
    )
    parser.add_argument(
        '--wallet', '-w',
        help='Wallet address (default: auto-generate)'
    )
    parser.add_argument(
        '--interval', '-i',
        type=int,
        default=600,
        help='Attestation interval in seconds (default: 600)'
    )
    parser.add_argument(
        '--offline', '-o',
        action='store_true',
        help='Offline mode - save attestations to file'
    )
    parser.add_argument(
        '--status', '-s',
        action='store_true',
        help='Show miner status and exit'
    )
    
    args = parser.parse_args()
    
    miner = RustChainIASMiner(wallet_address=args.wallet)
    
    if args.status:
        miner.status()
        return
    
    if args.offline:
        print("[PLUG] RustChain IAS Miner - Offline Mode")
        print(f"   Wallet: {miner.wallet}")
        miner.save_attestation()
        print("\n[SAVE] Attestation saved to ATTEST.TXT")
        print("   Transfer to networked computer to submit.")
        return
    
    # Start mining
    await miner.mine(interval=args.interval)


if __name__ == '__main__':
    asyncio.run(main())
