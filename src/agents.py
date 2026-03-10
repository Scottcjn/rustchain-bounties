from crewai import Agent
from src.tools.rustchain_tools import query_rustchain_network, execute_bottube_action, beacon_coordinate

def create_blockchain_analyst():
    return Agent(
        role='RustChain Data Analyst',
        goal='Analyze RustChain network status and execute BoTTube actions.',
        backstory='An expert in the RustChain ecosystem, highly capable of reading chain data and interacting with BoTTube smart contracts.',
        verbose=True,
        allow_delegation=False,
        tools=[query_rustchain_network, execute_bottube_action]
    )

def create_beacon_coordinator():
    return Agent(
        role='Beacon Network Coordinator',
        goal='Coordinate findings with other agents via the Beacon protocol.',
        backstory='A communication specialist agent that uses Beacon to broadcast vital ecosystem updates and align multi-agent tasks.',
        verbose=True,
        allow_delegation=False,
        tools=[beacon_coordinate]
    )
