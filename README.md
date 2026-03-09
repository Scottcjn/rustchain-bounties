# RustChain CrewAI Template

A ready-to-use template for integrating [RustChain](https://github.com/Scottcjn/rustchain-bounties) and Beacon into [CrewAI](https://github.com/joaomdmoura/crewAI) orchestration.

## Setup Instructions

1. **Clone & Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. **Configuration**
   Create a `.env` file in the root directory and add your keys:
   ```env
   OPENAI_API_KEY=sk-your-openai-key
   RUSTCHAIN_API_KEY=your-rustchain-key
   ```

3. **Run the Example End-to-End**
   ```bash
   python -m src.main
   ```

## Features
- Direct integration with `rustchain-langchain` tools.
- Custom Beacon Tool for agent-to-agent signal broadcasts.
- Modular CrewAI architecture (`agents.py`, `tasks.py`, `tools.py`).
