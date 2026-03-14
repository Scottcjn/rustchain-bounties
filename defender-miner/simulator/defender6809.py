#!/usr/bin/env python3
"""
Defender 街机 (1981) - Motorola 6809 CPU 模拟器
用于 RustChain 矿工移植开发和测试

硬件规格:
- CPU: Motorola 6809 @ 1 MHz
- RAM: 8-16 KB
- ROM: 24-48 KB
- 显示：300x256 @ 60Hz
"""

import sys
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass, field
from enum import IntEnum, auto


# ============================================================================
# 6809 CPU 寄存器
# ============================================================================

@dataclass
class Registers:
    """Motorola 6809 寄存器组"""
    # 8 位累加器
    A: int = 0x00
    B: int = 0x00
    
    # 16 位寄存器 (D = A:B)
    @property
    def D(self) -> int:
        return ((self.A & 0xFF) << 8) | (self.B & 0xFF)
    
    @D.setter
    def D(self, value: int):
        self.A = (value >> 8) & 0xFF
        self.B = value & 0xFF
    
    # 16 位索引寄存器
    X: int = 0x0000
    Y: int = 0x0000
    
    # 16 位栈指针
    S: int = 0x0000  # 系统栈
    U: int = 0x0000  # 用户栈
    
    # 16 位程序计数器
    PC: int = 0x0000
    
    # 8 位直接页寄存器
    DP: int = 0x00
    
    # 8 位条件码寄存器
    CC: int = 0x00
    
    # 条件码标志位
    FLAG_C = 0x01  # 进位
    FLAG_V = 0x02  # 溢出
    FLAG_Z = 0x04  # 零
    FLAG_N = 0x08  # 负
    FLAG_I = 0x10  # 中断屏蔽
    FLAG_H = 0x20  # 半进位
    FLAG_F = 0x40  # 整个中断屏蔽
    FLAG_E = 0x80  # 整个中断
    
    def set_flag(self, flag: int, value: bool):
        if value:
            self.CC |= flag
        else:
            self.CC &= ~flag
    
    def get_flag(self, flag: int) -> bool:
        return bool(self.CC & flag)
    
    def set_nz(self, value: int, bits: int = 8):
        """设置 N 和 Z 标志"""
        mask = (1 << bits) - 1
        result = value & mask
        self.set_flag(self.FLAG_Z, result == 0)
        self.set_flag(self.FLAG_N, bool(result & (1 << (bits - 1))))
    
    def __repr__(self):
        return (f"CPU: A={self.A:02X} B={self.B:02X} X={self.X:04X} "
                f"Y={self.Y:04X} S={self.S:04X} U={self.U:04X} "
                f"PC={self.PC:04X} DP={self.DP:02X} CC={self.CC:02X}")


# ============================================================================
# 内存映射
# ============================================================================

class MemoryMap:
    """Defender 街机内存映射"""
    
    # ROM 区域
    ROM_START = 0x0000
    ROM_END = 0xBFFF  # 48 KB ROM
    
    # RAM 区域
    RAM_START = 0xC000
    RAM_END = 0xCFFF  # 4 KB RAM
    
    # 视频 RAM
    VRAM_START = 0xD000
    VRAM_END = 0xD7FF  # 2 KB 视频 RAM
    
    # I/O 区域
    IO_START = 0xE000
    IO_END = 0xFFFF  # 8 KB I/O
    
    def __init__(self, ram_size: int = 0x1000, rom_size: int = 0xC000):
        self.ram = bytearray(ram_size)
        self.rom = bytearray(rom_size)
        self.vram = bytearray(0x800)  # 2 KB VRAM
        self.io = bytearray(0x2000)  # 8 KB I/O
        
    def read_byte(self, addr: int) -> int:
        """读取一个字节"""
        addr &= 0xFFFF
        if self.ROM_START <= addr <= self.ROM_END:
            return self.rom[addr - self.ROM_START]
        elif self.RAM_START <= addr <= self.RAM_END:
            return self.ram[addr - self.RAM_START]
        elif self.VRAM_START <= addr <= self.VRAM_END:
            return self.vram[addr - self.VRAM_START]
        elif self.IO_START <= addr <= self.IO_END:
            return self.io[addr - self.IO_START]
        else:
            return 0x00
    
    def write_byte(self, addr: int, value: int):
        """写入一个字节"""
        addr &= 0xFFFF
        value &= 0xFF
        if self.RAM_START <= addr <= self.RAM_END:
            self.ram[addr - self.RAM_START] = value
        elif self.VRAM_START <= addr <= self.VRAM_END:
            self.vram[addr - self.VRAM_START] = value
        elif self.IO_START <= addr <= self.IO_END:
            self.io[addr - self.IO_START] = value
        # ROM 区域不可写
    
    def read_word(self, addr: int) -> int:
        """读取一个字 (16 位)"""
        hi = self.read_byte(addr)
        lo = self.read_byte(addr + 1)
        return (hi << 8) | lo
    
    def write_word(self, addr: int, value: int):
        """写入一个字 (16 位)"""
        self.write_byte(addr, (value >> 8) & 0xFF)
        self.write_byte(addr + 1, value & 0xFF)
    
    def load_rom(self, data: bytes, offset: int = 0):
        """加载 ROM 数据"""
        for i, byte in enumerate(data):
            if offset + i < len(self.rom):
                self.rom[offset + i] = byte
    
    def load_program(self, program: List[int], offset: int = 0):
        """加载程序到 RAM"""
        for i, byte in enumerate(program):
            addr = self.RAM_START + offset + i
            if addr <= self.RAM_END:
                self.write_byte(addr, byte)


