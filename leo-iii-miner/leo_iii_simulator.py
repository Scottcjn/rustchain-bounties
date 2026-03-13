#!/usr/bin/env python3
"""
LEO III (1961) Simulator - RustChain Proof-of-Antiquity Miner

This module simulates the LEO III computer, the world's first mass-produced
commercial computer, and implements a conceptual RustChain miner.

Author: RustChain Bounty Hunter
Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
License: MIT OR Apache-2.0
"""

import random
import time
import argparse
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class CoreMemory:
    """Ferrite core memory simulation for LEO III"""
    size_words: int = 8192  # 8K words default
    words: List[int] = field(default_factory=list)
    residual_pattern: int = 0
    
    def __post_init__(self):
        if not self.words:
            self.words = [0] * self.size_words
        if self.residual_pattern == 0:
            # Unique residual magnetization pattern (simulated)
            self.residual_pattern = random.randint(0, 0xFFFFFFFF)
    
    def read(self, address: int) -> int:
        """Read a 32-bit word from memory"""
        if 0 <= address < self.size_words:
            return self.words[address] & 0xFFFFFFFF
        return 0
    
    def write(self, address: int, value: int):
        """Write a 32-bit word to memory"""
        if 0 <= address < self.size_words:
            self.words[address] = value & 0xFFFFFFFF
    
    def get_fingerprint(self) -> str:
        """Get unique core memory fingerprint"""
        return f"{self.residual_pattern:08X}"


@dataclass
class MagneticTape:
    """Magnetic tape unit simulation"""
    unit_id: int
    records: List[str] = field(default_factory=list)
    
    def write_record(self, record: str):
        """Write a record to tape"""
        self.records.append(record)
    
    def read_records(self) -> List[str]:
        """Read all records from tape"""
        return self.records.copy()


@dataclass
class MiningShare:
    """RustChain mining share structure"""
    timestamp: int
    wallet: str
    fingerprint: str
    nonce: int
    hash_value: int
    difficulty: int
    job_number: int
    
    def is_valid(self) -> bool:
        return self.hash_value < self.difficulty
    
    def to_paper_tape(self) -> str:
        """Format share as 80-character paper tape record"""
        # Format: wallet(16) + fingerprint(16) + nonce(8) + hash(8) + difficulty(8) + timestamp(16) + job(2) + checksum(6) = 80
        wallet_short = self.wallet[:16] if len(self.wallet) > 16 else self.wallet
        fp_short = self.fingerprint[:16] if len(self.fingerprint) > 16 else self.fingerprint
        result = (
            f"{wallet_short:<16}"
            f"{fp_short:<16}"
            f"{self.nonce:08X}"
            f"{self.hash_value:08X}"
            f"{self.difficulty:08X}"
            f"{self.timestamp:016d}"
            f"{self.job_number:02d}"
        )
        # Pad or truncate to exactly 80 characters
        if len(result) < 80:
            result = result.ljust(80)
        return result[:80]
    
    def __str__(self) -> str:
        return (
            f"Wallet:     {self.wallet}\n"
            f"Fingerprint: {self.fingerprint}\n"
            f"Nonce:      {self.nonce:06X}\n"
            f"Hash:       {self.hash_value:06X}\n"
            f"Difficulty: {self.difficulty:06X}\n"
            f"Timestamp:  {self.timestamp}\n"
            f"Job:        {self.job_number}"
        )


class MasterProgram:
    """LEO III Master Program OS simulation"""
    
    def __init__(self, time_slice_ms: int = 100, max_jobs: int = 12):
        self.time_slice_ms = time_slice_ms
        self.max_jobs = max_jobs
        self.jobs: List[dict] = []
        self.current_job: int = 0
        self.job_counter: int = 0
    
    def register_job(self, name: str, priority: str = "Low", memory_kb: int = 2) -> int:
        """Register a new job with Master Program"""
        if len(self.jobs) >= self.max_jobs:
            raise RuntimeError("Maximum jobs (12) reached")
        
        job_number = self.job_counter + 1
        self.job_counter += 1
        
        self.jobs.append({
            'number': job_number,
            'name': name,
            'priority': priority,
            'memory_kb': memory_kb,
            'start_time': None,
            'time_remaining': 0
        })
        
        return job_number
    
    def check_time(self) -> bool:
        """Check if current job's time slice is still valid"""
        if self.current_job >= len(self.jobs):
            return False
        
        job = self.jobs[self.current_job]
        if job['time_remaining'] <= 0:
            return False
        
        return True
    
    def yield_cpu(self):
        """Yield CPU to Master Program scheduler"""
        if self.current_job < len(self.jobs):
            self.jobs[self.current_job]['time_remaining'] = 0
    
    def schedule_next(self):
        """Schedule next job (round-robin)"""
        if self.jobs:
            self.current_job = (self.current_job + 1) % len(self.jobs)
            job = self.jobs[self.current_job]
            job['time_remaining'] = self.time_slice_ms
    
    def get_current_job_number(self) -> int:
        """Get current job number"""
        if self.jobs and self.current_job < len(self.jobs):
            return self.jobs[self.current_job]['number']
        return 0


