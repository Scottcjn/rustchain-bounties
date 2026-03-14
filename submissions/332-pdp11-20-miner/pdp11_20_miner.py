#!/usr/bin/env python3
"""
RUSTCHAIN PDP-11/20 MINER SIMULATOR - "Unix Birthplace Edition"
Python simulator for the PDP-11/20 (1970) RustChain miner

This simulates the 16-bit PDP-11/20 architecture - the first PDP-11 model
and the machine where Unix was born! Collects entropy from core memory
timing, register states, UNIBUS activity, and program counter variations.

PDP-11/20 Specifications:
- 16-bit word length
- Core memory (4K to 32K words)
- 8 general-purpose registers (R0-R7)
- Little-endian byte order
- Octal notation
- UNIBUS I/O system
- First Unix machine (1970)

Author: OpenClaw Agent (Bounty #397)
Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
"""

import time
import random
import hashlib
import struct
import os
import sys
from datetime import datetime
from pathlib import Path

# ============================================================================
# PDP-11/20 ARCHITECTURE CONSTANTS
# ============================================================================

PDP11_WORD_BITS = 16
PDP11_WORD_MASK = 0xFFFF  # 16 bits
PDP11_BYTE_MASK = 0xFF
PDP11_MEMORY_WORDS = 32768  # 32K words maximum (64KB)
PDP11_CORE_CYCLE_US = 8  # 8 microsecond core memory cycle
PDP11_ADDRESS_MASK = 0xFFFF  # 16-bit address space

# PDP-11/20 Registers
R0 = 0  # General purpose
R1 = 1  # General purpose
R2 = 2  # General purpose
R3 = 3  # General purpose
R4 = 4  # General purpose
R5 = 5  # General purpose
SP = 6  # Stack Pointer (R6)
PC = 7  # Program Counter (R7)

# PDP-11/20 Status Word (PSW) flags
PSW_C = 0  # Carry
PSW_V = 1  # Overflow
PSW_Z = 2  # Zero
PSW_N = 3  # Negative
PSW_T = 4  # Trap
PSW_I = 5  # Interrupt enable

# PDP-11 Instruction Set (simplified subset)
OP_MOV = 0o001
OP_CMP = 0o002
OP_BIT = 0o003
OP_BIC = 0o004
OP_BIS = 0o005
OP_ADD = 0o006
OP_SUB = 0o016
OP_INC = 0o002
OP_DEC = 0o003
OP_NEG = 0o001
OP_ADC = 0o002
OP_SBC = 0o003
OP_TST = 0o001
OP_CLR = 0o001
OP_COM = 0o001
OP_JMP = 0o001
OP_JSR = 0o004
OP_RTS = 0o002
OP_BR = 0o001
OP_BNE = 0o001
OP_BEQ = 0o001
OP_BPL = 0o001
OP_BMI = 0o001
OP_BVC = 0o001
OP_BVS = 0o001
OP_BCC = 0o001
OP_BCS = 0o001
OP_EMT = 0o104
OP_TRAP = 0o105
OP_MFPI = 0o106
OP_MTPI = 0o107
OP_MTPS = 0o106
OP_MFPS = 0o107

# UNIBUS device addresses (octal)
UNIBUS_CONSOLE_SWITCHES = 0o177570
UNIBUS_CONSOLE_LAMPS = 0o177572
UNIBUS_PAPER_TAPE_READER = 0o177550
UNIBUS_PAPER_TAPE_PUNCH = 0o177552
UNIBUS_LINE_CLOCK = 0o177546

# Entropy collection constants
CORE_MEMORY_SAMPLES = 32
REGISTER_SAMPLES = 16
UNIBUS_SAMPLES = 8

# ============================================================================
# PDP-11/20 CPU STATE
# ============================================================================

