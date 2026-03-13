#!/usr/bin/env python3
"""
Harvard Mark II Miner Simulator

A Python simulator for the Harvard Mark II (ASCC) electromechanical relay computer,
demonstrating the RustChain Proof-of-Antiquity protocol conceptually.

This simulator models:
- Decimal (BCD) arithmetic
- Relay switching delays
- Paper tape I/O
- Mining state machine

Author: RustChain Bounty Hunter
Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
"""

import time
import sys
from enum import Enum
from typing import List, Optional
from dataclasses import dataclass

# ============================================================================
# CONSTANTS
# ============================================================================

RELAY_SWITCH_TIME_MS = 10  # Typical relay switching time
ADD_TIME_SECONDS = 0.3     # Harvard Mark II addition time
PRINT_TIME_PER_CHAR = 0.5  # Time to punch one character

WALLET_ADDRESS = "RTC4325af95d26d59c3ef025963656d22af638bb96b"
ANTIQUITY_MULTIPLIER = 2.5  # Museum tier (pre-1980)

# ============================================================================
# ENUMS
# ============================================================================

class MinerState(Enum):
    """Mining state machine states"""
    INITIAL = 0
    IDLE = 1
    MINING = 2
    ATTESTING = 3

class OpCode(Enum):
    """Paper tape instruction opcodes"""
    LOAD = 'L'
    STORE = 'S'
    ADD = 'A'
    MULTIPLY = 'M'
    DIVIDE = 'D'
    COMPARE = 'C'
    JUMP = 'J'
    JUMP_IF_ZERO = 'Z'
    PRINT = 'P'
    HALT = 'H'

# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class RelayBank:
    """Simulates a bank of relays storing a decimal value"""
    name: str
    num_digits: int = 23
    value: int = 0
    
    def load(self, value: int):
        """Load a value into the relay bank"""
        self.value = value
        self._simulate_relay_switches()
    
    def _simulate_relay_switches(self):
        """Simulate relay switching delay"""
        num_relays = self.num_digits * 4  # 4 relays per BCD digit
        time.sleep(num_relays * RELAY_SWITCH_TIME_MS / 1000)
    
    def __str__(self):
        return f"{self.name}: {self.value}"

@dataclass
class PaperTape:
    """Simulates paper tape I/O"""
    data: List[str]
    position: int = 0
    
    def read_char(self) -> Optional[str]:
        """Read next character from tape"""
        if self.position < len(self.data):
            char = self.data[self.position]
            self.position += 1
            time.sleep(0.1)  # Read delay
            return char
        return None
    
    def write_char(self, char: str):
        """Write character to output tape"""
        self.data.append(char)
        time.sleep(PRINT_TIME_PER_CHAR)  # Punch delay
    
    def reset(self):
        """Reset tape to beginning"""
        self.position = 0

# ============================================================================
# SIMULATOR
# ============================================================================

class HarvardMarkIIMiner:
    """
    Harvard Mark II Miner Simulator
    
    Simulates the conceptual operation of a RustChain miner on the
    Harvard Mark II electromechanical relay computer from 1947.
    """
    
    def __init__(self):
        # Initialize relay banks
        self.accumulator = RelayBank("ACCUMULATOR")
        self.epoch_counter = RelayBank("EPOCH_COUNTER", num_digits=10)
        self.state_register = RelayBank("STATE_REGISTER", num_digits=1)
        self.temp_register = RelayBank("TEMP_REGISTER")
        
        # Paper tape I/O
        self.input_tape = PaperTape(data=[])
        self.output_tape = PaperTape(data=[])
        
        # State machine
        self.state = MinerState.INITIAL
        self.running = False
        
        # Statistics
        self.operations_count = 0
        self.total_time = 0.0
    
    def initialize(self):
        """Initialize the miner (power-on sequence)"""
        print("=" * 60)
        print("HARVARD MARK II MINER - INITIALIZING")
        print("=" * 60)
        print(f"Epoch Counter: {self.epoch_counter.value}")
        print(f"State: {self.state.name}")
        print(f"Wallet: {WALLET_ADDRESS}")
        print(f"Antiquity Multiplier: {ANTIQUITY_MULTIPLIER}x (MUSEUM TIER)")
        print("=" * 60)
        
        self.state = MinerState.IDLE
        self._print_status("INITIALIZED")
    
    def _print_status(self, message: str):
        """Print status message to output tape"""
        start_time = time.time()
        for char in message:
            self.output_tape.write_char(char)
        self.output_tape.write_char('\n')
        elapsed = time.time() - start_time
        self.total_time += elapsed
        print(f"[OUTPUT] {message} ({elapsed:.2f}s)")
    
    def _decimal_add(self, a: int, b: int) -> int:
        """Perform decimal addition with simulated delay"""
        start_time = time.time()
        time.sleep(ADD_TIME_SECONDS)  # Simulate relay addition time
        result = a + b
        self.operations_count += 1
        elapsed = time.time() - start_time
        self.total_time += elapsed
        print(f"[ADD] {a} + {b} = {result} ({elapsed:.2f}s)")
        return result
    
    def _compare(self, a: int, b: int) -> int:
        """Compare two values"""
        if a < b:
            return -1
        elif a > b:
            return 1
        else:
            return 0
    
    def run_mining_cycle(self, epoch_number: int):
        """Run one complete mining cycle"""
        print("\n" + "=" * 60)
        print(f"MINING CYCLE - EPOCH {epoch_number}")
        print("=" * 60)
        
        # State: IDLE → MINING
        self.state = MinerState.MINING
        self.state_register.load(self.state.value)
        self._print_status(f"STATE: MINING")
        
        # Simulate "mining" (increment epoch)
        self.epoch_counter.load(epoch_number)
        new_epoch = self._decimal_add(self.epoch_counter.value, 1)
        self.epoch_counter.load(new_epoch)
        
        # State: MINING → ATTESTING
        self.state = MinerState.ATTESTING
        self.state_register.load(self.state.value)
        self._print_status(f"STATE: ATTESTING")
        
        # Generate attestation
        self._generate_attestation(new_epoch)
        
        # State: ATTESTING → IDLE
        self.state = MinerState.IDLE
        self.state_register.load(self.state.value)
        self._print_status(f"STATE: IDLE")
        self._print_status(f"CYCLE COMPLETE")
    
    def _generate_attestation(self, epoch: int):
        """Generate attestation output"""
        print("\n--- ATTESTATION ---")
        self._print_status("=" * 40)
        self._print_status("RUSTCHAIN PROOF-OF-ANTIQUITY")
        self._print_status("=" * 40)
        self._print_status(f"EPOCH: {epoch}")
        self._print_status(f"WALLET: {WALLET_ADDRESS}")
        self._print_status(f"HARDWARE: HARVARD MARK II (1947)")
        self._print_status(f"ANTIQUITY: MUSEUM TIER")
        self._print_status(f"MULTIPLIER: {ANTIQUITY_MULTIPLIER}x")
        self._print_status(f"STATUS: ATTESTED")
        self._print_status("=" * 40)
    
    def run(self, num_epochs: int = 3):
        """Run the miner for specified number of epochs"""
        self.initialize()
        
        print("\nStarting mining operation...")
        print(f"Number of epochs: {num_epochs}")
        print("(Note: Time is accelerated - real Mark II would be much slower)")
        print()
        
        start_epoch = self.epoch_counter.value
        
        for i in range(num_epochs):
            epoch = start_epoch + i + 1
            self.run_mining_cycle(epoch)
            print()
        
        # Print final statistics
        self._print_statistics()
    
    def _print_statistics(self):
        """Print mining statistics"""
        print("\n" + "=" * 60)
        print("MINING STATISTICS")
        print("=" * 60)
        print(f"Total Operations: {self.operations_count}")
        print(f"Total Simulation Time: {self.total_time:.2f}s")
        print(f"Average Operation Time: {self.total_time/self.operations_count:.3f}s")
        print(f"Final Epoch: {self.epoch_counter.value}")
        print(f"Final State: {self.state.name}")
        print()
        print("OUTPUT TAPE CONTENTS:")
        print("-" * 60)
        print(''.join(self.output_tape.data))
        print("-" * 60)
        print("=" * 60)
        print("MINING COMPLETE")
        print("=" * 60)

