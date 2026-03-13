# BHP Beacon AI Agent

A demonstration AI agent integrating with Beacon 2.6 for the Bounty Hunter Project (BHP).

## Overview

This agent demonstrates three core Beacon 2.6 features:
1. **Heartbeat** - Announcing presence via `beacon.ping()` and `beacon.listen()`
2. **Mayday** - Sending and responding to distress signals
3. **Contracts** - Using property contracts for resource management

## Bonus Features

- **Multi-agent coordination** - Coordinating tasks across multiple agents
- **Creative use case** - Distributed training task coordination

## Requirements

- Python 3.8+
- beacon-skill >= 2.11.1

## Installation

```bash
pip install -r requirements.txt
```

## Configuration

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your settings:
   ```
   AGENT_ID=your-agent-id
   AGENT_ROLE=worker
   ```

## Usage

### Run All Demonstrations

```bash
python bhp_beacon_agent.py
```

### Use as Library

```python
from bhp_beacon_agent import BHPBeaconAgent

# Create agent
agent = BHPBeaconAgent(agent_id="my-agent", role="worker")

# Send heartbeat
agent.send_single_heartbeat()

# Send mayday
agent.send_mayday("need_compute", {"task": "inference"})

# Offer contract
agent.offer_contract("gpu_hours", price=10, duration_seconds=3600)

# Shutdown
agent.shutdown()
```

## Features Demonstrated

### 1. Heartbeat
- Regular presence announcements
- Neighbor discovery
- Network scanning

### 2. Mayday Distress Signals
- Emergency resource requests
- Priority-based signaling
- Historical tracking

### 3. Property Contracts
- Resource offering
- Resource renting
- Contract management

### 4. Multi-Agent Coordination (Bonus)
- Task distribution
- Agent communication
- Distributed training coordination

## Project Structure

```
bhp-beacon-agent/
├── bhp_beacon_agent.py    # Main agent implementation
├── requirements.txt       # Python dependencies
├── .env.example          # Environment configuration template
└── README.md             # This file
```

## Testing

Run the built-in demonstrations:

```bash
python bhp_beacon_agent.py
```

This will execute:
1. Heartbeat demo
2. Mayday demo
3. Contracts demo
4. Multi-agent coordination demo

## Bounty Submission

This implementation satisfies the following requirements:
- ✅ Uses Beacon 2.6
- ✅ Implements Heartbeat feature
- ✅ Implements Mayday feature
- ✅ Implements Contracts feature
- ✅ Open source (MIT license)
- ✅ Includes demonstration code
- ✅ Multi-agent coordination (bonus)
- ✅ Creative use case: Distributed training (bonus)

## Author

Jack - BHP Team

## License

MIT License - See LICENSE file for details

## Resources

- [beacon-skill on GitHub](https://github.com/Scottcjn/beacon-skill)
- [beacon-skill on PyPI](https://pypi.org/project/beacon-skill/)
- [RustChain Network](https://50.28.86.131/explorer)
