import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain_openai import ChatOpenAI

# Import RustChain tools from the rustchain-langchain toolkit
from rustchain_langchain.tools import (
    RustChainTransactionTool,
    BoTTubeUploadTool,
    BeaconCoordinationTool
)

# Load environment variables (API keys, RPC endpoints)
load_dotenv()

def main():
    # Initialize LLM
    llm = ChatOpenAI(model='gpt-4-turbo', temperature=0.7)

    # Initialize RustChain Tools
    tx_tool = RustChainTransactionTool()
    bottube_tool = BoTTubeUploadTool()
    beacon_tool = BeaconCoordinationTool()

    # Define the Web3 Agent utilizing Rustchain ecosystem
    rustchain_agent = Agent(
        role='RustChain Integration Specialist',
        goal='Execute blockchain transactions and coordinate cross-agent tasks using RustChain and Beacon.',
        backstory='An expert AI agent specialized in Web3 operations, RustChain transactions, and decentralized content publishing via BoTTube.',
        verbose=True,
        allow_delegation=False,
        tools=[tx_tool, bottube_tool, beacon_tool],
        llm=llm
    )

    # Define Tasks
    transaction_task = Task(
        description='Use the RustChainTransactionTool to query the latest block and send a 10 RTC test transaction to the oracle address. Then broadcast a coordination signal via Beacon using BeaconCoordinationTool.',
        expected_output='A transaction hash confirming the transfer and a Beacon coordination signal receipt.',
        agent=rustchain_agent
    )

    bottube_task = Task(
        description='Upload the transaction summary report to BoTTube using the BoTTubeUploadTool.',
        expected_output='A BoTTube video/document link containing the transaction summary.',
        agent=rustchain_agent
    )

    # Form the Crew with sequential processing
    rustchain_crew = Crew(
        agents=[rustchain_agent],
        tasks=[transaction_task, bottube_task],
        process=Process.sequential
    )

    # Kickoff the agent process
    print('Starting RustChain x CrewAI integration...')
    result = rustchain_crew.kickoff()
    
    print('\n================================================')
    print('CrewAI Execution Completed!')
    print('================================================')
    print(result)

if __name__ == '__main__':
    main()
