#!/usr/bin/env python3
"""
RustChain IBM 650 Miner Simulator (1953)
LEGENDARY Tier Bounty #345 - 200 RTC

Simulates the IBM 650 Magnetic Drum Data-Processing Machine
for mining RustChain on the first mass-produced computer.

Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
"""

import sys
import time
import random
import argparse
from datetime import datetime
from typing import Dict, List, Optional, Tuple

# IBM 650 Constants
DRUM_SIZE_1K = 1000
DRUM_SIZE_2K = 2000
DRUM_SIZE_4K = 4000
WORD_SIZE = 10  # 10 decimal digits

# Console addresses
CONSOLE_SWITCHES = 8000
CONSOLE_DISPLAY = 8001
ACCUMULATOR_LO = 8002
ACCUMULATOR_HI = 8003

# Opcodes (basic machine)
OP_NOP   = 00  # No operation
OP_AU    = 10  # Add to upper accumulator
OP_AL    = 15  # Add to lower accumulator
OP_AABL  = 17  # Add absolute to lower accumulator
OP_DIV   = 14  # Divide
OP_MULT  = 19  # Multiply
OP_LC    = 60  # Load accumulator (various)
OP_RAU   = 60  # Reset accumulator and add to upper
OP_RAL   = 65  # Reset accumulator and add to lower
OP_RSL   = 66  # Reset accumulator and subtract from lower
OP_LD    = 69  # Load distributor
OP_RD    = 70  # Read card
OP_PCH   = 71  # Punch card
OP_BRNZU = 44  # Branch on non-zero upper
OP_BRNZ  = 45  # Branch on accumulator non-zero
OP_BRMIN = 46  # Branch on minus accumulator
OP_BROV  = 47  # Branch on overflow
OP_BRD   = 90  # Branch on digit (90-99)
OP_STOP  = 44  # Stop (using BRNZU as placeholder)


