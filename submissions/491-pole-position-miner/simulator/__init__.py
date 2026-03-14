"""
Pole Position Miner Simulator
RustChain 矿工移植到 Pole Position 街机 (1982)
"""

from .z80_cpu import Z80CPU
from .miner_core import MinerCore, SimplifiedHash
from .visualizer import TextVisualizer, PolePositionVisualizer, ArcadeScreenVisualizer

__version__ = "1.0.0"
__author__ = "OpenClaw Agent"
__wallet__ = "RTC4325af95d26d59c3ef025963656d22af638bb96b"

__all__ = [
    'Z80CPU',
    'MinerCore',
    'SimplifiedHash',
    'TextVisualizer',
    'PolePositionVisualizer',
    'ArcadeScreenVisualizer'
]
