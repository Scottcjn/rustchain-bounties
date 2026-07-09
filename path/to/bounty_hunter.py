# Complete code for bounty_hunter.py
"""
Bounty Hunter script to compare RustChain to another blockchain project.
"""
import os
import markdown
from datetime import datetime

def compare_blockchains(project1, project2):
    """
    Compare two blockchain projects.

    Args:
        project1 (str): Name of the first blockchain project.
        project2 (str): Name of the second blockchain project.

    Returns:
        str: Comparison of the two blockchain projects in Markdown format.
    """
    comparison = f"# Comparison of {project1} and {project2}\n\n"
    comparison += f"## Consensus Mechanism Differences\n\n"
    comparison += f"* {project1}: {get_consensus_mechanism(project1)}\n"
    comparison += f"* {project2}: {get_consensus_mechanism(project2)}\n\n"
    comparison += f"## Hardware Requirements\n\n"
    comparison += f"* {project1}: {get_hardware_requirements(project1)}\n"
    comparison += f"* {project2}: {get_hardware_requirements(project2)}\n\n"
    comparison += f"## Environmental Approach\n\n"
    comparison += f"* {project1}: {get_environmental_approach(project1)}\n"
    comparison += f"* {project2}: {get_environmental_approach(project2)}\n\n"
    comparison += f"## Community Model\n\n"
    comparison += f"* {project1}: {get_community_model(project1)}\n"
    comparison += f"* {project2}: {get_community_model(project2)}\n\n"
    comparison += f"## What Each Project Does Better\n\n"
    comparison += f"* {project1}: {get_better_features(project1)}\n"
    comparison += f"* {project2}: {get_better_features(project2)}\n"
    return comparison

def get_consensus_mechanism(project):
    """
    Get the consensus mechanism of a blockchain project.

    Args:
        project (str): Name of the blockchain project.

    Returns:
        str: Consensus mechanism of the project.
    """
    if project == "RustChain":
        return "Proof of Antiquity"
    elif project == "Ethereum":
        return "Proof of Stake"
    elif project == "Bitcoin":
        return "Proof of Work"
    else:
        return "Unknown"

def get_hardware_requirements(project):
    """
    Get the hardware requirements of a blockchain project.

    Args:
        project (str): Name of the blockchain project.

    Returns:
        str: Hardware requirements of the project.
    """
    if project == "RustChain":
        return "Low-end hardware"
    elif project == "Ethereum":
        return "Mid-range hardware"
    elif project == "Bitcoin":
        return "High-end hardware"
    else:
        return "Unknown"

def get_environmental_approach(project):
    """
    Get the environmental approach of a blockchain project.

    Args:
        project (str): Name of the blockchain project.

    Returns:
        str: Environmental approach of the project.
    """
    if project == "RustChain":
        return "Carbon-neutral"
    elif project == "Ethereum":
        return "Carbon-neutral"
    elif project == "Bitcoin":
        return "Carbon-intensive"
    else:
        return "Unknown"

def get_community_model(project):
    """
    Get the community model of a blockchain project.

    Args:
        project (str): Name of the blockchain project.

    Returns:
        str: Community model of the project.
    """
    if project == "RustChain":
        return "Decentralized"
    elif project == "Ethereum":
        return "Decentralized"
    elif project == "Bitcoin":
        return "Centralized"
    else:
        return "Unknown"

def get_better_features(project):
    """
    Get the better features of a blockchain project.

    Args:
        project (str): Name of the blockchain project.

    Returns:
        str: Better features of the project.
    """
    if project == "RustChain":
        return "Scalability, security, and environmental sustainability"
    elif project == "Ethereum":
        return "Smart contracts, decentralized finance, and non-fungible tokens"
    elif project == "Bitcoin":
        return "Security, decentralization, and limited supply"
    else:
        return "Unknown"

def main():
    project1 = "RustChain"
    project2 = "Ethereum"
    comparison = compare_blockchains(project1, project2)
    with open("bounties/comparison.md", "w") as f:
        f.write(comparison)
    print("Comparison written to bounties/comparison.md")

if __name__ == "__main__":
    main()