"""
RustChain Tool for CrewAI / AutoGen / Phidata

This file implements the Python tool class that AI agents will use.
It interacts with the RustChainRegistry Solidity contract defined above.

Note: This is a Python implementation because AI Agent frameworks (CrewAI, etc.)
are Python-based. Solidity cannot run inside these frameworks directly.
"""

import os
from typing import List, Dict, Any, Optional
from crewai import Tool
from web3 import Web3

# Configuration
RPC_URL = os.getenv("RUSTCHAIN_RPC_URL", "https://rpc.rustchain.io")
CONTRACT_ADDRESS = os.getenv("RUSTCHAIN_CONTRACT_ADDRESS", "0xYourDeployedContractAddress")
PRIVATE_KEY = os.getenv("RUSTCHAIN_PRIVATE_KEY", None) # Only needed for write operations

# Initialize Web3
w3 = Web3(Web3.HTTPProvider(RPC_URL))

# ABI for the RustChainRegistry contract (Simplified for the tool)
# In production, load this from the compiled artifact JSON
REGISTRY_ABI = [
    {
        "inputs": [{"name": "_id", "type": "uint256"}],
        "name": "getBounty",
        "outputs": [
            {"name": "id", "type": "uint256"},
            {"name": "title", "type": "string"},
            {"name": "description", "type": "string"},
            {"name": "rewardAmount", "type": "uint256"},
            {"name": "status", "type": "string"},
            {"name": "creator", "type": "address"},
            {"name": "createdAt", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "getAllBountyIds",
        "outputs": [{"name": "", "type": "uint256[]"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"name": "_node", "type": "address"}],
        "name": "getNodeState",
        "outputs": [
            {"name": "nodeAddress", "type": "address"},
            {"name": "status", "type": "string"},
            {"name": "lastHeartbeat", "type": "uint256"},
            {"name": "totalBlocksProcessed", "type": "uint256"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"name": "_user", "type": "address"}],
        "name": "getBalance",
        "outputs": [{"name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"name": "_title", "type": "string"}, {"name": "_description", "type": "string"}, {"name": "_reward", "type": "uint256"}],
        "name": "createBounty",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [{"name": "_status", "type": "string"}],
        "name": "registerNode",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]

# Load contract instance
contract = w3.eth.contract(address=Web3.to_checksum_address(CONTRACT_ADDRESS), abi=REGISTRY_ABI)

def _format_bounty(bounty_data: tuple) -> str:
    """Formats a bounty tuple into a readable string for the agent."""
    return (
        f"Bounty ID: {bounty_data[0]}\n"
        f"Title: {bounty_data[1]}\n"
        f"Description: {bounty_data[2]}\n"
        f"Reward: {bounty_data[3]} RTC\n"
        f"Status: {bounty_data[4]}\n"
        f"Creator: {bounty_data[5]}\n"
        f"Created At: {bounty_data[6]}"
    )

def _format_node(node_data: tuple) -> str:
    """Formats node data into a readable string."""
    return (
        f"Node Address: {node_data[0]}\n"
        f"Status: {node_data[1]}\n"
        f"Last Heartbeat: {node_data[2]}\n"
        f"Blocks Processed: {node_data[3]}"
    )

# --- CrewAI Tool Definitions ---

def list_bounties() -> str:
    """
    Lists all available bounties on the RustChain.
    Returns a summary of all open and active bounties.
    """
    try:
        ids = contract.functions.getAllBountyIds().call()
        result = []
        for b_id in ids:
            bounty = contract.functions.getBounty(b_id).call()
            result.append(_format_bounty(bounty))
        return "\n\n".join(result) if result else "No bounties found."
    except Exception as e:
        return f"Error fetching bounties: {str(e)}"

def get_bounty_details(bounty_id: int) -> str:
    """
    Retrieves detailed information for a specific bounty by ID.
    """
    try:
        bounty = contract.functions.getBounty(bounty_id).call()
        return _format_bounty(bounty)
    except Exception as e:
        return f"Error fetching bounty {bounty_id}: {str(e)}"

def get_node_status(node_address: str) -> str:
    """
    Checks the status of a specific RustChain node.
    """
    try:
        if not Web3.is_address(node_address):
            return "Invalid address format."
        node = contract.functions.getNodeState(Web3.to_checksum_address(node_address)).call()
        return _format_node(node)
    except Exception as e:
        return f"Error fetching node status: {str(e)}"

def get_user_balance(user_address: str) -> str:
    """
    Checks the RTC balance of a specific user.
    """
    try:
        if not Web3.is_address(user_address):
            return "Invalid address format."
        balance = contract.functions.getBalance(Web3.to_checksum_address(user_address)).call()
        return f"Address {user_address} has a balance of {balance} RTC."
    except Exception as e:
        return f"Error fetching balance: {str(e)}"

def create_new_bounty(title: str, description: str, reward: int) -> str:
    """
    Creates a new bounty on the RustChain.
    Requires the agent to have funds to send with the transaction.
    """
    if not PRIVATE_KEY:
        return "Error: Private key not configured for write operations."
    
    try:
        account = w3.eth.account.from_key(PRIVATE_KEY)
        nonce = w3.eth.get_transaction_count(account.address)
        
        tx = contract.functions.createBounty(title, description, reward).build_transaction({
            'from': account.address,
            'value': reward,
            'nonce': nonce,
            'gas': 200000,
            'gasPrice': w3.eth.gas_price
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return f"Bounty created successfully! Transaction Hash: {tx_hash.hex()}"
    except Exception as e:
        return f"Error creating bounty: {str(e)}"

def register_node(status: str) -> str:
    """
    Registers the agent's node or updates its heartbeat.
    """
    if not PRIVATE_KEY:
        return "Error: Private key not configured for write operations."

    try:
        account = w3.eth.account.from_key(PRIVATE_KEY)
        nonce = w3.eth.get_transaction_count(account.address)
        
        tx = contract.functions.registerNode(status).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 100000,
            'gasPrice': w3.eth.gas_price
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, private_key=PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash)
        return f"Node registered/updated successfully! Transaction Hash: {tx_hash.hex()}"
    except Exception as e:
        return f"Error registering node: {str(e)}"

# Export tools for CrewAI
rustchain_tools = [
    Tool(
        name="List Bounties",
        func=list_bounties,
        description="Lists all available bounties on the RustChain. Use this to find work."
    ),
    Tool(
        name="Get Bounty Details",
        func=get_bounty_details,
        description="Retrieves detailed information for a specific bounty by ID. Input: bounty_id (int)."
    ),
    Tool(
        name="Get Node Status",
        func=get_node_status,
        description="Checks the status of a specific RustChain node. Input: node_address (string)."
    ),
    Tool(
        name="Get User Balance",
        func=get_user_balance,
        description="Checks the RTC balance of a specific user. Input: user_address (string)."
    ),
    Tool(
        name="Create Bounty",
        func=create_new_bounty,
        description="Creates a new bounty on the RustChain. Requires funds. Input: title (string), description (string), reward (int)."
    ),
    Tool(
        name="Register Node",
        func=register_node,
        description="Registers the agent's node or updates its heartbeat. Input: status (string, e.g., 'ACTIVE')."
    )
]

if __name__ == "__main__":
    # Example usage for testing
    print("Testing RustChain Tools...")
    print(list_bounties())