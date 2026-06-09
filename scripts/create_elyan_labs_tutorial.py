#!/usr/bin/env python3
"""
Elyan Labs Video Tutorial Creator
Bounty: 5 RTC
Requirements: 2+ minute video, upload to YouTube or BoTTube

This script generates a complete video tutorial script for any Elyan Labs project.
"""

import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional

# Project configurations with detailed instructions
PROJECTS = {
    "1": {
        "name": "RustChain Miner",
        "description": "Install and run the RustChain miner",
        "repo": "https://github.com/ElyanLabs/rustchain",
        "steps": [
            "Clone the repository: git clone https://github.com/ElyanLabs/rustchain.git",
            "Install Rust if not present: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh",
            "Build the project: cargo build --release",
            "Configure miner settings in config.toml",
            "Run the miner: cargo run --release --bin miner",
            "Verify mining activity in terminal output"
        ],
        "key_points": [
            "RustChain is a proof-of-work blockchain written in Rust",
            "Mining contributes to network security",
            "Monitor hash rate and accepted shares"
        ],
        "duration_estimate": "3-4 minutes"
    },
    "2": {
        "name": "BoTTube API",
        "description": "Upload a video to BoTTube via the API",
        "repo": "https://github.com/ElyanLabs/bottube",
        "steps": [
            "Get API key from BoTTube dashboard",
            "Install required tools: pip install requests",
            "Prepare a short video file (MP4 format)",
            "Use curl or Python to upload via API endpoint",
            "Verify upload in BoTTube dashboard",
            "Share the video link"
        ],
        "key_points": [
            "BoTTube is a decentralized video platform",
            "API supports multiple video formats",
            "Videos are stored on IPFS"
        ],
        "duration_estimate": "2-3 minutes"
    },
    "3": {
        "name": "TrashClaw with Local LLM",
        "description": "Use TrashClaw with a local LLM",
        "repo": "https://github.com/ElyanLabs/trashclaw",
        "steps": [
            "Clone TrashClaw: git clone https://github.com/ElyanLabs/trashclaw.git",
            "Install dependencies: pip install -r requirements.txt",
            "Download a local LLM (e.g., Llama 2 or Mistral)",
            "Configure TrashClaw to use local model",
            "Run TrashClaw with sample input",
            "Demonstrate output and customization options"
        ],
        "key_points": [
            "TrashClaw is a CLI tool for text processing",
            "Local LLMs provide privacy and offline capability",
            "Supports multiple model formats"
        ],
        "duration_estimate": "3-5 minutes"
    },
    "4": {
        "name": "rustchain-mcp in Claude Code",
        "description": "Set up rustchain-mcp in Claude Code",
        "repo": "https://github.com/ElyanLabs/rustchain-mcp",
        "steps": [
            "Install Claude Code CLI",
            "Clone rustchain-mcp: git clone https://github.com/ElyanLabs/rustchain-mcp.git",
            "Follow setup instructions in README",
            "Configure MCP server settings",
            "Test integration with Claude Code",
            "Demonstrate a sample query"
        ],
        "key_points": [
            "MCP enables AI assistants to interact with RustChain",
            "Claude Code can query blockchain data",
            "Useful for developers building on RustChain"
        ],
        "duration_estimate": "2-4 minutes"
    }
}

def print_header():
    """Print the script header with branding."""
    print("=" * 60)
    print("  ELYAN LABS VIDEO TUTORIAL CREATOR")
    print("  Bounty: 5 RTC")
    print("=" * 60)
    print()

def select_project() -> Optional[Dict]:
    """Prompt user to select a project and return its configuration."""
    print("Available Projects:")
    print("-" * 40)
    for key, project in PROJECTS.items():
        print(f"  {key}. {project['name']} - {project['description']}")
    print()
    
    while True:
        choice = input("Select a project (1-4): ").strip()
        if choice in PROJECTS:
            return PROJECTS[choice]
        print("Invalid choice. Please enter 1, 2, 3, or 4.")