class LEOIII:
    """LEO III Computer Simulator"""
    
    # Instruction opcodes
    OP_LOAD = 0x01
    OP_STORE = 0x02
    OP_ADD = 0x03
    OP_SUB = 0x04
    OP_MUL = 0x05
    OP_DIV = 0x06
    OP_JUMP = 0x07
    OP_JPOS = 0x08
    OP_JNEG = 0x09
    OP_JZER = 0x0A
    OP_INPUT = 0x0B
    OP_OUTPUT = 0x0C
    OP_MASTER = 0x0D
    OP_AND = 0x0E
    OP_OR = 0x0F
    OP_XOR = 0x10
    OP_SOUND = 0x11
    OP_PUNCH = 0x12
    OP_STOP = 0x00
    
    def __init__(self, memory_size: int = 8192):
        self.memory = CoreMemory(size_words=memory_size)
        self.accumulator = 0
        self.program_counter = 0
        self.halted = False
        self.instructions_executed = 0
        self.tape_units: List[MagneticTape] = []
        self.master_program = MasterProgram()
        self.loudspeaker_active = False
        self.last_sound_frequency = 0
        self.output_buffer: List[str] = []
        self.punched_tapes: List[str] = []
        
        # Initialize with some tape units
        for i in range(4):
            self.tape_units.append(MagneticTape(unit_id=i))
    
    def load_program(self, program: List[int], start_address: int = 0):
        """Load a program into memory"""
        for i, instruction in enumerate(program):
            self.memory.write(start_address + i, instruction)
    
    def get_fingerprint(self) -> str:
        """Generate system fingerprint"""
        core_fp = self.memory.get_fingerprint()
        tape_fp = sum(t.unit_id for t in self.tape_units) & 0xFFFFFFFF
        combined = (int(core_fp, 16) ^ tape_fp) & 0xFFFFFFFFFFFFFFFF
        return f"{combined:016X}"
    
    def execute_instruction(self) -> bool:
        """Execute a single instruction"""
        if self.halted:
            return False
        
        instruction = self.memory.read(self.program_counter)
        opcode = (instruction >> 24) & 0xFF
        address = instruction & 0xFFFF
        
        self.instructions_executed += 1
        
        if opcode == self.OP_STOP:
            self.halted = True
            return False
        
        elif opcode == self.OP_LOAD:
            self.accumulator = self.memory.read(address)
            self.program_counter += 1
        
        elif opcode == self.OP_STORE:
            self.memory.write(address, self.accumulator)
            self.program_counter += 1
        
        elif opcode == self.OP_ADD:
            self.accumulator = (self.accumulator + self.memory.read(address)) & 0xFFFFFFFF
            self.program_counter += 1
        
        elif opcode == self.OP_SUB:
            self.accumulator = (self.accumulator - self.memory.read(address)) & 0xFFFFFFFF
            self.program_counter += 1
        
        elif opcode == self.OP_MUL:
            self.accumulator = (self.accumulator * self.memory.read(address)) & 0xFFFFFFFF
            self.program_counter += 1
        
        elif opcode == self.OP_DIV:
            divisor = self.memory.read(address)
            if divisor != 0:
                self.accumulator = self.accumulator // divisor
            self.program_counter += 1
        
        elif opcode == self.OP_JUMP:
            self.program_counter = address
        
        elif opcode == self.OP_JPOS:
            if self.accumulator > 0:
                self.program_counter = address
            else:
                self.program_counter += 1
        
        elif opcode == self.OP_JNEG:
            if self.accumulator < 0:
                self.program_counter = address
            else:
                self.program_counter += 1
        
        elif opcode == self.OP_JZER:
            if self.accumulator == 0:
                self.program_counter = address
            else:
                self.program_counter += 1
        
        elif opcode == self.OP_AND:
            self.accumulator = self.accumulator & self.memory.read(address)
            self.program_counter += 1
        
        elif opcode == self.OP_OR:
            self.accumulator = self.accumulator | self.memory.read(address)
            self.program_counter += 1
        
        elif opcode == self.OP_XOR:
            self.accumulator = self.accumulator ^ self.memory.read(address)
            self.program_counter += 1
        
        elif opcode == self.OP_OUTPUT:
            # Output to printer (simulated)
            self.output_buffer.append(f"OUTPUT[{address}]: {self.accumulator:08X}")
            self.program_counter += 1
        
        elif opcode == self.OP_PUNCH:
            # Punch paper tape
            self.punched_tapes.append(f"{self.accumulator:08X}")
            self.program_counter += 1
        
        elif opcode == self.OP_SOUND:
            # Generate audio tone
            self.loudspeaker_active = True
            self.last_sound_frequency = address  # Frequency in Hz
            self.program_counter += 1
        
        elif opcode == self.OP_MASTER:
            # Master Program OS call
            if address == 1:  # CHECK_TIME
                if not self.master_program.check_time():
                    self.accumulator = 0
                else:
                    self.accumulator = 1
            elif address == 2:  # YIELD
                self.master_program.yield_cpu()
            self.program_counter += 1
        
        elif opcode == self.OP_INPUT:
            # Input from paper tape (simulated)
            self.accumulator = random.randint(0, 0xFFFFFFFF)
            self.program_counter += 1
        
        else:
            # Unknown opcode - treat as NOP
            self.program_counter += 1
        
        return True
    
    def run(self, max_instructions: int = 10000):
        """Run the program"""
        count = 0
        while not self.halted and count < max_instructions:
            self.execute_instruction()
            count += 1
            
            # Simulate Master Program scheduling
            if count % 1000 == 0:
                self.master_program.schedule_next()