# ============================================================================
# 6809 CPU 模拟器
# ============================================================================

class Motorola6809:
    """Motorola 6809 CPU 模拟器"""
    
    def __init__(self, memory: MemoryMap):
        self.regs = Registers()
        self.mem = memory
        self.running = False
        self.cycle_count = 0
        
        # 操作码表 (部分实现)
        self.opcodes = {
            0x00: self._neg_direct,      # NEG
            0x01: self._nop,             # NOP (实际是 OIM)
            0x06: self._nop,             # AIM
            0x0A: self._nop,             # OIM
            0x0C: self._nop,             # EIM
            0x0E: self._nop,             # TIM
            0x10: self._prefix_10,       # 16-bit 操作码前缀
            0x11: self._prefix_11,       # 8-bit 操作码前缀
            0x12: self._nop,             # SYNC
            0x13: self._nop,             # SEXW
            0x19: self._abx,             # ABX
            0x1F: self._nop,             # EXG
            0x30: self._leax,            # LEAX
            0x31: self._leay,            # LEAY
            0x32: self._leas,            # LEAS
            0x33: self._leau,            # LEAU
            0x34: self._pshs,            # PSHS
            0x35: self._puls,            # PULS
            0x36: self._pshu,            # PSHU
            0x37: self._pulu,            # PULU
            0x39: self._rts,             # RTS
            0x3A: self._abx,             # ABX (重复)
            0x3C: self._andcc,           # ANDCC
            0x3D: self._mul,             # MUL
            0x3E: self._nop,             # SWI
            0x3F: self._swi2,            # SWI2
            0x40: self._nega,            # NEGA
            0x43: self._coma,            # COMA
            0x44: self._lsra,            # LSRA
            0x46: self._rora,            # RORA
            0x47: self._asra,            # ASRA
            0x48: self._asla,            # ASLA
            0x49: self._rola,            # ROLA
            0x4A: self._deca,            # DECA
            0x4C: self._coma,            # COMA (重复)
            0x4E: self._lsra,            # LSRA (重复)
            0x50: self._negb,            # NEGB
            0x53: self._comb,            # COMB
            0x54: self._lsrb,            # LSRB
            0x56: self._rorb,            # RORB
            0x57: self._asrb,            # ASRB
            0x58: self._aslb,            # ASLB
            0x59: self._rolb,            # ROLB
            0x5A: self._decb,            # DECB
            0x5C: self._comb,            # COMB (重复)
            0x5E: self._lsrb,            # LSRB (重复)
            0x80: self._suba_imm,        # SUBA #imm
            0x81: self._cmpa_imm,        # CMPA #imm
            0x82: self._sbca_imm,        # SBCA #imm
            0x83: self._subd_imm,        # SUBD #imm
            0x84: self._anda_imm,        # ANDA #imm
            0x85: self._bita_imm,        # BITA #imm
            0x86: self._lda_imm,         # LDA #imm
            0x87: self._sta_imm,         # STA #imm (实际不存在)
            0x88: self._eora_imm,        # EORA #imm
            0x89: self._adca_imm,        # ADCA #imm
            0x8A: self._ora_imm,         # ORA #imm
            0x8B: self._adda_imm,        # ADDA #imm
            0x8C: self._cmpx_imm,        # CMPX #imm
            0x8D: self._bsr,             # BSR
            0x8E: self._ldx_imm,         # LDX #imm
            0x93: self._subd_dir,        # SUBD direct
            0x96: self._lda_dir,         # LDA direct
            0x97: self._sta_dir,         # STA direct
            0x9C: self._cmpx_dir,        # CMPX direct
            0x9E: self._ldx_dir,         # LDX direct
            0x9F: self._stx_dir,         # STX direct
            0xA6: self._lda_idx,         # LDA indexed
            0xA7: self._sta_idx,         # STA indexed
            0xAE: self._ldx_idx,         # LDX indexed
            0xAF: self._stx_idx,         # STX indexed
            0xC6: self._ldb_imm,         # LDB #imm
            0xC7: self._stb_imm,         # STB #imm (实际不存在)
            0xCC: self._ldd_imm,         # LDD #imm
            0xCD: self._ldd_imm,         # LDD #imm (重复)
            0xCE: self._ldu_imm,         # LDU #imm
            0xCF: self._lds_imm,         # LDS #imm
            0xD6: self._ldb_dir,         # LDB direct
            0xD7: self._stb_dir,         # STB direct
            0xDC: self._ldd_dir,         # LDD direct
            0xDD: self._std_dir,         # STD direct
            0xDE: self._ldu_dir,         # LDU direct
            0xDF: self._stu_dir,         # STU direct
            0xE6: self._ldb_idx,         # LDB indexed
            0xE7: self._stb_idx,         # STB indexed
            0xEC: self._ldd_idx,         # LDD indexed
            0xED: self._std_idx,         # STD indexed
            0xEE: self._ldu_idx,         # LDU indexed
            0xEF: self._stu_idx,         # STU indexed
            0x0C: self._nop,             # NOP
            0x12: self._nop,             # NOP
            0x13: self._nop,             # NOP
        }
    
    # -------------------------------------------------------------------------
    # 基础操作
    # -------------------------------------------------------------------------
    
    def _fetch_byte(self) -> int:
        """取一个字节"""
        byte = self.mem.read_byte(self.regs.PC)
        self.regs.PC = (self.regs.PC + 1) & 0xFFFF
        self.cycle_count += 1
        return byte
    
    def _fetch_word(self) -> int:
        """取一个字"""
        word = self.mem.read_word(self.regs.PC)
        self.regs.PC = (self.regs.PC + 2) & 0xFFFF
        self.cycle_count += 2
        return word
    
    def _push_s(self, value: int, size: int = 8):
        """压入系统栈"""
        if size == 16:
            self.regs.S = (self.regs.S - 2) & 0xFFFF
            self.mem.write_word(self.regs.S, value)
        else:
            self.regs.S = (self.regs.S - 1) & 0xFFFF
            self.mem.write_byte(self.regs.S, value & 0xFF)
    
    def _pull_s(self, size: int = 8) -> int:
        """从系统栈弹出"""
        if size == 16:
            value = self.mem.read_word(self.regs.S)
            self.regs.S = (self.regs.S + 2) & 0xFFFF
            return value
        else:
            value = self.mem.read_byte(self.regs.S)
            self.regs.S = (self.regs.S + 1) & 0xFFFF
            return value
    
    # -------------------------------------------------------------------------
    # 指令实现 (部分)
    # -------------------------------------------------------------------------
    
    def _nop(self):
        """空操作"""
        self.cycle_count += 1
    
    def _neg_direct(self):
        """NEG direct: 取反 (简化实现)"""
        addr = self._fetch_byte()
        if self.regs.DP != 0:
            addr = (self.regs.DP << 8) | addr
        value = self.mem.read_byte(addr)
        result = (-value) & 0xFF
        self.mem.write_byte(addr, result)
        self.regs.set_nz(result)
        self.cycle_count += 5
    
    def _sta_imm(self):
        """STA #imm: 不存在，作为 NOP 处理"""
        self._fetch_byte()
        self.cycle_count += 1
    
    def _stb_imm(self):
        """STB #imm: 不存在，作为 NOP 处理"""
        self._fetch_byte()
        self.cycle_count += 1
    
    def _pshu(self):
        """PSHU: 压入用户栈 (简化为 PSHS)"""
        self._pshs()
    
    def _pulu(self):
        """PULU: 从用户栈弹出 (简化为 PULS)"""
        self._puls()
    
    def _cmpx_dir(self):
        """CMPX direct: 比较 X 与直接页地址的值"""
        addr = self._fetch_byte()
        if self.regs.DP != 0:
            addr = (self.regs.DP << 8) | addr
        value = self.mem.read_word(addr)
        result = self.regs.X - value
        self.regs.set_flag(self.regs.FLAG_C, result < 0)
        self.regs.set_nz(result & 0xFFFF, bits=16)
        self.cycle_count += 5
    
    def _ldx_dir(self):
        """LDX direct: 从直接页加载到 X"""
        addr = self._fetch_byte()
        if self.regs.DP != 0:
            addr = (self.regs.DP << 8) | addr
        self.regs.X = self.mem.read_word(addr)
        self.regs.set_nz(self.regs.X, bits=16)
        self.cycle_count += 4
    
    def _stx_dir(self):
        """STX direct: 存储 X 到直接页"""
        addr = self._fetch_byte()
        if self.regs.DP != 0:
            addr = (self.regs.DP << 8) | addr
        self.mem.write_word(addr, self.regs.X)
        self.cycle_count += 4
    
    def _lda_idx(self):
        """LDA indexed: 从变址加载到 A"""
        self.regs.A = self.mem.read_byte(self.regs.X)
        self.regs.set_nz(self.regs.A)
        self.regs.X = (self.regs.X + 1) & 0xFFFF
        self.cycle_count += 3
    
    def _sta_idx(self):
        """STA indexed: 存储 A 到变址"""
        self.mem.write_byte(self.regs.X, self.regs.A)
        self.regs.X = (self.regs.X + 1) & 0xFFFF
        self.cycle_count += 3
    
    def _ldx_idx(self):
        """LDX indexed: 从变址加载到 X"""
        self.regs.X = self.mem.read_word(self.regs.X)
        self.regs.set_nz(self.regs.X, bits=16)
        self.cycle_count += 4
    
    def _stx_idx(self):
        """STX indexed: 存储 X 到变址"""
        self.mem.write_word(self.regs.X, self.regs.X)
        self.cycle_count += 4
    
    def _ldb_idx(self):
        """LDB indexed: 从变址加载到 B"""
        self.regs.B = self.mem.read_byte(self.regs.X)
        self.regs.set_nz(self.regs.B)
        self.regs.X = (self.regs.X + 1) & 0xFFFF
        self.cycle_count += 3
    
    def _stb_idx(self):
        """STB indexed: 存储 B 到变址"""
        self.mem.write_byte(self.regs.X, self.regs.B)
        self.regs.X = (self.regs.X + 1) & 0xFFFF
        self.cycle_count += 3
    
    def _ldd_idx(self):
        """LDD indexed: 从变址加载到 D"""
        self.regs.D = self.mem.read_word(self.regs.X)
        self.regs.set_nz(self.regs.D, bits=16)
        self.regs.X = (self.regs.X + 2) & 0xFFFF
        self.cycle_count += 4
    
    def _std_idx(self):
        """STD indexed: 存储 D 到变址"""
        self.mem.write_word(self.regs.X, self.regs.D)
        self.regs.X = (self.regs.X + 2) & 0xFFFF
        self.cycle_count += 4
    
    def _ldu_idx(self):
        """LDU indexed: 从变址加载到 U"""
        self.regs.U = self.mem.read_word(self.regs.X)
        self.regs.set_nz(self.regs.U, bits=16)
        self.regs.X = (self.regs.X + 2) & 0xFFFF
        self.cycle_count += 4
    
    def _stu_idx(self):
        """STU indexed: 存储 U 到变址"""
        self.mem.write_word(self.regs.X, self.regs.U)
        self.regs.X = (self.regs.X + 2) & 0xFFFF
        self.cycle_count += 4
    
    def _ldu_dir(self):
        """LDU direct: 从直接页加载到 U"""
        addr = self._fetch_byte()
        if self.regs.DP != 0:
            addr = (self.regs.DP << 8) | addr
        self.regs.U = self.mem.read_word(addr)
        self.regs.set_nz(self.regs.U, bits=16)
        self.cycle_count += 4
    
    def _stu_dir(self):
        """STU direct: 存储 U 到直接页"""
        addr = self._fetch_byte()
        if self.regs.DP != 0:
            addr = (self.regs.DP << 8) | addr
        self.mem.write_word(addr, self.regs.U)
        self.cycle_count += 4
    
    def _lds_imm(self):
        """LDS #imm: 加载立即数到 S"""
        self.regs.S = self._fetch_word()
        self.regs.set_nz(self.regs.S, bits=16)
        self.cycle_count += 3
    
    def _mul(self):
        """MUL: D = A × B (硬件乘法!)"""
        result = self.regs.A * self.regs.B
        self.regs.D = result
        self.regs.set_flag(self.regs.FLAG_C, bool(result & 0x80))
        self.regs.set_nz(result, bits=16)
        self.cycle_count += 10
    
    def _abx(self):
        """ABX: X = X + B"""
        self.regs.X = (self.regs.X + self.regs.B) & 0xFFFF
        self.cycle_count += 1
    
    def _rts(self):
        """RTS: 从子程序返回"""
        self.regs.PC = self._pull_s(16)
        self.cycle_count += 3
    
    def _pshs(self):
        """PSHS: 压入系统栈"""
        reg_mask = self._fetch_byte()
        if reg_mask & 0x80:  # PC
            self._push_s(self.regs.PC, 16)
        if reg_mask & 0x40:  # U
            self._push_s(self.regs.U, 16)
        if reg_mask & 0x20:  # Y
            self._push_s(self.regs.Y, 16)
        if reg_mask & 0x10:  # X
            self._push_s(self.regs.X, 16)
        if reg_mask & 0x08:  # DP
            self._push_s(self.regs.DP, 8)
        if reg_mask & 0x04:  # B
            self._push_s(self.regs.B, 8)
        if reg_mask & 0x02:  # A
            self._push_s(self.regs.A, 8)
        if reg_mask & 0x01:  # CC
            self._push_s(self.regs.CC, 8)
        self.cycle_count += 5
    
    def _puls(self):
        """PULS: 从系统栈弹出"""
        reg_mask = self._fetch_byte()
        if reg_mask & 0x01:  # CC
            self.regs.CC = self._pull_s(8)
        if reg_mask & 0x02:  # A
            self.regs.A = self._pull_s(8)
        if reg_mask & 0x04:  # B
            self.regs.B = self._pull_s(8)
        if reg_mask & 0x08:  # DP
            self.regs.DP = self._pull_s(8)
        if reg_mask & 0x10:  # X
            self.regs.X = self._pull_s(16)
        if reg_mask & 0x20:  # Y
            self.regs.Y = self._pull_s(16)
        if reg_mask & 0x40:  # U
            self.regs.U = self._pull_s(16)
        if reg_mask & 0x80:  # PC
            self.regs.PC = self._pull_s(16)
        self.cycle_count += 5
    
    def _leax(self):
        """LEAX: 加载有效地址到 X"""
        eff_addr = self._get_effective_address()
        self.regs.X = eff_addr
        self.regs.set_flag(self.regs.FLAG_Z, eff_addr == 0)
        self.cycle_count += 4
    
    def _leay(self):
        """LEAY: 加载有效地址到 Y"""
        eff_addr = self._get_effective_address()
        self.regs.Y = eff_addr
        self.regs.set_flag(self.regs.FLAG_Z, eff_addr == 0)
        self.cycle_count += 4
    
    def _leas(self):
        """LEAS: 加载有效地址到 S"""
        self.regs.S = self._get_effective_address()
        self.cycle_count += 4
    
    def _leau(self):
        """LEAU: 加载有效地址到 U"""
        self.regs.U = self._get_effective_address()
        self.cycle_count += 4
    
    def _get_effective_address(self) -> int:
        """计算有效地址 (简化版)"""
        post_byte = self._fetch_byte()
        
        # 5 位寄存器字段
        reg = (post_byte >> 5) & 0x07
        
        # 获取基址寄存器
        if reg == 0:
            base = self.regs.X
        elif reg == 1:
            base = self.regs.Y
        elif reg == 2:
            base = self.regs.U
        elif reg == 3:
            base = self.regs.S
        else:
            base = 0
        
        # 5 位偏移字段
        offset_bits = post_byte & 0x1F
        
        if offset_bits == 0:
            # 无偏移
            return base
        elif offset_bits <= 0x0F:
            # 4 位正偏移
            return (base + offset_bits) & 0xFFFF
        else:
            # 需要额外字节
            offset = self._fetch_byte()
            if offset_bits == 0x1F:
                # 16 位偏移
                offset = self._fetch_byte() << 8 | self._fetch_byte()
            return (base + offset) & 0xFFFF
    
    # -------------------------------------------------------------------------
    # 立即数指令
    # -------------------------------------------------------------------------
    
    def _lda_imm(self):
        """LDA #imm: 加载立即数到 A"""
        self.regs.A = self._fetch_byte()
        self.regs.set_nz(self.regs.A)
        self.cycle_count += 2
    
    def _ldb_imm(self):
        """LDB #imm: 加载立即数到 B"""
        self.regs.B = self._fetch_byte()
        self.regs.set_nz(self.regs.B)
        self.cycle_count += 2
    
    def _ldd_imm(self):
        """LDD #imm: 加载立即数到 D"""
        self.regs.D = self._fetch_word()
        self.regs.set_nz(self.regs.D, bits=16)
        self.cycle_count += 3
    
    def _ldx_imm(self):
        """LDX #imm: 加载立即数到 X"""
        self.regs.X = self._fetch_word()
        self.regs.set_nz(self.regs.X, bits=16)
        self.cycle_count += 3
    
    def _ldu_imm(self):
        """LDU #imm: 加载立即数到 U"""
        self.regs.U = self._fetch_word()
        self.regs.set_nz(self.regs.U, bits=16)
        self.cycle_count += 3
    
    def _suba_imm(self):
        """SUBA #imm: A = A - imm"""
        imm = self._fetch_byte()
        result = self.regs.A - imm
        self.regs.set_flag(self.regs.FLAG_C, result < 0)
        self.regs.A = result & 0xFF
        self.regs.set_nz(self.regs.A)
        self.cycle_count += 2
    
    def _adda_imm(self):
        """ADDA #imm: A = A + imm"""
        imm = self._fetch_byte()
        result = self.regs.A + imm
        self.regs.set_flag(self.regs.FLAG_C, result > 0xFF)
        self.regs.A = result & 0xFF
        self.regs.set_nz(self.regs.A)
        self.cycle_count += 2
    
    def _anda_imm(self):
        """ANDA #imm: A = A & imm"""
        self.regs.A &= self._fetch_byte()
        self.regs.set_nz(self.regs.A)
        self.cycle_count += 2
    
    def _ora_imm(self):
        """ORA #imm: A = A | imm"""
        self.regs.A |= self._fetch_byte()
        self.regs.set_nz(self.regs.A)
        self.cycle_count += 2
    
    def _eora_imm(self):
        """EORA #imm: A = A ^ imm"""
        self.regs.A ^= self._fetch_byte()
        self.regs.set_nz(self.regs.A)
        self.cycle_count += 2
    
    def _cmpa_imm(self):
        """CMPA #imm: 比较 A 与 imm"""
        imm = self._fetch_byte()
        result = self.regs.A - imm
        self.regs.set_flag(self.regs.FLAG_C, result < 0)
        self.regs.set_nz(result & 0xFF)
        self.cycle_count += 2
    
    # -------------------------------------------------------------------------
    # 直接寻址指令
    # -------------------------------------------------------------------------
    
    def _lda_dir(self):
        """LDA <dir: 从直接页加载到 A"""
        addr = self._fetch_byte()  # 直接页地址
        if self.regs.DP != 0:
            addr = (self.regs.DP << 8) | addr
        self.regs.A = self.mem.read_byte(addr)
        self.regs.set_nz(self.regs.A)
        self.cycle_count += 3
    
    def _ldb_dir(self):
        """LDB <dir: 从直接页加载到 B"""
        addr = self._fetch_byte()
        if self.regs.DP != 0:
            addr = (self.regs.DP << 8) | addr
        self.regs.B = self.mem.read_byte(addr)
        self.regs.set_nz(self.regs.B)
        self.cycle_count += 3
    
    def _ldd_dir(self):
        """LDD <dir: 从直接页加载到 D"""
        addr = self._fetch_byte()
        if self.regs.DP != 0:
            addr = (self.regs.DP << 8) | addr
        self.regs.D = self.mem.read_word(addr)
        self.regs.set_nz(self.regs.D, bits=16)
        self.cycle_count += 4
    
    def _sta_dir(self):
        """STA <dir: 存储 A 到直接页"""
        addr = self._fetch_byte()
        if self.regs.DP != 0:
            addr = (self.regs.DP << 8) | addr
        self.mem.write_byte(addr, self.regs.A)
        self.cycle_count += 3
    
    def _stb_dir(self):
        """STB <dir: 存储 B 到直接页"""
        addr = self._fetch_byte()
        if self.regs.DP != 0:
            addr = (self.regs.DP << 8) | addr
        self.mem.write_byte(addr, self.regs.B)
        self.cycle_count += 3
    
    def _std_dir(self):
        """STD <dir: 存储 D 到直接页"""
        addr = self._fetch_byte()
        if self.regs.DP != 0:
            addr = (self.regs.DP << 8) | addr
        self.mem.write_word(addr, self.regs.D)
        self.cycle_count += 4
    
    def _ldx_dir(self):
        """LDX <dir: 从直接页加载到 X"""
        addr = self._fetch_byte()
        if self.regs.DP != 0:
            addr = (self.regs.DP << 8) | addr
        self.regs.X = self.mem.read_word(addr)
        self.regs.set_nz(self.regs.X, bits=16)
        self.cycle_count += 4
    
    def _stx_dir(self):
        """STX <dir: 存储 X 到直接页"""
        addr = self._fetch_byte()
        if self.regs.DP != 0:
            addr = (self.regs.DP << 8) | addr
        self.mem.write_word(addr, self.regs.X)
        self.cycle_count += 4
    
    # -------------------------------------------------------------------------
    # 变址寻址指令
    # -------------------------------------------------------------------------
    
    def _lda_idx(self):
        """LDA ,X: 从变址加载到 A"""
        self.regs.A = self.mem.read_byte(self.regs.X)
        self.regs.set_nz(self.regs.A)
        self.regs.X = (self.regs.X + 1) & 0xFFFF
        self.cycle_count += 3
    
    def _ldb_idx(self):
        """LDB ,X: 从变址加载到 B"""
        self.regs.B = self.mem.read_byte(self.regs.X)
        self.regs.set_nz(self.regs.B)
        self.regs.X = (self.regs.X + 1) & 0xFFFF
        self.cycle_count += 3
    
    def _ldd_idx(self):
        """LDD ,X: 从变址加载到 D"""
        self.regs.D = self.mem.read_word(self.regs.X)
        self.regs.set_nz(self.regs.D, bits=16)
        self.regs.X = (self.regs.X + 2) & 0xFFFF
        self.cycle_count += 4
    
    def _sta_idx(self):
        """STA ,X: 存储 A 到变址"""
        self.mem.write_byte(self.regs.X, self.regs.A)
        self.regs.X = (self.regs.X + 1) & 0xFFFF
        self.cycle_count += 3
    
    def _stb_idx(self):
        """STB ,X: 存储 B 到变址"""
        self.mem.write_byte(self.regs.X, self.regs.B)
        self.regs.X = (self.regs.X + 1) & 0xFFFF
        self.cycle_count += 3
    
    def _std_idx(self):
        """STD ,X: 存储 D 到变址"""
        self.mem.write_word(self.regs.X, self.regs.D)
        self.regs.X = (self.regs.X + 2) & 0xFFFF
        self.cycle_count += 4
    
    # -------------------------------------------------------------------------
    # 其他指令
    # -------------------------------------------------------------------------
    
    def _bsr(self):
        """BSR: 分支到子程序"""
        offset = self._fetch_byte()
        # 符号扩展
        if offset & 0x80:
            offset = offset - 256
        self._push_s(self.regs.PC, 16)
        self.regs.PC = (self.regs.PC + offset) & 0xFFFF
        self.cycle_count += 7
    
    def _cmpx_imm(self):
        """CMPX #imm: 比较 X 与立即数"""
        imm = self._fetch_word()
        result = self.regs.X - imm
        self.regs.set_flag(self.regs.FLAG_C, result < 0)
        self.regs.set_nz(result & 0xFFFF, bits=16)
        self.cycle_count += 4
    
    def _andcc(self):
        """ANDCC: 与条件码"""
        mask = self._fetch_byte()
        self.regs.CC &= mask
        self.cycle_count += 3
    
    def _prefix_10(self):
        """16-bit 操作码前缀"""
        opcode = self._fetch_byte()
        # 简化处理：跳过
        self.cycle_count += 1
    
    def _prefix_11(self):
        """8-bit 操作码前缀"""
        opcode = self._fetch_byte()
        # 简化处理：跳过
        self.cycle_count += 1
    
    def _swi2(self):
        """SWI2: 软件中断 2"""
        self._push_s(self.regs.PC, 16)
        self.regs.PC = self.mem.read_word(0xFFF4)  # SWI2 向量
        self.cycle_count += 7
    
    # -------------------------------------------------------------------------
    # 算术运算 (A/B 寄存器)
    # -------------------------------------------------------------------------
    
    def _nega(self):
        """NEGA: A = -A"""
        self.regs.A = (-self.regs.A) & 0xFF
        self.regs.set_nz(self.regs.A)
        self.cycle_count += 1
    
    def _negb(self):
        """NEGB: B = -B"""
        self.regs.B = (-self.regs.B) & 0xFF
        self.regs.set_nz(self.regs.B)
        self.cycle_count += 1
    
    def _coma(self):
        """COMA: A = ~A"""
        self.regs.A = (~self.regs.A) & 0xFF
        self.regs.set_nz(self.regs.A)
        self.cycle_count += 1
    
    def _comb(self):
        """COMB: B = ~B"""
        self.regs.B = (~self.regs.B) & 0xFF
        self.regs.set_nz(self.regs.B)
        self.cycle_count += 1
    
    def _deca(self):
        """DECA: A = A - 1"""
        self.regs.A = (self.regs.A - 1) & 0xFF
        self.regs.set_nz(self.regs.A)
        self.cycle_count += 1
    
    def _decb(self):
        """DECB: B = B - 1"""
        self.regs.B = (self.regs.B - 1) & 0xFF
        self.regs.set_nz(self.regs.B)
        self.cycle_count += 1
    
    def _asla(self):
        """ASLA: A = A << 1"""
        self.regs.set_flag(self.regs.FLAG_C, bool(self.regs.A & 0x80))
        self.regs.A = (self.regs.A << 1) & 0xFF
        self.regs.set_nz(self.regs.A)
        self.cycle_count += 1
    
    def _aslb(self):
        """ASLB: B = B << 1"""
        self.regs.set_flag(self.regs.FLAG_C, bool(self.regs.B & 0x80))
        self.regs.B = (self.regs.B << 1) & 0xFF
        self.regs.set_nz(self.regs.B)
        self.cycle_count += 1
    
    def _lsra(self):
        """LSRA: A = A >> 1 (逻辑右移)"""
        self.regs.set_flag(self.regs.FLAG_C, bool(self.regs.A & 0x01))
        self.regs.A = self.regs.A >> 1
        self.regs.set_nz(self.regs.A)
        self.cycle_count += 1
    
    def _lsrb(self):
        """LSRB: B = B >> 1 (逻辑右移)"""
        self.regs.set_flag(self.regs.FLAG_C, bool(self.regs.B & 0x01))
        self.regs.B = self.regs.B >> 1
        self.regs.set_nz(self.regs.B)
        self.cycle_count += 1
    
    def _asra(self):
        """ASRA: A = A >> 1 (算术右移)"""
        self.regs.set_flag(self.regs.FLAG_C, bool(self.regs.A & 0x01))
        sign = self.regs.A & 0x80
        self.regs.A = (self.regs.A >> 1) | sign
        self.regs.set_nz(self.regs.A)
        self.cycle_count += 1
    
    def _asrb(self):
        """ASRB: B = B >> 1 (算术右移)"""
        self.regs.set_flag(self.regs.FLAG_C, bool(self.regs.B & 0x01))
        sign = self.regs.B & 0x80
        self.regs.B = (self.regs.B >> 1) | sign
        self.regs.set_nz(self.regs.B)
        self.cycle_count += 1
    
    def _rola(self):
        """ROLA: A = A << 1 | C"""
        c = 1 if self.regs.get_flag(self.regs.FLAG_C) else 0
        self.regs.set_flag(self.regs.FLAG_C, bool(self.regs.A & 0x80))
        self.regs.A = ((self.regs.A << 1) | c) & 0xFF
        self.regs.set_nz(self.regs.A)
        self.cycle_count += 1
    
    def _rolb(self):
        """ROLB: B = B << 1 | C"""
        c = 1 if self.regs.get_flag(self.regs.FLAG_C) else 0
        self.regs.set_flag(self.regs.FLAG_C, bool(self.regs.B & 0x80))
        self.regs.B = ((self.regs.B << 1) | c) & 0xFF
        self.regs.set_nz(self.regs.B)
        self.cycle_count += 1
    
    def _rora(self):
        """RORA: A = A >> 1 | C<<7"""
        c = 0x80 if self.regs.get_flag(self.regs.FLAG_C) else 0
        self.regs.set_flag(self.regs.FLAG_C, bool(self.regs.A & 0x01))
        self.regs.A = (self.regs.A >> 1) | c
        self.regs.set_nz(self.regs.A)
        self.cycle_count += 1
    
    def _rorb(self):
        """RORB: B = B >> 1 | C<<7"""
        c = 0x80 if self.regs.get_flag(self.regs.FLAG_C) else 0
        self.regs.set_flag(self.regs.FLAG_C, bool(self.regs.B & 0x01))
        self.regs.B = (self.regs.B >> 1) | c
        self.regs.set_nz(self.regs.B)
        self.cycle_count += 1
    
    def _adca_imm(self):
        """ADCA #imm: A = A + imm + C"""
        imm = self._fetch_byte()
        c = 1 if self.regs.get_flag(self.regs.FLAG_C) else 0
        result = self.regs.A + imm + c
        self.regs.set_flag(self.regs.FLAG_C, result > 0xFF)
        self.regs.A = result & 0xFF
        self.regs.set_nz(self.regs.A)
        self.cycle_count += 2
    
    def _sbca_imm(self):
        """SBCA #imm: A = A - imm - C"""
        imm = self._fetch_byte()
        c = 1 if self.regs.get_flag(self.regs.FLAG_C) else 0
        result = self.regs.A - imm - c
        self.regs.set_flag(self.regs.FLAG_C, result < 0)
        self.regs.A = result & 0xFF
        self.regs.set_nz(self.regs.A)
        self.cycle_count += 2
    
    def _subd_imm(self):
        """SUBD #imm: D = D - imm"""
        imm = self._fetch_word()
        result = self.regs.D - imm
        self.regs.set_flag(self.regs.FLAG_C, result < 0)
        self.regs.D = result & 0xFFFF
        self.regs.set_nz(self.regs.D, bits=16)
        self.cycle_count += 4
    
    def _subd_dir(self):
        """SUBD <dir: D = D - [addr]"""
        addr = self._fetch_byte()
        if self.regs.DP != 0:
            addr = (self.regs.DP << 8) | addr
        imm = self.mem.read_word(addr)
        result = self.regs.D - imm
        self.regs.set_flag(self.regs.FLAG_C, result < 0)
        self.regs.D = result & 0xFFFF
        self.regs.set_nz(self.regs.D, bits=16)
        self.cycle_count += 5
    
    def _bita_imm(self):
        """BITA #imm: 测试 A & imm (不存储)"""
        result = self.regs.A & self._fetch_byte()
        self.regs.set_nz(result)
        self.cycle_count += 2
    
    # -------------------------------------------------------------------------
    # 主循环
    # -------------------------------------------------------------------------
    
    def step(self) -> int:
        """执行一条指令，返回周期数"""
        opcode = self._fetch_byte()
        
        if opcode in self.opcodes:
            self.opcodes[opcode]()
        else:
            # 未知操作码 - 跳过
            print(f"警告：未知操作码 0x{opcode:02X} @ PC=0x{self.regs.PC-1:04X}")
            self.cycle_count += 1
        
        return self.cycle_count
    
    def run(self, max_cycles: int = 0):
        """运行 CPU"""
        self.running = True
        start_cycles = self.cycle_count
        
        while self.running:
            if max_cycles > 0 and (self.cycle_count - start_cycles) >= max_cycles:
                break
            
            self.step()
    
    def stop(self):
        """停止 CPU"""
        self.running = False
    
    def reset(self):
        """重置 CPU"""
        self.regs = Registers()
        # 从复位向量加载 PC
        self.regs.PC = self.mem.read_word(0xFFF6)
        self.cycle_count = 0
    
    def get_state(self) -> dict:
        """获取 CPU 状态"""
        return {
            'registers': str(self.regs),
            'cycles': self.cycle_count,
            'running': self.running
        }


