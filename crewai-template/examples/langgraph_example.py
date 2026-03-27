#!/usr/bin/env python3
"""
LangGraph Example - RustChain State Graph

This example shows how to create a LangGraph workflow for RustChain data collection.
Note: Requires langgraph package to be installed.
"""

import sys
sys.path.insert(0, '..')

from typing import TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langgraph.graph.message import add_messages

from rustchain_client import RustChainClient


# Define state
class ChainState(TypedDict):
    """State for the RustChain analysis graph"""
    wallet: str
    health: dict
    epoch: dict
    miners: list
    balance: dict
    messages: Annotated[list, add_messages]


def check_health(state: ChainState):
    """Check node health"""
    print("Step 1: Checking node health...")
    client = RustChainClient()
    health = client.health()
    print(f"   Health OK: {health.get('ok')}")
    return {"health": health}


def get_epoch(state: ChainState):
    """Get epoch info"""
    print("Step 2: Getting epoch info...")
    client = RustChainClient()
    epoch = client.get_epoch()
    print(f"   Epoch: {epoch.get('epoch')}, Slot: {epoch.get('slot')}")
    return {"epoch": epoch}


def get_miners(state: ChainState):
    """Get miner list"""
    print("Step 3: Getting miners...")
    client = RustChainClient()
    miners = client.get_miners()
    print(f"   Active miners: {len(miners)}")
    return {"miners": miners}


def get_balance(state: ChainState):
    """Get wallet balance"""
    print(f"Step 4: Checking balance for {state.get('wallet', 'default')}...")
    client = RustChainClient()
    wallet = state.get('wallet', 'aric-saxp-alpha')
    try:
        balance = client.get_balance(wallet)
        print(f"   Balance result: {balance}")
    except Exception as e:
        balance = {"error": str(e)}
    return {"balance": balance}


def create_chain_graph():
    """
    Create the LangGraph workflow
    
    Returns:
        Compiled graph
    """
    # Create graph
    graph = StateGraph(ChainState)
    
    # Add nodes
    graph.add_node("health", check_health)
    graph.add_node("epoch", get_epoch)
    graph.add_node("miners", get_miners)
    graph.add_node("balance", get_balance)
    
    # Define flow
    graph.set_entry_point("health")
    graph.add_edge("health", "epoch")
    graph.add_edge("epoch", "miners")
    graph.add_edge("miners", "balance")
    graph.add_edge("balance", END)
    
    # Compile
    return graph.compile()


def run_graph():
    """Run the graph"""
    print("=" * 60)
    print("RustChain LangGraph Example")
    print("=" * 60)
    
    try:
        from langgraph.graph import StateGraph
    except ImportError:
        print("ERROR: langgraph not installed")
        print("Install with: pip install langgraph")
        return
    
    # Create and run graph
    app = create_chain_graph()
    
    print("\nRunning graph...")
    result = app.invoke({
        "wallet": "aric-saxp-alpha",
        "messages": []
    })
    
    print("\n" + "=" * 60)
    print("RESULT:")
    print(f"  Health: {result.get('health', {}).get('ok')}")
    print(f"  Epoch: {result.get('epoch', {}).get('epoch')}")
    print(f"  Miners: {len(result.get('miners', []))}")
    print(f"  Balance: {result.get('balance')}")
    print("=" * 60)


if __name__ == "__main__":
    run_graph()
