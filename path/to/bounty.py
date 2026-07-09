# Complete code for bounty.py
"""
This script creates a bounty for the comparison task.

Usage:
    python bounty.py
"""
import comparison

def main():
    print("Creating bounty for comparison task!")
    bounty_description = "Compare RustChain to another blockchain project."
    bounty_reward = 3
    comparison_result = comparison.compare_projects("RustChain", "Ethereum")
    print(comparison_result)

if __name__ == "__main__":
    main()