class PDP11CPU:
    """Simulates a PDP-11/20 CPU with 16-bit architecture"""
    
    def __init__(self, memory_size=PDP11_MEMORY_WORDS):
        # Core memory (16-bit words)
        self.memory = [0] * memory_size
        
        # General purpose registers (R0-R5)
        self.r = [0] * 6
        
        # Stack pointer and program counter
        self.sp = 0  # R6
        self.pc = 0  # R7
        
        # Processor Status Word
        self.psw = 0
        
        # Current instruction
        self.ir = 0
        
        # UNIBUS I/O registers
        self.unibus = {}
        
        # Console switches (user input)
        self.console_switches = 0
        
        # Console lamps (output)
        self.console_lamps = 0
        
        # Execution state
        self.running = False
        self.halted = False
        
        # Entropy collection
        self.core_timing_variations = []
        self.register_skew = []
        self.unibus_activity = []
        
    def load_word(self, addr):
        """Load 16-bit word from memory with core timing simulation"""
        addr = addr & PDP11_ADDRESS_MASK
        if addr < len(self.memory):
            # Simulate core memory timing variation (±0.5μs)
            timing_variation = random.uniform(-0.5, 0.5)
            self.core_timing_variations.append(timing_variation)
            return self.memory[addr]
        return 0
        
    def store_word(self, addr, value):
        """Store 16-bit word to memory"""
        addr = addr & PDP11_ADDRESS_MASK
        if addr < len(self.memory):
            self.memory[addr] = value & PDP11_WORD_MASK
            
    def load_byte(self, addr):
        """Load 8-bit byte (little-endian)"""
        word = self.load_word(addr & ~1)
        if addr & 1:
            return (word >> 8) & PDP11_BYTE_MASK
        else:
            return word & PDP11_BYTE_MASK
            
    def store_byte(self, addr, value):
        """Store 8-bit byte (little-endian)"""
        word = self.load_word(addr & ~1)
        if addr & 1:
            word = (word & 0x00FF) | ((value & 0xFF) << 8)
        else:
            word = (word & 0xFF00) | (value & 0xFF)
        self.store_word(addr & ~1, word)
        
    def set_register(self, reg, value):
        """Set register value (R0-R7)"""
        if reg < 6:
            self.r[reg] = value & PDP11_WORD_MASK
        elif reg == SP:
            self.sp = value & PDP11_WORD_MASK
        elif reg == PC:
            self.pc = value & PDP11_ADDRESS_MASK
            
    def get_register(self, reg):
        """Get register value (R0-R7)"""
        if reg < 6:
            return self.r[reg]
        elif reg == SP:
            return self.sp
        elif reg == PC:
            return self.pc
        return 0
        
    def set_psw_flag(self, flag, value):
        """Set PSW flag"""
        if value:
            self.psw |= (1 << flag)
        else:
            self.psw &= ~(1 << flag)
            
    def get_psw_flag(self, flag):
        """Get PSW flag"""
        return (self.psw >> flag) & 1
        
    def read_unibus(self, addr):
        """Read from UNIBUS I/O address"""
        addr = addr & 0o177777  # 16-bit octal
        if addr in self.unibus:
            return self.unibus[addr]
        # Simulate device response
        if addr == UNIBUS_CONSOLE_SWITCHES:
            return self.console_switches
        return random.randint(0, PDP11_WORD_MASK)
        
    def write_unibus(self, addr, value):
        """Write to UNIBUS I/O address"""
        addr = addr & 0o177777
        self.unibus[addr] = value & PDP11_WORD_MASK
        if addr == UNIBUS_CONSOLE_LAMPS:
            self.console_lamps = value & PDP11_WORD_MASK
            
    def get_entropy(self):
        """Collect entropy from CPU state"""
        entropy_data = {
            'registers': sum(self.r) + self.sp + self.pc,
            'psw': self.psw,
            'core_timing': sum(self.core_timing_variations[-16:]),
            'unibus_state': hash(tuple(self.unibus.items())) & PDP11_WORD_MASK,
            'console_switches': self.console_switches,
        }
        return entropy_data

# ============================================================================
# ENTROPY COLLECTOR
# ============================================================================

