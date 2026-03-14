"""
Pole Position Miner - Z80 CPU 模拟器
模拟 1982 年 Pole Position 街机的 Z80 CPU
"""

class Z80CPU:
    """Z80 CPU 模拟器"""
    
    def __init__(self):
        # 8 位寄存器
        self.A = 0  # 累加器
        self.B = 0
        self.C = 0
        self.D = 0
        self.E = 0
        self.H = 0
        self.L = 0
        
        # 16 位寄存器
        self.PC = 0x0000  # 程序计数器
        self.SP = 0xC000  # 栈指针
        
        # 标志位
        self.flags = {
            'S': False,  # 符号标志
            'Z': False,  # 零标志
            'H': False,  # 半进位标志
            'P': False,  # 奇偶标志
            'N': False,  # 加减标志
            'C': False   # 进位标志
        }
        
        # 内存 (64 KB)
        self.memory = bytearray(65536)
        
        # 状态
        self.running = False
        self.cycles = 0
        
        # 挖矿相关
        self.miner_data = {
            'nonce': 0,
            'hash_result': 0,
            'shares': 0
        }
    
    def read_memory(self, address):
        """读取内存"""
        return self.memory[address & 0xFFFF]
    
    def write_memory(self, address, value):
        """写入内存"""
        self.memory[address & 0xFFFF] = value & 0xFF
    
    def read_word(self, address):
        """读取 16 位字"""
        low = self.read_memory(address)
        high = self.read_memory((address + 1) & 0xFFFF)
        return (high << 8) | low
    
    def write_word(self, address, value):
        """写入 16 位字"""
        self.write_memory(address, value & 0xFF)
        self.write_memory((address + 1) & 0xFFFF, (value >> 8) & 0xFF)
    
    def fetch(self):
        """取指令"""
        opcode = self.read_memory(self.PC)
        self.PC = (self.PC + 1) & 0xFFFF
        self.cycles += 1
        return opcode
    
    def update_flags(self, value, bit8=False):
        """更新标志位"""
        if bit8:
            self.flags['S'] = (value & 0x80) != 0
        else:
            self.flags['S'] = (value & 0x8000) != 0
        
        if bit8:
            self.flags['Z'] = (value & 0xFF) == 0
        else:
            self.flags['Z'] = value == 0
        
        self.flags['H'] = False  # 简化处理
        self.flags['P'] = bin(value & 0xFF).count('1') % 2 == 0
        self.flags['N'] = False
    
    # Z80 基本指令实现
    def execute(self, opcode):
        """执行指令"""
        if opcode == 0x00:  # NOP
            pass
        
        elif opcode == 0x3E:  # LD A, n
            self.A = self.fetch()
            self.cycles += 2
        
        elif opcode == 0x06:  # LD B, n
            self.B = self.fetch()
            self.cycles += 2
        
        elif opcode == 0x0E:  # LD C, n
            self.C = self.fetch()
            self.cycles += 2
        
        elif opcode == 0x16:  # LD D, n
            self.D = self.fetch()
            self.cycles += 2
        
        elif opcode == 0x1E:  # LD E, n
            self.E = self.fetch()
            self.cycles += 2
        
        elif opcode == 0x26:  # LD H, n
            self.H = self.fetch()
            self.cycles += 2
        
        elif opcode == 0x2E:  # LD L, n
            self.L = self.fetch()
            self.cycles += 2
        
        elif opcode == 0x78:  # LD A, B
            self.A = self.B
        
        elif opcode == 0x79:  # LD A, C
            self.A = self.C
        
        elif opcode == 0x7A:  # LD A, D
            self.A = self.D
        
        elif opcode == 0x7B:  # LD A, E
            self.A = self.E
        
        elif opcode == 0x7C:  # LD A, H
            self.A = self.H
        
        elif opcode == 0x7D:  # LD A, L
            self.A = self.L
        
        elif opcode == 0x47:  # LD B, A
            self.B = self.A
        
        elif opcode == 0x4F:  # LD C, A
            self.C = self.A
        
        elif opcode == 0x57:  # LD D, A
            self.D = self.A
        
        elif opcode == 0x5F:  # LD E, A
            self.E = self.A
        
        elif opcode == 0x67:  # LD H, A
            self.H = self.A
        
        elif opcode == 0x6F:  # LD L, A
            self.L = self.A
        
        elif opcode == 0x80:  # ADD A, B
            result = self.A + self.B
            self.flags['C'] = result > 0xFF
            self.A = result & 0xFF
            self.update_flags(self.A)
            self.cycles += 1
        
        elif opcode == 0x81:  # ADD A, C
            result = self.A + self.C
            self.flags['C'] = result > 0xFF
            self.A = result & 0xFF
            self.update_flags(self.A)
            self.cycles += 1
        
        elif opcode == 0x82:  # ADD A, D
            result = self.A + self.D
            self.flags['C'] = result > 0xFF
            self.A = result & 0xFF
            self.update_flags(self.A)
            self.cycles += 1
        
        elif opcode == 0x83:  # ADD A, E
            result = self.A + self.E
            self.flags['C'] = result > 0xFF
            self.A = result & 0xFF
            self.update_flags(self.A)
            self.cycles += 1
        
        elif opcode == 0x84:  # ADD A, H
            result = self.A + self.H
            self.flags['C'] = result > 0xFF
            self.A = result & 0xFF
            self.update_flags(self.A)
            self.cycles += 1
        
        elif opcode == 0x85:  # ADD A, L
            result = self.A + self.L
            self.flags['C'] = result > 0xFF
            self.A = result & 0xFF
            self.update_flags(self.A)
            self.cycles += 1
        
        elif opcode == 0xC6:  # ADD A, n
            n = self.fetch()
            result = self.A + n
            self.flags['C'] = result > 0xFF
            self.A = result & 0xFF
            self.update_flags(self.A)
            self.cycles += 2
        
        elif opcode == 0x90:  # SUB A, B
            result = self.A - self.B
            self.flags['C'] = result < 0
            self.A = result & 0xFF
            self.update_flags(self.A)
            self.flags['N'] = True
            self.cycles += 1
        
        elif opcode == 0xA8:  # XOR A, B
            self.A = self.A ^ self.B
            self.update_flags(self.A)
            self.flags['N'] = False
            self.cycles += 1
        
        elif opcode == 0xA9:  # XOR A, C
            self.A = self.A ^ self.C
            self.update_flags(self.A)
            self.flags['N'] = False
            self.cycles += 1
        
        elif opcode == 0xAA:  # XOR A, D
            self.A = self.A ^ self.D
            self.update_flags(self.A)
            self.flags['N'] = False
            self.cycles += 1
        
        elif opcode == 0xAB:  # XOR A, E
            self.A = self.A ^ self.E
            self.update_flags(self.A)
            self.flags['N'] = False
            self.cycles += 1
        
        elif opcode == 0xAC:  # XOR A, H
            self.A = self.A ^ self.H
            self.update_flags(self.A)
            self.flags['N'] = False
            self.cycles += 1
        
        elif opcode == 0xAD:  # XOR A, L
            self.A = self.A ^ self.L
            self.update_flags(self.A)
            self.flags['N'] = False
            self.cycles += 1
        
        elif opcode == 0xEE:  # XOR A, n
            n = self.fetch()
            self.A = self.A ^ n
            self.update_flags(self.A)
            self.flags['N'] = False
            self.cycles += 2
        
        elif opcode == 0x07:  # RLCA (Rotate Left Circular)
            bit7 = (self.A & 0x80) >> 7
            self.A = ((self.A << 1) | bit7) & 0xFF
            self.flags['C'] = bit7 != 0
            self.flags['N'] = False
            self.flags['H'] = False
            self.cycles += 1
        
        elif opcode == 0x17:  # RLA (Rotate Left through Carry)
            bit7 = (self.A & 0x80) >> 7
            self.A = ((self.A << 1) | (1 if self.flags['C'] else 0)) & 0xFF
            self.flags['C'] = bit7 != 0
            self.flags['N'] = False
            self.flags['H'] = False
            self.cycles += 1
        
        elif opcode == 0x0F:  # RRCA (Rotate Right Circular)
            bit0 = self.A & 0x01
            self.A = ((self.A >> 1) | (bit0 << 7)) & 0xFF
            self.flags['C'] = bit0 != 0
            self.flags['N'] = False
            self.flags['H'] = False
            self.cycles += 1
        
        elif opcode == 0x1F:  # RRA (Rotate Right through Carry)
            bit0 = self.A & 0x01
            self.A = ((self.A >> 1) | ((0x80 if self.flags['C'] else 0))) & 0xFF
            self.flags['C'] = bit0 != 0
            self.flags['N'] = False
            self.flags['H'] = False
            self.cycles += 1
        
        elif opcode == 0x04:  # INC B
            self.B = (self.B + 1) & 0xFF
            self.update_flags(self.B)
            self.flags['N'] = False
            self.cycles += 1
        
        elif opcode == 0x0C:  # INC C
            self.C = (self.C + 1) & 0xFF
            self.update_flags(self.C)
            self.flags['N'] = False
            self.cycles += 1
        
        elif opcode == 0x14:  # INC D
            self.D = (self.D + 1) & 0xFF
            self.update_flags(self.D)
            self.flags['N'] = False
            self.cycles += 1
        
        elif opcode == 0x1C:  # INC E
            self.E = (self.E + 1) & 0xFF
            self.update_flags(self.E)
            self.flags['N'] = False
            self.cycles += 1
        
        elif opcode == 0x24:  # INC H
            self.H = (self.H + 1) & 0xFF
            self.update_flags(self.H)
            self.flags['N'] = False
            self.cycles += 1
        
        elif opcode == 0x2C:  # INC L
            self.L = (self.L + 1) & 0xFF
            self.update_flags(self.L)
            self.flags['N'] = False
            self.cycles += 1
        
        elif opcode == 0x3C:  # INC A
            self.A = (self.A + 1) & 0xFF
            self.update_flags(self.A)
            self.flags['N'] = False
            self.cycles += 1
        
        elif opcode == 0x05:  # DEC B
            self.B = (self.B - 1) & 0xFF
            self.update_flags(self.B)
            self.flags['N'] = True
            self.cycles += 1
        
        elif opcode == 0x0D:  # DEC C
            self.C = (self.C - 1) & 0xFF
            self.update_flags(self.C)
            self.flags['N'] = True
            self.cycles += 1
        
        elif opcode == 0x15:  # DEC D
            self.D = (self.D - 1) & 0xFF
            self.update_flags(self.D)
            self.flags['N'] = True
            self.cycles += 1
        
        elif opcode == 0x1D:  # DEC E
            self.E = (self.E - 1) & 0xFF
            self.update_flags(self.E)
            self.flags['N'] = True
            self.cycles += 1
        
        elif opcode == 0x25:  # DEC H
            self.H = (self.H - 1) & 0xFF
            self.update_flags(self.H)
            self.flags['N'] = True
            self.cycles += 1
        
        elif opcode == 0x2D:  # DEC L
            self.L = (self.L - 1) & 0xFF
            self.update_flags(self.L)
            self.flags['N'] = True
            self.cycles += 1
        
        elif opcode == 0x3D:  # DEC A
            self.A = (self.A - 1) & 0xFF
            self.update_flags(self.A)
            self.flags['N'] = True
            self.cycles += 1
        
        elif opcode == 0x18:  # JR e (Jump Relative)
            offset = self.fetch()
            if offset > 127:  # 负数
                offset -= 256
            self.PC = (self.PC + offset) & 0xFFFF
            self.cycles += 3
        
        elif opcode == 0x20:  # JR NZ, e
            offset = self.fetch()
            if not self.flags['Z']:
                if offset > 127:
                    offset -= 256
                self.PC = (self.PC + offset) & 0xFFFF
            self.cycles += 3 if not self.flags['Z'] else 2
        
        elif opcode == 0x28:  # JR Z, e
            offset = self.fetch()
            if self.flags['Z']:
                if offset > 127:
                    offset -= 256
                self.PC = (self.PC + offset) & 0xFFFF
            self.cycles += 3 if self.flags['Z'] else 2
        
        elif opcode == 0x30:  # JR NC, e
            offset = self.fetch()
            if not self.flags['C']:
                if offset > 127:
                    offset -= 256
                self.PC = (self.PC + offset) & 0xFFFF
            self.cycles += 3 if not self.flags['C'] else 2
        
        elif opcode == 0x38:  # JR C, e
            offset = self.fetch()
            if self.flags['C']:
                if offset > 127:
                    offset -= 256
                self.PC = (self.PC + offset) & 0xFFFF
            self.cycles += 3 if self.flags['C'] else 2
        
        elif opcode == 0x03:  # INC BC
            bc = (self.B << 8) | self.C
            bc = (bc + 1) & 0xFFFF
            self.B = (bc >> 8) & 0xFF
            self.C = bc & 0xFF
            self.cycles += 2
        
        elif opcode == 0x0B:  # DEC BC
            bc = (self.B << 8) | self.C
            bc = (bc - 1) & 0xFFFF
            self.B = (bc >> 8) & 0xFF
            self.C = bc & 0xFF
            self.cycles += 2
        
        elif opcode == 0x01:  # LD BC, nn
            self.C = self.fetch()
            self.B = self.fetch()
            self.cycles += 3
        
        elif opcode == 0x11:  # LD DE, nn
            self.E = self.fetch()
            self.D = self.fetch()
            self.cycles += 3
        
        elif opcode == 0x21:  # LD HL, nn
            self.L = self.fetch()
            self.H = self.fetch()
            self.cycles += 3
        
        elif opcode == 0x31:  # LD SP, nn
            low = self.fetch()
            high = self.fetch()
            self.SP = (high << 8) | low
            self.cycles += 3
        
        elif opcode == 0x7E:  # LD A, (HL)
            self.A = self.read_memory((self.H << 8) | self.L)
            self.cycles += 2
        
        elif opcode == 0x77:  # LD (HL), A
            self.write_memory((self.H << 8) | self.L, self.A)
            self.cycles += 2
        
        elif opcode == 0x46:  # LD B, (HL)
            self.B = self.read_memory((self.H << 8) | self.L)
            self.cycles += 2
        
        elif opcode == 0x4E:  # LD C, (HL)
            self.C = self.read_memory((self.H << 8) | self.L)
            self.cycles += 2
        
        elif opcode == 0x56:  # LD D, (HL)
            self.D = self.read_memory((self.H << 8) | self.L)
            self.cycles += 2
        
        elif opcode == 0x5E:  # LD E, (HL)
            self.E = self.read_memory((self.H << 8) | self.L)
            self.cycles += 2
        
        elif opcode == 0x66:  # LD H, (HL)
            self.H = self.read_memory((self.H << 8) | self.L)
            self.cycles += 2
        
        elif opcode == 0x6E:  # LD L, (HL)
            self.L = self.read_memory((self.H << 8) | self.L)
            self.cycles += 2
        
        elif opcode == 0x32:  # LD (nn), A
            addr = self.fetch() | (self.fetch() << 8)
            self.write_memory(addr, self.A)
            self.cycles += 4
        
        elif opcode == 0x3A:  # LD A, (nn)
            addr = self.fetch() | (self.fetch() << 8)
            self.A = self.read_memory(addr)
            self.cycles += 4
        
        elif opcode == 0xC3:  # JP nn
            low = self.fetch()
            high = self.fetch()
            self.PC = (high << 8) | low
            self.cycles += 3
        
        elif opcode == 0xC2:  # JP NZ, nn
            low = self.fetch()
            high = self.fetch()
            if not self.flags['Z']:
                self.PC = (high << 8) | low
            else:
                self.cycles += 1
            self.cycles += 3
        
        elif opcode == 0xCA:  # JP Z, nn
            low = self.fetch()
            high = self.fetch()
            if self.flags['Z']:
                self.PC = (high << 8) | low
            else:
                self.cycles += 1
            self.cycles += 3
        
        elif opcode == 0xD3:  # OUT (n), A
            port = self.fetch()
            # 简化：不实现实际 IO
            self.cycles += 3
        
        elif opcode == 0xDB:  # IN A, (n)
            port = self.fetch()
            self.A = 0  # 简化：返回 0
            self.cycles += 3
        
        elif opcode == 0xCD:  # CALL nn
            low = self.fetch()
            high = self.fetch()
            addr = (high << 8) | low
            # Push PC to stack
            self.write_memory(self.SP - 1, (self.PC >> 8) & 0xFF)
            self.write_memory(self.SP - 2, self.PC & 0xFF)
            self.SP -= 2
            self.PC = addr
            self.cycles += 5
        
        elif opcode == 0xC9:  # RET
            low = self.read_memory(self.SP)
            high = self.read_memory(self.SP + 1)
            self.PC = (high << 8) | low
            self.SP += 2
            self.cycles += 4
        
        elif opcode == 0x00:  # NOP
            self.cycles += 1
        
        elif opcode == 0x76:  # HALT
            self.running = False
            self.cycles += 1
        
        else:
            # 未实现的指令
            print(f"Warning: Unimplemented opcode 0x{opcode:02X} at PC=0x{self.PC-1:04X}")
            self.cycles += 1
    
    def run(self, max_cycles=1000000):
        """运行 CPU"""
        self.running = True
        start_cycles = self.cycles
        
        while self.running and (self.cycles - start_cycles) < max_cycles:
            opcode = self.fetch()
            self.execute(opcode)
        
        return self.cycles - start_cycles
    
    def reset(self):
        """重置 CPU"""
        self.A = self.B = self.C = self.D = self.E = self.H = self.L = 0
        self.PC = 0x0000
        self.SP = 0xC000
        self.flags = {k: False for k in self.flags}
        self.running = False
        self.cycles = 0
    
    def get_state(self):
        """获取 CPU 状态"""
        return {
            'A': self.A, 'B': self.B, 'C': self.C, 'D': self.D,
            'E': self.E, 'H': self.H, 'L': self.L,
            'PC': self.PC, 'SP': self.SP,
            'cycles': self.cycles,
            'flags': self.flags.copy()
        }
    
    def load_program(self, data, offset=0):
        """加载程序到内存"""
        for i, byte in enumerate(data):
            self.memory[offset + i] = byte & 0xFF
    
    def z80_mine_hash(self, header, nonce):
        """
        Z80 简化哈希函数
        模拟 Z80 汇编中的哈希计算
        """
        result = 0
        for byte in header:
            result = ((result << 5) | (result >> 27)) ^ byte
            result &= 0xFFFFFFFF
        
        # 添加 nonce
        for i in range(4):
            nonce_byte = (nonce >> (i * 8)) & 0xFF
            result = ((result << 5) | (result >> 27)) ^ nonce_byte
            result &= 0xFFFFFFFF
        
        return result


if __name__ == "__main__":
    # 测试 Z80 CPU
    cpu = Z80CPU()
    
    # 加载简单测试程序
    test_program = [
        0x3E, 0x05,  # LD A, 5
        0x06, 0x03,  # LD B, 3
        0x80,        # ADD A, B
        0x76         # HALT
    ]
    
    cpu.load_program(test_program)
    cpu.run()
    
    print("Z80 CPU Test:")
    print(f"  A = {cpu.A} (expected: 8)")
    print(f"  B = {cpu.B} (expected: 3)")
    print(f"  Cycles = {cpu.cycles}")
    print(f"  State: {cpu.get_state()}")