# ============================================================================
# 测试程序
# ============================================================================

def test_cpu():
    """测试 CPU 模拟器"""
    print("=" * 60)
    print("Motorola 6809 CPU 模拟器测试")
    print("=" * 60)
    
    mem = MemoryMap()
    cpu = Motorola6809(mem)
    
    # 测试 1: MUL 指令 (硬件乘法)
    print("\n[测试 1] MUL 指令 - 硬件乘法")
    cpu.regs.A = 0x12
    cpu.regs.B = 0x34
    cpu.mem.write_byte(0xC000, 0x3D)  # MUL
    cpu.regs.PC = 0xC000
    cpu.step()
    print(f"  {0x12:02X} × {0x34:02X} = {cpu.regs.D:04X}")
    print(f"  预期：{0x12 * 0x34:04X}, 结果：{'✓' if cpu.regs.D == 0x12 * 0x34 else '✗'}")
    
    # 测试 2: LDA 立即数
    print("\n[测试 2] LDA #imm 指令")
    cpu.regs.A = 0x00
    cpu.mem.write_byte(0xC000, 0x86)  # LDA #imm
    cpu.mem.write_byte(0xC001, 0xAB)  # 立即数
    cpu.regs.PC = 0xC000
    cpu.step()
    print(f"  A = 0x{cpu.regs.A:02X}")
    print(f"  预期：0xAB, 结果：{'✓' if cpu.regs.A == 0xAB else '✗'}")
    
    # 测试 3: ADDA 立即数
    print("\n[测试 3] ADDA #imm 指令")
    cpu.regs.A = 0x10
    cpu.mem.write_byte(0xC000, 0x8B)  # ADDA #imm
    cpu.mem.write_byte(0xC001, 0x05)  # 立即数
    cpu.regs.PC = 0xC000
    cpu.step()
    print(f"  0x10 + 0x05 = 0x{cpu.regs.A:02X}")
    print(f"  预期：0x15, 结果：{'✓' if cpu.regs.A == 0x15 else '✗'}")
    
    # 测试 4: 变址寻址
    print("\n[测试 4] LDA ,X 变址寻址")
    cpu.regs.X = 0xC100
    cpu.mem.write_byte(0xC100, 0x55)
    cpu.mem.write_byte(0xC000, 0xA6)  # LDA ,X
    cpu.regs.PC = 0xC000
    cpu.step()
    print(f"  X=0xC100, [X]=0x{cpu.regs.A:02X}")
    print(f"  预期：0x55, 结果：{'✓' if cpu.regs.A == 0x55 else '✗'}")
    
    # 测试 5: 栈操作
    print("\n[测试 5] PSHS/PULS 栈操作")
    cpu.regs.S = 0xCFFF
    cpu.regs.A = 0xAA
    cpu.regs.B = 0xBB
    cpu.mem.write_byte(0xC000, 0x34)  # PSHS
    cpu.mem.write_byte(0xC001, 0x06)  # 压入 A 和 B
    cpu.regs.PC = 0xC000
    cpu.step()
    print(f"  压入 A=0xAA, B=0xBB, S=0x{cpu.regs.S:04X}")
    
    cpu.mem.write_byte(0xC002, 0x35)  # PULS
    cpu.mem.write_byte(0xC003, 0x06)  # 弹出 A 和 B
    cpu.regs.PC = 0xC002
    cpu.regs.A = 0x00
    cpu.regs.B = 0x00
    cpu.step()
    print(f"  弹出后 A=0x{cpu.regs.A:02X}, B=0x{cpu.regs.B:02X}")
    print(f"  预期：A=0xAA, B=0xBB, 结果：{'✓' if cpu.regs.A == 0xAA and cpu.regs.B == 0xBB else '✗'}")
    
    print("\n" + "=" * 60)
    print("测试完成!")
    print("=" * 60)


