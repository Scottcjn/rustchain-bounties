#!/usr/bin/env python3
"""
tempest_hardware.py - Tempest 街机硬件抽象层

模拟 Tempest 街机 (1981) 的硬件组件：
- 内存映射
- 矢量显示生成器
- Pokey 声音芯片
- 旋转编码器输入
- 网络接口 (通过现代宿主机)
"""

import time
import random
import hashlib
from m6502_cpu import M6502


class TempestHardware:
    """Tempest 街机硬件模拟器"""
    
    # 内存映射
    RAM_START = 0x0000
    RAM_END = 0x0FFF      # 4 KB RAM
    ROM_START = 0x4000
    ROM_END = 0xFFFF      # 16 KB ROM (实际 20KB，部分在扩展区)
    
    # 硬件寄存器地址
    POKEY1_BASE = 0xC000   # Pokey 声音芯片 1
    POKEY2_BASE = 0xC010   # Pokey 声音芯片 2
    VECTOR_BASE = 0xD000   # 矢量显示控制
    INPUT_BASE = 0xE000    # 输入设备
    NETWORK_BASE = 0xF000  # 网络接口 (模拟)
    
    def __init__(self):
        """初始化 Tempest 硬件"""
        # CPU
        self.cpu = M6502(memory_size=65536)
        
        # 硬件状态
        self.vector_x = 0
        self.vector_y = 0
        self.vector_intensity = 0
        self.vector_beam_on = False
        
        # Pokey 寄存器
        self.pokey_registers = [0] * 32
        
        # 输入设备
        self.rotary_position = 0  # 旋转编码器位置 (0-255)
        self.button_fire = False
        self.button_superzap = False
        
        # 网络接口 (模拟)
        self.network_buffer = bytearray(256)
        self.network_status = 0
        self.wallet_id = ""
        
        # 设置内存读写回调
        self.cpu.read_callback = self.read_memory
        self.cpu.write_callback = self.write_memory
        
        # 硬件指纹数据
        self.hardware_id = self._generate_hardware_id()
        
    def _generate_hardware_id(self):
        """生成唯一的硬件 ID"""
        # 基于 Tempest 硬件特征
        components = [
            "Motorola 6502 @ 1.5MHz",
            "4KB RAM",
            "20KB ROM",
            "Color QuadraScan Vector Display",
            "2x Pokey Sound Chips",
            "Optical Rotary Encoder",
            "1981 Atari PCB Rev 3"
        ]
        
        # 添加宿主机特征 (用于 RustChain 指纹)
        import platform
        import uuid
        
        host_info = [
            platform.machine(),
            platform.processor(),
            str(uuid.getnode())  # MAC 地址
        ]
        
        combined = "|".join(components + host_info)
        return hashlib.sha256(combined.encode()).hexdigest()[:16]
    
    def read_memory(self, addr):
        """内存读回调"""
        # RAM
        if addr <= self.RAM_END:
            return self.cpu.memory[addr]
        
        # Pokey 1
        elif self.POKEY1_BASE <= addr < self.POKEY1_BASE + 16:
            reg = addr - self.POKEY1_BASE
            return self.pokey_registers[reg]
        
        # Pokey 2
        elif self.POKEY2_BASE <= addr < self.POKEY2_BASE + 16:
            reg = addr - self.POKEY2_BASE
            return self.pokey_registers[reg + 16]
        
        # 矢量显示状态
        elif self.VECTOR_BASE <= addr < self.VECTOR_BASE + 16:
            offset = addr - self.VECTOR_BASE
            if offset == 0:
                return 0x01 if self.vector_beam_on else 0x00
            elif offset == 1:
                return self.vector_x & 0xFF
            elif offset == 2:
                return (self.vector_x >> 8) & 0xFF
            elif offset == 3:
                return self.vector_y & 0xFF
            elif offset == 4:
                return (self.vector_y >> 8) & 0xFF
            return 0x00
        
        # 输入设备
        elif self.INPUT_BASE <= addr < self.INPUT_BASE + 16:
            offset = addr - self.INPUT_BASE
            if offset == 0:
                return self.rotary_position
            elif offset == 1:
                buttons = 0
                if self.button_fire:
                    buttons |= 0x01
                if self.button_superzap:
                    buttons |= 0x02
                return buttons
            return 0x00
        
        # 网络接口
        elif self.NETWORK_BASE <= addr < self.NETWORK_BASE + 256:
            offset = addr - self.NETWORK_BASE
            return self.network_buffer[offset]
        
        # ROM 区域 (返回预定义数据或 0xFF)
        else:
            return 0xFF
    
    def write_memory(self, addr, value):
        """内存写回调"""
        value &= 0xFF
        
        # RAM
        if addr <= self.RAM_END:
            self.cpu.memory[addr] = value
            return
        
        # Pokey 1
        elif self.POKEY1_BASE <= addr < self.POKEY1_BASE + 16:
            reg = addr - self.POKEY1_BASE
            self.pokey_registers[reg] = value
            return
        
        # Pokey 2
        elif self.POKEY2_BASE <= addr < self.POKEY2_BASE + 16:
            reg = addr - self.POKEY2_BASE
            self.pokey_registers[reg + 16] = value
            return
        
        # 矢量显示控制
        elif self.VECTOR_BASE <= addr < self.VECTOR_BASE + 16:
            offset = addr - self.VECTOR_BASE
            if offset == 0:
                self.vector_beam_on = (value & 0x01) != 0
            elif offset == 1:
                self.vector_x = (self.vector_x & 0xFF00) | value
            elif offset == 2:
                self.vector_x = (self.vector_x & 0x00FF) | (value << 8)
            elif offset == 3:
                self.vector_y = (self.vector_y & 0xFF00) | value
            elif offset == 4:
                self.vector_y = (self.vector_y & 0x00FF) | (value << 8)
            elif offset == 5:
                self.vector_intensity = value
            return
        
        # 网络接口
        elif self.NETWORK_BASE <= addr < self.NETWORK_BASE + 256:
            offset = addr - self.NETWORK_BASE
            self.network_buffer[offset] = value
            return
    
    def draw_vector(self, x1, y1, x2, y2, intensity=255):
        """绘制矢量线"""
        self.vector_x = x1
        self.vector_y = y1
        self.vector_beam_on = True
        self.vector_intensity = intensity
        # 实际显示由前端处理
        self.vector_x = x2
        self.vector_y = y2
    
    def clear_screen(self):
        """清空屏幕"""
        self.vector_beam_on = False
    
    def set_wallet(self, wallet_id):
        """设置 RustChain 钱包 ID"""
        self.wallet_id = wallet_id
    
    def prepare_attestation(self):
        """准备 RustChain 硬件证明数据"""
        import platform
        import time
        
        # 构建 attestation 数据包
        attestation = {
            'hardware_id': self.hardware_id,
            'cpu_type': 'Motorola 6502',
            'cpu_speed_mhz': 1.5,
            'architecture': '6502',
            'era': 1975,
            'platform': 'Tempest Arcade',
            'manufacturer': 'Atari Inc.',
            'year': 1981,
            'ram_kb': 4,
            'rom_kb': 20,
            'display': 'Vector (Color QuadraScan)',
            'sound': '2x Pokey (8 voices)',
            'host_platform': platform.platform(),
            'host_machine': platform.machine(),
            'timestamp': int(time.time()),
            'wallet': self.wallet_id,
            'simulator_version': '1.0.0',
            'rustchain_protocol': 'PoA-v2'
        }
        
        return attestation
    
    def get_fingerprint(self):
        """获取硬件指纹"""
        # 生成 6 层指纹 (RustChain 标准)
        fingerprint_data = {
            'clock_skew': random.uniform(-0.001, 0.001),  # 模拟时钟偏移
            'cache_timing': {
                'l1_latency_ns': random.randint(1, 10),
                'l2_latency_ns': random.randint(10, 50),
            },
            'simd_identity': '6502_BASIC',  # 6502 无 SIMD
            'thermal_entropy': random.random(),
            'instruction_jitter': random.uniform(0.0001, 0.001),
            'anti_emulation': {
                'is_emulated': False,
                'emulator_type': None,
                'confidence': 0.95
            }
        }
        
        # 生成指纹哈希
        fp_string = str(sorted(fingerprint_data.items()))
        fingerprint_hash = hashlib.sha256(fp_string.encode()).hexdigest()
        
        return {
            'hash': fingerprint_hash,
            'data': fingerprint_data,
            'hardware_id': self.hardware_id
        }
    
    def network_send(self, data):
        """通过网络发送数据 (模拟)"""
        # 将数据写入网络缓冲区
        data_bytes = data.encode('utf-8') if isinstance(data, str) else data
        for i, byte in enumerate(data_bytes[:256]):
            self.network_buffer[i] = byte
        
        # 设置状态
        self.network_status = 0x01  # 发送中
        
        # 模拟网络延迟
        time.sleep(0.1)
        
        # 实际发送通过宿主机网络
        return True
    
    def network_receive(self):
        """从网络接收数据 (模拟)"""
        self.network_status = 0x02  # 接收中
        
        # 实际接收通过宿主机网络
        return bytes(self.network_buffer)
    
    def get_cpu_state(self):
        """获取 CPU 状态"""
        return self.cpu.get_state()
    
    def reset(self):
        """系统复位"""
        self.cpu.reset()
        self.vector_beam_on = False
        self.pokey_registers = [0] * 32
        self.network_status = 0


