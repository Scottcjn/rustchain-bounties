#!/usr/bin/env python3
"""
Pole Position Miner - 主程序
RustChain 矿工移植到 Pole Position 街机 (1982)

使用方法:
    python main.py --wallet RTC4325af95d26d59c3ef025963656d22af638bb96b

奖励：200 RTC ($20) - LEGENDARY Tier!
"""

import argparse
import sys
import time
from simulator import Z80CPU, MinerCore, TextVisualizer, ArcadeScreenVisualizer


def parse_args():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description='Pole Position Miner - RustChain on Z80 (1982 Arcade)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py --wallet RTC4325af95d26d59c3ef025963656d22af638bb96b
  python main.py --wallet YOUR_WALLET --difficulty 500
  python main.py --demo

Wallet for bounty: RTC4325af95d26d59c3ef025963656d22af638bb96b
        """
    )
    
    parser.add_argument(
        '--wallet', '-w',
        type=str,
        default='RTC4325af95d26d59c3ef025963656d22af638bb96b',
        help='RustChain wallet address (default: bounty wallet)'
    )
    
    parser.add_argument(
        '--difficulty', '-d',
        type=int,
        default=1000,
        help='Mining difficulty (default: 1000)'
    )
    
    parser.add_argument(
        '--max-nonces', '-n',
        type=int,
        default=100000,
        help='Maximum nonces to try per block (default: 100000)'
    )
    
    parser.add_argument(
        '--blocks', '-b',
        type=int,
        default=0,
        help='Number of blocks to mine (0 = continuous, default: 0)'
    )
    
    parser.add_argument(
        '--visualizer', '-v',
        type=str,
        choices=['text', 'arcade'],
        default='arcade',
        help='Visualizer type (default: arcade)'
    )
    
    parser.add_argument(
        '--demo',
        action='store_true',
        help='Run demo mode with preset settings'
    )
    
    parser.add_argument(
        '--quiet', '-q',
        action='store_true',
        help='Quiet mode - only show final results'
    )
    
    return parser.parse_args()


def print_banner():
    """打印启动横幅"""
    banner = """
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║     █▀▀▀█ ▄  █ ▀▀▀█▄   ▄▀▀▀▄ ▄     █▀▀▀█ ▄  █ ▄▀▀▀▄         ║
║     █   █ █  █   ▄▀   █▄▄▄█ █     █   █ █  █ █ █▄▄▄█         ║
║     █▄▄▄█ █▄▄█ ▄▀▀▀▄   █   █ █▄▄   █▄▄▄█ █▄▄█ █ █            ║
║                                                              ║
║              MINER - RustChain on Z80 (1982)                 ║
║                                                              ║
╠══════════════════════════════════════════════════════════════╣
║  Hardware: Z80 @ 3.072 MHz, 48 KB RAM                        ║
║  Bounty:   200 RTC ($20) - LEGENDARY Tier!                   ║
║  Wallet:   RTC4325af95d26d59c3ef025963656d22af638bb96b       ║
╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)


def run_demo():
    """运行演示模式"""
    print("\n🎮 Running Demo Mode...\n")
    
    # 初始化 Z80 CPU
    z80 = Z80CPU()
    
    # 初始化矿工
    wallet = "RTC4325af95d26d59c3ef025963656d22af638bb96b"
    miner = MinerCore(z80, wallet)
    miner.difficulty = 500  # 降低难度用于演示
    
    print("⚙️  Z80 CPU Initialized")
    print(f"   PC: 0x{z80.PC:04X}, SP: 0x{z80.SP:04X}")
    print(f"   Memory: 64 KB")
    print()
    
    print(f"💰 Wallet: {wallet}")
    print(f"   Difficulty: {miner.difficulty}")
    print()
    
    # 运行几个区块
    print("⛏️  Starting mining...\n")
    
    for i in range(3):
        result = miner.mine_block(i, max_nonces=20000)
        
        if result['found']:
            print(f"   ✅ Block {i}: FOUND! Nonce={result['nonce']}")
        else:
            print(f"   ❌ Block {i}: No share found")
        
        time.sleep(0.5)
    
    # 打印统计
    print("\n")
    miner.print_stats()
    
    print("\n🏁 Demo completed!")
    print(f"   Total shares: {miner.shares}")
    print(f"   Blocks found: {miner.blocks_found}")
    
    return miner


def run_continuous(args):
    """运行连续挖矿模式"""
    print_banner()
    
    # 初始化
    z80 = Z80CPU()
    miner = MinerCore(z80, args.wallet)
    miner.difficulty = args.difficulty
    
    print(f"\n⚙️  Configuration:")
    print(f"   Wallet: {args.wallet}")
    print(f"   Difficulty: {args.difficulty}")
    print(f"   Max Nonces: {args.max_nonces}")
    print(f"   Visualizer: {args.visualizer}")
    print()
    
    # 选择可视化器
    if args.visualizer == 'arcade':
        visualizer = ArcadeScreenVisualizer(miner)
    else:
        visualizer = TextVisualizer(miner)
    
    print("🚀 Starting miner... (Press Ctrl+C to stop)\n")
    time.sleep(2)
    
    # 运行可视化
    visualizer.run(update_interval=2.0)


def run_blocks_mode(args):
    """运行指定区块数量模式"""
    print_banner()
    
    # 初始化
    z80 = Z80CPU()
    miner = MinerCore(z80, args.wallet)
    miner.difficulty = args.difficulty
    
    print(f"\n⚙️  Configuration:")
    print(f"   Wallet: {args.wallet}")
    print(f"   Difficulty: {args.difficulty}")
    print(f"   Blocks: {args.blocks}")
    print(f"   Max Nonces: {args.max_nonces}")
    print()
    
    miner.start_mining()
    
    # 挖掘指定数量的区块
    for i in range(args.blocks):
        if not args.quiet:
            print(f"\n🎮 Mining Block #{i}...")
        
        result = miner.mine_block(i, max_nonces=args.max_nonces)
        
        if not args.quiet:
            if result['found']:
                print(f"   ✅ Share found! Nonce: {result['nonce']}")
            else:
                print(f"   ❌ No share found")
    
    # 打印最终统计
    print("\n")
    miner.print_stats()
    
    print("\n🏁 Mining completed!")
    print(f"   Total shares: {miner.shares}")
    print(f"   Blocks found: {miner.blocks_found}")
    
    return miner


def main():
    """主函数"""
    args = parse_args()
    
    try:
        if args.demo:
            run_demo()
        elif args.blocks > 0:
            run_blocks_mode(args)
        else:
            run_continuous(args)
    
    except KeyboardInterrupt:
        print("\n\n🏁 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if not args.quiet:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
