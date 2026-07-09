# Complete code for comparison.py
"""
This script compares RustChain to another blockchain project.

Usage:
    python comparison.py <project_name>
"""
import sys

def get_project_info(project_name):
    """
    Returns information about the given project.

    Args:
        project_name (str): Name of the project.

    Returns:
        dict: Project information.
    """
    project_info = {
        'Bitcoin': {
            'consensus': 'PoW',
            'hardware_requirements': 'High-end GPUs',
            'environmental_approach': 'Energy-intensive',
            'community_model': 'Decentralized',
            'strengths': ['Fast transaction times', 'High security'],
            'weaknesses': ['Energy consumption', 'Centralization']
        },
        'Ethereum': {
            'consensus': 'PoS',
            'hardware_requirements': 'High-end GPUs',
            'environmental_approach': 'Energy-intensive',
            'community_model': 'Decentralized',
            'strengths': ['Smart contracts', 'High scalability'],
            'weaknesses': ['Energy consumption', 'Centralization']
        },
        'Solana': {
            'consensus': 'PoH',
            'hardware_requirements': 'High-end GPUs',
            'environmental_approach': 'Energy-intensive',
            'community_model': 'Decentralized',
            'strengths': ['Fast transaction times', 'High scalability'],
            'weaknesses': ['Energy consumption', 'Centralization']
        }
    }
    return project_info.get(project_name, {})

def compare_projects(project1, project2):
    """
    Compares two blockchain projects.

    Args:
        project1 (str): Name of the first project.
        project2 (str): Name of the second project.

    Returns:
        str: Comparison result.
    """
    project1_info = get_project_info(project1)
    project2_info = get_project_info(project2)

    if not project1_info or not project2_info:
        return "One or both projects not found."

    comparison_result = f"Comparison between {project1} and {project2}:\n"
    comparison_result += f"Consensus mechanism: {project1_info['consensus']} vs {project2_info['consensus']}\n"
    comparison_result += f"Hardware requirements: {project1_info['hardware_requirements']} vs {project2_info['hardware_requirements']}\n"
    comparison_result += f"Environmental approach: {project1_info['environmental_approach']} vs {project2_info['environmental_approach']}\n"
    comparison_result += f"Community model: {project1_info['community_model']} vs {project2_info['community_model']}\n"
    comparison_result += f"Strengths: {project1_info['strengths']} vs {project2_info['strengths']}\n"
    comparison_result += f"Weaknesses: {project1_info['weaknesses']} vs {project2_info['weaknesses']}"

    return comparison_result

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python comparison.py <project_name>")
        sys.exit(1)

    project_name = sys.argv[1]
    project_info = get_project_info(project_name)
    if not project_info:
        print("Project not found.")
        sys.exit(1)

    project1 = project_name
    project2 = input("Enter another project name: ")
    comparison_result = compare_projects(project1, project2)
    print(comparison_result)