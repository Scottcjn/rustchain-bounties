# RustChain x CrewAI Template

A ready-to-use template integrating RustChain tools and Beacon coordination within the CrewAI orchestration framework.

## Overview
This project demonstrates how autonomous agents can leverage the `rustchain-langchain` toolset to query chain data, execute BoTTube actions, and coordinate via the Beacon protocol using CrewAI.

## Setup Instructions

1. Clone the repository.
2. Create a virtual environment: `python -m venv venv`
3. Activate the environment:
   - Mac/Linux: `source venv/bin/activate`
   - Windows: `venv\Scripts\activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Set up your environment variables by copying `.env.example` to `.env` and adding your API keys.

## Running the Example
Execute the main script to kick off the agent workflow end-to-end:
```bash
python -m src.main
```