class RustChainMiner:
    """RustChain Proof-of-Antiquity Miner for LEO III"""
    
    def __init__(self, computer: LEOIII, wallet: str, difficulty: int = 0x01000):
        self.computer = computer
        self.wallet = wallet
        self.difficulty = difficulty
        self.shares_found: List[MiningShare] = []
        self.nonce = 0
        self.attempts = 0
        self.job_number = 0
    
    def initialize(self):
        """Initialize miner with Master Program"""
        self.job_number = self.computer.master_program.register_job(
            name="RustChain Miner",
            priority="Low",
            memory_kb=2
        )
        self.computer.master_program.current_job = self.job_number - 1
        self.computer.master_program.jobs[self.job_number - 1]['time_remaining'] = 1000
    
    def generate_fingerprint(self) -> str:
        """Generate hardware fingerprint"""
        return self.computer.get_fingerprint()
    
    def compute_hash(self, fingerprint: str, nonce: int) -> int:
        """Compute hash (simplified XOR for LEO III)"""
        fp_int = int(fingerprint, 16) & 0xFFFFFFFF
        return (fp_int ^ nonce) & 0xFFFFFFFF
    
    def mine_share(self) -> Optional[MiningShare]:
        """Attempt to mine a share"""
        fingerprint = self.generate_fingerprint()
        
        # Single mining attempt (simulates ~10 instructions per attempt)
        self.nonce += 1
        self.attempts += 1
        self.computer.instructions_executed += 10  # Simulate instruction execution
        
        hash_value = self.compute_hash(fingerprint, self.nonce)
        
        if hash_value < self.difficulty:
            # Share found!
            share = MiningShare(
                timestamp=int(time.time()),
                wallet=self.wallet,
                fingerprint=fingerprint,
                nonce=self.nonce,
                hash_value=hash_value,
                difficulty=self.difficulty,
                job_number=self.job_number
            )
            
            # Generate audio proof
            self.computer.loudspeaker_active = True
            self.computer.last_sound_frequency = 440  # A4 tone
            
            # Output share
            self.computer.output_buffer.append("SHARE FOUND!")
            self.computer.punched_tapes.append(share.to_paper_tape())
            
            self.shares_found.append(share)
            return share
        
        return None
    
    def mine(self, duration_seconds: float = 10.0) -> dict:
        """Run mining for specified duration"""
        start_time = time.time()
        end_time = start_time + duration_seconds
        
        print(f"[MINER] Starting RustChain Mining Session on LEO III")
        print(f"Difficulty: 0x{self.difficulty:06X}")
        print(f"Duration:   {duration_seconds}s")
        print(f"Wallet:     {self.wallet}")
        print(f"Master Program Job: {self.job_number}")
        print("=" * 60)
        
        while time.time() < end_time:
            share = self.mine_share()
            
            if share:
                print(f"\n[LOUDSPEAKER] ~ Tone {self.computer.last_sound_frequency} Hz")
                print("=" * 60)
                print("SHARE FOUND!")
                print("=" * 60)
                print(share)
                print("=" * 60)
            
            # Simulate Master Program time slicing
            self.computer.master_program.schedule_next()
        
        elapsed = time.time() - start_time
        
        print("\n" + "=" * 60)
        print("MINING SESSION COMPLETE")
        print("=" * 60)
        print(f"Duration:     {elapsed:.2f}s")
        print(f"Attempts:     {self.attempts}")
        print(f"Shares Found: {len(self.shares_found)}")
        print(f"Instructions: {self.computer.instructions_executed}")
        print(f"Cycles:       {self.computer.instructions_executed}")
        print(f"Master Program Time Slices: {self.computer.instructions_executed // 1000}")
        print("=" * 60)
        
        return {
            'duration': elapsed,
            'attempts': self.attempts,
            'shares': len(self.shares_found),
            'instructions': self.computer.instructions_executed
        }


