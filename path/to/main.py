# Complete code for main.py
"""
This script runs the comparison script.

Usage:
    python main.py
"""
import comparison

def main():
    print("Welcome to the comparison script!")
    project_name = input("Enter a project name: ")
    comparison_result = comparison.compare_projects(project_name, "Ethereum")
    print(comparison_result)

if __name__ == "__main__":
    main()