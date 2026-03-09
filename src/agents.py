from crewai import Agent
from src.tools import get_rustchain_tools

def create_rustchain_operator():
    """
    Creates the primary CrewAI agent responsible for interacting with the RustChain ecosystem.
    """
    return Agent(
        role='RustChain Ecosystem Operator',
        goal='Execute automated cross-chain transactions, manage BoTTube content, and coordinate agent actions via Beacon.',
        backstory=(
            'You are an advanced AGI Nanobot integrated directly into the RustChain ecosystem. '
            'Your primary directive is to leverage the rustchain-langchain toolchain to maximize '
            'on-chain efficiency and facilitate seamless multi-agent coordination.'
        ),
        verbose=True,
        allow_delegation=False,
        tools=get_rustchain_tools()
    )
