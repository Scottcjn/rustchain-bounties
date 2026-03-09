import os
from crewai import Agent
from rustchain_langchain import RustChainToolKit

# Initialize RustChain toolkit globally for agents to access
toolkit = RustChainToolKit(
    rpc_url=os.getenv("RUSTCHAIN_RPC_URL"),
    private_key=os.getenv("RUSTCHAIN_PRIVATE_KEY"),
    beacon_key=os.getenv("BEACON_API_KEY")
)
rustchain_tools = toolkit.get_tools()

def create_rustchain_analyst():
    return Agent(
        role='RustChain Data Analyst',
        goal='Analyze RustChain network metrics, verify balances, and decode on-chain state.',
        backstory='An expert in blockchain data analysis, specifically tailored for the RustChain ecosystem.',
        verbose=True,
        allow_delegation=False,
        tools=rustchain_tools
    )

def create_bottube_curator():
    return Agent(
        role='BoTTube Content Curator',
        goal='Interact with BoTTube tools to publish metadata, retrieve trending content, and organize decentralized media.',
        backstory='A meticulous content curator focused on Web3 media distribution via BoTTube contracts.',
        verbose=True,
        allow_delegation=True,
        tools=rustchain_tools
    )
