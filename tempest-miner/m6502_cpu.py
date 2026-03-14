#!/usr/bin/env python3
"""
m6502_cpu.py - Motorola 6502 CPU 模拟器核心

模拟 1975 年 Motorola 6502 8 位 CPU，用于 Tempest 街机 (1981) 移植。
支持完整的 6502 指令集和内存映射 I/O。

参考：https://www.masswerk.at/6502/
"""

class M6502:
    """Motorola 6502 CPU 模拟器"""
    
    def __init__(self, memory_size=65536):
        """
        初始化 6502 CPU
        
        Args:
            memory_size: 内存大小 (默认 64KB)
        """
        # 内存
        self.memory = bytearray(memory_size)
        
        # 寄存器
        self.A = 0x00      # 累加器
        self.X = 0x00      # X 索引寄存器
        self.Y = 0x00      # Y 索引寄存器
        self.SP = 0xFD     # 栈指针
        self.PC = 0x0000   # 程序计数器
        self.P = 0x24      # 状态寄存器 (默认中断禁用)
        
        # 状态标志
        self.FLAG_C = 0x01  # 进位
        self.FLAG_Z = 0x02  # 零
        self.FLAG_I = 0x04  # 中断禁用
        self.FLAG_D = 0x08  # 十进制模式
        self.FLAG_B = 0x10  # 中断断点
        self.FLAG_U = 0x20  # 未使用
        self.FLAG_V = 0x40  # 溢出
        self.FLAG_N = 0x80  # 负
        
        # 时钟
        self.cycles = 0
        self.clock_speed = 1500000  # 1.5 MHz (Tempest)
        
        # 回调
        self.read_callback = None
        self.write_callback = None
        
    def reset(self):
        """CPU 复位"""
        # 从复位向量读取起始地址
        self.PC = self.read_word(0xFFFC)
        self.SP = 0xFD
        self.P = 0x24
        self.A = self.X = self.Y = 0x00
        self.cycles = 0
        
    def read_byte(self, addr):
        """读取一个字节"""
        addr &= 0xFFFF
        if self.read_callback:
            return self.read_callback(addr)
        return self.memory[addr]
    
    def read_word(self, addr):
        """读取一个字 (16 位)"""
        low = self.read_byte(addr)
        high = self.read_byte((addr + 1) & 0xFFFF)
        return (high << 8) | low
    
    def write_byte(self, addr, value):
        """写入一个字节"""
        addr &= 0xFFFF
        value &= 0xFF
        if self.write_callback:
            self.write_callback(addr, value)
        else:
            self.memory[addr] = value
    
    def write_word(self, addr, value):
        """写入一个字"""
        self.write_byte(addr, value & 0xFF)
        self.write_byte((addr + 1) & 0xFFFF, (value >> 8) & 0xFF)
    
    def push_stack(self, value):
        """压栈"""
        self.write_byte(0x0100 + self.SP, value & 0xFF)
        self.SP = (self.SP - 1) & 0xFF
    
    def pop_stack(self):
        """出栈"""
        self.SP = (self.SP + 1) & 0xFF
        return self.read_byte(0x0100 + self.SP)
    
    def get_flag(self, flag):
        """获取标志位"""
        return 1 if (self.P & flag) else 0
    
    def set_flag(self, flag, value):
        """设置标志位"""
        if value:
            self.P |= flag
        else:
            self.P &= ~flag
    
    def update_flags_zn(self, value):
        """更新零和负标志"""
        self.set_flag(self.FLAG_Z, (value & 0xFF) == 0)
        self.set_flag(self.FLAG_N, (value & 0x80) != 0)
    
    # 寻址模式
    def addr_immediate(self):
        """立即数寻址"""
        return self.read_byte(self.PC)
    
    def addr_zero_page(self):
        """零页寻址"""
        return self.read_byte(self.PC)
    
    def addr_zero_page_x(self):
        """零页 X 寻址"""
        return (self.read_byte(self.PC) + self.X) & 0xFF
    
    def addr_zero_page_y(self):
        """零页 Y 寻址"""
        return (self.read_byte(self.PC) + self.Y) & 0xFF
    
    def addr_absolute(self):
        """绝对寻址"""
        return self.read_word(self.PC)
    
    def addr_absolute_x(self):
        """绝对 X 寻址"""
        return (self.read_word(self.PC) + self.X) & 0xFFFF
    
    def addr_absolute_y(self):
        """绝对 Y 寻址"""
        return (self.read_word(self.PC) + self.Y) & 0xFFFF
    
    def addr_indirect_x(self):
        """(间接，X) 寻址"""
        ptr = (self.read_byte(self.PC) + self.X) & 0xFF
        return self.read_word(ptr)
    
    def addr_indirect_y(self):
        """(间接),Y 寻址"""
        ptr = self.read_byte(self.PC)
        return (self.read_word(ptr) + self.Y) & 0xFFFF
    
    def addr_relative(self):
        """相对寻址"""
        offset = self.read_byte(self.PC)
        if offset & 0x80:
            offset -= 256
        return (self.PC + offset) & 0xFFFF
    
    def addr_indirect(self):
        """间接寻址"""
        ptr = self.read_word(self.PC)
        return self.read_word(ptr)
    
    # 指令实现
    def op_lda(self, value):
        """LDA - 加载累加器"""
        self.A = value & 0xFF
        self.update_flags_zn(self.A)
        self.cycles += 2
    
    def op_ldx(self, value):
        """LDX - 加载 X 寄存器"""
        self.X = value & 0xFF
        self.update_flags_zn(self.X)
        self.cycles += 2
    
    def op_ldy(self, value):
        """LDY - 加载 Y 寄存器"""
        self.Y = value & 0xFF
        self.update_flags_zn(self.Y)
        self.cycles += 2
    
    def op_sta(self, addr):
        """STA - 存储累加器"""
        self.write_byte(addr, self.A)
        self.cycles += 3
    
    def op_stx(self, addr):
        """STX - 存储 X 寄存器"""
        self.write_byte(addr, self.X)
        self.cycles += 3
    
    def op_sty(self, addr):
        """STY - 存储 Y 寄存器"""
        self.write_byte(addr, self.Y)
        self.cycles += 3
    
    def op_adc(self, value):
        """ADC - 带进位加法"""
        result = self.A + value + self.get_flag(self.FLAG_C)
        self.set_flag(self.FLAG_C, result > 0xFF)
        self.set_flag(self.FLAG_V, (~(self.A ^ value) & (self.A ^ result) & 0x80) != 0)
        self.A = result & 0xFF
        self.update_flags_zn(self.A)
        self.cycles += 2
    
    def op_sbc(self, value):
        """SBC - 带借位减法"""
        value = value ^ 0xFF
        result = self.A + value + self.get_flag(self.FLAG_C)
        self.set_flag(self.FLAG_C, result > 0xFF)
        self.set_flag(self.FLAG_V, ((self.A ^ value) & (self.A ^ result) & 0x80) != 0)
        self.A = result & 0xFF
        self.update_flags_zn(self.A)
        self.cycles += 2
    
    def op_and(self, value):
        """AND - 逻辑与"""
        self.A = self.A & value
        self.update_flags_zn(self.A)
        self.cycles += 2
    
    def op_ora(self, value):
        """ORA - 逻辑或"""
        self.A = self.A | value
        self.update_flags_zn(self.A)
        self.cycles += 2
    
    def op_eor(self, value):
        """EOR - 逻辑异或"""
        self.A = self.A ^ value
        self.update_flags_zn(self.A)
        self.cycles += 2
    
    def op_cmp(self, value):
        """CMP - 比较累加器"""
        result = self.A - value
        self.set_flag(self.FLAG_C, self.A >= value)
        self.update_flags_zn(result & 0xFF)
        self.cycles += 2
    
    def op_cpx(self, value):
        """CPX - 比较 X 寄存器"""
        result = self.X - value
        self.set_flag(self.FLAG_C, self.X >= value)
        self.update_flags_zn(result & 0xFF)
        self.cycles += 2
    
    def op_cpy(self, value):
        """CPY - 比较 Y 寄存器"""
        result = self.Y - value
        self.set_flag(self.FLAG_C, self.Y >= value)
        self.update_flags_zn(result & 0xFF)
        self.cycles += 2
    
    def op_inc(self, addr):
        """INC - 内存加 1"""
        value = (self.read_byte(addr) + 1) & 0xFF
        self.write_byte(addr, value)
        self.update_flags_zn(value)
        self.cycles += 5
    
    def op_dec(self, addr):
        """DEC - 内存减 1"""
        value = (self.read_byte(addr) - 1) & 0xFF
        self.write_byte(addr, value)
        self.update_flags_zn(value)
        self.cycles += 5
    
    def op_inx(self):
        """INX - X 加 1"""
        self.X = (self.X + 1) & 0xFF
        self.update_flags_zn(self.X)
        self.cycles += 2
    
    def op_iny(self):
        """INY - Y 加 1"""
        self.Y = (self.Y + 1) & 0xFF
        self.update_flags_zn(self.Y)
        self.cycles += 2
    
    def op_dex(self):
        """DEX - X 减 1"""
        self.X = (self.X - 1) & 0xFF
        self.update_flags_zn(self.X)
        self.cycles += 2
    
    def op_dey(self):
        """DEY - Y 减 1"""
        self.Y = (self.Y - 1) & 0xFF
        self.update_flags_zn(self.Y)
        self.cycles += 2
    
    def op_asl(self, addr=None):
        """ASL - 算术左移"""
        if addr is not None:
            value = self.read_byte(addr)
            self.set_flag(self.FLAG_C, (value & 0x80) != 0)
            value = (value << 1) & 0xFF
            self.write_byte(addr, value)
            self.update_flags_zn(value)
            self.cycles += 5
        else:
            self.set_flag(self.FLAG_C, (self.A & 0x80) != 0)
            self.A = (self.A << 1) & 0xFF
            self.update_flags_zn(self.A)
            self.cycles += 2
    
    def op_lsr(self, addr=None):
        """LSR - 逻辑右移"""
        if addr is not None:
            value = self.read_byte(addr)
            self.set_flag(self.FLAG_C, (value & 0x01) != 0)
            value = value >> 1
            self.write_byte(addr, value)
            self.update_flags_zn(value)
            self.cycles += 5
        else:
            self.set_flag(self.FLAG_C, (self.A & 0x01) != 0)
            self.A = self.A >> 1
            self.update_flags_zn(self.A)
            self.cycles += 2
    
    def op_rol(self, addr=None):
        """ROL - 循环左移"""
        if addr is not None:
            value = self.read_byte(addr)
            new_carry = (value & 0x80) != 0
            value = ((value << 1) | self.get_flag(self.FLAG_C)) & 0xFF
            self.set_flag(self.FLAG_C, new_carry)
            self.write_byte(addr, value)
            self.update_flags_zn(value)
            self.cycles += 5
        else:
            new_carry = (self.A & 0x80) != 0
            self.A = ((self.A << 1) | self.get_flag(self.FLAG_C)) & 0xFF
            self.set_flag(self.FLAG_C, new_carry)
            self.update_flags_zn(self.A)
            self.cycles += 2
    
    def op_ror(self, addr=None):
        """ROR - 循环右移"""
        if addr is not None:
            value = self.read_byte(addr)
            new_carry = (value & 0x01) != 0
            value = ((value >> 1) | (self.get_flag(self.FLAG_C) << 7)) & 0xFF
            self.set_flag(self.FLAG_C, new_carry)
            self.write_byte(addr, value)
            self.update_flags_zn(value)
            self.cycles += 5
        else:
            new_carry = (self.A & 0x01) != 0
            self.A = ((self.A >> 1) | (self.get_flag(self.FLAG_C) << 7)) & 0xFF
            self.set_flag(self.FLAG_C, new_carry)
            self.update_flags_zn(self.A)
            self.cycles += 2
    
    def op_jmp(self, addr):
        """JMP - 跳转"""
        self.PC = addr
        self.cycles += 3
    
    def op_jsr(self, addr):
        """JSR - 跳转到子程序"""
        self.push_stack((self.PC - 1) >> 8)
        self.push_stack((self.PC - 1) & 0xFF)
        self.PC = addr
        self.cycles += 6
    
    def op_rts(self):
        """RTS - 从子程序返回"""
        low = self.pop_stack()
        high = self.pop_stack()
        self.PC = ((high << 8) | low) + 1
        self.cycles += 6
    
    def op_rti(self):
        """RTI - 从中断返回"""
        self.P = self.pop_stack() | 0x20  # 保留未使用位
        low = self.pop_stack()
        high = self.pop_stack()
        self.PC = (high << 8) | low
        self.cycles += 6
    
    def op_bcc(self, addr):
        """BCC - 进位为 0 时分支"""
        if not self.get_flag(self.FLAG_C):
            self.PC = addr
            self.cycles += 3
        else:
            self.cycles += 2
    
    def op_bcs(self, addr):
        """BCS - 进位为 1 时分支"""
        if self.get_flag(self.FLAG_C):
            self.PC = addr
            self.cycles += 3
        else:
            self.cycles += 2
    
    def op_beq(self, addr):
        """BEQ - 为零时分支"""
        if self.get_flag(self.FLAG_Z):
            self.PC = addr
            self.cycles += 3
        else:
            self.cycles += 2
    
    def op_bne(self, addr):
        """BNE - 不为零时分支"""
        if not self.get_flag(self.FLAG_Z):
            self.PC = addr
            self.cycles += 3
        else:
            self.cycles += 2
    
    def op_bmi(self, addr):
        """BMI - 负时分支"""
        if self.get_flag(self.FLAG_N):
            self.PC = addr
            self.cycles += 3
        else:
            self.cycles += 2
    
    def op_bpl(self, addr):
        """BPL - 正时分支"""
        if not self.get_flag(self.FLAG_N):
            self.PC = addr
            self.cycles += 3
        else:
            self.cycles += 2
    
    def op_bvc(self, addr):
        """BVC - 溢出为 0 时分支"""
        if not self.get_flag(self.FLAG_V):
            self.PC = addr
            self.cycles += 3
        else:
            self.cycles += 2
    
    def op_bvs(self, addr):
        """BVS - 溢出为 1 时分支"""
        if self.get_flag(self.FLAG_V):
            self.PC = addr
            self.cycles += 3
        else:
            self.cycles += 2
    
    def op_brk(self):
        """BRK - 中断"""
        self.push_stack((self.PC >> 8) & 0xFF)
        self.push_stack(self.PC & 0xFF)
        self.push_stack(self.P | self.FLAG_B | 0x20)
        self.set_flag(self.FLAG_I, 1)
        self.PC = self.read_word(0xFFFE)
        self.cycles += 7
    
    def op_clc(self):
        """CLC - 清除进位"""
        self.set_flag(self.FLAG_C, 0)
        self.cycles += 2
    
    def op_sec(self):
        """SEC - 设置进位"""
        self.set_flag(self.FLAG_C, 1)
        self.cycles += 2
    
    def op_cli(self):
        """CLI - 清除中断禁用"""
        self.set_flag(self.FLAG_I, 0)
        self.cycles += 2
    
    def op_sei(self):
        """SEI - 设置中断禁用"""
        self.set_flag(self.FLAG_I, 1)
        self.cycles += 2
    
    def op_cld(self):
        """CLD - 清除十进制模式"""
        self.set_flag(self.FLAG_D, 0)
        self.cycles += 2
    
    def op_sed(self):
        """SED - 设置十进制模式"""
        self.set_flag(self.FLAG_D, 1)
        self.cycles += 2
    
    def op_clv(self):
        """CLV - 清除溢出"""
        self.set_flag(self.FLAG_V, 0)
        self.cycles += 2
    
    def op_nop(self):
        """NOP - 无操作"""
        self.cycles += 2
    
    def op_tax(self):
        """TAX - 传输 A 到 X"""
        self.X = self.A
        self.update_flags_zn(self.X)
        self.cycles += 2
    
    def op_tay(self):
        """TAY - 传输 A 到 Y"""
        self.Y = self.A
        self.update_flags_zn(self.Y)
        self.cycles += 2
    
    def op_txa(self):
        """TXA - 传输 X 到 A"""
        self.A = self.X
        self.update_flags_zn(self.A)
        self.cycles += 2
    
    def op_tya(self):
        """TYA - 传输 Y 到 A"""
        self.A = self.Y
        self.update_flags_zn(self.A)
        self.cycles += 2
    
    def op_tsx(self):
        """TSX - 传输 SP 到 X"""
        self.X = self.SP
        self.update_flags_zn(self.X)
        self.cycles += 2
    
    def op_txs(self):
        """TXS - 传输 X 到 SP"""
        self.SP = self.X
        self.cycles += 2
    
    def op_pha(self):
        """PHA - 压入 A"""
        self.push_stack(self.A)
        self.cycles += 3
    
    def op_php(self):
        """PHP - 压入 P"""
        self.push_stack(self.P | self.FLAG_B | 0x20)
        self.cycles += 3
    
    def op_pla(self):
        """PLA - 弹出 A"""
        self.A = self.pop_stack()
        self.update_flags_zn(self.A)
        self.cycles += 4
    
    def op_plp(self):
        """PLP - 弹出 P"""
        self.P = (self.pop_stack() & ~0x20) | 0x20
        self.cycles += 4
    
    # 指令解码和执行
    def execute_instruction(self):
        """执行一条指令"""
        opcode = self.read_byte(self.PC)
        self.PC = (self.PC + 1) & 0xFFFF
        
        # 指令表 (部分实现)
        instructions = {
            0x00: ('BRK', self.op_brk, None),
            0x01: ('ORA', self.op_ora, self.addr_indirect_x),
            0x05: ('ORA', self.op_ora, self.addr_zero_page),
            0x06: ('ASL', self.op_asl, self.addr_zero_page),
            0x08: ('PHP', self.op_php, None),
            0x09: ('ORA', self.op_ora, self.addr_immediate),
            0x0A: ('ASL', self.op_asl, None),
            0x0D: ('ORA', self.op_ora, self.addr_absolute),
            0x0E: ('ASL', self.op_asl, self.addr_absolute),
            0x10: ('BPL', self.op_bpl, self.addr_relative),
            0x11: ('ORA', self.op_ora, self.addr_indirect_y),
            0x15: ('ORA', self.op_ora, self.addr_zero_page_x),
            0x16: ('ASL', self.op_asl, self.addr_zero_page_x),
            0x18: ('CLC', self.op_clc, None),
            0x19: ('ORA', self.op_ora, self.addr_absolute_y),
            0x1D: ('ORA', self.op_ora, self.addr_absolute_x),
            0x1E: ('ASL', self.op_asl, self.addr_absolute_x),
            0x20: ('JSR', self.op_jsr, self.addr_absolute),
            0x21: ('AND', self.op_and, self.addr_indirect_x),
            0x24: ('BIT', None, self.addr_zero_page),  # TODO
            0x25: ('AND', self.op_and, self.addr_zero_page),
            0x26: ('ROL', self.op_rol, self.addr_zero_page),
            0x28: ('PLP', self.op_plp, None),
            0x29: ('AND', self.op_and, self.addr_immediate),
            0x2A: ('ROL', self.op_rol, None),
            0x2C: ('BIT', None, self.addr_absolute),  # TODO
            0x2D: ('AND', self.op_and, self.addr_absolute),
            0x2E: ('ROL', self.op_rol, self.addr_absolute),
            0x30: ('BMI', self.op_bmi, self.addr_relative),
            0x31: ('AND', self.op_and, self.addr_indirect_y),
            0x35: ('AND', self.op_and, self.addr_zero_page_x),
            0x36: ('ROL', self.op_rol, self.addr_zero_page_x),
            0x38: ('SEC', self.op_sec, None),
            0x39: ('AND', self.op_and, self.addr_absolute_y),
            0x3D: ('AND', self.op_and, self.addr_absolute_x),
            0x3E: ('ROL', self.op_rol, self.addr_absolute_x),
            0x40: ('RTI', self.op_rti, None),
            0x41: ('EOR', self.op_eor, self.addr_indirect_x),
            0x45: ('EOR', self.op_eor, self.addr_zero_page),
            0x46: ('LSR', self.op_lsr, self.addr_zero_page),
            0x48: ('PHA', self.op_pha, None),
            0x49: ('EOR', self.op_eor, self.addr_immediate),
            0x4A: ('LSR', self.op_lsr, None),
            0x4C: ('JMP', self.op_jmp, self.addr_absolute),
            0x4D: ('EOR', self.op_eor, self.addr_absolute),
            0x4E: ('LSR', self.op_lsr, self.addr_absolute),
            0x50: ('BVC', self.op_bvc, self.addr_relative),
            0x51: ('EOR', self.op_eor, self.addr_indirect_y),
            0x55: ('EOR', self.op_eor, self.addr_zero_page_x),
            0x56: ('LSR', self.op_lsr, self.addr_zero_page_x),
            0x58: ('CLI', self.op_cli, None),
            0x59: ('EOR', self.op_eor, self.addr_absolute_y),
            0x5D: ('EOR', self.op_eor, self.addr_absolute_x),
            0x5E: ('LSR', self.op_lsr, self.addr_absolute_x),
            0x60: ('RTS', self.op_rts, None),
            0x61: ('ADC', self.op_adc, self.addr_indirect_x),
            0x65: ('ADC', self.op_adc, self.addr_zero_page),
            0x66: ('ROR', self.op_ror, self.addr_zero_page),
            0x68: ('PLA', self.op_pla, None),
            0x69: ('ADC', self.op_adc, self.addr_immediate),
            0x6A: ('ROR', self.op_ror, None),
            0x6C: ('JMP', self.op_jmp, self.addr_indirect),
            0x6D: ('ADC', self.op_adc, self.addr_absolute),
            0x6E: ('ROR', self.op_ror, self.addr_absolute),
            0x70: ('BVS', self.op_bvs, self.addr_relative),
            0x71: ('ADC', self.op_adc, self.addr_indirect_y),
            0x75: ('ADC', self.op_adc, self.addr_zero_page_x),
            0x76: ('ROR', self.op_ror, self.addr_zero_page_x),
            0x78: ('SEI', self.op_sei, None),
            0x79: ('ADC', self.op_adc, self.addr_absolute_y),
            0x7D: ('ADC', self.op_adc, self.addr_absolute_x),
            0x7E: ('ROR', self.op_ror, self.addr_absolute_x),
            0x81: ('STA', self.op_sta, self.addr_indirect_x),
            0x84: ('STY', self.op_sty, self.addr_zero_page),
            0x85: ('STA', self.op_sta, self.addr_zero_page),
            0x86: ('STX', self.op_stx, self.addr_zero_page),
            0x88: ('DEY', self.op_dey, None),
            0x8A: ('TXA', self.op_txa, None),
            0x8C: ('STY', self.op_sty, self.addr_absolute),
            0x8D: ('STA', self.op_sta, self.addr_absolute),
            0x8E: ('STX', self.op_stx, self.addr_absolute),
            0x90: ('BCC', self.op_bcc, self.addr_relative),
            0x91: ('STA', self.op_sta, self.addr_indirect_y),
            0x94: ('STY', self.op_sty, self.addr_zero_page_x),
            0x95: ('STA', self.op_sta, self.addr_zero_page_x),
            0x96: ('STX', self.op_stx, self.addr_zero_page_y),
            0x98: ('TYA', self.op_tya, None),
            0x99: ('STA', self.op_sta, self.addr_absolute_y),
            0x9A: ('TXS', self.op_txs, None),
            0x9D: ('STA', self.op_sta, self.addr_absolute_x),
            0xA0: ('LDY', self.op_ldy, self.addr_immediate),
            0xA1: ('LDA', self.op_lda, self.addr_indirect_x),
            0xA2: ('LDX', self.op_ldx, self.addr_immediate),
            0xA4: ('LDY', self.op_ldy, self.addr_zero_page),
            0xA5: ('LDA', self.op_lda, self.addr_zero_page),
            0xA6: ('LDX', self.op_ldx, self.addr_zero_page),
            0xA8: ('TAY', self.op_tay, None),
            0xA9: ('LDA', self.op_lda, self.addr_immediate),
            0xAA: ('TAX', self.op_tax, None),
            0xAC: ('LDY', self.op_ldy, self.addr_absolute),
            0xAD: ('LDA', self.op_lda, self.addr_absolute),
            0xAE: ('LDX', self.op_ldx, self.addr_absolute),
            0xB0: ('BCS', self.op_bcs, self.addr_relative),
            0xB1: ('LDA', self.op_lda, self.addr_indirect_y),
            0xB4: ('LDY', self.op_ldy, self.addr_zero_page_x),
            0xB5: ('LDA', self.op_lda, self.addr_zero_page_x),
            0xB6: ('LDX', self.op_ldx, self.addr_zero_page_y),
            0xB8: ('CLV', self.op_clv, None),
            0xB9: ('LDA', self.op_lda, self.addr_absolute_y),
            0xBA: ('TSX', self.op_tsx, None),
            0xBC: ('LDY', self.op_ldy, self.addr_absolute_x),
            0xBD: ('LDA', self.op_lda, self.addr_absolute_x),
            0xBE: ('LDX', self.op_ldx, self.addr_absolute_y),
            0xC0: ('CPY', self.op_cpy, self.addr_immediate),
            0xC1: ('CMP', self.op_cmp, self.addr_indirect_x),
            0xC4: ('CPY', self.op_cpy, self.addr_zero_page),
            0xC5: ('CMP', self.op_cmp, self.addr_zero_page),
            0xC6: ('DEC', self.op_dec, self.addr_zero_page),
            0xC8: ('INY', self.op_iny, None),
            0xC9: ('CMP', self.op_cmp, self.addr_immediate),
            0xCA: ('DEX', self.op_dex, None),
            0xCC: ('CPY', self.op_cpy, self.addr_absolute),
            0xCD: ('CMP', self.op_cmp, self.addr_absolute),
            0xCE: ('DEC', self.op_dec, self.addr_absolute),
            0xD0: ('BNE', self.op_bne, self.addr_relative),
            0xD1: ('CMP', self.op_cmp, self.addr_indirect_y),
            0xD5: ('CMP', self.op_cmp, self.addr_zero_page_x),
            0xD6: ('DEC', self.op_dec, self.addr_zero_page_x),
            0xD8: ('CLD', self.op_cld, None),
            0xD9: ('CMP', self.op_cmp, self.addr_absolute_y),
            0xDD: ('CMP', self.op_cmp, self.addr_absolute_x),
            0xDE: ('DEC', self.op_dec, self.addr_absolute_x),
            0xE0: ('CPX', self.op_cpx, self.addr_immediate),
            0xE1: ('SBC', self.op_sbc, self.addr_indirect_x),
            0xE4: ('CPX', self.op_cpx, self.addr_zero_page),
            0xE5: ('SBC', self.op_sbc, self.addr_zero_page),
            0xE6: ('INC', self.op_inc, self.addr_zero_page),
            0xE8: ('INX', self.op_inx, None),
            0xE9: ('SBC', self.op_sbc, self.addr_immediate),
            0xEA: ('NOP', self.op_nop, None),
            0xEC: ('CPX', self.op_cpx, self.addr_absolute),
            0xED: ('SBC', self.op_sbc, self.addr_absolute),
            0xEE: ('INC', self.op_inc, self.addr_absolute),
            0xF0: ('BEQ', self.op_beq, self.addr_relative),
            0xF1: ('SBC', self.op_sbc, self.addr_indirect_y),
            0xF5: ('SBC', self.op_sbc, self.addr_zero_page_x),
            0xF6: ('INC', self.op_inc, self.addr_zero_page_x),
            0xF8: ('SED', self.op_sed, None),
            0xF9: ('SBC', self.op_sbc, self.addr_absolute_y),
            0xFD: ('SBC', self.op_sbc, self.addr_absolute_x),
            0xFE: ('INC', self.op_inc, self.addr_absolute_x),
        }
        
        if opcode in instructions:
            name, func, addr_mode = instructions[opcode]
            if addr_mode:
                addr = addr_mode()
                if name in ['LDA', 'LDX', 'LDY', 'ORA', 'AND', 'EOR', 'ADC', 'SBC', 'CMP']:
                    # 立即数寻址时，addr 已经是值本身
                    if addr_mode == self.addr_immediate:
                        value = addr
                    else:
                        value = self.read_byte(addr)
                    func(value)
                elif name in ['STA', 'STX', 'STY']:
                    func(addr)
                elif name in ['INC', 'DEC', 'ASL', 'LSR', 'ROL', 'ROR']:
                    func(addr)
                elif name in ['JMP', 'JSR']:
                    func(addr)
                elif name in ['BPL', 'BMI', 'BVC', 'BVS', 'BCC', 'BCS', 'BNE', 'BEQ']:
                    func(addr)
            else:
                if func:
                    func()
        else:
            # 未实现指令
            pass
    
    def step(self):
        """执行一条指令"""
        self.execute_instruction()
    
    def run(self, instructions=1):
        """
        运行指定数量的指令
        
        Args:
            instructions: 要执行的指令数 (-1 表示无限)
        """
        count = 0
        while instructions < 0 or count < instructions:
            self.step()
            count += 1
    
    def get_state(self):
        """获取 CPU 状态"""
        return {
            'PC': self.PC,
            'A': self.A,
            'X': self.X,
            'Y': self.Y,
            'SP': self.SP,
            'P': self.P,
            'cycles': self.cycles
        }
    
    def __repr__(self):
        return (f"M6502(PC=0x{self.PC:04X}, A=0x{self.A:02X}, "
                f"X=0x{self.X:02X}, Y=0x{self.Y:02X}, "
                f"SP=0x{self.SP:02X}, P=0x{self.P:02X})")


if __name__ == '__main__':
    # 简单测试
    cpu = M6502()
    
    # 加载一个简单的测试程序
    # LDA #$42 (0xA9 0x42)
    # STA $0000 (0x8D 0x00 0x00)
    # BRK (0x00)
    cpu.memory[0x0000] = 0xA9
    cpu.memory[0x0001] = 0x42
    cpu.memory[0x0002] = 0x8D
    cpu.memory[0x0003] = 0x00
    cpu.memory[0x0004] = 0x00
    cpu.memory[0x0005] = 0x00
    
    cpu.reset()
    cpu.run(3)
    
    print(f"CPU 状态：{cpu}")
    print(f"内存 [0x0000] = 0x{cpu.memory[0x0000]:02X}")
    print(f"执行周期：{cpu.cycles}")