def demo_miner():
    """演示简化挖矿循环"""
    print("\n" + "=" * 60)
    print("Defender 矿工演示 - 简化挖矿循环")
    print("=" * 60)
    
    mem = MemoryMap()
    cpu = Motorola6809(mem)
    
    # 初始化挖矿数据
    block_header = 0x1234
    difficulty = 0x00FF
    nonce = 0x0000
    
    print(f"\n初始状态:")
    print(f"  区块头：0x{block_header:04X}")
    print(f"  难度目标：0x{difficulty:04X}")
    print(f"  初始 Nonce: 0x{nonce:04X}")
    
    # 模拟挖矿循环
    print(f"\n开始挖矿 (最多 1000 次尝试)...")
    found = False
    
    for i in range(1000):
        # 简化哈希计算 (使用乘法模拟)
        hash_result = (block_header * (nonce + 1)) & 0xFFFF
        
        if hash_result < difficulty:
            print(f"\n✓ 找到有效区块!")
            print(f"  Nonce: 0x{nonce:04X}")
            print(f"  哈希：0x{hash_result:04X}")
            found = True
            break
        
        nonce = (nonce + 1) & 0xFFFF
        
        if i % 100 == 0:
            print(f"  已尝试 {i} 次，当前 Nonce: 0x{nonce:04X}")
    
    if not found:
        print(f"\n✗ 未在 1000 次内找到有效区块")
    
    print(f"\nCPU 周期数：{cpu.cycle_count}")
    print("=" * 60)


if __name__ == "__main__":
    test_cpu()
    demo_miner()
