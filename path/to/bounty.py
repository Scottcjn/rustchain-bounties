# complete code
"""
This script generates a bounty for the comparison task.

It includes the following information:
- Bounty title
- Bounty description
- Bounty reward
- Bounty difficulty
- Bounty time estimate
- Bounty skills required
"""

import json

def generate_bounty():
    # Define the bounty details
    bounty = {
        "title": "Compare RustChain to Another Blockchain Project",
        "description": "Research RustChain and compare it to another blockchain project you know.",
        "reward": 3,
        "difficulty": "Easy-Medium",
        "time_estimate": "30-45 min",
        "skills_required": ["Research", "Writing"]
    }

    # Print the bounty details
    print(json.dumps(bounty, indent=4))

if __name__ == "__main__":
    try:
        generate_bounty()
    except Exception as e:
        print(f"An error occurred: {e}")