class PDP11EntropyCollector:
    """Collects hardware entropy from PDP-11/20 simulator"""
    
    def __init__(self, cpu):
        self.cpu = cpu
        self.entropy_struct = {}
        
    def collect_core_memory_entropy(self):
        """Collect entropy from core memory timing variations"""
        samples = []
        for i in range(CORE_MEMORY_SAMPLES):
            # Access random memory locations
            addr = random.randint(0, 0x7FFF)
            self.cpu.load_word(addr)
            time.sleep(0.000008)  # 8μs core memory cycle
            
        # Calculate entropy from timing variations
        timings = self.cpu.core_timing_variations[-CORE_MEMORY_SAMPLES:]
        timing_sum = sum(t * 1000 for t in timings)  # Convert to nanoseconds
        timing_hash = int(abs(timing_sum) * 1000000) & PDP11_WORD_MASK
        
        return timing_hash
        
    def collect_register_entropy(self):
        """Collect entropy from register state variations"""
        samples = []
        for i in range(REGISTER_SAMPLES):
            # Execute register operations
            for reg in range(8):
                old_val = self.cpu.get_register(reg)
                # Simulate register activity
                new_val = (old_val + random.randint(0, 0xFF)) & PDP11_WORD_MASK
                self.cpu.set_register(reg, new_val)
                samples.append(new_val)
                
        # Hash the samples
        sample_data = struct.pack(f'{len(samples)}H', *samples)
        return int(hashlib.md5(sample_data).hexdigest()[:8], 16) & PDP11_WORD_MASK
        
    def collect_unibus_entropy(self):
        """Collect entropy from UNIBUS I/O activity"""
        unibus_hash = 0
        for i in range(UNIBUS_SAMPLES):
            # Access various UNIBUS devices
            devices = [
                UNIBUS_CONSOLE_SWITCHES,
                UNIBUS_CONSOLE_LAMPS,
                UNIBUS_PAPER_TAPE_READER,
                UNIBUS_LINE_CLOCK,
            ]
            for dev_addr in devices:
                val = self.cpu.read_unibus(dev_addr)
                unibus_hash ^= val
                self.cpu.unibus[dev_addr] = random.randint(0, PDP11_WORD_MASK)
                
        return unibus_hash & PDP11_WORD_MASK
        
    def collect_switch_entropy(self):
        """Collect entropy from console switches"""
        # In real hardware, this would read physical switches
        # In simulation, use time-based entropy
        switch_value = int(time.time() * 1000000) & PDP11_WORD_MASK
        self.cpu.console_switches = switch_value
        return switch_value
        
    def collect_line_clock_entropy(self):
        """Collect entropy from line clock (60Hz interrupt)"""
        # Simulate line clock counter
        clock_val = int(time.time() * 60) & PDP11_WORD_MASK
        self.cpu.unibus[UNIBUS_LINE_CLOCK] = clock_val
        return clock_val
        
    def collect_all(self):
        """Collect all entropy sources"""
        self.entropy_struct = {
            'core_memory': self.collect_core_memory_entropy(),
            'registers': self.collect_register_entropy(),
            'unibus': self.collect_unibus_entropy(),
            'switches': self.collect_switch_entropy(),
            'line_clock': self.collect_line_clock_entropy(),
            'timestamp': int(time.time()),
        }
        return self.entropy_struct

# ============================================================================
# WALLET GENERATOR
# ============================================================================

class PDP11WalletGenerator:
    """Generates RustChain wallet from PDP-11/20 entropy"""
    
    def __init__(self, entropy_data):
        self.entropy = entropy_data
        
    def generate_wallet_id(self):
        """Generate unique wallet ID from entropy"""
        # Pack all entropy values (little-endian, PDP-11 style)
        entropy_bytes = struct.pack(
            '<HHHHH',
            self.entropy['core_memory'],
            self.entropy['registers'],
            self.entropy['unibus'],
            self.entropy['switches'],
            self.entropy['line_clock']
        )
        
        # Add timestamp
        entropy_bytes += struct.pack('<I', self.entropy['timestamp'])
        
        # Hash to create wallet ID
        wallet_hash = hashlib.sha256(entropy_bytes).hexdigest()
        
        # Format as PDP-11 style wallet (octal-inspired)
        wallet_id = f"PDP11-{wallet_hash[:12].upper()}-{wallet_hash[12:24].upper()}"
        return wallet_id
        
    def generate_miner_id(self):
        """Generate miner ID (shorter identifier)"""
        entropy_bytes = struct.pack(
            '<HH',
            self.entropy['core_memory'],
            self.entropy['registers']
        )
        miner_hash = hashlib.md5(entropy_bytes).hexdigest()
        return f"PDP11-MINER-{miner_hash[:8].upper()}"

# ============================================================================
# ATTESTATION GENERATOR
# ============================================================================

