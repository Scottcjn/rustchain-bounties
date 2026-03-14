#!/usr/bin/env python3
"""
Defender 矿工 - 挖矿逻辑模拟器
模拟在 6809 CPU 上运行的简化挖矿算法
"""

import hashlib
import time
from typing import Tuple, Optional
from dataclasses import dataclass


@dataclass
class BlockHeader:
    """简化区块头 (适合 8 位系统)"""
    version: int = 1
    prev_hash: int = 0xDEADBEEF
    merkle_root: int = 0xCAFEBABE
    timestamp: int = 0
    bits: int = 0x1D00FFFF  # 难度目标
    nonce: int = 0
    
    def to_bytes(self) -> bytes:
        """转换为字节序列 (简化版)"""
        return (
            self.version.to_bytes(2, 'big') +
            self.prev_hash.to_bytes(4, 'big') +
            self.merkle_root.to_bytes(4, 'big') +
            self.timestamp.to_bytes(4, 'big') +
            self.bits.to_bytes(4, 'big') +
            self.nonce.to_bytes(2, 'big')  # 16 位 nonce (6809 限制)
        )


class DefenderMiner:
    """Defender 街机矿工模拟器"""
    
    def __init__(self, difficulty_bits: int = 16):
        self.difficulty_bits = difficulty_bits
        self.difficulty_target = (1 << (256 - difficulty_bits))
        self.hashes_computed = 0
        self.blocks_found = 0
        
    def compute_hash_6809_style(self, header: BlockHeader) -> int:
        """
        模拟 6809 风格的哈希计算
        使用简化的乘法哈希 (实际硬件会使用 SHA-256 子集)
        """
        # 利用 6809 的硬件乘法器
        data = header.to_bytes()
        
        # 简化哈希：使用乘法和 XOR 混合
        hash_val = 0
        for i in range(0, len(data), 2):
            if i + 1 < len(data):
                word = (data[i] << 8) | data[i + 1]
            else:
                word = data[i] << 8
            
            # 6809 MUL 指令：8 位×8 位→16 位
            hi = (word >> 8) & 0xFF
            lo = word & 0xFF
            product = (hi * lo) & 0xFFFF
            
            hash_val = (hash_val ^ product) & 0xFFFF
        
        # 多轮混合 (模拟 SHA-256 的多轮)
        for _ in range(4):
            hash_val = ((hash_val * 0x1235) + 0x6789) & 0xFFFF
        
        return hash_val
    
    def mine_block(self, header: BlockHeader, max_attempts: int = 65536) -> Tuple[bool, int]:
        """
        挖矿：寻找有效 nonce
        
        返回：(是否成功，尝试次数)
        """
        start_time = time.time()
        
        for nonce in range(max_attempts):
            header.nonce = nonce
            hash_result = self.compute_hash_6809_style(header)
            self.hashes_computed += 1
            
            # 检查是否满足难度
            if hash_result < (0xFFFF >> (self.difficulty_bits - 16)):
                elapsed = time.time() - start_time
                self.blocks_found += 1
                return True, nonce
        
        elapsed = time.time() - start_time
        return False, -1
    
    def estimate_hashrate(self, duration_seconds: float = 1.0) -> float:
        """估算哈希率 (H/s)"""
        start_hashes = self.hashes_computed
        start_time = time.time()
        
        # 运行固定时间
        dummy_header = BlockHeader()
        while time.time() - start_time < duration_seconds:
            dummy_header.nonce = self.hashes_computed
            self.compute_hash_6809_style(dummy_header)
        
        elapsed = time.time() - start_time
        hashes = self.hashes_computed - start_hashes
        
        return hashes / elapsed if elapsed > 0 else 0


