#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Galaga Hardware Simulation Module
Simulates Z80 CPU timing and hardware characteristics for fingerprinting
"""

import time
import random
import hashlib
import json
import math


class Z80Simulator:
    """Simulate Z80 CPU @ 3.072 MHz"""
    
    def __init__(self):
        self.clock_speed = 3072000  # 3.072 MHz
        self.t_state = 0
        self.entropy_samples = []
        
    def execute_instruction(self, instruction, cycles):
        """
        Simulate Z80 instruction execution.
        Each instruction takes a specific number of T-states.
        """
        start = time.perf_counter()
        
        # Simulate T-states
        for _ in range(cycles):
            self.t_state += 1
            # Simulate clock cycle (busy wait)
            for _ in range(100):
                pass
        
        elapsed = time.perf_counter() - start
        return elapsed
    
    def collect_timing_entropy(self, sample_count=32):
        """
        Collect timing entropy from Z80 simulation.
        Real Z80 CPUs have unique clock skew due to analog components.
        """
        samples = []
        
        # Mix of different instruction types
        instructions = [
            ("NOP", 4),
            ("LD A,B", 4),
            ("ADD A,B", 4),
            ("JP nn", 10),
            ("CALL nn", 17),
            ("RET", 10),
        ]
        
        for i in range(sample_count):
            # Random instruction mix
            instr, cycles = random.choice(instructions)
            
            # Add analog drift (simulates oscillator drift)
            drift = random.gauss(0, cycles * 0.001)
            adjusted_cycles = int(cycles + drift)
            
            elapsed = self.execute_instruction(instr, adjusted_cycles)
            samples.append(elapsed)
        
        self.entropy_samples = samples
        return samples
    
    def get_timing_statistics(self):
        """Calculate timing statistics for fingerprint"""
        if not self.entropy_samples:
            self.collect_timing_entropy()
        
        samples = self.entropy_samples
        n = len(samples)
        
        mean = sum(samples) / n
        variance = sum((x - mean) ** 2 for x in samples) / n
        std_dev = math.sqrt(variance)
        min_val = min(samples)
        max_val = max(samples)
        
        return {
            "mean": mean,
            "variance": variance,
            "std_dev": std_dev,
            "min": min_val,
            "max": max_val,
            "samples": samples,
        }


class GalagaVideoSimulator:
    """Simulate Galaga video hardware timing"""
    
    def __init__(self):
        # NTSC timing parameters
        self.h_sync = 15734.264  # Hz
        self.v_sync = 59.94  # Hz
        self.pixel_clock = 5369317.5  # Hz
        self.resolution = (288, 224)  # H x V
        
    def collect_video_timing(self):
        """
        Collect video timing characteristics.
        CRT displays have unique analog signatures.
        """
        # Simulate oscillator drift (temperature-dependent)
        temp_drift = random.gauss(0, 0.01)
        
        h_sync_measured = self.h_sync + temp_drift
        v_sync_measured = self.v_sync + temp_drift * 0.5
        
        return {
            "h_sync": h_sync_measured,
            "v_sync": v_sync_measured,
            "pixel_clock": self.pixel_clock,
            "resolution": self.resolution,
        }


class GalagaAudioSimulator:
    """Simulate Galaga PSG audio chip"""
    
    def __init__(self):
        # PSG channel characteristics
        self.channels = 3
        self.sample_rate = 48000
        
    def collect_audio_fingerprint(self):
        """
        Collect audio chip characteristics.
        Each PSG chip has unique frequency response.
        """
        # Simulate channel frequencies with analog drift
        base_freqs = [440.0, 880.0, 1760.0]  # A4, A5, A6
        measured_freqs = [f + random.gauss(0, 0.5) for f in base_freqs]
        
        return {
            "channels": self.channels,
            "sample_rate": self.sample_rate,
            "frequencies": measured_freqs,
        }


class GalagaHardwareFingerprint:
    """Generate complete Galaga hardware fingerprint"""
    
    def __init__(self):
        self.z80 = Z80Simulator()
        self.video = GalagaVideoSimulator()
        self.audio = GalagaAudioSimulator()
        
    def generate(self):
        """Generate complete fingerprint"""
        # Collect all hardware characteristics
        z80_stats = self.z80.get_timing_statistics()
        video_timing = self.video.collect_video_timing()
        audio_fp = self.audio.collect_audio_fingerprint()
        
        # Combine into fingerprint data
        fp_data = {
            "z80": {
                "clock_speed": self.z80.clock_speed,
                "timing": {
                    "mean": z80_stats["mean"],
                    "variance": z80_stats["variance"],
                    "std_dev": z80_stats["std_dev"],
                },
                "samples": z80_stats["samples"],
            },
            "video": video_timing,
            "audio": audio_fp,
            "ram_kb": 6,
            "vram_kb": 2,
            "year": 1981,
        }
        
        # Generate hash
        fp_string = json.dumps(fp_data, sort_keys=True, default=str)
        fp_hash = hashlib.sha256(fp_string.encode()).hexdigest()
        
        return {
            "hash": fp_hash,
            "data": fp_data,
        }
    
    def verify_fingerprint(self, stored_hash):
        """Verify fingerprint matches stored hash"""
        current = self.generate()
        return current["hash"] == stored_hash


def demo_fingerprint():
    """Demonstrate fingerprint generation"""
    print("=" * 60)
    print("Galaga Hardware Fingerprint Generator")
    print("=" * 60)
    
    fp_gen = GalagaHardwareFingerprint()
    
    print("\nGenerating fingerprint...")
    fp = fp_gen.generate()
    
    print(f"\nFingerprint Hash: {fp['hash']}")
    print(f"\nZ80 CPU:")
    print(f"  Clock: {fp['data']['z80']['clock_speed']} Hz")
    print(f"  Timing Mean: {fp['data']['z80']['timing']['mean']:.10f} s")
    print(f"  Timing StdDev: {fp['data']['z80']['timing']['std_dev']:.10f} s")
    
    print(f"\nVideo:")
    print(f"  H-Sync: {fp['data']['video']['h_sync']:.3f} Hz")
    print(f"  V-Sync: {fp['data']['video']['v_sync']:.3f} Hz")
    
    print(f"\nAudio:")
    print(f"  Channels: {fp['data']['audio']['channels']}")
    print(f"  Frequencies: {fp['data']['audio']['frequencies']}")
    
    print(f"\nHardware:")
    print(f"  RAM: {fp['data']['ram_kb']} KB")
    print(f"  VRAM: {fp['data']['vram_kb']} KB")
    print(f"  Year: {fp['data']['year']}")
    
    print("\n" + "=" * 60)
    
    return fp


if __name__ == '__main__':
    demo_fingerprint()