# ============================================================================
# PAPER TAPE ENCODER/DECODER
# ============================================================================

class PaperTapeEncoder:
    """Encode data to 8-channel paper tape format"""
    
    @staticmethod
    def encode_char(char: str) -> int:
        """Encode a character to 8-channel paper tape code"""
        ascii_val = ord(char)
        # 7 data bits + 1 sprocket bit
        return ascii_val | 0x80  # Set sprocket bit (channel 8)
    
    @staticmethod
    def encode_string(text: str) -> List[int]:
        """Encode a string to paper tape format"""
        return [PaperTapeEncoder.encode_char(c) for c in text]
    
    @staticmethod
    def decode_char(code: int) -> str:
        """Decode a paper tape code to character"""
        # Mask off sprocket bit
        ascii_val = code & 0x7F
        return chr(ascii_val)
    
    @staticmethod
    def decode_tape(codes: List[int]) -> str:
        """Decode paper tape codes to string"""
        return ''.join([PaperTapeEncoder.decode_char(c) for c in codes])

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Main entry point"""
    print("\n" + "=" * 60)
    print("HARVARD MARK II MINER SIMULATOR")
    print("RustChain Proof-of-Antiquity")
    print("=" * 60)
    print()
    print("Hardware: Harvard Mark II (ASCC), 1947")
    print("Technology: Electromechanical Relays (~3,300)")
    print("Arithmetic: Decimal (BCD)")
    print("Input/Output: 8-channel Paper Tape")
    print()
    
    # Create and run miner
    miner = HarvardMarkIIMiner()
    
    # Parse command line arguments
    num_epochs = 3
    if len(sys.argv) > 1:
        try:
            num_epochs = int(sys.argv[1])
        except ValueError:
            print(f"Usage: {sys.argv[0]} [num_epochs]")
            print(f"  num_epochs: Number of mining epochs (default: 3)")
            sys.exit(1)
    
    # Run simulation
    miner.run(num_epochs)
    
    # Demonstrate paper tape encoding
    print("\n" + "=" * 60)
    print("PAPER TAPE ENCODING DEMO")
    print("=" * 60)
    
    test_text = f"EPOCH:123 WALLET:{WALLET_ADDRESS[:10]}..."
    encoded = PaperTapeEncoder.encode_string(test_text)
    decoded = PaperTapeEncoder.decode_tape(encoded)
    
    print(f"Original: {test_text}")
    print(f"Encoded:  {encoded[:20]}... ({len(encoded)} codes)")
    print(f"Decoded:  {decoded}")
    print(f"Match:    {test_text == decoded}")
    
    print("\n" + "=" * 60)
    print("SIMULATION COMPLETE")
    print("=" * 60)
    print(f"\nBounty Wallet: {WALLET_ADDRESS}")
    print("Issue: #393 - LEGENDARY Tier (200 RTC)")
    print()

if __name__ == "__main__":
    main()