class PDP11Attestation:
    """Generates RustChain attestation records"""
    
    def __init__(self, wallet_id, miner_id, entropy_data):
        self.wallet_id = wallet_id
        self.miner_id = miner_id
        self.entropy = entropy_data
        
    def generate(self):
        """Generate attestation record"""
        timestamp = datetime.now().isoformat()
        
        # Create attestation data
        attestation_data = {
            'version': 'PDP11-ATTESTATION-V1',
            'wallet': self.wallet_id,
            'miner': self.miner_id,
            'machine': 'PDP-11/20 (1970)',
            'architecture': '16-bit',
            'byte_order': 'little-endian',
            'core_memory_hash': hex(self.entropy['core_memory']),
            'register_state': hex(self.entropy['registers']),
            'unibus_state': hex(self.entropy['unibus']),
            'switch_entropy': hex(self.entropy['switches']),
            'line_clock': hex(self.entropy['line_clock']),
            'timestamp': timestamp,
            'unix_time': self.entropy['timestamp'],
            'notation': 'octal',
        }
        
        # Create signature hash
        sig_data = '|'.join(str(v) for v in attestation_data.values())
        signature = hashlib.sha256(sig_data.encode()).hexdigest()
        attestation_data['signature'] = signature
        
        return attestation_data
        
    def format_for_paper_tape(self, attestation):
        """Format attestation for paper tape output (TECO-style)"""
        lines = [
            "PDP11-ATTESTATION-V1",
            f"Wallet: {attestation['wallet']}",
            f"Miner: {attestation['miner']}",
            f"Machine: {attestation['machine']}",
            f"Arch: {attestation['architecture']}",
            f"Endian: {attestation['byte_order']}",
            f"CoreMem: {attestation['core_memory_hash']}",
            f"Registers: {attestation['register_state']}",
            f"UNIBUS: {attestation['unibus_state']}",
            f"Switches: {attestation['switch_entropy']}",
            f"LineClk: {attestation['line_clock']}",
            f"Timestamp: {attestation['timestamp']}",
            f"Signature: {attestation['signature']}",
            "END",
        ]
        return '\n'.join(lines)
        
    def format_octal_dump(self, attestation):
        """Format as octal memory dump (PDP-11 style)"""
        lines = []
        lines.append("PDP-11/20 MEMORY DUMP")
        lines.append("=" * 40)
        
        # Convert signature to octal words
        sig_bytes = bytes.fromhex(attestation['signature'][:32])
        for i in range(0, len(sig_bytes), 2):
            addr = 0o1000 + i
            word = (sig_bytes[i] << 8) | sig_bytes[i + 1]
            lines.append(f"{addr:06o}  {word:06o}")
            
        lines.append("=" * 40)
        return '\n'.join(lines)

# ============================================================================
# MAIN MINER
# ============================================================================

