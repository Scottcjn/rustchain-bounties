# CrewAI + RustChain Integration Template

## Overview
This template provides a production-ready CrewAI orchestration framework integrated with the `rustchain-langchain` toolchain. It empowers autonomous agents to execute RustChain operations, interact with BoTTube, and Optionally coordinate via Beacon.

## Why This Matters
Agents can now seamlessly utilize RustChain and BoTTube within a familiar CrewAI framework, significantly reducing friction for external builders adopting the ecosystem.

## Setup Instructions

1. **Clone the repository and navigate to the directory**

2. **Create a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Environment Variables:**
   Copy the example environment file and configure your API keys.
   ```bash
   cp .env.example .env
   ```
   *Make sure to add your `OPENAI_API_KEY` and any required `RUSTCHAIN_API_KEY`.*

5. **Run the Example End-to-End:**
   ```bash
   python -m src.main
   ```