def generate_intercode_program() -> str:
    """Generate Intercode assembly program listing"""
    return """
         TITLE   RUSTCHAIN MINER FOR LEO III
         ORG     6000            ; Job 7 memory region
         
; ============================================================
; CONSTANTS
; ============================================================
DIFFICULTY  EQU     01000          ; Mining difficulty
ONE         EQU     1              ; Constant: 1
FINGERPRINT EQU     7000           ; Core memory fingerprint location

; ============================================================
; VARIABLES
; ============================================================
NONCE       DS      1              ; Current nonce (word)
HASH        DS      1              ; Hash result (word)
SHARE_COUNT DS      1              ; Shares found counter

; ============================================================
; MINING ROUTINE
; ============================================================
START:    LOAD    FINGERPRINT    ; A ← core memory fingerprint
          ADD     NONCE          ; A ← A + nonce
          STORE   HASH           ; Store hash result
          
          SUB     DIFFICULTY     ; A ← A - difficulty
          JPOS    CONTINUE       ; If A > 0, no share
          
          ; SHARE FOUND!
          LOAD    SHARE_COUNT
          ADD     ONE
          STORE   SHARE_COUNT
          
          OUTPUT  SHARE_MSG      ; Print "SHARE FOUND"
          SOUND   440            ; Audio proof (A4 tone)
          PUNCH   SHARE_DATA     ; Punch details to tape
          
CONTINUE: LOAD    NONCE
          ADD     ONE
          STORE   NONCE
          
          ; Check Master Program time slice
          MASTER  CHECK_TIME     ; OS call
          JZER    START          ; Continue if time remains
          
          ; Time slice expired, yield to Master Program
          MASTER  YIELD
          JUMP    START
          
; ============================================================
; DATA
; ============================================================
SHARE_MSG:  TXT     'SHARE FOUND - '
SHARE_DATA: DS      10             ; Share data buffer

          END     START
"""


def main():
    parser = argparse.ArgumentParser(
        description='LEO III (1961) Simulator - RustChain Miner',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --demo                    Run mining demonstration
  %(prog)s --mine --duration 60      Mine for 60 seconds
  %(prog)s --program                 Generate Intercode program
  %(prog)s --difficulty 0x01000      Set mining difficulty
        """
    )
    
    parser.add_argument('--demo', action='store_true',
                        help='Run mining demonstration')
    parser.add_argument('--mine', action='store_true',
                        help='Run mining session')
    parser.add_argument('--duration', type=float, default=10.0,
                        help='Mining duration in seconds (default: 10)')
    parser.add_argument('--difficulty', type=str, default='0x01000',
                        help='Mining difficulty in hex (default: 0x01000)')
    parser.add_argument('--program', action='store_true',
                        help='Generate Intercode program listing')
    parser.add_argument('--output', type=str,
                        help='Output file for program')
    parser.add_argument('--wallet', type=str,
                        default='RTC4325af95d26d59c3ef025963656d22af638bb96b',
                        help='RTC wallet address')
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("LEO III Simulator")
    print("RustChain Proof-of-Antiquity Miner")
    print("=" * 60)
    print()
    
    if args.program:
        program = generate_intercode_program()
        if args.output:
            with open(args.output, 'w') as f:
                f.write(program)
            print(f"Intercode program written to {args.output}")
        else:
            print(program)
        return
    
    # Create LEO III computer
    computer = LEOIII(memory_size=8192)
    
    # Create miner
    difficulty = int(args.difficulty, 16)
    miner = RustChainMiner(
        computer=computer,
        wallet=args.wallet,
        difficulty=difficulty
    )
    
    # Initialize
    miner.initialize()
    
    # Run mining
    if args.mine or args.demo:
        miner.mine(duration_seconds=args.duration)


if __name__ == '__main__':
    main()
