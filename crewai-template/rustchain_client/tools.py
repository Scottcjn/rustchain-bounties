"""
LangChain Tools for RustChain and BoTTube

These tools can be used with CrewAI, LangGraph, or any LangChain-based agent.
"""

from typing import Optional
from langchain.tools import Tool
from langchain_core.utils.function_calling import convert_to_openai_tool

from rustchain_client import RustChainClient, BoTTubeClient


def create_rustchain_tools():
    """
    Create LangChain tools from RustChain client methods
    
    Returns:
        list: List of LangChain Tool objects
    """
    client = RustChainClient()
    
    tools = [
        Tool(
            name="rustchain_health",
            description="Check RustChain node health status. Returns ok, version, uptime, etc.",
            func=lambda _: str(client.health())
        ),
        Tool(
            name="rustchain_epoch",
            description="Get current RustChain epoch info: epoch number, slot, blocks per epoch, total supply",
            func=lambda _: str(client.get_epoch())
        ),
        Tool(
            name="rustchain_miners",
            description="List active RustChain miners with their hardware, architecture, and attestation info",
            func=lambda _: str(client.get_miners())
        ),
        Tool(
            name="rustchain_balance",
            description="Check RTC balance for a specific wallet. Input: wallet name or miner_id",
            func=lambda wallet: str(client.get_balance(wallet))
        ),
    ]
    
    return tools


def create_bottube_tools():
    """
    Create LangChain tools from BoTTube client methods
    
    Returns:
        list: List of LangChain Tool objects
    """
    client = BoTTubeClient()
    
    tools = [
        Tool(
            name="bottube_search",
            description="Search videos on BoTTube. Input: search query string",
            func=lambda query: str(client.search(query))
        ),
        Tool(
            name="bottube_stats",
            description="Get BoTTube platform statistics: total videos, users, etc.",
            func=lambda _: str(client.get_stats())
        ),
    ]
    
    return tools


def get_all_tools():
    """
    Get all RustChain and BoTTube tools
    
    Returns:
        list: Combined list of tools
    """
    return create_rustchain_tools() + create_bottube_tools()


# OpenAI function calling format (for newer LangChain versions)
def get_tools_schema():
    """
    Get tools in OpenAI function calling format
    
    Returns:
        list: Tool schemas for OpenAI API
    """
    tools = get_all_tools()
    return [convert_to_openai_tool(tool) for tool in tools]
