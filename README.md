# RustChain CrewAI Template

This template demonstrates how to integrate the RustChain toolchain, BoTTube actions, and the Beacon coordination network within a CrewAI orchestration framework.

## Setup Instructions

1. Clone the repository.
2. Create a virtual environment: `python -m venv venv && source venv/bin/activate`
3. Install dependencies: `pip install -r requirements.txt`
4. Copy `.env.example` to `.env` and populate your API keys and RustChain RPC configurations.
5. Run the example end-to-end: `python src/main.py`

## Ecosystem Features included
- **RustChain Interactions**: Reads balances and executes transfers natively via LangChain tool wrappers.
- **BoTTube Actions**: Placeholder/tool wrapper for retrieving video metadata or publishing bot-generated actions.
- **Beacon Coordination**: Enables autonomous agents to broadcast signaling messages to other agents in the swarm.