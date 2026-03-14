#!/usr/bin/env python3
"""
examples/mining_demo.py - Tempest 矿工挖矿演示

展示如何在 Tempest 街机上运行 RustChain 矿工。
"""

import sys
import time
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from tempest_hardware import TempestMiner


def print_header(text):
    """打印标题"""
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def demo_basic_mining():
    """基础挖矿演示"""
    print_header("基础挖矿演示")
    
    wallet = "RTC4325af95d26d59c3ef025963656d22af638bb96b"
    miner = TempestMiner(wallet)
    
    print(f"\n钱包地址：{wallet}")
    print(f"硬件：Tempest Arcade (1981)")
    print(f"CPU: Motorola 6502 @ 1.5MHz")
    
    # 启动
    miner.start()
    
    # 运行 3 个 epoch
    for i in range(3):
        print(f"\n⛏️  Epoch {i+1}/3")
        miner.run_epoch(epoch_duration=1)
        time.sleep(0.5)
    
    # 统计
    miner.print_stats()
    miner.stop()


def demo_hardware_fingerprint():
    """硬件指纹演示"""
    print_header("硬件指纹演示")
    
    from tempest_hardware import TempestHardware
    
    hardware = TempestHardware()
    
    print("\n📋 Tempest 硬件信息:\n")
    print(f"  硬件 ID: {hardware.hardware_id}")
    print(f"  CPU: Motorola 6502")
    print(f"  时钟：1.5 MHz")
    print(f"  RAM: 4 KB")
    print(f"  ROM: 20 KB")
    
    print("\n🔍 指纹数据:\n")
    fingerprint = hardware.get_fingerprint()
    
    print(f"  哈希：{fingerprint['hash']}")
    print(f"\n  详细数据:")
    print(f"    时钟偏移：{fingerprint['data']['clock_skew']:.6f}")
    print(f"    L1 延迟：{fingerprint['data']['cache_timing']['l1_latency_ns']} ns")
    print(f"    L2 延迟：{fingerprint['data']['cache_timing']['l2_latency_ns']} ns")
    print(f"    SIMD: {fingerprint['data']['simd_identity']}")
    print(f"    热熵：{fingerprint['data']['thermal_entropy']:.6f}")
    print(f"    指令抖动：{fingerprint['data']['instruction_jitter']:.6f}")
    print(f"    反模拟置信度：{fingerprint['data']['anti_emulation']['confidence']*100:.1f}%")
    
    print("\n📊 乘数计算:\n")
    base = 3.0  # 6502
    era = 1.5   # 50+ 年
    rarity = 1.25  # 街机
    total = base * era * rarity
    
    print(f"  基础乘数 (6502): {base}x")
    print(f"  年代加成 (50+ 年): {era}x")
    print(f"  稀有度加成 (街机): {rarity}x")
    print(f"  ─────────────────────")
    print(f"  总乘数：{total}x")


def demo_cpu_simulation():
    """CPU 模拟演示"""
    print_header("6502 CPU 模拟演示")
    
    from m6502_cpu import M6502
    
    cpu = M6502()
    
    print("\n📋 6502 CPU 状态:\n")
    print(f"  初始状态：{cpu}")
    
    # 加载测试程序
    print("\n📝 加载测试程序:\n")
    print("  0x0000: LDA #$42    ; 加载 0x42 到 A")
    print("  0x0002: STA $0100   ; 存储 A 到 $0100")
    print("  0x0005: LDX #$05    ; 加载 5 到 X")
    print("  0x0007: LOOP: DEX   ; X = X - 1")
    print("  0x0008: BNE LOOP    ; 如果 X != 0 则跳转")
    print("  0x000A: BRK         ; 中断")
    
    # 编写程序到内存
    program = [
        0xA9, 0x42,       # LDA #$42
        0x8D, 0x00, 0x01, # STA $0100
        0xA2, 0x05,       # LDX #$05
        0xCA,             # DEX
        0xD0, 0xFD,       # BNE LOOP (-3)
        0x00              # BRK
    ]
    
    for i, byte in enumerate(program):
        cpu.memory[i] = byte
    
    # 运行
    print("\n▶️  执行 CPU...\n")
    cpu.reset()
    cpu.run(20)  # 运行最多 20 条指令
    
    print(f"  最终状态：{cpu}")
    print(f"  执行周期：{cpu.cycles}")
    print(f"  内存 [$0100] = 0x{cpu.memory[0x0100]:02X}")
    print(f"  X 寄存器 = 0x{cpu.X:02X}")


def demo_reward_calculation():
    """奖励计算演示"""
    print_header("奖励计算演示")
    
    print("\n💰 RustChain Epoch 奖励计算\n")
    
    base_reward = 1.5  # RTC per epoch
    print(f"基础 epoch 奖励：{base_reward} RTC")
    
    scenarios = [
        (1, 1.5),
        (5, 0.3),
        (10, 0.15),
        (50, 0.03),
        (100, 0.015),
    ]
    
    print(f"\n{'矿工数':<10} {'份额':<10} {'Tempest 收益':<15} {'USD 价值':<10}")
    print("─" * 50)
    
    multiplier = 3.0 * 1.5 * 1.25  # 5.625x
    
    for miners, share in scenarios:
        tempest_reward = share * multiplier
        usd_value = tempest_reward * 0.10
        print(f"{miners:<10} {share:<10.4f} {tempest_reward:<15.4f} ${usd_value:<9.2f}")
    
    print("\n📈 日收益估算 (144 epochs/天):\n")
    
    for miners, share in [(10, 0.15), (50, 0.03), (100, 0.015)]:
        daily_rtc = share * multiplier * 144
        daily_usd = daily_rtc * 0.10
        monthly_usd = daily_usd * 30
        print(f"  {miners} 矿工：{daily_rtc:.2f} RTC/天 (${daily_usd:.2f}/天, ${monthly_usd:.2f}/月)")


def main():
    """主演示"""
    print("\n")
    print("╔═══════════════════════════════════════════════════════════╗")
    print("║                                                           ║")
    print("║   🎮 TEMPEST MINER - Mining Demo                         ║")
    print("║      RustChain Proof of Antiquity                        ║")
    print("║                                                           ║")
    print("╚═══════════════════════════════════════════════════════════╝")
    
    try:
        # 运行所有演示
        demo_basic_mining()
        demo_hardware_fingerprint()
        demo_cpu_simulation()
        demo_reward_calculation()
        
        print("\n" + "=" * 60)
        print("  ✅ 所有演示完成!")
        print("=" * 60 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  演示中断\n")


if __name__ == '__main__':
    main()
