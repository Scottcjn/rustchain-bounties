from crewai import Agent
from langchain_openai import ChatOpenAI
from tools import fetch_rustchain_activity, beacon_broadcast

class RustChainAgents:
    def __init__(self):
        self.llm = ChatOpenAI(model_name="gpt-4", temperature=0.7)

    def onchain_analyst(self):
        return Agent(
            role='RustChain Data Analyst',
            goal='Extract and analyze on-chain BoTTube and RTC transaction data.',
            backstory='An expert in blockchain analytics, specializing in the RustChain toolchain.',
            tools=[fetch_rustchain_activity],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )

    def beacon_coordinator(self):
        return Agent(
            role='Beacon Ecosystem Coordinator',
            goal='Coordinate agent actions and broadcast analytical findings to the Beacon network.',
            backstory='You are responsible for agent-to-agent synchronization using the Beacon layer.',
            tools=[beacon_broadcast],
            llm=self.llm,
            verbose=True,
            allow_delegation=False
        )
