#!/usr/bin/env python3
"""
PDP-1 Magnetic-Core Memory Model

Ferrite core memory was revolutionary for its time:
- Non-volatile (retains data when power off)
- Random access
- Reliable (MTBF in years)
- 5 microsecond access time

Each core stores one bit via magnetic polarity.
The PDP-1 used 18 planes of 4,096 cores each.
"""

import time


class CoreMemoryPlane:
    """Single plane of magnetic cores (one bit per word)"""
    
    def __init__(self, size=4096):
        self.size = size
        self.cores = [0] * size  # 0 or 1 for each core
        self.access_time_us = 5  # 5 microseconds
        
    def read(self, address):
        """Read bit from core (destructive read - must rewrite)"""
        if 0 <= address < self.size:
            time.sleep(self.access_time_us / 1_000_000)  # Simulate access time
            return self.cores[address]
        raise MemoryError(f"Address {address} out of range")
    
    def write(self, address, value):
        """Write bit to core"""
        if 0 <= address < self.size:
            time.sleep(self.access_time_us / 1_000_000)
            self.cores[address] = 1 if value else 0
        else:
            raise MemoryError(f"Address {address} out of range")
    
    def dump(self, start=0, length=64):
        """Dump core plane contents"""
        output = []
        for i in range(start, min(start + length, self.size), 16):
            line = f"{i:04o}: "
            for j in range(16):
                if i + j < self.size:
                    line += "█" if self.cores[i + j] else "·"
            output.append(line)
        return "\n".join(output)


class PDP1CoreMemory:
    """Complete PDP-1 core memory - 18 planes × 4,096 cores"""
    
    def __init__(self, size=4096, word_bits=18):
        self.size = size
        self.word_bits = word_bits
        self.planes = [CoreMemoryPlane(size) for _ in range(word_bits)]
        self.access_time_us = 5
        
    def read(self, address):
        """Read 18-bit word from memory"""
        if 0 <= address < self.size:
            word = 0
            for plane in range(self.word_bits):
                bit = self.planes[plane].read(address)
                word |= (bit << plane)
            return word & 0x3FFFF  # Mask to 18 bits
        raise MemoryError(f"Address {address} out of range")
    
    def write(self, address, value):
        """Write 18-bit word to memory"""
        if 0 <= address < self.size:
            for plane in range(self.word_bits):
                bit = (value >> plane) & 1
                self.planes[plane].write(address, bit)
        else:
            raise MemoryError(f"Address {address} out of range")
    
    def dump(self, start=0, length=64):
        """Dump memory contents in octal format"""
        output = []
        for i in range(start, min(start + length, self.size), 8):
            line = f"{i:04o}: "
            for j in range(8):
                if i + j < self.size:
                    word = self.read(i + j)
                    line += f"{word:06o} "
            output.append(line)
        return "\n".join(output)
    
    def dump_visual(self, start=0, length=256):
        """Visual dump showing core activity"""
        output = []
        output.append("PDP-1 Core Memory Dump")
        output.append("=" * 60)
        
        for i in range(start, min(start + length, self.size), 32):
            line = f"{i:04o}: "
            for j in range(32):
                if i + j < self.size:
                    word = self.read(i + j)
                    # Show activity level (non-zero = active)
                    if word == 0:
                        line += "·"
                    elif word < 0o10000:
                        line += "░"
                    elif word < 0o20000:
                        line += "▒"
                    elif word < 0o30000:
                        line += "▓"
                    else:
                        line += "█"
            output.append(line)
        
        output.append("=" * 60)
        output.append("Legend: ·=empty ░=low ▒=med ▓=high █=full")
        return "\n".join(output)
    
    def get_statistics(self):
        """Get memory usage statistics"""
        total_words = self.size
        used_words = sum(1 for i in range(self.size) if self.read(i) != 0)
        usage_percent = (used_words / total_words) * 100
        
        return {
            'total_words': total_words,
            'used_words': used_words,
            'free_words': total_words - used_words,
            'usage_percent': usage_percent,
            'total_bits': total_words * self.word_bits,
            'total_bytes': (total_words * self.word_bits) // 8
        }


def test_core_memory():
    """Test core memory operations"""
    print("PDP-1 Core Memory Test")
    print("=" * 60)
    
    memory = PDP1CoreMemory()
    
    # Test write and read
    test_values = [0o000000, 0o123456, 0o377777, 0o200000, 0o000001]
    
    print("Write/Read Test:")
    for i, value in enumerate(test_values):
        address = 0o100 + i
        memory.write(address, value)
        read_value = memory.read(address)
        status = "✓" if read_value == value else "✗"
        print(f"  {status} Addr {address:04o}: wrote {value:06o}, read {read_value:06o}")
    
    # Memory statistics
    print("\nMemory Statistics:")
    stats = memory.get_statistics()
    for key, value in stats.items():
        print(f"  {key}: {value}")
    
    # Visual dump
    print("\n" + memory.dump_visual(0, 128))
    
    print("=" * 60)


if __name__ == "__main__":
    test_core_memory()
