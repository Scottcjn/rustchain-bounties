"""
AVIDAC (1953) Simulator

A simulator for the AVIDAC computer, the first digital computer at Argonne National Laboratory.
Based on the IAS (von Neumann) architecture with 40-bit parallel binary words.
"""

__version__ = "0.1.0"
__author__ = "RustChain AVIDAC Bounty Team"

from .cpu import AVIDACCPU
from .williams_tube import WilliamsTubeMemory
from .paper_tape import PaperTapeIO
from .assembler import AVIDACAssembler

__all__ = [
    'AVIDACCPU',
    'WilliamsTubeMemory', 
    'PaperTapeIO',
    'AVIDACAssembler'
]
