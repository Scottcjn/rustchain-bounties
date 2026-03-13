#!/usr/bin/env python3
"""
AVIDAC Simulator Test Runner

Run all tests for the AVIDAC simulator.
"""

import subprocess
import sys
import os

def main():
    """Run test suite."""
    # Change to simulator directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    simulator_dir = os.path.join(script_dir, 'simulator')
    
    print("=" * 60)
    print("AVIDAC Simulator Test Suite")
    print("=" * 60)
    print()
    
    # Run pytest
    cmd = [sys.executable, '-m', 'pytest', simulator_dir, '-v', '--tb=short']
    
    # Add coverage if available
    try:
        import pytest_cov
        cmd.extend(['--cov=simulator', '--cov-report=term-missing'])
    except ImportError:
        pass
    
    result = subprocess.run(cmd, cwd=script_dir)
    
    print()
    print("=" * 60)
    if result.returncode == 0:
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed!")
    print("=" * 60)
    
    return result.returncode

if __name__ == '__main__':
    sys.exit(main())
