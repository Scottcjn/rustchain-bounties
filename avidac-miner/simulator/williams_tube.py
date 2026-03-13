"""
Williams-Kilburn Tube Memory Simulator

Simulates the Williams-Kilburn CRT memory tubes used in AVIDAC.
These tubes were electrostatic storage devices that required constant refresh
and were prone to drift and bit errors.

Key characteristics:
- 1024 words × 40 bits = 5 KB total
- Required refresh ~100 Hz
- Temperature sensitive
- Unique drift patterns per tube
"""

import random
import time
from typing import Optional, List, Dict, Any

try:
    from .arithmetic import MASK_40, mask_40bit
except ImportError:
    from arithmetic import MASK_40, mask_40bit


class WilliamsTubeMemory:
    """
    Simulates Williams-Kilburn CRT memory tubes.
    
    Williams tubes were used in AVIDAC, IAS, MANIAC I, and other early computers.
    They stored data as charged spots on a CRT phosphor surface.
    
    Characteristics simulated:
    - Drift over time (charge leakage)
    - Temperature-dependent error rates
    - Refresh requirements
    - Unique per-tube characteristics
    """
    
    def __init__(
        self,
        words: int = 1024,
        bits_per_word: int = 40,
        refresh_rate_hz: float = 100.0,
        temperature_celsius: float = 25.0,
        enable_drift: bool = True,
        enable_errors: bool = True
    ):
        """
        Initialize Williams tube memory.
        
        Args:
            words: Number of words (default 1024 for AVIDAC)
            bits_per_word: Bits per word (default 40 for AVIDAC)
            refresh_rate_hz: Required refresh rate in Hz (default 100)
            temperature_celsius: Operating temperature (affects error rate)
            enable_drift: Enable drift simulation
            enable_errors: Enable random bit errors
        """
        self.words = words
        self.bits_per_word = bits_per_word
        self.refresh_rate = refresh_rate_hz
        self.temperature = temperature_celsius
        self.enable_drift = enable_drift
        self.enable_errors = enable_errors
        
        # Actual memory storage
        self.data = [0] * words
        
        # Drift simulation: unique pattern per memory location
        # Simulates phosphor degradation and charge leakage patterns
        self.drift_pattern = self._generate_drift_pattern()
        
        # Timing
        self.last_refresh_time = time.time()
        self.refresh_interval = 1.0 / refresh_rate_hz
        
        # Error rate parameters
        self.base_error_rate = 0.0001  # 0.01% base error rate per read
        self.drift_error_rate = 0.0005  # Additional error rate from drift
        
        # Statistics
        self.read_count = 0
        self.write_count = 0
        self.error_count = 0
        self.refresh_count = 0
        
        # Debug: track which addresses have errors
        self.error_log: List[Dict[str, Any]] = []
    
    def _generate_drift_pattern(self) -> List[int]:
        """
        Generate unique drift pattern for each memory location.
        
        This simulates the unique characteristics of each spot on the CRT,
        including phosphor aging, electron beam alignment, etc.
        """
        # Use a fixed seed for reproducibility
        random.seed(42)
        return [random.randint(0, 0xFF) for _ in range(self.words)]
    
    def _calculate_drift_factor(self) -> float:
        """
        Calculate drift factor based on time since last refresh.
        
        Returns:
            Float between 0.0 (just refreshed) and 1.0 (maximum drift)
        """
        if not self.enable_drift:
            return 0.0
        
        time_since_refresh = time.time() - self.last_refresh_time
        drift_factor = min(1.0, time_since_refresh / self.refresh_interval)
        return drift_factor
    
    def _calculate_error_rate(self) -> float:
        """
        Calculate bit error rate based on temperature and drift.
        
        Error rate increases with:
        - Higher temperature
        - Longer time since refresh
        """
        if not self.enable_errors:
            return 0.0
        
        # Temperature factor: errors increase above 25°C
        temp_factor = 1.0 + max(0, self.temperature - 25.0) * 0.05
        
        # Drift factor: errors increase as charge leaks
        drift_factor = 1.0 + self._calculate_drift_factor() * 0.5
        
        return self.base_error_rate * temp_factor * drift_factor
    
    def _calculate_reliability(self) -> float:
        """
        Calculate write reliability (0.0 to 1.0).
        
        Reliability decreases with temperature.
        """
        # Base reliability 99.9%, decreases with temperature
        reliability = 0.999 - max(0, self.temperature - 25.0) * 0.001
        return max(0.9, reliability)  # Minimum 90% reliability
    
    def read(self, address: int, simulate_errors: bool = True) -> int:
        """
        Read word from memory with drift and error simulation.
        
        Args:
            address: Memory address (0-1023)
            simulate_errors: Whether to simulate bit errors
        
        Returns:
            40-bit value (may contain errors if enabled)
        
        Raises:
            ValueError: If address is out of range
        """
        if address < 0 or address >= self.words:
            raise ValueError(f"Address {address} out of range [0, {self.words-1}]")
        
        self.read_count += 1
        base_value = self.data[address]
        
        # Apply drift (XOR with drift pattern)
        if self.enable_drift:
            drift_factor = self._calculate_drift_factor()
            drift = int(self.drift_pattern[address] * drift_factor) & 0xFF
            # Drift primarily affects high bits (more significant bits)
            drifted_value = base_value ^ (drift << 32)
        else:
            drifted_value = base_value
        
        # Apply random bit errors
        if simulate_errors and self.enable_errors:
            error_rate = self._calculate_error_rate()
            if random.random() < error_rate:
                # Flip a random bit
                error_bit = random.randint(0, self.bits_per_word - 1)
                drifted_value ^= (1 << error_bit)
                self.error_count += 1
                
                # Log error for debugging
                if len(self.error_log) < 100:  # Limit log size
                    self.error_log.append({
                        'time': time.time(),
                        'address': address,
                        'original': base_value,
                        'corrupted': drifted_value,
                        'error_bit': error_bit
                    })
        
        return mask_40bit(drifted_value)
    
    def write(self, address: int, value: int) -> bool:
        """
        Write word to memory with temperature-dependent reliability.
        
        Args:
            address: Memory address (0-1023)
            value: 40-bit value to write
        
        Returns:
            True if write succeeded, False if it failed (rare)
        
        Raises:
            ValueError: If address is out of range
        """
        if address < 0 or address >= self.words:
            raise ValueError(f"Address {address} out of range [0, {self.words-1}]")
        
        self.write_count += 1
        
        # Check write reliability
        if random.random() > self._calculate_reliability():
            return False  # Write failed
        
        self.data[address] = mask_40bit(value)
        return True
    
    def refresh(self) -> None:
        """
        Refresh all memory cells.
        
        Williams tubes required constant refresh (~100 Hz) to maintain charge.
        This should be called periodically by the simulator.
        """
        self.last_refresh_time = time.time()
        self.refresh_count += 1
        
        # In real Williams tubes, refresh re-writes all values
        # We simulate this by just updating the timestamp
        # (actual data doesn't change, but drift resets)
    
    def read_raw(self, address: int) -> int:
        """
        Read word without error simulation.
        
        Use for debugging or when errors should be disabled.
        """
        if address < 0 or address >= self.words:
            raise ValueError(f"Address {address} out of range [0, {self.words-1}]")
        
        return self.data[address]
    
    def write_raw(self, address: int, value: int) -> None:
        """
        Write word without reliability check.
        
        Use for debugging or initialization.
        """
        if address < 0 or address >= self.words:
            raise ValueError(f"Address {address} out of range [0, {self.words-1}]")
        
        self.data[address] = mask_40bit(value)
    
    def get_status(self) -> Dict[str, Any]:
        """
        Get memory status and statistics.
        
        Returns:
            Dictionary with memory statistics
        """
        time_since_refresh = time.time() - self.last_refresh_time
        drift_factor = self._calculate_drift_factor()
        error_rate = self._calculate_error_rate()
        
        return {
            'words': self.words,
            'bits_per_word': self.bits_per_word,
            'total_bits': self.words * self.bits_per_word,
            'total_bytes': (self.words * self.bits_per_word) // 8,
            'temperature_celsius': self.temperature,
            'refresh_rate_hz': self.refresh_rate,
            'time_since_refresh_s': time_since_refresh,
            'drift_factor': drift_factor,
            'current_error_rate': error_rate,
            'statistics': {
                'reads': self.read_count,
                'writes': self.write_count,
                'errors': self.error_count,
                'refreshes': self.refresh_count,
                'error_rate_observed': self.error_count / max(1, self.read_count)
            },
            'features': {
                'drift_enabled': self.enable_drift,
                'errors_enabled': self.enable_errors
            }
        }
    
    def dump_memory(self, start: int = 0, length: int = 16) -> str:
        """
        Dump memory contents as hex string.
        
        Args:
            start: Starting address
            length: Number of words to dump
        
        Returns:
            Formatted hex dump string
        """
        lines = []
        for i in range(length):
            addr = start + i
            if addr >= self.words:
                break
            value = self.data[addr]
            lines.append(f"{addr:03X}: {value:010X}")
        return '\n'.join(lines)
    
    def set_temperature(self, temperature: float) -> None:
        """
        Set operating temperature.
        
        Higher temperatures increase error rates.
        """
        self.temperature = max(-10.0, min(60.0, temperature))
    
    def clear(self) -> None:
        """Clear all memory to zero."""
        self.data = [0] * self.words
        self.read_count = 0
        self.write_count = 0
        self.error_count = 0
        self.refresh_count = 0
        self.error_log = []


class WilliamsTubeBank:
    """
    Simulates a bank of multiple Williams tubes.
    
    AVIDAC used multiple tubes to store the full 40-bit words.
    This class manages multiple tubes and their collective behavior.
    """
    
    def __init__(self, num_tubes: int = 1, **kwargs):
        """
        Initialize a bank of Williams tubes.
        
        Args:
            num_tubes: Number of tubes in the bank
            **kwargs: Arguments passed to individual WilliamsTubeMemory
        """
        self.num_tubes = num_tubes
        self.tubes = [WilliamsTubeMemory(**kwargs) for _ in range(num_tubes)]
    
    def refresh_all(self) -> None:
        """Refresh all tubes in the bank."""
        for tube in self.tubes:
            tube.refresh()
    
    def get_bank_status(self) -> List[Dict[str, Any]]:
        """Get status of all tubes."""
        return [tube.get_status() for tube in self.tubes]
