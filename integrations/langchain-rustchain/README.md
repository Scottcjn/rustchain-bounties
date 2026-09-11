# LangChain RustChain integration

A small, read-only LangChain `BaseTool` for RustChain's public API, built for bounty [Scottcjn/rustchain-bounties#3074](https://github.com/Scottcjn/rustchain-bounties/issues/3074).

## Install

```bash
pip install -e ./integrations/langchain-rustchain
```

## Usage

```python
from langchain_rustchain import RustChainTool

tool = RustChainTool()
print(tool.invoke({"action": "get_node_health"}))
print(tool.invoke({"action": "get_current_epoch"}))
print(tool.invoke({"action": "check_balance", "wallet_id": "crewcontentstudiocom"}))
print(tool.invoke({"action": "list_bounties", "limit": 5}))
```

The package exposes the required direct methods as well: `check_balance`, `list_bounties`, `get_node_health`, and `get_current_epoch`.

## Safety and scope

The integration is intentionally read-only. It does not claim bounties, transfer RTC, sign transactions, or require private keys.

## Validation

```bash
python -m pip install -e "integrations/langchain-rustchain[test]"
python -m pytest integrations/langchain-rustchain/tests -q
python integrations/langchain-rustchain/examples/agent_example.py
```

AI assistance was used to implement and test this contribution and is disclosed in the linked bounty claim/PR.
