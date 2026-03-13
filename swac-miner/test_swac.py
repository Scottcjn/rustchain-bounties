#!/usr/bin/env python3
"""
SWAC Miner 测试套件
验证 SWAC 模拟器和 SHA256 实现
"""

import hashlib
import sys
import os

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from swac_simulator import SWACSimulator


def test_sha256_empty():
    """测试空字符串的 SHA256"""
    expected = hashlib.sha256(b"").hexdigest()
    
    sim = SWACSimulator()
    
    # 空消息的 SHA256 预处理块
    # 0x80 后跟填充和长度
    empty_block = bytes([0x80]) + bytes([0x00] * 55) + bytes([0x00] * 7) + bytes([0x00])
    
    # 加载消息块
    words = []
    for i in range(0, 64, 4):
        word = int.from_bytes(empty_block[i:i+4], 'big')
        words.append(word)
    
    sim.load_data(words, 80)  # 消息调度区
    
    # 运行模拟
    sim.run(max_cycles=10000)
    
    # 获取结果
    result = sim.get_hash_state()
    result_hex = ''.join(f'{h:08x}' for h in result)
    
    print(f"空字符串测试:")
    print(f"  期望：{expected}")
    print(f"  结果：{result_hex}")
    print(f"  状态：{'[PASS]' if expected == result_hex else '[FAIL]'}")
    
    return expected == result_hex


def test_sha256_abc():
    """测试 "abc" 的 SHA256"""
    expected = hashlib.sha256(b"abc").hexdigest()
    
    # "abc" 的 SHA256 预处理块
    # abc = 0x61626300
    # 填充：0x80 + 零 + 长度 (24 位 = 0x18)
    abc_block = (
        bytes([0x61, 0x62, 0x63, 0x80]) +  # "abc" + 0x80
        bytes([0x00] * 52) +                # 填充
        bytes([0x00] * 7) +                 # 高 7 字节长度
        bytes([0x18])                       # 24 位 = 3 字节 * 8
    )
    
    sim = SWACSimulator()
    
    # 加载消息块
    words = []
    for i in range(0, 64, 4):
        word = int.from_bytes(abc_block[i:i+4], 'big')
        words.append(word)
    
    sim.load_data(words, 80)
    
    # 运行模拟
    sim.run(max_cycles=10000)
    
    # 获取结果
    result = sim.get_hash_state()
    result_hex = ''.join(f'{h:08x}' for h in result)
    
    print(f"\n'abc' 测试:")
    print(f"  期望：{expected}")
    print(f"  结果：{result_hex}")
    print(f"  状态：{'[PASS]' if expected == result_hex else '[FAIL]'}")
    
    return expected == result_hex


def test_memory_layout():
    """测试内存布局"""
    sim = SWACSimulator()
    
    print(f"\n内存布局测试:")
    print(f"  K 常量区 (32-63): {'[OK]' if sim.memory[32] == 0x428a2f98 else '[FAIL]'}")
    print(f"  H0 初始值 (64): {'[OK]' if sim.memory[64] == 0x6a09e667 else '[FAIL]'}")
    print(f"  H7 初始值 (71): {'[OK]' if sim.memory[71] == 0x5be0cd19 else '[FAIL]'}")
    
    # 验证所有初始哈希值
    h_init = [
        0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a,
        0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19,
    ]
    
    all_correct = True
    for i, expected in enumerate(h_init):
        if sim.memory[64 + i] != expected:
            all_correct = False
            print(f"  H{i} 错误：期望 {expected:08X}, 实际 {sim.memory[64 + i]:08X}")
    
    return all_correct


def test_instruction_set():
    """测试指令集"""
    sim = SWACSimulator()
    
    # 简单程序：加载值，加法，存储
    program = [
        0x40000040,  # LD 64 (加载 H0)
        0x00000041,  # ADD 65 (加 H1)
        0x500000C0,  # ST 192 (存储到临时区)
    ]
    
    sim.load_program(program, start_addr=0)
    sim.run(max_cycles=10)
    
    expected = (0x6a09e667 + 0xbb67ae85) & 0x1FFFFFFFF
    actual = sim.memory[192]
    
    print(f"\n指令集测试:")
    print(f"  期望：{expected:011X}")
    print(f"  实际：{actual:011X}")
    print(f"  状态：{'[PASS]' if expected == actual else '[FAIL]'}")
    
    return expected == actual


def run_all_tests():
    """运行所有测试"""
    print("=" * 60)
    print("SWAC Miner 测试套件")
    print("=" * 60)
    print(f"钱包：RTC4325af95d26d59c3ef025963656d22af638bb96b")
    print("=" * 60)
    
    results = []
    
    results.append(("内存布局", test_memory_layout()))
    results.append(("指令集", test_instruction_set()))
    results.append(("SHA256 空字符串", test_sha256_empty()))
    results.append(("SHA256 'abc'", test_sha256_abc()))
    
    print("\n" + "=" * 60)
    print("测试结果汇总:")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {name}: {status}")
    
    print(f"\n总计：{passed}/{total} 通过")
    print("=" * 60)
    
    return passed == total


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
