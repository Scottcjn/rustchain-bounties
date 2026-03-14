"""
Pole Position Miner - 可视化界面
使用 Pole Position 游戏风格显示挖矿状态
"""

import time
import sys
from datetime import datetime


class PolePositionVisualizer:
    """
    Pole Position 风格可视化
    使用 ASCII 艺术模拟街机显示效果
    """
    
    def __init__(self, miner_core):
        self.miner = miner_core
        self.width = 60
        self.height = 24
        self.running = False
        
        # Pole Position 配色 (ASCII 表示)
        self.colors = {
            'sky': '█',
            'track': '░',
            'grass': '▒',
            'car': '🏎️',
            'text': ''
        }
    
    def clear_screen(self):
        """清屏"""
        print('\033[2J\033[H', end='')
    
    def draw_header(self):
        """绘制顶部标题栏"""
        print("╔" + "═" * (self.width - 2) + "╗")
        title = "🎮 POLE POSITION MINER v1.0.0"
        subtitle = "RustChain on Z80 (1982 Arcade)"
        print(f"║ {title.center(self.width - 4)} ║")
        print(f"║ {subtitle.center(self.width - 4)} ║")
        print("╠" + "═" * (self.width - 2) + "╣")
    
    def draw_wallet(self, wallet: str):
        """绘制钱包地址"""
        wallet_display = f"Wallet: {wallet[:20]}...{wallet[-10:]}"
        print(f"║ {wallet_display:<{self.width - 4}} ║")
    
    def draw_stats_bar(self, label: str, value: str, max_width=40):
        """绘制统计条"""
        line = f"{label}: {value}"
        print(f"║ {line:<{self.width - 4}} ║")
    
    def draw_speedometer(self, hashrate: float):
        """
        绘制速度表显示算力
        Pole Position 经典速度表样式
        """
        print("╠" + "═" * (self.width - 2) + "╣")
        print(f"║ {'HASHRATE (KH/s)':^{self.width - 4}} ║")
        print("║" + " " * (self.width - 2) + "║")
        
        # 速度表刻度
        max_hashrate = 10.0  # 最大显示算力
        normalized = min(hashrate / 1000 / max_hashrate, 1.0)
        bar_width = int(normalized * 40)
        
        bar = "█" * bar_width + "░" * (40 - bar_width)
        print(f"║  [{bar}] {hashrate/1000:.2f} ║")
        print("║" + " " * (self.width - 2) + "║")
    
    def draw_gear_indicator(self, difficulty: int):
        """
        绘制档位显示难度
        """
        gear = min(difficulty // 100, 5) + 1
        gear_str = " ".join(["D" if i == gear else "□" for i in range(1, 6)])
        print(f"║  GEAR: {gear_str} (Difficulty: {difficulty})".ljust(self.width - 4) + " ║")
    
    def draw_lap_counter(self, shares: int):
        """
        绘制圈数计数器 (Share 数量)
        """
        print(f"║  LAPS (Shares): {shares}".ljust(self.width - 4) + " ║")
    
    def draw_position(self, rank: int = 1):
        """
        绘制位置显示
        """
        positions = ["1st 🥇", "2nd 🥈", "3rd 🥉", "4th", "5th"]
        pos_str = positions[rank - 1] if rank <= len(positions) else f"{rank}th"
        print(f"║  POSITION: {pos_str}".ljust(self.width - 4) + " ║")
    
    def draw_track(self, progress: float):
        """
        绘制赛道显示挖矿进度
        """
        track_length = 50
        car_pos = int(progress * track_length)
        
        track = "─" * car_pos + "🏎️" + "─" * (track_length - car_pos - 1)
        print(f"║  [{track}]".ljust(self.width - 4) + " ║")
    
    def draw_status(self, status: str):
        """绘制状态"""
        status_icons = {
            'MINING': '⛏️',
            'IDLE': '💤',
            'FOUND': '✅',
            'ERROR': '❌'
        }
        icon = status_icons.get(status, '❓')
        print(f"║  STATUS: {icon} {status}".ljust(self.width - 4) + " ║")
    
    def draw_timer(self, elapsed: float):
        """绘制计时器"""
        minutes = int(elapsed // 60)
        seconds = int(elapsed % 60)
        print(f"║  TIME: {minutes:02d}:{seconds:02d}".ljust(self.width - 4) + " ║")
    
    def draw_footer(self):
        """绘制底部"""
        print("╠" + "═" * (self.width - 2) + "╣")
        footer = "Press Ctrl+C to stop"
        print(f"║ {footer.center(self.width - 4)} ║")
        print("╚" + "═" * (self.width - 2) + "╝")
    
    def draw_frame(self):
        """绘制一帧"""
        self.clear_screen()
        
        stats = self.miner.get_stats()
        
        self.draw_header()
        self.draw_wallet(stats['wallet'])
        print("╠" + "═" * (self.width - 2) + "╣")
        self.draw_speedometer(stats['hashrate'])
        self.draw_gear_indicator(stats['difficulty'])
        self.draw_lap_counter(stats['shares'])
        self.draw_position(1)
        print("╠" + "═" * (self.width - 2) + "╣")
        
        # 挖矿进度
        if self.miner.current_block is not None:
            progress = (time.time() % 10) / 10  # 模拟进度
            self.draw_track(progress)
        
        self.draw_status('MINING')
        self.draw_timer(stats['elapsed_time'])
        
        self.draw_footer()
    
    def run(self, update_interval=1.0):
        """运行可视化"""
        self.running = True
        self.miner.start_mining()
        
        try:
            while self.running:
                self.draw_frame()
                time.sleep(update_interval)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """停止可视化"""
        self.running = False
        self.miner.stop_mining()
        self.clear_screen()
        print("🏁 Mining stopped!")
        self.miner.print_stats()


class TextVisualizer:
    """
    简化文本可视化
    适用于无 ANSI 支持的终端
    """
    
    def __init__(self, miner_core):
        self.miner = miner_core
        self.running = False
    
    def print_status(self):
        """打印状态"""
        stats = self.miner.get_stats()
        
        print("\n" + "=" * 60)
        print("     POLE POSITION MINER - RustChain on Z80")
        print("=" * 60)
        print(f"  Wallet:   {stats['wallet']}")
        print(f"  Hashrate: {stats['hashrate']:.2f} H/s")
        print(f"  Shares:   {stats['shares']}")
        print(f"  Blocks:   {stats['blocks_found']}")
        print(f"  Time:     {stats['uptime']}")
        print(f"  Status:   MINING...")
        print("=" * 60)
        print("  Press Ctrl+C to stop")
        print()
    
    def run(self, update_interval=5.0):
        """运行可视化"""
        self.running = True
        self.miner.start_mining()
        
        try:
            while self.running:
                self.print_status()
                time.sleep(update_interval)
        except KeyboardInterrupt:
            self.stop()
    
    def stop(self):
        """停止可视化"""
        self.running = False
        self.miner.stop_mining()
        print("\n🏁 Mining stopped!")
        self.miner.print_stats()


class ArcadeScreenVisualizer:
    """
    模拟 Pole Position 街机屏幕
    使用更丰富的 ASCII 艺术
    """
    
    def __init__(self, miner_core):
        self.miner = miner_core
        self.width = 70
        self.height = 30
    
    def clear_screen(self):
        print('\033[2J\033[H', end='')
    
    def draw_arcade_screen(self):
        """绘制完整的街机屏幕效果"""
        self.clear_screen()
        
        stats = self.miner.get_stats()
        
        # 顶部边框
        print("╔" + "═" * (self.width - 2) + "╗")
        
        # 标题 - 模拟 Pole Position 标题
        title = """
  █▀▀▀█ ▄  █ ▀▀▀█▄   ▄▀▀▀▄ ▄     █▀▀▀█ ▄  █ ▄▀▀▀▄
  █   █ █  █   ▄▀   █▄▄▄█ █     █   █ █  █ █ █▄▄▄█
  █▄▄▄█ █▄▄█ ▄▀▀▀▄   █   █ █▄▄   █▄▄▄█ █▄▄█ █ █
        """
        for line in title.split('\n'):
            if line.strip():
                print(f"║ {line:^{self.width - 4}} ║")
        
        print("╠" + "═" * (self.width - 2) + "╣")
        
        # 挖矿信息
        print(f"║  MINING RUSTCHAIN ON Z80 @ 3MHz".ljust(self.width - 4) + " ║")
        print(f"║  Wallet: {stats['wallet']}".ljust(self.width - 4) + " ║")
        
        print("╠" + "═" * (self.width - 2) + "╣")
        
        # 统计信息
        print(f"║  HASHRATE:  {stats['hashrate']:>10.2f} H/s".ljust(self.width - 4) + " ║")
        print(f"║  SHARES:    {stats['shares']:>10}".ljust(self.width - 4) + " ║")
        print(f"║  BLOCKS:    {stats['blocks_found']:>10}".ljust(self.width - 4) + " ║")
        print(f"║  TIME:      {stats['uptime']:>10}".ljust(self.width - 4) + " ║")
        
        print("╠" + "═" * (self.width - 2) + "╣")
        
        # 模拟赛道视图
        print("║" + " " * (self.width - 2) + "║")
        print("║                    🏁 FINISH LINE                    ║")
        print("║                   ═══════════                        ║")
        print("║                                                      ║")
        print("║                                                      ║")
        print("║                        🏎️                            ║")
        print("║                       /|\\                            ║")
        print("║                                                      ║")
        print("║          ════════════════════════════                ║")
        print("║                                                      ║")
        
        print("╠" + "═" * (self.width - 2) + "╣")
        
        # 状态
        print(f"║  STATUS: ⛏️  MINING...".ljust(self.width - 4) + " ║")
        
        # 底部
        print("╚" + "═" * (self.width - 2) + "╝")
        print("  Press Ctrl+C to stop | Bounty: 200 RTC ($20)")
        print()
    
    def run(self, update_interval=2.0):
        """运行可视化"""
        self.miner.start_mining()
        
        try:
            while True:
                self.draw_arcade_screen()
                time.sleep(update_interval)
        except KeyboardInterrupt:
            self.miner.stop_mining()
            print("\n🏁 Mining stopped!")
            self.miner.print_stats()


if __name__ == "__main__":
    # 测试可视化
    from miner_core import MinerCore
    from z80_cpu import Z80CPU
    
    print("Testing Pole Position Visualizer...")
    
    z80 = Z80CPU()
    miner = MinerCore(z80, "RTC4325af95d26d59c3ef025963656d22af638bb96b")
    
    # 使用简化文本可视化
    visualizer = TextVisualizer(miner)
    
    # 运行 10 秒
    import threading
    def stop_after():
        time.sleep(10)
        visualizer.stop()
    
    thread = threading.Thread(target=stop_after)
    thread.start()
    visualizer.run(update_interval=2.0)
