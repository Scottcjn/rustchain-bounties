from langchain_rustchain import RustChainTool


tool = RustChainTool()
print("health:", tool.invoke({"action": "get_node_health"}))
print("epoch:", tool.invoke({"action": "get_current_epoch"}))
print("balance:", tool.invoke({"action": "check_balance", "wallet_id": "crewcontentstudiocom"}))
try:
    print("bounties:", tool.invoke({"action": "list_bounties", "limit": 3}))
except RuntimeError as exc:
    print("bounty endpoint unavailable on this node:", exc)
