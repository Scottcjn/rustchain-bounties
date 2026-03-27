#!/usr/bin/env python3
"""
CrewAI Example - RustChain Analyst Agent

This example shows how to create a CrewAI agent that uses RustChain tools.
Note: Requires crewai and langchain packages to be installed.
"""

import os
import sys

# Add parent to path
sys.path.insert(0, '..')

from langchain_openai import ChatOpenAI
from langchain.agents import AgentExecutor, create_openai_functions_agent
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder

from rustchain_client.tools import create_rustchain_tools, get_tools_schema


def create_rustchain_agent():
    """
    Create a CrewAI-style agent with RustChain tools
    
    Returns:
        AgentExecutor: Configured agent with tools
    """
    # Initialize LLM
    llm = ChatOpenAI(
        model="gpt-4",
        api_key=os.environ.get("OPENAI_API_KEY"),
        temperature=0
    )
    
    # Get tools
    tools = create_rustchain_tools()
    
    # Create prompt
    prompt = ChatPromptTemplate.from_messages([
        ("system", """You are a RustChain blockchain analyst. 
Your role is to gather and analyze data from the RustChain network.
Use the provided tools to fetch real data about the chain.
Provide accurate, up-to-date information."""),
        ("user", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad")
    ])
    
    # Create agent
    agent = create_openai_functions_agent(llm, tools, prompt)
    
    # Create executor
    executor = AgentExecutor(
        agent=agent,
        tools=tools,
        verbose=True,
        max_iterations=5
    )
    
    return executor


def run_analysis():
    """Run a sample analysis"""
    # Check for API key
    if not os.environ.get("OPENAI_API_KEY"):
        print("ERROR: OPENAI_API_KEY not set")
        print("Set it with: export OPENAI_API_KEY=your_key")
        return
    
    print("Creating RustChain Analyst Agent...")
    executor = create_rustchain_agent()
    
    print("\nRunning analysis: 'What's the current state of the RustChain network?'")
    print("-" * 60)
    
    try:
        result = executor.invoke({
            "input": "What's the current state of the RustChain network? Include epoch, slot, and miner info."
        })
        print("\n" + "=" * 60)
        print("RESULT:")
        print(result.get("output", "No output"))
    except Exception as e:
        print(f"Error: {e}")
        print("\nNote: You need OPENAI_API_KEY set and crewai/langchain installed")


if __name__ == "__main__":
    run_analysis()
