#!/usr/bin/env python3
"""
RustChain MCP Server - Query RustChain blockchain data via MCP protocol
"""

import os
import json
from mcp.server.fastmcp import FastMCP
import requests

# Initialize MCP server
mcp = FastMCP("RustChain")

# Configuration
RPC_URL = os.getenv("RUSTCHAIN_RPC_URL", "https://rpc.rustchain.com")


@mcp.tool()
def get_block(block_number: int = None, block_hash: str = None) -> dict:
    """
    Get block information by number or hash.
    
    Args:
        block_number: Block number (optional)
        block_hash: Block hash (optional)
    
    Returns:
        Block information including transactions, timestamp, etc.
    """
    if block_number is not None:
        method = "eth_getBlockByNumber"
        params = [hex(block_number), True]
    elif block_hash:
        method = "eth_getBlockByHash"
        params = [block_hash, True]
    else:
        return {"error": "Either block_number or block_hash must be provided"}
    
    payload = {
        "jsonrpc": "2.0",
        "method": method,
        "params": params,
        "id": 1
    }
    
    try:
        response = requests.post(RPC_URL, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        return result.get("result", {"error": "No result returned"})
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_transaction(tx_hash: str) -> dict:
    """
    Get transaction details by hash.
    
    Args:
        tx_hash: Transaction hash
    
    Returns:
        Transaction information including from, to, value, gas, etc.
    """
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionByHash",
        "params": [tx_hash],
        "id": 1
    }
    
    try:
        response = requests.post(RPC_URL, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        return result.get("result", {"error": "Transaction not found"})
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_balance(address: str) -> dict:
    """
    Get account balance.
    
    Args:
        address: Account address
    
    Returns:
        Balance in wei and RTC
    """
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [address, "latest"],
        "id": 1
    }
    
    try:
        response = requests.post(RPC_URL, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        balance_wei = result.get("result", "0x0")
        balance_rtc = int(balance_wei, 16) / 1e18 if balance_wei != "0x0" else 0
        return {
            "address": address,
            "balance_wei": balance_wei,
            "balance_rtc": balance_rtc
        }
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_latest_blocks(count: int = 10) -> list:
    """
    Get the latest N blocks.
    
    Args:
        count: Number of blocks to retrieve (default: 10)
    
    Returns:
        List of recent blocks
    """
    # First get latest block number
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_blockNumber",
        "params": [],
        "id": 1
    }
    
    try:
        response = requests.post(RPC_URL, json=payload, timeout=10)
        response.raise_for_status()
        result = response.json()
        latest_block = int(result.get("result", "0x0"), 16)
        
        blocks = []
        for i in range(count):
            block_num = latest_block - i
            block_info = get_block(block_number=block_num)
            if "error" not in block_info:
                blocks.append(block_info)
        
        return blocks
    except Exception as e:
        return {"error": str(e)}


@mcp.tool()
def get_network_status() -> dict:
    """
    Get network status information.
    
    Returns:
        Network info including chain ID, latest block, gas price, etc.
    """
    try:
        # Get chain ID
        chain_id_payload = {
            "jsonrpc": "2.0",
            "method": "eth_chainId",
            "params": [],
            "id": 1
        }
        
        # Get latest block
        block_payload = {
            "jsonrpc": "2.0",
            "method": "eth_blockNumber",
            "params": [],
            "id": 2
        }
        
        # Get gas price
        gas_payload = {
            "jsonrpc": "2.0",
            "method": "eth_gasPrice",
            "params": [],
            "id": 3
        }
        
        responses = []
        for payload in [chain_id_payload, block_payload, gas_payload]:
            response = requests.post(RPC_URL, json=payload, timeout=10)
            response.raise_for_status()
            responses.append(response.json())
        
        chain_id = int(responses[0].get("result", "0x0"), 16)
        latest_block = int(responses[1].get("result", "0x0"), 16)
        gas_price = int(responses[2].get("result", "0x0"), 16)
        
        return {
            "chain_id": chain_id,
            "latest_block": latest_block,
            "gas_price_wei": gas_price,
            "gas_price_gwei": gas_price / 1e9,
            "rpc_url": RPC_URL
        }
    except Exception as e:
        return {"error": str(e)}


if __name__ == "__main__":
    # Run the MCP server
    mcp.run()
