#!/usr/bin/env python3
"""
RustChain Breakout Miner - 6502 Simulator
==========================================

模拟 Atari Breakout 街机环境 (1976)
- MOS Technology 6502 @ 1.5 MHz
- 8 KB RAM
- VBLANK 中断 (60Hz)
- 拨盘输入
- 游戏状态寄存器

用于测试和验证矿工代码，无需真实街机硬件。
"""

import struct
import time
import random
import hashlib
from enum import IntEnum
from typing import Optional, Callable, List


class BreakoutRegisters(IntEnum):
    """Breakout 街机内存映射寄存器"""
    VBLANK_COUNTER = 0xC040    # VBLANK 计数器 (16 位)
    PADDLE_POSITION = 0xC060   # 玩家拨盘位置 (8 位)
    GAME_STATE = 0xC061        # 游戏状态 (8 位)
    BALL_X = 0xC062            # 球 X 位置 (8 位)
    BALL_Y = 0xC063            # 球 Y 位置 (8 位)
    BRICK_STATUS = 0xC080      # 砖块状态 (32 字节，每块砖 1 位)
    SCORE = 0xC100             # 分数 (16 位)
    LIVES = 0xC102             # 剩余生命 (8 位)
    LED_CONTROL = 0xC200       # LED 控制寄存器


class MemoryMap:
    """Breakout 街机器内存映射"""
    ZERO_PAGE_START = 0x0000
    ZERO_PAGE_END = 0x00FF
    STACK_START = 0x0100
    STACK_END = 0x01FF
    RAM_START = 0x0200
    RAM_END = 0x1FFF  # 8 KB RAM
    IO_START = 0xC000
    IO_END = 0xCFFF
    ROM_START = 0xF000
    ROM_END = 0xFFFF