def simulate_defender_miner():
    """模拟 Defender 矿工运行"""
    print("=" * 70)
    print("Defender 街机 (1981) - RustChain 矿工模拟")
    print("=" * 70)
    
    miner = DefenderMiner(difficulty_bits=20)
    
    print(f"\n硬件配置:")
    print(f"  CPU: Motorola 6809 @ 1 MHz")
    print(f"  架构：8 位，带 16 位特性")
    print(f"  RAM: 4 KB 可用")
    print(f"  ROM: 48 KB")
    print(f"  硬件乘法器：✓ (8 位×8 位→16 位)")
    
    print(f"\n挖矿配置:")
    print(f"  难度：{miner.difficulty_bits} 位")
    print(f"  难度目标：0x{(0xFFFF >> (miner.difficulty_bits - 16)):04X}")
    print(f"  Nonce 范围：0x0000 - 0xFFFF (16 位)")
    
    # 创建示例区块
    header = BlockHeader(
        version=1,
        prev_hash=0x8392AABB,
        merkle_root=0xCCDDEEFF,
        timestamp=int(time.time()) & 0xFFFFFFFF,
        bits=0x1D00FFFF,
        nonce=0
    )
    
    print(f"\n区块头:")
    print(f"  版本：{header.version}")
    print(f"  前块哈希：0x{header.prev_hash:08X}")
    print(f"  Merkle 根：0x{header.merkle_root:08X}")
    print(f"  时间戳：{header.timestamp} (0x{header.timestamp:08X})")
    print(f"  难度位：0x{header.bits:08X}")
    
    print(f"\n开始挖矿...")
    print("-" * 70)
    
    # 挖矿
    start_time = time.time()
    success, nonce = miner.mine_block(header, max_attempts=10000)
    elapsed = time.time() - start_time
    
    if success:
        print(f"\n✓ 找到有效区块!")
        print(f"  Nonce: 0x{nonce:04X} ({nonce})")
        header.nonce = nonce
        final_hash = miner.compute_hash_6809_style(header)
        print(f"  区块哈希：0x{final_hash:04X}")
        print(f"  用时：{elapsed:.3f} 秒")
        print(f"  尝试次数：{nonce + 1}")
        print(f"  哈希率：{(nonce + 1) / elapsed:.2f} H/s")
    else:
        print(f"\n✗ 未在 10000 次内找到有效区块")
        print(f"  用时：{elapsed:.3f} 秒")
    
    print("-" * 70)
    
    # 性能估算
    print(f"\n性能估算:")
    hashrate = miner.estimate_hashrate(0.5)
    print(f"  估算哈希率：{hashrate:.2f} H/s")
    print(f"  每哈希周期：{1000000 / hashrate:.0f} CPU 周期 (假设 1 MHz)")
    
    print(f"\n统计:")
    print(f"  总哈希数：{miner.hashes_computed}")
    print(f"  找到区块：{miner.blocks_found}")
    
    # 与真实 SHA-256 对比
    print(f"\n" + "=" * 70)
    print("真实 SHA-256 对比 (仅用于验证)")
    print("=" * 70)
    
    header.nonce = 0
    sha256_hash = hashlib.sha256(header.to_bytes()).hexdigest()
    print(f"  SHA-256 哈希：{sha256_hash[:16]}...")
    print(f"  (注意：实际 6809 实现会使用简化哈希算法)")
    
    print("\n" + "=" * 70)
    print("模拟完成!")
    print("=" * 70)


def benchmark_6809_operations():
    """基准测试 6809 操作"""
    print("\n" + "=" * 70)
    print("6809 操作基准测试")
    print("=" * 70)
    
    from defender6809 import Motorola6809, MemoryMap
    
    mem = MemoryMap()
    cpu = Motorola6809(mem)
    
    # 测试 MUL 指令性能
    print(f"\nMUL 指令 (硬件乘法):")
    start_cycles = cpu.cycle_count
    for i in range(1000):
        cpu.regs.A = i & 0xFF
        cpu.regs.B = (i * 3) & 0xFF
        cpu.mem.write_byte(0xC000, 0x3D)  # MUL
        cpu.regs.PC = 0xC000
        cpu.step()
    
    cycles = cpu.cycle_count - start_cycles
    print(f"  1000 次乘法：{cycles} 周期")
    print(f"  平均每指令：{cycles / 1000:.1f} 周期")
    print(f"  理论速度：{1000000 / (cycles / 1000):.0f} 次乘法/秒 (@ 1 MHz)")
    
    # 测试 ADD 指令
    cpu.cycle_count = 0
    print(f"\nADDA 指令 (加法):")
    start_cycles = cpu.cycle_count
    for i in range(1000):
        cpu.regs.A = i & 0xFF
        cpu.mem.write_byte(0xC000, 0x8B)  # ADDA #imm
        cpu.mem.write_byte(0xC001, 0x01)
        cpu.regs.PC = 0xC000
        cpu.step()
    
    cycles = cpu.cycle_count - start_cycles
    print(f"  1000 次加法：{cycles} 周期")
    print(f"  平均每指令：{cycles / 1000:.1f} 周期")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    simulate_defender_miner()
    benchmark_6809_operations()
