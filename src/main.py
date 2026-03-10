import os
from dotenv import load_dotenv
from crewai import Crew, Process
from src.agents import create_blockchain_analyst, create_beacon_coordinator
from src.tasks import analyze_chain_task, broadcast_status_task

def main():
    # Load environment variables
    load_dotenv()
    
    # Ensure OpenAI API key is set for CrewAI's default LLM dependency
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY is not set. Execution might fail if LLM is called.")

    print("Initializing Agents...")
    analyst = create_blockchain_analyst()
    coordinator = create_beacon_coordinator()

    print("Initializing Tasks...")
    task1 = analyze_chain_task(analyst)
    task2 = broadcast_status_task(coordinator)

    # Form the Crew
    rustchain_crew = Crew(
        agents=[analyst, coordinator],
        tasks=[task1, task2],
        process=Process.sequential,
        verbose=True
    )

    print("\n==========================================")
    print("Starting RustChain x CrewAI Execution...")
    print("==========================================\n")
    
    result = rustchain_crew.kickoff()
    
    print("\n######################")
    print("EXECUTION COMPLETE")
    print("######################\n")
    print("Final Output:\n", result)

if __name__ == "__main__":
    main()
