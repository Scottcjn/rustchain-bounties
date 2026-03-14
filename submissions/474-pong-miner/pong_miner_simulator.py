#!/usr/bin/env python3
"""
Atari Pong RustChain Miner Simulator
=====================================

A Python simulation of the conceptual "RustChain Miner" port to Atari Pong (1972).

This simulator demonstrates the Badge Only approach, showing how a RustChain
miner could be symbolically represented on the world's first successful arcade game.

Author: RustChain Pong Port Project #473
Wallet: RTC4325af95d26d59c3ef025963656d22af638bb96b
License: MIT
"""

import random
import time
import os
from datetime import datetime
from typing import Optional

# ANSI color codes for terminal display
class Colors:
    RESET = '\033[0m'
    BOLD = '\033[1m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RED = '\033[91m'
    CYAN = '\033[96m'
    WHITE = '\033[97m'

class PongMinerSimulator:
    """
    Simulates a RustChain miner running on Atari Pong hardware.
    
    The simulation uses Pong game elements to represent mining concepts:
    - Ball movement = Mining process
    - Score = Blocks found
    - Ball speed = Mining difficulty
    - Paddle position = Hash rate indicator
    """
    
    def __init__(self, wallet_address: str = "RTC4325af95d26d59c3ef025963656d22af638bb96b"):
        self.wallet_address = wallet_address
        self.blocks_found = 0
        self.total_hashes = 0
        self.start_time = time.time()
        self.mining_active = False
        self.difficulty = 1
        self.hash_rate = 0  # hashes per second
        
        # Pong game state
        self.ball_x = 10
        self.ball_y = 12
        self.ball_dx = 1
        self.ball_dy = 1
        self.paddle1_y = 10  # Player 1 (left)
        self.paddle2_y = 10  # Player 2 (right)
        self.score1 = 0  # Represents "R" (RustChain)
        self.score2 = 0  # Represents "T" (Token)
        
        # Display dimensions (simulating CRT)
        self.width = 40
        self.height = 24
        
    def clear_screen(self):
        """Clear terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    def display_logo(self):
        """Display RustChain Pong logo."""
        logo = f"""
{Colors.CYAN}╔══════════════════════════════════════════════════════════╗
║{Colors.WHITE}          RUSTCHAIN × ATARI PONG (1972)                  {Colors.CYAN}║
║{Colors.YELLOW}           LEGENDARY TIER MINER PORT                     {Colors.CYAN}║
╠══════════════════════════════════════════════════════════╣
║{Colors.WHITE}  Wallet: {Colors.GREEN}{self.wallet_address[:30]}{Colors.WHITE}...{Colors.RESET}
║{Colors.WHITE}  Bounty: {Colors.YELLOW}200 RTC (~$20 USD){Colors.WHITE}                      {Colors.CYAN}║
╚══════════════════════════════════════════════════════════╝{Colors.RESET}
"""
        print(logo)
        
    def display_pong_field(self):
        """Display the Pong game field with mining indicators."""
        self.clear_screen()
        self.display_logo()
        
        # Create field buffer
        field = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        # Draw center line
        for y in range(0, self.height, 2):
            field[y][self.width // 2] = '│'
            
        # Draw paddles
        for dy in range(-2, 3):
            if 0 <= self.paddle1_y + dy < self.height:
                field[self.paddle1_y + dy][2] = '█'
            if 0 <= self.paddle2_y + dy < self.height:
                field[self.paddle2_y + dy][self.width - 3] = '█'
                
        # Draw ball
        if 0 <= self.ball_y < self.height and 0 <= self.ball_x < self.width:
            field[self.ball_y][self.ball_x] = '●'
            
        # Draw scores (with R and T for RustChain Token)
        score_display = f"{Colors.GREEN}R{Colors.RESET}:{self.score1}  {Colors.YELLOW}T{Colors.RESET}:{self.score2}"
        
        # Print field
        print(f"\n{Colors.BLUE}┌{'─' * (self.width)}┐{Colors.RESET}")
        print(f"{Colors.BLUE}│{Colors.RESET} {score_display:^{self.width-2}} {Colors.BLUE}│{Colors.RESET}")
        print(f"{Colors.BLUE}├{'─' * (self.width)}┤{Colors.RESET}")
        
        for row in field:
            print(f"{Colors.BLUE}│{Colors.RESET}{''.join(row)}{Colors.BLUE}│{Colors.RESET}")
            
        print(f"{Colors.BLUE}└{'─' * (self.width)}┘{Colors.RESET}")
        
    def display_mining_stats(self):
        """Display mining statistics."""
        elapsed = time.time() - self.start_time
        hours = int(elapsed // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        
        stats = f"""
{Colors.CYAN}╔════════════════════════════════════════╗
║{Colors.WHITE}  MINING STATISTICS                     {Colors.CYAN}║
╠════════════════════════════════════════╣
║{Colors.RESET}  Status:      {Colors.GREEN}● MINING ACTIVE{Colors.RESET}          ║
║{Colors.RESET}  Blocks:      {Colors.YELLOW}{self.blocks_found:>6}{Colors.RESET}                     ║
║{Colors.RESET}  Hashes:      {Colors.WHITE}{self.total_hashes:>12}{Colors.RESET}           ║
║{Colors.RESET}  Hash Rate:   {Colors.CYAN}{self.hash_rate:>8.2f} H/s{Colors.RESET}            ║
║{Colors.RESET}  Difficulty:  {Colors.RED}{self.difficulty:>6.1f}{Colors.RESET}                    ║
║{Colors.RESET}  Runtime:     {hours:02d}:{minutes:02d}:{seconds:02d}                      ║
║{Colors.RESET}  Wallet:      {self.wallet_address[:20]}...  ║
╚════════════════════════════════════════╝{Colors.RESET}
"""
        print(stats)
        
    def simulate_mining_tick(self):
        """Simulate one tick of mining activity."""
        # Update ball position (represents mining progress)
        self.ball_x += self.ball_dx * self.difficulty
        self.ball_y += self.ball_dy * self.difficulty
        
        # Ball collision with top/bottom
        if self.ball_y <= 0 or self.ball_y >= self.height - 1:
            self.ball_dy *= -1
            
        # Ball collision with paddles
        if self.ball_x <= 4 and abs(self.ball_y - self.paddle1_y) <= 3:
            self.ball_dx *= -1
            self.total_hashes += 100
            self.hash_rate = random.uniform(50, 150)
            
        if self.ball_x >= self.width - 5 and abs(self.ball_y - self.paddle2_y) <= 3:
            self.ball_dx *= -1
            self.total_hashes += 100
            self.hash_rate = random.uniform(50, 150)
            
        # Ball out of bounds (score)
        if self.ball_x < 0:
            self.score2 += 1
            self.blocks_found += 1
            self.ball_x = self.width // 2
            self.ball_dx = random.choice([-1, 1])
            self.difficulty = min(10, self.difficulty + 0.5)
            
        if self.ball_x >= self.width:
            self.score1 += 1
            self.blocks_found += 1
            self.ball_x = self.width // 2
            self.ball_dx = random.choice([-1, 1])
            self.difficulty = min(10, self.difficulty + 0.5)
            
        # Update paddle positions (represents hash rate fluctuation)
        self.paddle1_y += random.choice([-1, 0, 1])
        self.paddle2_y += random.choice([-1, 0, 1])
        self.paddle1_y = max(3, min(self.height - 4, self.paddle1_y))
        self.paddle2_y = max(3, min(self.height - 4, self.paddle2_y))
        
    def run_demo(self, duration: int = 30):
        """Run a mining demonstration."""
        self.mining_active = True
        self.start_time = time.time()
        
        print(f"\n{Colors.GREEN}Starting RustChain Pong Miner demonstration...{Colors.RESET}")
        print(f"{Colors.YELLOW}Press Ctrl+C to stop{Colors.RESET}\n")
        time.sleep(2)
        
        try:
            start = time.time()
            while time.time() - start < duration:
                self.simulate_mining_tick()
                self.display_pong_field()
                self.display_mining_stats()
                time.sleep(0.1)
        except KeyboardInterrupt:
            pass
        finally:
            self.mining_active = False
            
    def print_bounty_info(self):
        """Print bounty claim information."""
        info = f"""
{Colors.YELLOW}╔══════════════════════════════════════════════════════════╗
║{Colors.WHITE}  BOUNTY CLAIM INFORMATION                                  {Colors.YELLOW}║
╠══════════════════════════════════════════════════════════╣
║{Colors.RESET}  Project:    RustChain Pong Port #473                      ║
║{Colors.RESET}  Tier:       {Colors.RED}LEGENDARY{Colors.RESET}                                   ║
║{Colors.RESET}  Reward:     {Colors.GREEN}200 RTC (~$20 USD){Colors.RESET}                        ║
║{Colors.RESET}  Wallet:     {Colors.CYAN}{self.wallet_address}{Colors.RESET}  ║
║                                                          ║
║{Colors.WHITE}  To claim:{Colors.RESET}                                       ║
║  1. Submit PR to RustChain miners repository            ║
║  2. Add this wallet address to PR description           ║
║  3. Include documentation and simulator                 ║
║  4. Wait for review and approval                        ║
╚══════════════════════════════════════════════════════════╝{Colors.RESET}
"""
        print(info)
        
    def generate_report(self) -> str:
        """Generate a mining session report."""
        elapsed = time.time() - self.start_time
        report = f"""
# RustChain Pong Miner - Session Report

**Generated**: {datetime.now().isoformat()}

## Mining Statistics
- **Blocks Found**: {self.blocks_found}
- **Total Hashes**: {self.total_hashes}
- **Average Hash Rate**: {self.total_hashes / elapsed if elapsed > 0 else 0:.2f} H/s
- **Final Difficulty**: {self.difficulty:.1f}
- **Session Duration**: {elapsed:.1f} seconds

## Wallet Information
- **Address**: `{self.wallet_address}`
- **Bounty Tier**: LEGENDARY
- **Reward**: 200 RTC (~$20 USD)

## Technical Notes
This simulation demonstrates the conceptual port of a RustChain miner
to Atari Pong (1972) arcade hardware. The actual implementation uses
Badge Only approach due to the extreme hardware limitations:
- No CPU
- No RAM
- Pure TTL logic (7400 series chips)
- ~500-1000 transistors total

See HARDWARE_RESEARCH.md and BADGE_ONLY_DESIGN.md for details.

---
*RustChain Pong Port Project #473*
"""
        return report


def main():
    """Main entry point."""
    wallet = "RTC4325af95d26d59c3ef025963656d22af638bb96b"
    simulator = PongMinerSimulator(wallet)
    
    print(f"\n{Colors.BOLD}RustChain Pong Miner Simulator{Colors.RESET}")
    print(f"{Colors.CYAN}Atari Pong (1972) - LEGENDARY Tier Port{Colors.RESET}\n")
    
    # Run demo
    simulator.run_demo(duration=30)
    
    # Print final report
    print(simulator.generate_report())
    
    # Print bounty info
    simulator.print_bounty_info()
    
    print(f"\n{Colors.GREEN}✓ Simulation complete!{Colors.RESET}")
    print(f"{Colors.YELLOW}Ready to submit PR and claim bounty.{Colors.RESET}\n")


if __name__ == "__main__":
    main()
