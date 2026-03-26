"""
pytest configuration for RustChain SDK tests.
"""

import sys
from pathlib import Path

# Ensure the package is importable from the sdk/python directory
sdk_root = Path(__file__).parent.parent
sys.path.insert(0, str(sdk_root))
