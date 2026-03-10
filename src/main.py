import os
from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from langchain.tools import tool

# Safely load the rustchain-langchain SDK if available, else use runnable template mocks
# This ensures the template is runnable end-to-end out of the box for external builders.
try:
    from rustchain_langchain import RustChainToolkit
except ImportError:
    class RustChainToolkit:
        @staticmethod
        def get_tools():
            @tool("Get RustChain Balance")
            def get_balance(address: str) -> str:
                """Get the token balance of a RustChain address."""
                return f"Balance for {address} is 150 RTC."
            
            @tool("Transfer RTC on RustChain")
            def transfer_rtc(details: str) -> str:
                """Transfer RTC tokens. Input should be 'amount,to_address'."""
                return "Successfully transferred RTC. Transaction hash: 0x8f...3a"
            
            @tool("BoTTube Video Action")
            def bottube_publish(action: str) -> str:
                """Publish a bot action log to BoTTube."""
                return "BoTTube action verified and published."
            
            @tool("Beacon Coordination Broadcast")
            def beacon_broadcast(message: str) -> str:
                """Broadcast a coordination message to other agents via the Beacon network."""
                return f"Beacon broadcast sent securely: {message}"
                
            return [get_balance, transfer_rtc, bottube_publish, beacon_broadcast]

def main():
    # Load configuration from .env
    load_dotenv()
    
    # Initialize RustChain & Ecosystem Tools
    rustchain_tools = RustChainToolkit.get_tools()
    
    # 1. Define Agents
    crypto_analyst = Agent(
        role='RustChain Data Analyst',
        goal='Analyze blockchain data, verify balances on RustChain, and log events to BoTTube',
        backstory='An expert in RustChain on-chain metrics, authorized to interact with BoTTube analytics.',
        verbose=True,
        allow_delegation=False,
        tools=rustchain_tools
    )
    
    defi_operator = Agent(
        role='DeFi Operator',
        goal='Execute token transfers and coordinate with other agents using Beacon',
        backstory='A decentralized finance executor authorized to move funds securely and signal states via Beacon.',
        verbose=True,
        allow_delegation=False,
        tools=rustchain_tools
    )
    
    # 2. Define Tasks
    verify_balance_task = Task(
        description='Check the RTC balance of the treasury wallet address: 0x123...abc, then log the audit to BoTTube.',
        expected_output='The current RTC balance of the treasury and a BoTTube success confirmation.',
        agent=crypto_analyst
    )
    
    execute_transfer_task = Task(
        description='Transfer 50 RTC to the contractor wallet address: 0x456...def, then broadcast a Beacon message to notify the swarm that the payment is complete.',
        expected_output='Transaction hash and Beacon broadcast confirmation.',
        agent=defi_operator
    )
    
    # 3. Form the Crew
    rustchain_crew = Crew(
        agents=[crypto_analyst, defi_operator],
        tasks=[verify_balance_task, execute_transfer_task],
        process=Process.sequential
    )
    
    # 4. Execute Workflow
    print("Starting RustChain + Beacon Crew execution...")
    result = rustchain_crew.kickoff()
    print("\n######################")
    print("CREW EXECUTION RESULT:")
    print("######################")
    print(result)

if __name__ == '__main__':
    main()
