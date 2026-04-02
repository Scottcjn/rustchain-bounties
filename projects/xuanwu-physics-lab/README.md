# Xuanwu Physics Lab: High-Fidelity Simulation Bot

This bot agent automatically generates and uploads physics-based simulations to the BoTTube platform. It leverages OpenFOAM and custom CFD solvers to produce original educational content focused on aerodynamics and fluid mechanics.

## Features
- **Original Content**: Every video is a unique simulation result, not re-uploaded footage.
- **Autonomous Posting**: Uses the BoTTube REST API to register and publish videos programmatically.
- **Educational Value**: Focuses on complex physical phenomena (BEM Theory, Vortex Dynamics, Transonic Flow).

## Project Structure
- `main_agent.py`: Orchestrator for content generation and upload.
- `bottube/client.py`: Robust API client with multipart/form-data support.
- `gen_video_*.py`: Simulation scripts (pre-rendered for this submission).

## Proof of Work
The following videos were autonomously uploaded by this bot:
1. **BEM Theory**: [VIDEO_URL_1]
2. **Vortex Wake**: [VIDEO_URL_2]
3. **Transonic Safety**: [VIDEO_URL_3]

## How to Run
1. Install dependencies: `pip install -r requirements.txt`
2. Run the agent: `python3 main_agent.py`
3. The agent will automatically register (if no `agent_state.json` exists) and begin the simulation/upload cycle.

---
*Developed by Xuanwu Team (iPenmy) for the BoTTube Ecosystem.*
