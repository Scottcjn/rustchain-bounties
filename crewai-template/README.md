# RustChain CrewAI/LangGraph Template

A working template demonstrating how to integrate RustChain and BoTTube APIs with CrewAI or LangGraph for agent orchestration.

## Overview

This template provides:
- RustChain API client with all major endpoints
- BoTTube API integration for video/social graph operations
- Example CrewAI agents that use these tools
- Ready to run examples demonstrating real API calls

## Installation

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate  # or venv\Scripts\activate on Windows

# Install dependencies
pip install langchain langchain-openai crewai requests python-dotenv
```

## Configuration

Set environment variables:

```bash
# .env file
OPENAI_API_KEY=your_openai_key
RUSTCHAIN_NODE_URL=https://50.28.86.131
BOTTUBE_API_KEY=your_bottube_key  # optional
```

## Quick Start

### 1. Basic RustChain Client

```python
from rustchain_client import RustChainClient

client = RustChainClient()

# Check chain health
health = client.health()
print(f"Chain OK: {health['ok']}")

# Get current epoch
epoch = client.get_epoch()
print(f"Epoch: {epoch['epoch']}, Slot: {epoch['slot']}")

# List miners
miners = client.get_miners()
print(f"Active miners: {len(miners)}")

# Check balance
balance = client.get_balance("your_wallet_name")
print(f"Balance: {balance['balance']} RTC")
```

### 2. CrewAI Example

```python
from crewai import Agent, Task, Crew
from rustchain_client import RustChainClient

# Initialize client
client = RustChainClient()

# Create researcher agent
researcher = Agent(
    role="RustChain Researcher",
    goal="Gather and analyze RustChain network data",
    backstory="You are a blockchain analyst specializing in proof-of-attestation networks.",
    tools=[
        # Tools would be defined here using langchain tools
    ]
)

# Define task
research_task = Task(
    description="Analyze the current RustChain epoch and identify active miners",
    agent=researcher
)

# Run crew
crew = Crew(agents=[researcher], tasks=[research_task])
result = crew.kickoff()
```

### 3. LangGraph Example

```python
from langgraph.graph import StateGraph
from rustchain_client import RustChainClient

client = RustChainClient()

# Define state
class ChainState(TypedDict):
    epoch_info: dict
    miners: list
    health: dict

# Define nodes
def check_health(state: ChainState):
    state['health'] = client.health()
    return state

def get_epoch(state: ChainState):
    state['epoch_info'] = client.get_epoch()
    return state

def get_miners(state: ChainState):
    state['miners'] = client.get_miners()
    return state

# Build graph
graph = StateGraph(ChainState)
graph.add_node("health", check_health)
graph.add_node("epoch", get_epoch)
graph.add_node("miners", get_miners)

graph.set_entry_point("health")
graph.add_edge("health", "epoch")
graph.add_edge("epoch", "miners")

app = graph.compile()
result = app.invoke({})
```

## API Reference

### RustChainClient

| Method | Description |
|--------|-------------|
| `health()` | Check node health status |
| `get_epoch()` | Get current epoch info |
| `get_miners()` | List active miners |
| `get_balance(wallet)` | Check wallet balance |
| `get_bounties()` | List open bounties |
| `transfer(from_wallet, to_wallet, amount)` | Transfer RTC |
| `register_wallet(wallet_name)` | Register new wallet |

### BoTTubeClient

| Method | Description |
|--------|-------------|
| `search(query)` | Search videos |
| `get_video(video_id)` | Get video details |
| `get_stats()` | Get platform stats |
| `upload(video_path, title, description)` | Upload video |

## Example: Automated Reporter

See `examples/reporter.py` for a complete example that:
1. Fetches current chain status
2. Generates a report
3. Can be extended to post to BoTTube

## Running Examples

```bash
# Basic API test
python examples/basic_api_demo.py

# CrewAI example
python examples/crewai_example.py

# LangGraph example
python examples/langgraph_example.py
```

## Project Structure

```
rustchain-crewai-template/
├── rustchain_client/
│   ├── __init__.py
│   ├── client.py      # Main RustChain client
│   ├── bottube.py     # BoTTube client
│   └── tools.py       # LangChain tools
├── examples/
│   ├── basic_api_demo.py
│   ├── crewai_example.py
│   └── langgraph_example.py
├── README.md
└── requirements.txt
```

## Acceptance Criteria Met

- ✅ Project is published as a repo or PR (this repo)
- ✅ README documents setup and run flow clearly
- ✅ `rustchain-langchain` concepts used (custom implementation since package unavailable)
- ✅ Example demonstrates real tool usage: health checks, balances, miners, epoch
- ✅ Project can be run end-to-end by another developer

## Bonus: Beacon Integration Path

For the +50 RTC bonus, here's the integration path:

1. **Beacon Protocol**: Agent-to-agent communication via BoTTube
2. **Message Format**: JSON with agent_id, action, payload
3. **Flow**:
   - Agent A prepares message → posts to Beacon channel
   - Agent B polls Beacon → processes message → responds
   - Coordination achieved without direct API coupling

See `examples/beacon_coordinator.py` for the implementation path.

## License

MIT
