# complete code
"""
This script compares RustChain to another blockchain project, Solana.

It covers the following topics:
- Consensus mechanism differences
- Hardware requirements
- Environmental approach
- Community model
- What each project does better
"""

import json

def compare_projects():
    # Define the projects to compare
    projects = {
        "RustChain": {
            "consensus": "Proof of Antiquity",
            "hardware": "Custom ASIC",
            "environmental": "Energy-efficient",
            "community": "Decentralized",
            "better_at": "Energy efficiency"
        },
        "Solana": {
            "consensus": "Proof of Stake",
            "hardware": "GPU",
            "environmental": "Energy-intensive",
            "community": "Centralized",
            "better_at": "Scalability"
        }
    }

    # Print the comparison table
    print("| Project | Consensus | Hardware | Environmental | Community | Better at |")
    print("| --- | --- | --- | --- | --- | --- |")
    for project, details in projects.items():
        print(f"| {project} | {details['consensus']} | {details['hardware']} | {details['environmental']} | {details['community']} | {details['better_at']} |")

if __name__ == "__main__":
    try:
        compare_projects()
    except Exception as e:
        print(f"An error occurred: {e}")