"""
Pole Position Miner - 挖矿核心
实现简化的 PoW 挖矿算法，适配 Z80 架构
"""

import time
import hashlib
from .z80_cpu import Z80CPU


class MinerCore:
    """挖矿核心 - 在 Z80 模拟器上运行"""
    
    def __init__(self, z80: Z80CPU, wallet: str):
        self.z80 = z80
        self.wallet = wallet
        self.hashrate = 0.0  # 哈希率 (H/s)
        self.shares = 0  # 找到的 share 数量
        self.blocks_found = 0
        self.start_time = None
        self.current_block = None
        self.difficulty = 1000  # 简化难度
        
        # 统计信息
        self.stats = {
            'total_hashes': 0,
            'valid_shares': 0,
            'start_time': None,
            'last_share_time': None
        }
    
    def start_mining(self):
        """开始挖矿"""
        self.start_time = time.time()
        self.stats['start_time'] = self.start_time
    
    def stop_mining(self):
        """停止挖矿"""
        self.z80.running = False
    
    def create_block_header(self, block_number: int) -> bytes:
        """创建区块头 (简化版)"""
        header = bytearray(32)
        
        # 区块号 (4 字节)
        header[0:4] = block_number.to_bytes(4, 'little')
        
        # 时间戳 (4 字节)
        timestamp = int(time.time())
        header[4:8] = timestamp.to_bytes(4, 'little')
        
        # 前一区块哈希 (简化，24 字节)
        header[8:32] = hashlib.sha256(str(block_number - 1).encode()).digest()[:24]
        
        return bytes(header)
    
    def z80_mine_hash(self, header: bytes, nonce: int) -> int:
        """
        使用 Z80 CPU 计算哈希
        模拟 Z80 汇编中的简化哈希算法
        """
        return self.z80.z80_mine_hash(header, nonce)
    
    def check_difficulty(self, hash_result: int) -> bool:
        """检查是否满足难度要求"""
        # 简化难度检查：哈希结果低字节为 0
        target = (2**32) // self.difficulty
        return hash_result < target
    
    def mine_single_nonce(self, header: bytes, nonce: int) -> tuple:
        """挖掘单个 nonce"""
        hash_result = self.z80_mine_hash(header, nonce)
        self.stats['total_hashes'] += 1
        
        if self.check_difficulty(hash_result):
            self.stats['valid_shares'] += 1
            self.stats['last_share_time'] = time.time()
            return True, hash_result
        
        return False, hash_result
    
    def mine_block(self, block_number: int, max_nonces=100000) -> dict:
        """
        挖掘一个区块
        
        Returns:
            dict: 包含挖矿结果
        """
        self.current_block = block_number
        header = self.create_block_header(block_number)
        
        print(f"\n🎮 Mining Block #{block_number}")
        print(f"   Wallet: {self.wallet}")
        print(f"   Difficulty: {self.difficulty}")
        print(f"   Header: {header.hex()[:32]}...")
        
        start_time = time.time()
        found_nonce = None
        found_hash = None
        
        for nonce in range(max_nonces):
            if not self.z80.running:
                break
            
            found, hash_result = self.mine_single_nonce(header, nonce)
            
            if found:
                found_nonce = nonce
                found_hash = hash_result
                self.shares += 1
                print(f"   ✅ Share found! Nonce: {nonce}, Hash: 0x{hash_result:08X}")
                break
            
            # 每 10000 个 nonce 更新一次状态
            if nonce % 10000 == 0 and nonce > 0:
                elapsed = time.time() - start_time
                if elapsed > 0:
                    self.hashrate = nonce / elapsed
                    print(f"   ⛏️  Mining... {nonce}/{max_nonces}, Hashrate: {self.hashrate:.2f} H/s", end='\r')
        
        elapsed = time.time() - start_time
        
        result = {
            'block_number': block_number,
            'found': found_nonce is not None,
            'nonce': found_nonce,
            'hash': found_hash,
            'nonces_tried': min(max_nonces, found_nonce + 1 if found_nonce else max_nonces),
            'time_elapsed': elapsed,
            'hashrate': (min(max_nonces, found_nonce + 1 if found_nonce else max_nonces) / elapsed) if elapsed > 0 else 0
        }
        
        if result['found']:
            self.blocks_found += 1
            print(f"\n   🎉 Block mined successfully!")
            print(f"   Time: {elapsed:.2f}s, Hashrate: {result['hashrate']:.2f} H/s")
        else:
            print(f"\n   ❌ No share found in {max_nonces} nonces")
            print(f"   Time: {elapsed:.2f}s, Hashrate: {result['hashrate']:.2f} H/s")
        
        return result
    
    def get_stats(self) -> dict:
        """获取挖矿统计信息"""
        elapsed = time.time() - self.start_time if self.start_time else 0
        
        return {
            'wallet': self.wallet,
            'shares': self.shares,
            'blocks_found': self.blocks_found,
            'total_hashes': self.stats['total_hashes'],
            'hashrate': self.hashrate,
            'elapsed_time': elapsed,
            'difficulty': self.difficulty,
            'current_block': self.current_block,
            'uptime': f"{elapsed:.0f}s" if elapsed < 60 else f"{elapsed/60:.1f}m"
        }
    
    def print_stats(self):
        """打印统计信息"""
        stats = self.get_stats()
        
        print("\n" + "=" * 50)
        print("📊 POLE POSITION MINER - Statistics")
        print("=" * 50)
        print(f"   Wallet:        {stats['wallet'][:20]}...{stats['wallet'][-10:]}")
        print(f"   Shares:        {stats['shares']}")
        print(f"   Blocks Found:  {stats['blocks_found']}")
        print(f"   Total Hashes:  {stats['total_hashes']:,}")
        print(f"   Hashrate:      {stats['hashrate']:.2f} H/s")
        print(f"   Difficulty:    {stats['difficulty']}")
        print(f"   Uptime:        {stats['uptime']}")
        print("=" * 50)


class SimplifiedHash:
    """
    简化哈希算法 - 适配 Z80 的 8 位架构
    使用 XOR 和位移操作，避免复杂计算
    """
    
    @staticmethod
    def hash_32(data: bytes, nonce: int) -> int:
        """32 位简化哈希"""
        result = 0x12345678
        
        for byte in data:
            result ^= byte
            result = ((result << 5) | (result >> 27)) & 0xFFFFFFFF
            result ^= (result >> 3)
        
        # 混合 nonce
        for i in range(4):
            nonce_byte = (nonce >> (i * 8)) & 0xFF
            result ^= nonce_byte
            result = ((result << 5) | (result >> 27)) & 0xFFFFFFFF
        
        return result
    
    @staticmethod
    def hash_64(data: bytes, nonce: int) -> int:
        """64 位简化哈希 (使用两个 32 位)"""
        h1 = SimplifiedHash.hash_32(data, nonce)
        h2 = SimplifiedHash.hash_32(data, nonce ^ 0xFFFFFFFF)
        return (h1 << 32) | h2
    
    @staticmethod
    def verify(hash_result: int, target: int) -> bool:
        """验证哈希是否满足难度"""
        return hash_result < target


if __name__ == "__main__":
    # 测试挖矿核心
    print("Testing Pole Position Miner Core...")
    
    z80 = Z80CPU()
    miner = MinerCore(z80, "RTC4325af95d26d59c3ef025963656d22af638bb96b")
    miner.start_mining()
    
    # 挖掘几个测试区块
    for i in range(3):
        result = miner.mine_block(i, max_nonces=50000)
    
    # 打印统计
    miner.print_stats()