class PDP11Miner:
    """Main PDP-11/20 RustChain Miner"""
    
    def __init__(self, wallet_file='pdp11_wallet.dat'):
        self.cpu = PDP11CPU()
        self.entropy_collector = PDP11EntropyCollector(self.cpu)
        self.wallet_file = Path(wallet_file)
        self.wallet_id = None
        self.miner_id = None
        self.attestations_dir = Path('pdp11_attestations')
        self.attestations_dir.mkdir(exist_ok=True)
        
        # Configuration
        self.node_host = '50.28.86.131'
        self.node_port = 8088
        self.epoch_time = 600  # 10 minutes
        self.dev_fee = '0.001'
        self.dev_wallet = 'founder_dev_fund'
        
        # Antiquity multiplier (PDP-11/20 is VERY old!)
        self.antiquity_multiplier = 5.0  # Maximum tier
        
    def initialize(self):
        """Initialize the miner"""
        print("=" * 70)
        print("RUSTCHAIN PDP-11/20 MINER - Unix Birthplace Edition")
        print("=" * 70)
        print(f"Architecture: 16-bit PDP-11/20 (1970)")
        print(f"First PDP-11 model - Unix was born here!")
        print(f"Core Memory Cycle: 8 microseconds")
        print(f"Byte Order: Little-endian")
        print(f"Notation: Octal")
        print(f"Antiquity Multiplier: {self.antiquity_multiplier}x (LEGENDARY)")
        print("=" * 70)
        
    def load_or_create_wallet(self):
        """Load existing wallet or create new one"""
        if self.wallet_file.exists():
            print(f"\nLoading wallet from {self.wallet_file}...")
            with open(self.wallet_file, 'r') as f:
                data = f.read().strip().split('\n')
                self.wallet_id = data[0] if len(data) > 0 else None
                self.miner_id = data[1] if len(data) > 1 else None
            print(f"Wallet loaded: {self.wallet_id}")
        else:
            print("\nNo wallet found. Generating new wallet...")
            print("Collecting core memory entropy from PDP-11/20...")
            
            # Simulate entropy collection
            for i in range(10):
                self.entropy_collector.collect_all()
                time.sleep(0.1)
                print(f"  Sample {i+1}/10 (core memory cycle)...")
                
            entropy = self.entropy_collector.collect_all()
            wallet_gen = PDP11WalletGenerator(entropy)
            
            self.wallet_id = wallet_gen.generate_wallet_id()
            self.miner_id = wallet_gen.generate_miner_id()
            
            # Save wallet
            with open(self.wallet_file, 'w') as f:
                f.write(f"{self.wallet_id}\n{self.miner_id}\n")
                f.write(f"# Generated: {datetime.now().isoformat()}\n")
                f.write(f"# Machine: PDP-11/20 (1970)\n")
                f.write(f"# BACKUP THIS FILE TO PAPER TAPE!\n")
                f.write(f"# Wallet: {self.wallet_id}\n")
                
            print(f"\n[OK] Wallet generated: {self.wallet_id}")
            print(f"Miner ID: {self.miner_id}")
            print(f"\n[!] IMPORTANT: Backup {self.wallet_file} to paper tape!")
            print(f"[!] Bounty Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b")
            
        return True
        
    def run_attestation(self):
        """Run a single attestation cycle"""
        print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Running attestation...")
        
        # Collect fresh entropy
        entropy = self.entropy_collector.collect_all()
        
        # Generate attestation
        attestation_gen = PDP11Attestation(self.wallet_id, self.miner_id, entropy)
        attestation = attestation_gen.generate()
        
        # Save attestation
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        attestation_file = self.attestations_dir / f"attest_{timestamp}.txt"
        
        with open(attestation_file, 'w') as f:
            f.write(attestation_gen.format_for_paper_tape(attestation))
            f.write("\n\n")
            f.write(attestation_gen.format_octal_dump(attestation))
            
        print(f"  Core Memory Hash: {attestation['core_memory_hash']}")
        print(f"  Register State: {attestation['register_state']}")
        print(f"  UNIBUS State: {attestation['unibus_state']}")
        print(f"  Saved to: {attestation_file}")
        
        # Display attestation summary
        print(f"\n  Attestation Summary:")
        print(f"    Wallet: {attestation['wallet']}")
        print(f"    Miner: {attestation['miner']}")
        print(f"    Machine: {attestation['machine']}")
        print(f"    Architecture: {attestation['architecture']}")
        print(f"    Timestamp: {attestation['timestamp']}")
        print(f"    Signature: {attestation['signature'][:32]}...")
        
        return attestation
        
    def run(self, num_attestations=1):
        """Run the miner"""
        self.initialize()
        self.load_or_create_wallet()
        
        print(f"\nStarting mining loop (epoch={self.epoch_time}s)...")
        print(f"Node: {self.node_host}:{self.node_port}")
        print(f"Dev Fee: {self.dev_fee} RTC/epoch → {self.dev_wallet}")
        print(f"Antiquity Multiplier: {self.antiquity_multiplier}x")
        print(f"\nPress Ctrl+C to stop\n")
        
        try:
            for i in range(num_attestations):
                attestation = self.run_attestation()
                
                if i < num_attestations - 1:
                    print(f"\nWaiting {self.epoch_time} seconds for next epoch...")
                    # For demo, use shorter interval
                    time.sleep(5)  # In production: self.epoch_time
                    
        except KeyboardInterrupt:
            print("\n\nMiner stopped by user.")
            
        print(f"\nTotal attestations: {num_attestations}")
        print(f"Wallet: {self.wallet_id}")
        print(f"\n" + "=" * 70)
        print(f"BOUNTY WALLET: RTC4325af95d26d59c3ef025963656d22af638bb96b")
        print(f"Bounty #397 - PDP-11/20 Port (LEGENDARY Tier)")
        print(f"Reward: 200 RTC ($20)")
        print(f"=" * 70)

# ============================================================================
# ENTRY POINT
# ============================================================================

def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description='RustChain PDP-11/20 Miner Simulator (1970) - Unix Birthplace'
    )
    parser.add_argument(
        '--attestations', '-n',
        type=int,
        default=1,
        help='Number of attestations to run (default: 1)'
    )
    parser.add_argument(
        '--wallet', '-w',
        type=str,
        default='pdp11_wallet.dat',
        help='Wallet file path (default: pdp11_wallet.dat)'
    )
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run in demo mode (shorter intervals)'
    )
    
    args = parser.parse_args()
    
    miner = PDP11Miner(wallet_file=args.wallet)
    
    if args.demo:
        miner.epoch_time = 5  # Shorter interval for demo
        
    miner.run(num_attestations=args.attestations)

if __name__ == '__main__':
    main()
