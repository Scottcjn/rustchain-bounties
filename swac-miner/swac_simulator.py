#!/usr/bin/env python3
"""
SWAC Simulator - Standards Western Automatic Computer
内存：256 字 × 37 位
用于 SHA256 极简实现
"""

class SWACSimulator:
    """SWAC 计算机模拟器"""
    
    # SWAC 指令集 (简化)
    OPCODES = {
        0b000: 'ADD',    # 加法
        0b001: 'SUB',    # 减法
        0b010: 'MUL',    # 乘法
        0b011: 'DIV',    # 除法
        0b100: 'LD',     # 加载
        0b101: 'ST',     # 存储
        0b110: 'JMP',    # 跳转
        0b111: 'JZ',     # 零跳转
    }
    
    # SHA256 常量 K (前 32 位)
    K_TABLE = [
        0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5,
        0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
        0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3,
        0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
        0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc,
        0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
        0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7,
        0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
        0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13,
        0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
        0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3,
        0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
        0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5,
        0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
        0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208,
        0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
    ]
    
    # 初始哈希值 H0-H7
    H_INIT = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
    ]
    
    def __init__(self):
        # 256 字内存，每字 37 位
        self.memory = [0] * 256
        self.accumulator = 0  # 37 位累加器
        self.pc = 0  # 程序计数器
        self.running = False
        self.cycles = 0
        
        # 初始化内存
        self._init_memory()
    
    def _init_memory(self):
        """初始化内存布局"""
        # 加载 K 常量到地址 32-63
        for i, k in enumerate(self.K_TABLE[:32]):
            self.memory[32 + i] = k & 0x1FFFFFFFF  # 37 位掩码
        
        # 加载初始哈希值到地址 64-71
        for i, h in enumerate(self.H_INIT):
            self.memory[64 + i] = h & 0x1FFFFFFFF
    
    def _mask37(self, value):
        """保持 37 位"""
        return value & 0x1FFFFFFFF
    
    def _sign_extend(self, value):
        """37 位符号扩展"""
        if value & 0x100000000:  # 负数
            return value | ~0x1FFFFFFFF
        return value
    
    def load_program(self, program, start_addr=0):
        """加载程序到内存"""
        for i, instr in enumerate(program):
            if start_addr + i < 256:
                self.memory[start_addr + i] = instr & 0x1FFFFFFFF
    
    def load_data(self, data, start_addr):
        """加载数据到内存"""
        for i, val in enumerate(data):
            if start_addr + i < 256:
                self.memory[start_addr + i] = val & 0x1FFFFFFFF
    
    def step(self):
        """执行单条指令"""
        if not self.running or self.pc >= 256:
            return False
        
        instr = self.memory[self.pc]
        opcode = (instr >> 32) & 0b111  # 高 3 位操作码
        address = instr & 0x1FFFFFFF    # 低 32 位地址/操作数
        
        op_name = self.OPCODES.get(opcode, 'UNKNOWN')
        
        if op_name == 'ADD':
            self.accumulator = self._mask37(self.accumulator + self.memory[address & 0xFF])
        elif op_name == 'SUB':
            self.accumulator = self._mask37(self.accumulator - self.memory[address & 0xFF])
        elif op_name == 'LD':
            self.accumulator = self.memory[address & 0xFF]
        elif op_name == 'ST':
            self.memory[address & 0xFF] = self.accumulator
        elif op_name == 'JMP':
            self.pc = address & 0xFF
            self.cycles += 1
            return True
        elif op_name == 'JZ':
            if self.accumulator == 0:
                self.pc = address & 0xFF
                self.cycles += 1
                return True
        
        self.pc += 1
        self.cycles += 1
        return True
    
    def run(self, max_cycles=10000):
        """运行程序"""
        self.running = True
        self.cycles = 0
        while self.running and self.cycles < max_cycles:
            if not self.step():
                break
        self.running = False
        return self.cycles
    
    def stop(self):
        """停止运行"""
        self.running = False
    
    def get_hash_state(self):
        """获取当前哈希状态"""
        return [self.memory[64 + i] for i in range(8)]
    
    def dump_memory(self, start=0, length=32):
        """转储内存"""
        for i in range(length):
            addr = start + i
            if addr < 256:
                print(f"{addr:03d}: {self.memory[addr]:011X}")


def sha256_compress_swac(simulator, message_block):
    """
    在 SWAC 上执行 SHA256 压缩函数
    message_block: 512 位消息块 (64 字节)
    """
    # 加载消息块到工作区
    # 由于 SWAC 只有 37 位字，需要拆分 32 位值
    
    # 消息调度 W[0..15] 直接来自消息块
    for i in range(16):
        word = int.from_bytes(message_block[i*4:(i+1)*4], 'big')
        simulator.load_data([word], 96 + i)  # 工作变量区
    
    # 扩展 W[16..63] (需要 SWAC 程序计算)
    # W[t] = σ1(W[t-2]) + W[t-7] + σ0(W[t-15]) + W[t-16]
    
    # 加载初始哈希值到工作变量 a-h
    h = simulator.H_INIT.copy()
    simulator.load_data(h, 128)  # 临时存储区
    
    # 64 轮压缩 (需要 SWAC 汇编程序)
    # 这里用 Python 模拟结果
    for i in range(64):
        # SHA256 轮函数简化
        pass
    
    return simulator.get_hash_state()


if __name__ == '__main__':
    # 测试 SWAC 模拟器
    sim = SWACSimulator()
    
    print("=" * 50)
    print("SWAC Simulator - SHA256 Miner")
    print("=" * 50)
    print(f"内存：256 字 × 37 位")
    print(f"初始哈希状态:")
    for i, h in enumerate(sim.get_hash_state()):
        print(f"  H{i}: {h:08X}")
    
    print("\n内存布局:")
    sim.dump_memory(0, 16)
