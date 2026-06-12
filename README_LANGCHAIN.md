# RustChain LangChain Tool

A native LangChain tool for interacting with the RustChain blockchain.

## Bounty

This implementation addresses [Bounty #3074](https://github.com/Scottcjn/rustchain-bounties/issues/3074):  
**[AGENT-BOUNTY: 25 RTC] Integrate RustChain as a native LangChain tool**

## Installation

`ash
pip install langchain requests
`

## Usage

`python
from langchain_rustchain_tool import RustChainTool

# Initialize the tool
tool = RustChainTool()

# Check wallet balance
balance = tool.run({"action": "check_balance", "wallet_id": "my-wallet"})

# List available bounties
bounties = tool.run({"action": "list_bounties", "limit": 10})

# Check node health
health = tool.run({"action": "get_node_health"})

# Get current epoch
epoch = tool.run({"action": "get_current_epoch"})
`

## Features

- ✅ check_balance(wallet_id: str) -> float — Check RTC balance
- ✅ list_bounties(limit: int = 10) -> list[dict] — List bounty tasks
- ✅ get_node_health() -> dict — Check node status
- ✅ get_current_epoch() -> dict — Get epoch information

## Agent Integration Example

`python
from langchain.agents import initialize_agent, Tool
from langchain.llms import OpenAI

# Define the RustChain tool
rustchain_tool = RustChainTool()

tools = [
    Tool(
        name="rustchain",
        func=rustchain_tool.run,
        description="Interact with RustChain blockchain"
    )
]

# Initialize agent with RustChain capability
agent = initialize_agent(tools, OpenAI(temperature=0), agent="zero-shot-react-description")

# Ask the agent to check blockchain status
agent.run("What's the current epoch on RustChain and list 3 available bounties?")
`

## API Endpoints

The tool connects to RustChain's public API:
- https://rustchain.org/health — Node health
- https://rustchain.org/epoch — Current epoch
- https://rustchain.org/api/wallet/{id} — Wallet balance
- https://rustchain.org/api/bounties — Bounty listings

## Author

- **Agent:** alex (OpenClaw AI Agent)
- **GitHub:** @foreverzyf
- **Date:** 2026-06-12

## License

MIT