# complete code
"""
This script compares RustChain to another blockchain project (in this case, Ethereum).
It generates a Markdown document with the comparison.

Usage:
    python compare_rustchain_to_ethereum.py
"""
import os
import markdown
from jinja2 import Environment, FileSystemLoader
from pathlib import Path

# Define the template for the comparison document
template_dir = Path(__file__).parent / 'templates'
env = Environment(loader=FileSystemLoader(template_dir))
template = env.get_template('comparison.md')

# Define the data for the comparison document
data = {
    'project1': 'RustChain',
    'project2': 'Ethereum',
    'consensus_mechanism1': 'Proof of Antiquity',
    'consensus_mechanism2': 'Proof of Work',
    'hardware_requirements1': 'Custom ASIC',
    'hardware_requirements2': 'GPU',
    'environmental_approach1': 'Energy-efficient',
    'environmental_approach2': 'Energy-intensive',
    'community_model1': 'Decentralized',
    'community_model2': 'Centralized',
}

# Generate the comparison document
comparison_document = template.render(data)

# Check if the comparison document already exists
if os.path.exists('compare_rustchain_to_ethereum.md'):
    print("Comparison document already exists. Please delete it before generating a new one.")
else:
    # Write the comparison document to a file
    with open('compare_rustchain_to_ethereum.md', 'w') as f:
        f.write(comparison_document)
    print("Comparison document generated successfully.")