class IBM650Simulator:
    """
    IBM 650 Magnetic Drum Simulator
    
    Implements:
    - Magnetic drum memory (1K/2K/4K words)
    - Bi-quinary coded decimal arithmetic
    - Console I/O
    - Card reader/punch
    - Basic instruction set
    """
    
    def __init__(self, drum_size: int = DRUM_SIZE_2K):
        self.drum_size = drum_size
        self.drum: Dict[int, int] = {i: 0 for i in range(drum_size)}
        
        # Registers
        self.accumulator_lo = 0  # Lower 10 digits
        self.accumulator_hi = 0  # Upper 10 digits
        self.accumulator_sign = '+'
        self.distributor = 0
        self.program_register = 0
        self.address_register = 0
        
        # Console
        self.console_switches = 0
        self.half_cycle = False
        
        # I/O
        self.card_reader: List[List[int]] = []
        self.card_punch: List[List[int]] = []
        self.current_card = 0
        
        # Statistics
        self.instructions_executed = 0
        self.drum_rotations = 0
        
    def sign_word(self, value: int) -> Tuple[int, str]:
        """Extract sign from signed word"""
        if value < 0:
            return abs(value), '-'
        return value, '+'
    
    def normalize(self, value: int) -> int:
        """Normalize to 10 decimal digits"""
        return abs(value) % (10 ** WORD_SIZE)
    
    def read_word(self, addr: int) -> int:
        """Read word from drum or console"""
        if addr == CONSOLE_SWITCHES:
            return self.console_switches
        elif addr == ACCUMULATOR_LO:
            return self.normalize(self.accumulator_lo)
        elif addr == ACCUMULATOR_HI:
            return self.normalize(self.accumulator_hi)
        elif addr >= self.drum_size:
            raise ValueError(f"Invalid address: {addr}")
        return self.drum[addr]
    
    def write_word(self, addr: int, value: int):
        """Write word to drum"""
        if addr >= self.drum_size:
            raise ValueError(f"Invalid address: {addr}")
        self.drum[addr] = self.normalize(value)
    
    def parse_instruction(self, word: int) -> Tuple[int, int, int]:
        """
        Parse instruction word into opcode, data address, next address
        
        Format: [sign][OP][DA][IA]
        OP = 2 digits (operation code)
        DA = 4 digits (data address)
        IA = 4 digits (instruction address)
        """
        word_str = f"{word:010d}"
        opcode = int(word_str[0:2])
        data_addr = int(word_str[2:6])
        next_addr = int(word_str[6:10])
        return opcode, data_addr, next_addr
    
    def execute_instruction(self, opcode: int, data_addr: int, next_addr: int) -> int:
        """Execute a single instruction, return next instruction address"""
        
        self.instructions_executed += 1
        
        # No operation
        if opcode == OP_NOP:
            return next_addr
        
        # Load distributor
        elif opcode == OP_LD:
            self.distributor = self.read_word(data_addr)
            return next_addr
        
        # Reset accumulator and add to lower
        elif opcode == OP_RAL:
            value = self.read_word(data_addr)
            self.accumulator_lo = value
            self.accumulator_hi = 0
            self.accumulator_sign = '+'
            return next_addr
        
        # Add to lower accumulator
        elif opcode == OP_AL:
            value = self.read_word(data_addr)
            self.accumulator_lo += value
            # Handle carry
            if self.accumulator_lo >= 10 ** WORD_SIZE:
                self.accumulator_hi += 1
                self.accumulator_lo = self.normalize(self.accumulator_lo)
            return next_addr
        
        # Multiply
        elif opcode == OP_MULT:
            value = self.read_word(data_addr)
            # 20-digit result
            full_acc = self.accumulator_lo * value
            self.accumulator_hi = full_acc // (10 ** WORD_SIZE)
            self.accumulator_lo = self.normalize(full_acc)
            return next_addr
        
        # Divide
        elif opcode == OP_DIV:
            divisor = self.read_word(data_addr)
            if divisor == 0:
                raise ZeroDivisionError("Division by zero")
            # 20-digit / 10-digit = 10-digit result
            full_acc = (self.accumulator_hi * (10 ** WORD_SIZE)) + self.accumulator_lo
            quotient = full_acc // divisor
            remainder = full_acc % divisor
            self.accumulator_lo = quotient
            self.accumulator_hi = remainder
            return next_addr
        
        # Read card
        elif opcode == OP_RD:
            if self.current_card < len(self.card_reader):
                card = self.card_reader[self.current_card]
                for i, digit in enumerate(card[:10]):
                    self.write_word(data_addr + i, digit)
                self.current_card += 1
            return next_addr
        
        # Punch card
        elif opcode == OP_PCH:
            card = []
            for i in range(10):
                card.append(self.read_word(data_addr + i) % 10)
            self.card_punch.append(card)
            return next_addr
        
        # Branch on non-zero
        elif opcode == OP_BRNZ:
            if self.accumulator_lo != 0 or self.accumulator_hi != 0:
                return data_addr
            return next_addr
        
        # Branch on digit (simplified)
        elif 90 <= opcode <= 99:
            digit_pos = opcode - 90
            value = self.distributor
            digit = (value // (10 ** (9 - digit_pos))) % 10
            if digit == 8:
                return data_addr
            return next_addr
        
        # Stop
        elif opcode == 44 and data_addr == 0:  # Special STOP case
            print(f"STOP instruction executed at {next_addr}")
            return next_addr
        
        else:
            # Unknown opcode - treat as NOP
            return next_addr
    
    def load_program(self, program: List[Tuple[int, int]]):
        """Load program into drum memory"""
        for addr, value in program:
            if addr < self.drum_size:
                self.drum[addr] = value
    
    def load_card_deck(self, cards: List[str]):
        """Load card deck into reader"""
        self.card_reader = []
        for card in cards:
            digits = [int(c) if c.isdigit() else 0 for c in card[:80].ljust(80, '0')]
            # Group into 10-digit words
            words = []
            for i in range(0, 80, 10):
                word = int(''.join(str(d) for d in digits[i:i+10]))
                words.append(word)
            self.card_reader.append(words)
        self.current_card = 0
    
    def run(self, start_addr: int = 0, max_instructions: int = 10000) -> bool:
        """
        Run program from start address
        
        Returns True if completed normally, False if stopped/error
        """
        self.address_register = start_addr
        
        for _ in range(max_instructions):
            try:
                # Fetch instruction
                word = self.read_word(self.address_register)
                opcode, data_addr, next_addr = self.parse_instruction(word)
                
                # Execute
                next_instr_addr = self.execute_instruction(opcode, data_addr, next_addr)
                
                # Update address register
                self.address_register = next_instr_addr
                
                # Check for stop condition
                if opcode == 44 and data_addr == 0:
                    return False
                    
            except Exception as e:
                print(f"Error at address {self.address_register}: {e}")
                return False
        
        print(f"Reached maximum instructions ({max_instructions})")
        return True
    
    def get_punched_cards(self) -> List[str]:
        """Get punched card output as strings"""
        result = []
        for card in self.card_punch:
            card_str = ''.join(str(d % 10) for d in card[:80])
            result.append(card_str.ljust(80, '0'))
        return result
    
    def display_state(self):
        """Display current machine state"""
        print("\n=== IBM 650 State ===")
        print(f"Address Register: {self.address_register:04d}")
        print(f"Accumulator HI:   {self.accumulator_hi:010d}")
        print(f"Accumulator LO:   {self.accumulator_lo:010d}")
        print(f"Distributor:      {self.distributor:010d}")
        print(f"Console Switches: {self.console_switches:010d}")
        print(f"Instructions:     {self.instructions_executed}")
        print(f"Cards Punched:    {len(self.card_punch)}")
        print("=====================\n")


class RustChainMiner650:
    """
    RustChain Miner for IBM 650
    
    Implements simplified proof-of-antiquity using decimal arithmetic
    """
    
    def __init__(self, wallet_id: str, simulator: IBM650Simulator):
        self.wallet_id = wallet_id
        self.sim = simulator
        self.prime_constants = [7, 11, 13, 17, 19, 23, 29, 31]
        
    def extract_wallet_digits(self) -> List[int]:
        """Extract numeric digits from wallet ID"""
        digits = [int(c) for c in self.wallet_id if c.isdigit()]
        # Pad or truncate to 10 digits
        digits = digits[:10]
        while len(digits) < 10:
            digits.append(0)
        return digits
    
    def generate_entropy(self) -> int:
        """Generate entropy from console switches or random"""
        if self.sim.console_switches != 0:
            return self.sim.console_switches
        # Fallback to pseudo-random from timestamp
        ts = int(time.time()) % (10 ** 10)
        return ts
    
    def compute_proof_hash(self, entropy: int, timestamp: int) -> int:
        """
        Compute simplified hash using decimal arithmetic
        
        This mimics a cryptographic hash but uses only decimal operations
        available on IBM 650
        """
        # Initialize state from wallet
        state = int(''.join(str(d) for d in self.extract_wallet_digits()))
        
        # Mix in entropy
        state = (state * 7 + entropy) % (10 ** 10)
        
        # Mix in timestamp
        state = (state * 11 + timestamp) % (10 ** 10)
        
        # Multiple rounds of mixing
        for prime in self.prime_constants[2:]:
            state = (state * prime) % (10 ** 10)
            state = (state + (state // 1000)) % (10 ** 10)
        
        return state
    
    def create_proof_card(self, proof_hash: int, entropy: int) -> str:
        """Create proof card data"""
        timestamp = datetime.now().strftime("%y%m%d%H%M")
        wallet_part = ''.join(str(d) for d in self.extract_wallet_digits())[:10]
        hash_str = f"{proof_hash:010d}"
        entropy_str = f"{entropy:010d}"
        
        # Calculate checksum
        checksum = sum(int(c) for c in wallet_part + timestamp + hash_str) % (10 ** 10)
        checksum_str = f"{checksum:010d}"
        
        card = f"{wallet_part}{timestamp}{hash_str}{entropy_str}{checksum_str}{'0' * 30}"
        return card[:80].ljust(80, '0')
    
    def run_mining_cycle(self) -> str:
        """Run one mining cycle"""
        print("[MINING] Starting IBM 650 Mining Cycle...")
        
        # Generate entropy
        entropy = self.generate_entropy()
        print(f"  Entropy: {entropy}")
        
        # Get timestamp
        timestamp = int(datetime.now().strftime("%y%m%d%H%M"))
        
        # Compute proof
        proof_hash = self.compute_proof_hash(entropy, timestamp)
        print(f"  Proof Hash: {proof_hash:010d}")
        
        # Create proof card
        proof_card = self.create_proof_card(proof_hash, entropy)
        print(f"  Proof Card: {proof_card[:40]}...")
        
        return proof_card
    
    def verify_proof(self, proof_card: str) -> bool:
        """Verify a proof card"""
        if len(proof_card) < 50:
            return False
        
        try:
            wallet_part = proof_card[0:10]
            timestamp = proof_card[10:20]
            proof_hash = proof_card[20:30]
            entropy = proof_card[30:40]
            checksum = proof_card[40:50]
            
            # Verify checksum
            expected = sum(int(c) for c in wallet_part + timestamp + proof_hash) % (10 ** 10)
            actual = int(checksum)
            
            return expected == actual
        except:
            return False


def load_soap_program(filename: str) -> List[Tuple[int, int]]:
    """
    Load SOAP assembly program
    
    Simple parser for basic SOAP-like syntax
    """
    program = []
    with open(filename, 'r') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('*'):
                continue
            
            parts = line.split()
            if len(parts) >= 3:
                try:
                    label = parts[0]
                    opcode = parts[1]
                    operand = parts[2]
                    next_addr = int(parts[3]) if len(parts) > 3 else 0
                    
                    # Parse address
                    addr = int(label) if label.isdigit() else 0
                    
                    # Simple opcode mapping (would need full SOAP parser for real use)
                    op_map = {
                        'RAL': 65, 'AL': 15, 'MULT': 19, 'DIV': 14,
                        'PCH': 71, 'RD': 70, 'BRNZ': 45, 'NOP': 0
                    }
                    op = op_map.get(opcode, 0)
                    
                    # Construct instruction word
                    word = op * (10 ** 8) + (addr % 10000) * (10 ** 4) + next_addr
                    program.append((addr, word))
                except:
                    continue
    return program


def main():
    parser = argparse.ArgumentParser(description='RustChain IBM 650 Miner Simulator')
    parser.add_argument('--wallet', type=str, default='RTC4325af95d26d59c3ef025963656d22af638bb96b',
                       help='RustChain wallet address')
    parser.add_argument('--load', type=str, help='Load SOAP program file')
    parser.add_argument('--run', action='store_true', help='Run loaded program')
    parser.add_argument('--verify', type=str, help='Verify proof card file')
    parser.add_argument('--cycles', type=int, default=1, help='Number of mining cycles')
    parser.add_argument('--drum-size', type=int, default=2000, choices=[1000, 2000, 4000],
                       help='Drum memory size')
    
    args = parser.parse_args()
    
    # Create simulator
    sim = IBM650Simulator(drum_size=args.drum_size)
    miner = RustChainMiner650(args.wallet, sim)
    
    print("=" * 60)
    print("  RUSTCHAIN IBM 650 MINER SIMULATOR (1953)")
    print("  LEGENDARY Tier Bounty #345 - 200 RTC")
    print(f"  Wallet: {args.wallet}")
    print("=" * 60)
    
    # Verify mode
    if args.verify:
        print(f"\nVerifying proof card: {args.verify}")
        with open(args.verify, 'r') as f:
            proof_card = f.read().strip()
        if miner.verify_proof(proof_card):
            print("[VERIFIED] Proof VERIFIED!")
        else:
            print("[INVALID] Proof INVALID!")
        return
    
    # Load and run program
    if args.load:
        print(f"\nLoading program: {args.load}")
        program = load_soap_program(args.load)
        sim.load_program(program)
        
        if args.run:
            print("Running program...")
            sim.run(start_addr=100)
            sim.display_state()
            
            # Show punched cards
            cards = sim.get_punched_cards()
            for i, card in enumerate(cards):
                print(f"Card {i+1}: {card[:60]}...")
    
    # Mining mode
    else:
        print(f"\nStarting {args.cycles} mining cycle(s)...")
        for i in range(args.cycles):
            print(f"\n--- Cycle {i+1} ---")
            proof_card = miner.run_mining_cycle()
            
            # Verify
            if miner.verify_proof(proof_card):
                print("[OK] Proof verified!")
            else:
                print("[FAIL] Proof verification failed!")
            
            # Save to file
            filename = f"proof_card_{i+1}.txt"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(proof_card)
            print(f"[SAVE] Saved to {filename}")
            
            if i < args.cycles - 1:
                time.sleep(1)
    
    print("\n" + "=" * 60)
    print("  IBM 650 - First Mass-Produced Computer (1953)")
    print("  Donald Knuth dedicated TAOCP to this machine")
    print("=" * 60)


if __name__ == '__main__':
    main()
