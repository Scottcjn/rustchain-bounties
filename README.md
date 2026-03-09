# RustChain CrewAI Integration Template

This template provides a working CrewAI orchestration example utilizing the `rustchain-langchain` tools and Beacon for agent-to-agent coordination.

## Setup Instructions

1. Create a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure Environment Variables:
   Copy `.env.example` to `.env` and add your keys.
   ```bash
   cp .env.example .env
   ```

4. Run the CrewAI Project:
   ```bash
   python src/main.py
   ```
