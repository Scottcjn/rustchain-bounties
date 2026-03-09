# RustChain CrewAI Orchestration Template

A production-ready template for orchestrating multi-agent workflows using [CrewAI](https://crewai.com/) and the `rustchain-langchain` toolchain. This integration allows AI agents to securely coordinate, query RustChain, and execute actions on BoTTube.

## Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone <repo-url>
   cd rustchain-crewai-template
   ```

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Configuration:**
   Copy the example environment file and fill in your API keys:
   ```bash
   cp .env.example .env
   ```

## Running the Framework

Execute the end-to-end multi-agent orchestration by running:
```bash
python src/main.py
```

## Beacon Integration (Optional)
To utilize Beacon for enhanced agent-to-agent discovery and state coordination, ensure `BEACON_API_KEY` is set in your `.env`. The RustChain ToolKit handles the middleware automatically when configured.