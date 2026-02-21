#!/usr/bin/env python3
"""
Beacon ClawNews Integration
Wrapper to enable 'beacon clawnews' command syntax
"""

import sys
import subprocess
from pathlib import Path

def main():
    """
    Main entry point for beacon clawnews integration
    Forwards commands to the ClawNews CLI
    """
    
    # Get the directory containing this script
    script_dir = Path(__file__).parent
    clawnews_cli = script_dir / "clawnews_cli.py"
    
    # Check if clawnews_cli.py exists
    if not clawnews_cli.exists():
        print(f"❌ Error: ClawNews CLI not found at {clawnews_cli}", file=sys.stderr)
        return 1
    
    # Forward all arguments to clawnews_cli.py
    # Remove 'clawnews' from the command if it's the first argument
    args = sys.argv[1:]
    if args and args[0] == 'clawnews':
        args = args[1:]
    
    try:
        # Execute the ClawNews CLI with forwarded arguments
        cmd = [sys.executable, str(clawnews_cli)] + args
        result = subprocess.run(cmd, check=False)
        return result.returncode
        
    except FileNotFoundError:
        print("❌ Error: Python interpreter not found", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"❌ Error executing ClawNews CLI: {e}", file=sys.stderr)
        return 1

if __name__ == "__main__":
    sys.exit(main())