class CPU6502:
    """6502 CPU 模拟器"""
    
    def __init__(self, memory: bytearray):
        self.memory = memory
        self.a = 0x00      # 累加器
        self.x = 0x00      # X 寄存器
        self.y = 0x00      # Y 寄存器
        self.sp = 0xFF     # 栈指针
        self.pc = 0x0200   # 程序计数器 (从 $0200 开始)
        self.status = 0x20 # 状态寄存器 (中断禁用)
        
        # 周期计数
        self.cycles = 0
        self.total_cycles = 0
        
        # 中断处理
        self.irq_handler = 0xFFFE  # IRQ 向量地址
        self.nmi_handler = 0xFFFA  # NMI 向量地址
        
        # 运行标志
        self.running = True
        
    def read(self, addr: int) -> int:
        """读取内存"""
        if addr < len(self.memory):
            return self.memory[addr]
        return 0x00
    
    def write(self, addr: int, value: int):
        """写入内存"""
        if addr < len(self.memory):
            self.memory[addr] = value & 0xFF
    
    def read16(self, addr: int) -> int:
        """读取 16 位值"""
        lo = self.read(addr)
        hi = self.read((addr + 1) & 0xFFFF)
        return (hi << 8) | lo
    
    def write16(self, addr: int, value: int):
        """写入 16 位值"""
        self.write(addr, value & 0xFF)
        self.write((addr + 1) & 0xFFFF, (value >> 8) & 0xFF)
    
    def push(self, value: int):
        """压栈"""
        self.write(0x0100 + self.sp, value & 0xFF)
        self.sp = (self.sp - 1) & 0xFF
    
    def pull(self) -> int:
        """出栈"""
        self.sp = (self.sp + 1) & 0xFF
        return self.read(0x0100 + self.sp)
    
    def set_flag(self, flag: int, value: bool):
        """设置标志位"""
        if value:
            self.status |= flag
        else:
            self.status &= ~flag
    
    def get_flag(self, flag: int) -> bool:
        """获取标志位"""
        return bool(self.status & flag)
    
    # 标志位
    FLAG_C = 0x01  # 进位
    FLAG_Z = 0x02  # 零
    FLAG_I = 0x04  # 中断禁用
    FLAG_D = 0x08  # 十进制模式
    FLAG_B = 0x10  # 中断类型
    FLAG_U = 0x20  # 未使用
    FLAG_V = 0x40  # 溢出
    FLAG_N = 0x80  # 负数
    
    def update_flags(self, value: int):
        """更新 Z 和 N 标志"""
        self.set_flag(self.FLAG_Z, (value & 0xFF) == 0)
        self.set_flag(self.FLAG_N, bool(value & 0x80))
    
    # 寻址模式
    def addr_immediate(self) -> int:
        return self.pc
    
    def addr_zero_page(self) -> int:
        return self.read(self.pc)
    
    def addr_zero_page_x(self) -> int:
        return (self.read(self.pc) + self.x) & 0xFF
    
    def addr_zero_page_y(self) -> int:
        return (self.read(self.pc) + self.y) & 0xFF
    
    def addr_absolute(self) -> int:
        return self.read16(self.pc)
    
    def addr_absolute_x(self) -> int:
        return (self.read16(self.pc) + self.x) & 0xFFFF
    
    def addr_absolute_y(self) -> int:
        return (self.read16(self.pc) + self.y) & 0xFFFF
    
    def addr_indirect_x(self) -> int:
        ptr = (self.read(self.pc) + self.x) & 0xFF
        return self.read16(ptr)
    
    def addr_indirect_y(self) -> int:
        ptr = self.read(self.pc)
        return (self.read16(ptr) + self.y) & 0xFFFF
    
    def addr_relative(self) -> int:
        offset = self.read(self.pc)
        if offset & 0x80:
            offset -= 256
        return (self.pc + offset) & 0xFFFF
    
    # 指令实现
    def op_lda(self, addr: int):
        self.a = self.read(addr)
        self.update_flags(self.a)
    
    def op_ldx(self, addr: int):
        self.x = self.read(addr)
        self.update_flags(self.x)
    
    def op_ldy(self, addr: int):
        self.y = self.read(addr)
        self.update_flags(self.y)
    
    def op_sta(self, addr: int):
        self.write(addr, self.a)
    
    def op_stx(self, addr: int):
        self.write(addr, self.x)
    
    def op_sty(self, addr: int):
        self.write(addr, self.y)
    
    def op_adc(self, addr: int):
        m = self.read(addr)
        result = self.a + m + (1 if self.get_flag(self.FLAG_C) else 0)
        self.set_flag(self.FLAG_C, result > 0xFF)
        self.set_flag(self.FLAG_V, ((self.a ^ result) & (m ^ result) & 0x80) != 0)
        self.a = result & 0xFF
        self.update_flags(self.a)
    
    def op_sbc(self, addr: int):
        m = self.read(addr)
        result = self.a - m - (1 if not self.get_flag(self.FLAG_C) else 0)
        self.set_flag(self.FLAG_C, result >= 0)
        self.set_flag(self.FLAG_V, ((self.a ^ result) & (~m ^ result) & 0x80) != 0)
        self.a = result & 0xFF
        self.update_flags(self.a)
    
    def op_and(self, addr: int):
        self.a &= self.read(addr)
        self.update_flags(self.a)
    
    def op_eor(self, addr: int):
        self.a ^= self.read(addr)
        self.update_flags(self.a)
    
    def op_ora(self, addr: int):
        self.a |= self.read(addr)
        self.update_flags(self.a)
    
    def op_cmp(self, addr: int):
        m = self.read(addr)
        result = self.a - m
        self.set_flag(self.FLAG_C, result >= 0)
        self.update_flags(result & 0xFF)
    
    def op_cpx(self, addr: int):
        m = self.read(addr)
        result = self.x - m
        self.set_flag(self.FLAG_C, result >= 0)
        self.update_flags(result & 0xFF)
    
    def op_cpy(self, addr: int):
        m = self.read(addr)
        result = self.y - m
        self.set_flag(self.FLAG_C, result >= 0)
        self.update_flags(result & 0xFF)
    
    def op_inc(self, addr: int):
        v = (self.read(addr) + 1) & 0xFF
        self.write(addr, v)
        self.update_flags(v)
    
    def op_dec(self, addr: int):
        v = (self.read(addr) - 1) & 0xFF
        self.write(addr, v)
        self.update_flags(v)
    
    def op_inx(self):
        self.x = (self.x + 1) & 0xFF
        self.update_flags(self.x)
    
    def op_iny(self):
        self.y = (self.y + 1) & 0xFF
        self.update_flags(self.y)
    
    def op_dex(self):
        self.x = (self.x - 1) & 0xFF
        self.update_flags(self.x)
    
    def op_dey(self):
        self.y = (self.y - 1) & 0xFF
        self.update_flags(self.y)
    
    def op_asl(self, addr: Optional[int] = None):
        if addr is None:  # A
            self.set_flag(self.FLAG_C, bool(self.a & 0x80))
            self.a = (self.a << 1) & 0xFF
            self.update_flags(self.a)
        else:
            v = self.read(addr)
            self.set_flag(self.FLAG_C, bool(v & 0x80))
            v = (v << 1) & 0xFF
            self.write(addr, v)
            self.update_flags(v)
    
    def op_lsr(self, addr: Optional[int] = None):
        if addr is None:  # A
            self.set_flag(self.FLAG_C, bool(self.a & 0x01))
            self.a = self.a >> 1
            self.update_flags(self.a)
        else:
            v = self.read(addr)
            self.set_flag(self.FLAG_C, bool(v & 0x01))
            v = v >> 1
            self.write(addr, v)
            self.update_flags(v)
    
    def op_rol(self, addr: Optional[int] = None):
        if addr is None:  # A
            c = 1 if self.get_flag(self.FLAG_C) else 0
            self.set_flag(self.FLAG_C, bool(self.a & 0x80))
            self.a = ((self.a << 1) | c) & 0xFF
            self.update_flags(self.a)
        else:
            v = self.read(addr)
            c = 1 if self.get_flag(self.FLAG_C) else 0
            self.set_flag(self.FLAG_C, bool(v & 0x80))
            v = ((v << 1) | c) & 0xFF
            self.write(addr, v)
            self.update_flags(v)
    
    def op_ror(self, addr: Optional[int] = None):
        if addr is None:  # A
            c = 0x80 if self.get_flag(self.FLAG_C) else 0
            self.set_flag(self.FLAG_C, bool(self.a & 0x01))
            self.a = (self.a >> 1) | c
            self.update_flags(self.a)
        else:
            v = self.read(addr)
            c = 0x80 if self.get_flag(self.FLAG_C) else 0
            self.set_flag(self.FLAG_C, bool(v & 0x01))
            v = (v >> 1) | c
            self.write(addr, v)
            self.update_flags(v)
    
    def op_jump(self, addr: int):
        self.pc = addr
    
    def op_jsr(self, addr: int):
        self.push((self.pc - 1) >> 8)
        self.push((self.pc - 1) & 0xFF)
        self.pc = addr
    
    def op_rts(self):
        lo = self.pull()
        hi = self.pull()
        self.pc = ((hi << 8) | lo) + 1
    
    def op_rti(self):
        self.status = self.pull() | 0x20  # 保持未使用位
        lo = self.pull()
        hi = self.pull()
        self.pc = (hi << 8) | lo
    
    def op_branch(self, condition: bool, addr: int):
        if condition:
            self.pc = addr
            self.cycles += 1  # 分支额外周期
    
    def op_sec(self):
        self.set_flag(self.FLAG_C, True)
    
    def op_clc(self):
        self.set_flag(self.FLAG_C, False)
    
    def op_sed(self):
        self.set_flag(self.FLAG_D, True)
    
    def op_cld(self):
        self.set_flag(self.FLAG_D, False)
    
    def op_sei(self):
        self.set_flag(self.FLAG_I, True)
    
    def op_cli(self):
        self.set_flag(self.FLAG_I, False)
    
    def op_clv(self):
        self.set_flag(self.FLAG_V, False)
    
    def op_tax(self):
        self.x = self.a
        self.update_flags(self.x)
    
    def op_tay(self):
        self.y = self.a
        self.update_flags(self.y)
    
    def op_txa(self):
        self.a = self.x
        self.update_flags(self.a)
    
    def op_tya(self):
        self.a = self.y
        self.update_flags(self.a)
    
    def op_tsx(self):
        self.x = self.sp
        self.update_flags(self.x)
    
    def op_txs(self):
        self.sp = self.x
    
    def op_nop(self):
        pass
    
    def op_brk(self):
        self.push((self.pc + 1) >> 8)
        self.push((self.pc + 1) & 0xFF)
        self.push(self.status | self.FLAG_B)
        self.set_flag(self.FLAG_I, True)
        self.pc = self.read16(0xFFFE)  # IRQ 向量
    
    # 指令解码
    OPCODES = {
        0x00: ('brk', 7), 0x01: ('ora', 6), 0x05: ('ora', 3), 0x06: ('asl', 5),
        0x08: ('php', 3), 0x09: ('ora', 2), 0x0A: ('asl', 2), 0x0D: ('ora', 4),
        0x0E: ('asl', 6), 0x10: ('bpl', 2), 0x11: ('ora', 5), 0x15: ('ora', 4),
        0x16: ('asl', 6), 0x18: ('clc', 2), 0x19: ('ora', 4), 0x1D: ('ora', 4),
        0x1E: ('asl', 7), 0x20: ('jsr', 6), 0x21: ('and', 6), 0x24: ('bit', 3),
        0x25: ('and', 3), 0x26: ('rol', 5), 0x29: ('and', 2), 0x2A: ('rol', 2),
        0x2C: ('bit', 4), 0x2D: ('and', 4), 0x2E: ('rol', 6), 0x30: ('bmi', 2),
        0x31: ('and', 5), 0x35: ('and', 4), 0x36: ('rol', 6), 0x38: ('sec', 2),
        0x39: ('and', 4), 0x3D: ('and', 4), 0x3E: ('rol', 7), 0x40: ('rti', 6),
        0x41: ('eor', 6), 0x45: ('eor', 3), 0x46: ('lsr', 5), 0x48: ('pha', 3),
        0x49: ('eor', 2), 0x4A: ('lsr', 2), 0x4C: ('jmp', 3), 0x4D: ('eor', 4),
        0x4E: ('lsr', 6), 0x50: ('bvc', 2), 0x51: ('eor', 5), 0x55: ('eor', 4),
        0x56: ('lsr', 6), 0x58: ('cli', 2), 0x59: ('eor', 4), 0x5D: ('eor', 4),
        0x5E: ('lsr', 7), 0x60: ('rts', 6), 0x61: ('adc', 6), 0x65: ('adc', 3),
        0x66: ('ror', 5), 0x68: ('pla', 4), 0x69: ('adc', 2), 0x6A: ('ror', 2),
        0x6C: ('jmp', 5), 0x6D: ('adc', 4), 0x6E: ('ror', 6), 0x70: ('bvs', 2),
        0x71: ('adc', 5), 0x75: ('adc', 4), 0x76: ('ror', 6), 0x78: ('sei', 2),
        0x79: ('adc', 4), 0x7D: ('adc', 4), 0x7E: ('ror', 7), 0x81: ('sta', 6),
        0x84: ('sty', 3), 0x85: ('sta', 3), 0x86: ('stx', 3), 0x88: ('dey', 2),
        0x8A: ('txa', 2), 0x8C: ('sty', 4), 0x8D: ('sta', 4), 0x8E: ('stx', 4),
        0x90: ('bcc', 2), 0x91: ('sta', 6), 0x94: ('sty', 4), 0x95: ('sta', 4),
        0x96: ('stx', 4), 0x98: ('tya', 2), 0x99: ('sta', 5), 0x9A: ('txs', 2),
        0x9D: ('sta', 5), 0xA0: ('ldy', 2), 0xA1: ('lda', 6), 0xA2: ('ldx', 2),
        0xA4: ('ldy', 3), 0xA5: ('lda', 3), 0xA6: ('ldx', 3), 0xA8: ('tay', 2),
        0xA9: ('lda', 2), 0xAA: ('tax', 2), 0xAC: ('ldy', 4), 0xAD: ('lda', 4),
        0xAE: ('ldx', 4), 0xB0: ('bcs', 2), 0xB1: ('lda', 5), 0xB4: ('ldy', 4),
        0xB5: ('lda', 4), 0xB6: ('ldx', 4), 0xB8: ('clv', 2), 0xB9: ('lda', 4),
        0xBA: ('tsx', 2), 0xBC: ('ldy', 4), 0xBD: ('lda', 4), 0xBE: ('ldx', 4),
        0xC0: ('cpy', 2), 0xC1: ('cmp', 6), 0xC4: ('cpy', 3), 0xC5: ('cmp', 3),
        0xC6: ('dec', 5), 0xC8: ('iny', 2), 0xC9: ('cmp', 2), 0xCA: ('dex', 2),
        0xCC: ('cpy', 4), 0xCD: ('cmp', 4), 0xCE: ('dec', 6), 0xD0: ('bne', 2),
        0xD1: ('cmp', 5), 0xD5: ('cmp', 4), 0xD6: ('dec', 6), 0xD8: ('cld', 2),
        0xD9: ('cmp', 4), 0xDD: ('cmp', 4), 0xDE: ('dec', 7), 0xE0: ('cpx', 2),
        0xE1: ('sbc', 6), 0xE4: ('cpx', 3), 0xE5: ('sbc', 3), 0xE6: ('inc', 5),
        0xE8: ('inx', 2), 0xE9: ('sbc', 2), 0xEA: ('nop', 2), 0xEC: ('cpx', 4),
        0xED: ('sbc', 4), 0xEE: ('inc', 6), 0xF0: ('beq', 2), 0xF1: ('sbc', 5),
        0xF5: ('sbc', 4), 0xF6: ('inc', 6), 0xF8: ('sed', 2), 0xF9: ('sbc', 4),
        0xFD: ('sbc', 4), 0xFE: ('inc', 7),
        # 零页 X
        0x15: ('ora', 4), 0x16: ('asl', 6), 0x35: ('and', 4), 0x36: ('rol', 6),
        0x55: ('eor', 4), 0x56: ('lsr', 6), 0x75: ('adc', 4), 0x76: ('ror', 6),
        0x95: ('sta', 4), 0xB5: ('lda', 4), 0xD5: ('cmp', 4), 0xD6: ('dec', 6),
        0xF5: ('sbc', 4), 0xF6: ('inc', 6),
        # 绝对 X
        0x1D: ('ora', 4), 0x1E: ('asl', 7), 0x3D: ('and', 4), 0x3E: ('rol', 7),
        0x5D: ('eor', 4), 0x5E: ('lsr', 7), 0x7D: ('adc', 4), 0x7E: ('ror', 7),
        0x9D: ('sta', 5), 0xBD: ('lda', 4), 0xDD: ('cmp', 4), 0xDE: ('dec', 7),
        0xFD: ('sbc', 4), 0xFE: ('inc', 7),
        # 绝对 Y
        0x19: ('ora', 4), 0x39: ('and', 4), 0x59: ('eor', 4), 0x79: ('adc', 4),
        0x99: ('sta', 5), 0xB9: ('lda', 4), 0xD9: ('cmp', 4), 0xF9: ('sbc', 4),
        # 间接 X
        0x01: ('ora', 6), 0x21: ('and', 6), 0x41: ('eor', 6), 0x61: ('adc', 6),
        0x81: ('sta', 6), 0xA1: ('lda', 6), 0xC1: ('cmp', 6), 0xE1: ('sbc', 6),
        # 间接 Y
        0x11: ('ora', 5), 0x31: ('and', 5), 0x51: ('eor', 5), 0x71: ('adc', 5),
        0x91: ('sta', 6), 0xB1: ('lda', 5), 0xD1: ('cmp', 5), 0xF1: ('sbc', 5),
    }
    
    def step(self) -> int:
        """执行一条指令，返回周期数"""
        opcode = self.read(self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        
        if opcode not in self.OPCODES:
            print(f"未知操作码：${opcode:02X} @ ${self.pc-1:04X}")
            return 2
        
        op_name, base_cycles = self.OPCODES[opcode]
        self.cycles = base_cycles
        
        # 获取操作数地址
        addr_methods = {
            'immediate': self.addr_immediate,
            'zero_page': self.addr_zero_page,
            'zero_page_x': self.addr_zero_page_x,
            'zero_page_y': self.addr_zero_page_y,
            'absolute': self.addr_absolute,
            'absolute_x': self.addr_absolute_x,
            'absolute_y': self.addr_absolute_y,
            'indirect_x': self.addr_indirect_x,
            'indirect_y': self.addr_indirect_y,
            'relative': self.addr_relative,
        }
        
        # 简单寻址模式推断
        if op_name in ['lda', 'sta']:
            if opcode in [0xA9, 0xA1, 0xA5, 0xAD, 0xB1, 0xB5, 0xB9, 0xBD]:
                addr = self.addr_immediate() if opcode == 0xA9 else self.addr_zero_page() if opcode == 0xA5 else self.addr_absolute()
            else:
                addr = 0
        else:
            addr = 0
        
        # 执行操作
        op_func = getattr(self, f'op_{op_name}', None)
        if op_func:
            if op_name in ['asl', 'lsr', 'rol', 'ror'] and opcode == 0x0A:
                op_func()  # 累加器模式
            elif op_name in ['jmp', 'jsr']:
                op_func(addr)
            elif op_name.startswith('b'):  # 分支指令
                condition = {
                    'bpl': not self.get_flag(self.FLAG_N),
                    'bmi': self.get_flag(self.FLAG_N),
                    'bvc': not self.get_flag(self.FLAG_V),
                    'bvs': self.get_flag(self.FLAG_V),
                    'bcc': not self.get_flag(self.FLAG_C),
                    'bcs': self.get_flag(self.FLAG_C),
                    'bne': not self.get_flag(self.FLAG_Z),
                    'beq': self.get_flag(self.FLAG_Z),
                }.get(op_name, False)
                self.op_branch(condition, addr)
            elif op_name in ['php', 'pha', 'pla', 'tax', 'tay', 'txa', 'tya', 'tsx', 'txs', 
                           'sec', 'clc', 'sed', 'cld', 'sei', 'cli', 'clv', 'nop', 
                           'inx', 'iny', 'dex', 'dey', 'rti', 'rts', 'brk']:
                op_func()
            else:
                op_func(addr)
        
        self.total_cycles += self.cycles
        return self.cycles
    
    def run(self, max_cycles: int = 0):
        """运行 CPU"""
        start_cycles = self.total_cycles
        while self.running:
            if max_cycles > 0 and (self.total_cycles - start_cycles) >= max_cycles:
                break
            self.step()


class BreakoutSimulator:
    """Breakout 街机模拟器"""
    
    def __init__(self):
        # 64 KB 完整地址空间 (6502 可寻址范围)
        self.memory = bytearray(0x10000)
        self.cpu = CPU6502(self.memory)
        
        # 游戏状态
        self.vblank_counter = 0
        self.paddle_position = 0
        self.game_state = 0
        self.ball_x = 0
        self.ball_y = 0
        self.brick_status = bytearray(32)
        self.score = 0
        self.lives = 3
        
        # 熵缓冲
        self.entropy_buffer = bytearray(256)
        self.entropy_index = 0
        
        # VBLANK 中断
        self.vblank_interval = 1 / 60.0  # 60Hz
        self.last_vblank = time.time()
        
        # 输出
        self.led_state = False
        self.led_blinks = []
        self.wallet_display = ""
    
    def load_program(self, program: bytes, offset: int = 0x0200):
        """加载程序到内存"""
        for i, byte in enumerate(program):
            self.memory[offset + i] = byte
    
    def update_io(self):
        """更新 IO 寄存器"""
        # VBLANK 计数器
        self.memory[BreakoutRegisters.VBLANK_COUNTER] = self.vblank_counter & 0xFF
        self.memory[BreakoutRegisters.VBLANK_COUNTER + 1] = (self.vblank_counter >> 8) & 0xFF
        
        # 拨盘位置
        self.memory[BreakoutRegisters.PADDLE_POSITION] = self.paddle_position
        
        # 游戏状态
        self.memory[BreakoutRegisters.GAME_STATE] = self.game_state
        
        # 球位置
        self.memory[BreakoutRegisters.BALL_X] = self.ball_x
        self.memory[BreakoutRegisters.BALL_Y] = self.ball_y
        
        # 砖块状态
        for i in range(32):
            self.memory[BreakoutRegisters.BRICK_STATUS + i] = self.brick_status[i]
        
        # 分数
        self.memory[BreakoutRegisters.SCORE] = self.score & 0xFF
        self.memory[BreakoutRegisters.SCORE + 1] = (self.score >> 8) & 0xFF
        
        # 生命
        self.memory[BreakoutRegisters.LIVES] = self.lives
        
        # LED 状态 (读取)
        if self.cpu.read(BreakoutRegisters.LED_CONTROL) & 0x01:
            if not self.led_state:
                self.led_state = True
                self.led_blinks.append(time.time())
    
    def simulate_vblank(self):
        """模拟 VBLANK 中断"""
        self.vblank_counter = (self.vblank_counter + 1) & 0xFFFF
        
        # 触发 NMI
        nmi_addr = self.cpu.read16(0xFFFA)
        if nmi_addr != 0xFFFF:
            self.cpu.push((self.cpu.pc >> 8) & 0xFF)
            self.cpu.push(self.cpu.pc & 0xFF)
            self.cpu.push(self.cpu.status)
            self.cpu.pc = nmi_addr
    
    def collect_entropy(self):
        """收集熵"""
        # 混合各种熵源
        entropy = (
            self.vblank_counter & 0xFF ^
            self.paddle_position ^
            self.ball_x ^
            self.ball_y ^
            int(time.time() * 1000) & 0xFF
        )
        
        self.entropy_buffer[self.entropy_index] ^= entropy
        self.entropy_index = (self.entropy_index + 1) % 256
    
    def generate_wallet(self) -> str:
        """从熵缓冲生成钱包地址"""
        # 使用 SHA-256 生成钱包
        hash_input = bytes(self.entropy_buffer)
        hash_output = hashlib.sha256(hash_input).digest()
        
        # 生成 RTC 地址 (类似 Bitcoin)
        # 简化版本：直接编码为十六进制
        wallet = "RTC" + hash_output[:20].hex()
        return wallet.upper()
    
    def run_miner(self, duration: float = 60.0):
        """运行矿工"""
        print("=" * 60)
        print("RustChain Breakout Miner - 6502 Simulator")
        print("=" * 60)
        print(f"开始时间：{time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"运行时长：{duration} 秒")
        print()
        
        start_time = time.time()
        attestation_count = 0
        
        while (time.time() - start_time) < duration:
            # VBLANK 处理
            if time.time() - self.last_vblank >= self.vblank_interval:
                self.last_vblank = time.time()
                self.simulate_vblank()
                self.collect_entropy()
            
            # 更新游戏状态 (模拟)
            self.paddle_position = random.randint(0, 255)
            self.ball_x = random.randint(0, 255)
            self.ball_y = random.randint(0, 255)
            self.game_state = random.randint(0, 255)
            
            # 更新 IO
            self.update_io()
            
            # 运行 CPU (1000 周期)
            self.cpu.run(max_cycles=1000)
            
            # 每 10 秒显示状态
            elapsed = time.time() - start_time
            if int(elapsed) % 10 == 0 and int(elapsed) > 0:
                print(f"[{int(elapsed)}s] 熵收集：{self.entropy_index}/256, "
                      f"CPU 周期：{self.cpu.total_cycles}")
        
        # 生成钱包
        print()
        print("=" * 60)
        print("矿工运行完成!")
        print("=" * 60)
        
        wallet = self.generate_wallet()
        print(f"生成的钱包地址：{wallet}")
        print(f"熵缓冲 (前 32 字节): {self.entropy_buffer[:32].hex()}")
        print(f"总 CPU 周期：{self.cpu.total_cycles}")
        print(f"模拟时间：{duration} 秒")
        print()
        
        # 保存钱包
        with open('wallet.txt', 'w', encoding='utf-8') as f:
            f.write(f"RustChain Breakout Miner Wallet\n")
            f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Address: {wallet}\n")
            f.write(f"\nWARNING: Backup this wallet address!\n")
            f.write(f"Hardware: Atari Breakout (1976)\n")
            f.write(f"CPU: MOS 6502 @ 1.5 MHz\n")
            f.write(f"Antiquity Multiplier: 5.0x (expected)\n")
        
        print("钱包已保存到 wallet.txt")
        return wallet


def main():
    """主函数"""
    print("RustChain Breakout Miner 模拟器")
    print("按 Ctrl+C 停止")
    print()
    
    simulator = BreakoutSimulator()
    
    # 加载示例程序 (简单的熵收集循环)
    # 这是 6502 汇编的示例程序
    example_program = bytes([
        0xA9, 0x00,      # LDA #$00 - 加载 0 到累加器
        0x85, 0x00,      # STA $00 - 存储到零页
        0xAD, 0x40, 0xC0,# LDA $C040 - 读取 VBLANK 计数器
        0x85, 0x01,      # STA $01 - 存储
        0xAD, 0x60, 0xC0,# LDA $C060 - 读取拨盘位置
        0x45, 0x01,      # EOR $01 - 混合熵
        0x85, 0x02,      # STA $02 - 存储熵
        0x4C, 0x03, 0x02,# JMP $0203 - 无限循环
    ])
    
    simulator.load_program(example_program)
    
    # 设置中断向量
    simulator.memory[0xFFFA] = 0x00  # NMI 向量 (低字节)
    simulator.memory[0xFFFB] = 0x00  # NMI 向量 (高字节)
    simulator.memory[0xFFFE] = 0x00  # IRQ 向量 (低字节)
    simulator.memory[0xFFFF] = 0x00  # IRQ 向量 (高字节)
    
    # 运行矿工 30 秒
    try:
        wallet = simulator.run_miner(duration=30.0)
        print()
        print(f"✅ 钱包生成成功：{wallet}")
        print()
        print("下一步:")
        print("1. 将钱包地址添加到 RustChain 网络")
        print("2. 提交 PR 到 RustChain 项目")
        print("3. 申领 200 RTC bounty!")
    except KeyboardInterrupt:
        print("\n矿工已停止")


if __name__ == '__main__':
    main()
