#!/usr/bin/env python3
"""
tests/test_all.py - Tempest 矿工测试套件

运行所有测试以验证功能正常。
"""

import sys
from pathlib import Path

# 添加父目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))


def test_cpu():
    """测试 6502 CPU 模拟器"""
    print("\n[TEST] 6502 CPU 模拟器...")
    
    from m6502_cpu import M6502
    
    cpu = M6502()
    
    # 设置复位向量为 0x0000
    cpu.memory[0xFFFC] = 0x00
    cpu.memory[0xFFFD] = 0x00
    
    # 测试 LDA/STA
    cpu.memory[0x0000] = 0xA9  # LDA #$FF
    cpu.memory[0x0001] = 0xFF
    cpu.memory[0x0002] = 0x8D  # STA $0100
    cpu.memory[0x0003] = 0x00
    cpu.memory[0x0004] = 0x01
    cpu.memory[0x0005] = 0xEA  # NOP
    
    cpu.reset()
    cpu.run(3)
    
    assert cpu.A == 0xFF, f"Expected A=0xFF, got 0x{cpu.A:02X}"
    assert cpu.memory[0x0100] == 0xFF, f"Expected mem[0x0100]=0xFF"
    
    print("  [PASS] LDA/STA 测试")
    
    # 测试算术运算
    cpu.reset()
    cpu.A = 0x10
    cpu.memory[0x0000] = 0x69  # ADC #$20
    cpu.memory[0x0001] = 0x20
    cpu.memory[0x0002] = 0xEA  # NOP
    
    cpu.run(2)
    
    assert cpu.A == 0x30, f"Expected A=0x30, got 0x{cpu.A:02X}"
    
    print("  [PASS] ADC 测试")
    
    # 测试分支
    cpu.reset()
    cpu.memory[0x0000] = 0xA2  # LDX #$05
    cpu.memory[0x0001] = 0x05
    cpu.memory[0x0002] = 0xCA  # DEX
    cpu.memory[0x0003] = 0xD0  # BNE -2 (跳回 DEX)
    cpu.memory[0x0004] = 0xFE
    cpu.memory[0x0005] = 0xEA  # NOP
    
    # LDX(1) + [DEX(1) + BNE(1)]×5 + NOP(1) = 1 + 10 + 1 = 12
    cpu.run(12)
    
    assert cpu.X == 0x00, f"Expected X=0x00, got 0x{cpu.X:02X}"
    
    print("  [PASS] 分支测试")
    
    print("  [OK] 6502 CPU 测试通过!\n")
    return True


def test_hardware():
    """测试 Tempest 硬件抽象层"""
    print("[TEST] Tempest 硬件抽象层...")
    
    from tempest_hardware import TempestHardware
    
    hardware = TempestHardware()
    
    # 测试硬件 ID 生成
    assert len(hardware.hardware_id) == 16, "Hardware ID should be 16 chars"
    print(f"  [PASS] 硬件 ID: {hardware.hardware_id}")
    
    # 测试内存读写
    hardware.cpu.write_byte(0x0100, 0x42)
    assert hardware.cpu.read_byte(0x0100) == 0x42
    print("  [PASS] RAM 读写测试")
    
    # 测试硬件寄存器
    hardware.write_memory(0xC000, 0x55)  # Pokey 寄存器
    assert hardware.read_memory(0xC000) == 0x55
    print("  [PASS] Pokey 寄存器测试")
    
    # 测试指纹生成
    fp = hardware.get_fingerprint()
    assert 'hash' in fp
    assert 'data' in fp
    assert len(fp['hash']) == 64  # SHA-256
    print(f"  [PASS] 指纹生成：{fp['hash'][:16]}...")
    
    # 测试 attestation 准备
    hardware.set_wallet("RTC123456789")
    attestation = hardware.prepare_attestation()
    assert attestation['cpu_type'] == 'Motorola 6502'
    assert attestation['wallet'] == "RTC123456789"
    print("  [PASS] Attestation 准备")
    
    print("  [OK] Tempest 硬件测试通过!\n")
    return True


def test_miner():
    """测试矿工核心功能"""
    print("[TEST] 矿工核心功能...")
    
    from tempest_hardware import TempestMiner
    
    wallet = "RTC4325af95d26d59c3ef025963656d22af638bb96b"
    miner = TempestMiner(wallet)
    
    # 测试启动
    miner.start()
    assert miner.running == True
    print("  [PASS] 矿工启动")
    
    # 测试奖励计算
    reward = miner.calculate_reward(base_reward=1.5, active_miners=10)
    expected = (1.5 / 10) * 3.0 * 1.5 * 1.25  # 0.84375
    assert abs(reward - expected) < 0.0001, f"Expected {expected}, got {reward}"
    print(f"  [PASS] 奖励计算：{reward:.4f} RTC")
    
    # 测试 epoch 运行
    miner.run_epoch(epoch_duration=1)
    assert miner.stats['epochs_completed'] == 1
    assert miner.stats['attestations_submitted'] == 1
    print("  [PASS] Epoch 运行")
    
    # 测试统计
    stats = miner.get_stats()
    assert 'rtc_earned' in stats
    assert 'uptime_seconds' in stats
    print("  [PASS] 统计获取")
    
    # 测试停止
    miner.stop()
    assert miner.running == False
    print("  [PASS] 矿工停止")
    
    print("  [OK] 矿工核心功能测试通过!\n")
    return True


def test_integration():
    """集成测试"""
    print("[TEST] 集成测试...")
    
    from tempest_hardware import TempestMiner
    import time
    
    wallet = "RTC4325af95d26d59c3ef025963656d22af638bb96b"
    miner = TempestMiner(wallet)
    
    # 运行 3 个快速 epoch
    miner.start()
    for i in range(3):
        miner.run_epoch(epoch_duration=1)
    
    # 验证统计
    stats = miner.get_stats()
    assert stats['epochs_completed'] == 3
    assert stats['attestations_submitted'] == 3
    assert stats['rtc_earned'] > 0
    
    miner.stop()
    
    print(f"  [PASS] 集成测试：3 epochs, {stats['rtc_earned']:.4f} RTC")
    print("  [OK] 集成测试通过!\n")
    return True


def main():
    """运行所有测试"""
    print("\n" + "="*60)
    print("  TEMPEST MINER - 测试套件")
    print("="*60 + "\n")
    
    tests = [
        ("6502 CPU", test_cpu),
        ("Tempest 硬件", test_hardware),
        ("矿工核心", test_miner),
        ("集成测试", test_integration),
    ]
    
    passed = 0
    failed = 0
    
    for name, test_func in tests:
        try:
            if test_func():
                passed += 1
        except Exception as e:
            print(f"  [FAIL] {name}: {e}\n")
            failed += 1
    
    print("="*60)
    print(f"  测试结果：{passed} 通过，{failed} 失败")
    print("="*60 + "\n")
    
    return failed == 0


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
