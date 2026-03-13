#!/usr/bin/env python3
"""
SWAC Miner 主入口
Standards Western Automatic Computer - SHA256 挖矿器

钱包：RTC4325af95d26d59c3ef025963656d22af638bb96b
"""

import sys
import os
import argparse

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from swac_simulator import SWACSimulator
from mcu_bridge import MCUBridge, MiningTask


def print_banner():
    """打印欢迎横幅"""
    print("=" * 60)
    print("  SWAC Miner - Standards Western Automatic Computer")
    print("  1950 架构 × 2026 挖矿")
    print("=" * 60)
    print(f"  钱包：RTC4325af95d26d59c3ef025963656d22af638bb96b")
    print(f"  内存：256 字 × 37 位")
    print(f"  奖励：200 RTC ($20) - LEGENDARY Tier")
    print("=" * 60)


def run_demo():
    """运行演示模式"""
    print("\n运行演示模式...\n")
    
    sim = SWACSimulator()
    
    print("SWAC 模拟器初始化:")
    print(f"  内存大小：{len(sim.memory)} 字")
    print(f"  字长：37 位")
    print(f"  初始 PC: {sim.pc}")
    
    print("\n初始哈希状态 (H0-H7):")
    for i, h in enumerate(sim.get_hash_state()):
        print(f"  H{i}: {h:08X}")
    
    print("\nK 常量前 8 个:")
    for i in range(8):
        print(f"  K{i}: {sim.memory[32 + i]:08X}")
    
    print("\n内存布局:")
    print("  0-31:   程序代码")
    print("  32-63:  SHA256 K 常量")
    print("  64-71:  哈希状态")
    print("  72-79:  工作变量")
    print("  80-143: 消息调度 W 表")
    print("  144-191:临时存储")
    print("  192-223:栈区")
    print("  224-255:I/O 缓冲区")
    
    print("\n演示完成!")


def run_test():
    """运行测试套件"""
    print("\n运行测试套件...\n")
    
    import subprocess
    result = subprocess.run([sys.executable, "test_swac.py"], 
                          capture_output=False)
    
    if result.returncode == 0:
        print("\n所有测试通过!")
    else:
        print("\n部分测试失败，请查看 IMPLEMENTATION.md")


def run_mine(args):
    """运行挖矿"""
    print(f"\n启动挖矿模式...")
    print(f"  矿池：{args.pool}")
    print(f"  端口：{args.port}")
    print(f"  Worker: {args.worker}")
    
    # 创建桥接
    bridge = MCUBridge(port=args.port_serial)
    
    if not bridge.connect():
        print("  使用软件模拟器模式")
    
    print("\n挖矿已启动 (演示模式)")
    print("  注意：需要配置实际矿池参数")
    print("  参考：network_bridge.py")


def main():
    parser = argparse.ArgumentParser(
        description="SWAC Miner - 1950 架构 SHA256 挖矿器"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="命令")
    
    # 演示命令
    demo_parser = subparsers.add_parser("demo", help="运行演示")
    
    # 测试命令
    test_parser = subparsers.add_parser("test", help="运行测试")
    
    # 挖矿命令
    mine_parser = subparsers.add_parser("mine", help="开始挖矿")
    mine_parser.add_argument("--pool", default="pool.example.com",
                            help="矿池地址")
    mine_parser.add_argument("--port", type=int, default=3333,
                            help="矿池端口")
    mine_parser.add_argument("--worker", default="swac-001",
                            help="Worker 名称")
    mine_parser.add_argument("--port-serial", default="COM3",
                            help="串口端口 (MCU)")
    
    args = parser.parse_args()
    
    print_banner()
    
    if args.command == "demo" or args.command is None:
        run_demo()
    elif args.command == "test":
        run_test()
    elif args.command == "mine":
        run_mine(args)
    else:
        parser.print_help()
    
    print("\n" + "=" * 60)
    print("SWAC Miner 完成")
    print("=" * 60)


if __name__ == "__main__":
    main()
