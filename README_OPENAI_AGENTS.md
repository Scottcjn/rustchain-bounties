# RustChain tools for the OpenAI Agents SDK

This integration exposes four native function tools:

- `check_balance(wallet_id)`
- `list_bounties(limit)`
- `get_node_health()`
- `get_current_epoch()`

Use Python 3.10 or newer, then install the SDK and the repository's HTTP
dependency:

```bash
python -m pip install "openai-agents>=0.7,<0.8" requests
```

Create and run an agent:

```python
from agents import Runner

from openai_agents_rustchain_tool import create_rustchain_agent

agent = create_rustchain_agent()
result = Runner.run_sync(agent, "List five open RustChain bounties.")
print(result.final_output)
```

`Runner` requires the normal OpenAI Agents SDK authentication. The underlying
tools only call public RustChain and GitHub endpoints, and can also be attached
to an existing agent:

```python
from agents import Agent

from openai_agents_rustchain_tool import RUSTCHAIN_TOOLS

agent = Agent(
    name="Bounty helper",
    instructions="Help contributors inspect public RustChain information.",
    tools=RUSTCHAIN_TOOLS,
)
```

HTTP failures, invalid JSON, and invalid arguments are returned as structured
`{"ok": false, "error": "..."}` results so an agent can explain the problem
instead of crashing.
