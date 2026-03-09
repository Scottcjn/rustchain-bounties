from crewai import Agent
from src.tools import get_rustchain_tools

def get_rustchain_operator():
    return Agent(
        role='RustChain Operations Specialist',
        goal='Execute RustChain network transactions and coordinate BoTTube uploads seamlessly.',
        backstory='An expert blockchain operator specializing in the RustChain ecosystem. Capable of communicating with other agents using the Beacon protocol.',
        tools=get_rustchain_tools(),
        verbose=True,
        allow_delegation=False
    )