def generate_script(project: Dict) -> str:
    """Generate a complete video script based on project configuration."""
    script = []
    
    # Title and intro
    script.append(f"# Video Tutorial: {project['name']}")
    script.append(f"**Description:** {project['description']}")
    script.append(f"**Estimated Duration:** {project['duration_estimate']}")
    script.append(f"**Repository:** {project['repo']}")
    script.append(f"**Date Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    script.append("")
    script.append("---")
    script.append("")
    
    # Introduction section
    script.append("## 1. Introduction (0:00 - 0:30)")
    script.append("- Greet the audience and introduce yourself")
    script.append(f"- Explain what {project['name']} is and why it's useful")
    script.append("- Mention this is part of the Elyan Labs ecosystem")
    script.append("- Outline what the tutorial will cover")
    script.append("")
    
    # Prerequisites section
    script.append("## 2. Prerequisites (0:30 - 1:00)")
    script.append("- List required software and tools")
    script.append("- Ensure viewers have the basics installed")
    script.append("- Provide links to download if needed")
    script.append("")
    
    # Step-by-step instructions
    script.append(f"## 3. Step-by-Step Guide (1:00 - {project['duration_estimate']})")
    for i, step in enumerate(project['steps'], 1):
        script.append(f"### Step {i}")
        script.append(f"- **Action:** {step}")
        script.append("- **Screen recording:** Show the terminal/IDE")
        script.append("- **Narration:** Explain what's happening")
        script.append("")
    
    # Key points section
    script.append("## 4. Key Takeaways")
    for point in project['key_points']:
        script.append(f"- {point}")
    script.append("")
    
    # Conclusion
    script.append("## 5. Conclusion")
    script.append("- Recap what was accomplished")
    script.append("- Encourage viewers to try it themselves")
    script.append("- Mention the 5 RTC bounty for creating tutorials")
    script.append("- Ask for likes, comments, and subscriptions")
    script.append("- Provide links to Elyan Labs resources")
    script.append("")
    
    # Upload instructions
    script.append("---")
    script.append("## Upload Instructions")
    script.append("1. Record your screen following the script above")
    script.append("2. Edit the video to ensure it's at least 2 minutes long")
    script.append("3. Upload to YouTube OR [bottube.ai](https://bottube.ai)")
    script.append("4. Comment on the GitHub issue with:")
    script.append("   - Video link")
    script.append("   - Your RTC wallet address")
    script.append("")
    script.append("**Note:** Video backlinks are the strongest SEO signal for Elyan Labs!")
    
    return "\n".join(script)

def save_script(script: str, project_name: str):
    """Save the generated script to a file."""
    filename = f"tutorial_{project_name.lower().replace(' ', '_')}.md"
    
    # Sanitize filename
    filename = "".join(c for c in filename if c.isalnum() or c in "._- ")
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(script)
        print(f"\n✅ Script saved to: {filename}")
        return filename
    except IOError as e:
        print(f"\n❌ Error saving file: {e}")
        return None

def print_instructions(project: Dict):
    """Print additional instructions for recording and uploading."""
    print("\n" + "=" * 60)
    print("  RECORDING & UPLOAD INSTRUCTIONS")
    print("=" * 60)
    print(f"""
Project: {project['name']}
Duration: {project['duration_estimate']}

Recording Tips:
- Use OBS Studio (free) or built-in screen recorder
- Ensure good audio quality
- Show terminal/IDE clearly
- Speak clearly and at a moderate pace

Upload Options:
1. YouTube: https://youtube.com
   - Title: "How to {project['description']} | Elyan Labs Tutorial"
   - Description: Include links to repo and Elyan Labs
   - Tags: ElyanLabs, RustChain, blockchain, tutorial

2. BoTTube: https://bottube.ai
   - Upload directly to decentralized platform
   - Supports IPFS storage

After Upload:
1. Copy the video URL
2. Go to: https://github.com/Scottcjn/rustchain-bounties/issues
3. Comment with:
   - Video link
   - Your RTC wallet address
   - Brief description of what you did

Bounty: 5 RTC will be sent to your wallet after verification.
""")

def main():
    """Main execution function."""
    print_header()
    
    # Select project
    project = select_project()
    if not project:
        print("No project selected. Exiting.")
        sys.exit(1)
    
    print(f"\nGenerating tutorial for: {project['name']}")
    print("-" * 40)
    
    # Generate script
    script = generate_script(project)
    
    # Save to file
    filename = save_script(script, project['name'])
    
    # Print instructions
    print_instructions(project)
    
    # Print the script to console
    print("\n" + "=" * 60)
    print("  GENERATED SCRIPT PREVIEW")
    print("=" * 60)
    print(script[:500] + "...\n")
    print(f"Full script saved to: {filename}")
    
    print("\n✅ Tutorial generation complete!")
    print("Follow the instructions above to record and upload your video.")

if __name__ == "__main__":
    main()