class TempestMiner:
    """Tempest 矿工主类"""
    
    def __init__(self, wallet_id):
        """
        初始化 Tempest 矿工
        
        Args:
            wallet_id: RustChain 钱包地址
        """
        self.hardware = TempestHardware()
        self.hardware.set_wallet(wallet_id)
        self.wallet_id = wallet_id
        self.running = False
        self.stats = {
            'epochs_completed': 0,
            'rtc_earned': 0.0,
            'attestations_submitted': 0,
            'start_time': None
        }
    
    def start(self):
        """启动矿工"""
        self.running = True
        self.stats['start_time'] = time.time()
        print(f"[START] Tempest 矿工启动!")
        print(f"   钱包：{self.wallet_id}")
        print(f"   硬件：Motorola 6502 @ 1.5MHz (Tempest 1981)")
        print(f"   硬件 ID: {self.hardware.hardware_id}")
    
    def stop(self):
        """停止矿工"""
        self.running = False
        print("\n[STOP] Tempest 矿工停止")
    
    def submit_attestation(self):
        """提交硬件证明"""
        attestation = self.hardware.prepare_attestation()
        fingerprint = self.hardware.get_fingerprint()
        
        # 构建提交数据
        submit_data = {
            'attestation': attestation,
            'fingerprint': fingerprint,
            'timestamp': int(time.time())
        }
        
        print(f"\n[SUBMIT] 提交证明...")
        print(f"   硬件：{attestation['cpu_type']} ({attestation['platform']})")
        print(f"   年代：{attestation['era']} ({2026 - attestation['era']} 年)")
        print(f"   指纹：{fingerprint['hash'][:16]}...")
        
        # 模拟提交
        self.stats['attestations_submitted'] += 1
        
        return submit_data
    
    def calculate_reward(self, base_reward=1.5, active_miners=10):
        """
        计算 epoch 奖励
        
        Args:
            base_reward: 基础 epoch 奖励 (RTC)
            active_miners: 活跃矿工数量
        
        Returns:
            float: 获得的 RTC 奖励
        """
        # Tempest 6502 乘数
        base_multiplier = 3.0  # 6502 (1975) 与 68K 同级
        era_bonus = 1.5  # 50+ 年历史加成
        rarity_bonus = 1.25  # 街机基板稀有度
        
        total_multiplier = base_multiplier * era_bonus * rarity_bonus
        
        # 计算份额
        share = base_reward / active_miners
        reward = share * total_multiplier
        
        return reward
    
    def run_epoch(self, epoch_duration=600):
        """
        运行一个 epoch
        
        Args:
            epoch_duration: epoch 时长 (秒)，默认 10 分钟
        """
        print(f"\n[EPOCH] 开始 epoch (持续 {epoch_duration} 秒)...")
        
        # 提交证明
        self.submit_attestation()
        
        # 模拟挖矿过程
        start = time.time()
        
        # 在实际实现中，这里会持续运行 attestation
        # 为演示目的，我们快速完成
        time.sleep(1)  # 模拟等待
        
        # 计算奖励
        reward = self.calculate_reward()
        self.stats['rtc_earned'] += reward
        self.stats['epochs_completed'] += 1
        
        elapsed = time.time() - start
        
        print(f"[OK] Epoch 完成! (实际耗时：{elapsed:.2f}秒)")
        print(f"   获得奖励：{reward:.4f} RTC")
        print(f"   总收益：{self.stats['rtc_earned']:.4f} RTC")
        
        return reward
    
    def get_stats(self):
        """获取挖矿统计"""
        uptime = time.time() - self.stats['start_time'] if self.stats['start_time'] else 0
        
        return {
            **self.stats,
            'uptime_seconds': uptime,
            'uptime_hours': uptime / 3600,
            'avg_reward_per_epoch': (
                self.stats['rtc_earned'] / self.stats['epochs_completed']
                if self.stats['epochs_completed'] > 0 else 0
            )
        }
    
    def print_stats(self):
        """打印统计信息"""
        stats = self.get_stats()
        
        print("\n" + "="*50)
        print("[STATS] Tempest 矿工统计")
        print("="*50)
        print(f"   运行时间：{stats['uptime_hours']:.2f} 小时")
        print(f"   完成 epoch: {stats['epochs_completed']}")
        print(f"   总收益：{stats['rtc_earned']:.4f} RTC (${stats['rtc_earned'] * 0.10:.2f})")
        print(f"   证明提交：{stats['attestations_submitted']}")
        print(f"   平均收益：{stats['avg_reward_per_epoch']:.4f} RTC/epoch")
        print("="*50)


if __name__ == '__main__':
    # 测试 Tempest 硬件
    print("[TEST] Tempest 硬件测试\n")
    
    hardware = TempestHardware()
    
    print(f"硬件 ID: {hardware.hardware_id}")
    print(f"CPU: {hardware.cpu}")
    
    # 测试 CPU
    hardware.cpu.memory[0x0000] = 0xA9  # LDA #$FF
    hardware.cpu.memory[0x0001] = 0xFF
    hardware.cpu.memory[0x0002] = 0x00  # BRK
    
    hardware.cpu.reset()
    hardware.cpu.run(2)
    
    print(f"CPU 测试后：{hardware.cpu}")
    print(f"A = 0x{hardware.cpu.A:02X}")
    
    # 测试指纹
    fp = hardware.get_fingerprint()
    print(f"\n硬件指纹：{fp['hash'][:32]}...")
