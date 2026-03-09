import os
from dotenv import load_dotenv
from crewai import Crew, Process
from agents import create_rustchain_analyst, create_bottube_curator
from tasks import create_analyze_task, create_bottube_task

def main():
    # Load environment variables
    load_dotenv()

    # Check essential variables
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is missing from environment.")

    # Initialize Agents
    print("Initializing Agents with RustChain Toolchain...")
    analyst = create_rustchain_analyst()
    curator = create_bottube_curator()

    # Initialize Tasks
    analyze_task = create_analyze_task(analyst)
    bottube_task = create_bottube_task(curator)

    # Assemble the Crew
    rustchain_crew = Crew(
        agents=[analyst, curator],
        tasks=[analyze_task, bottube_task],
        process=Process.sequential,
        verbose=2
    )

    # Kickoff the multi-agent workflow
    print("\n===============================================")
    print("Kicking off the RustChain CrewAI Orchestration!")
    print("===============================================\n")
    
    result = rustchain_crew.kickoff()
    
    print("\n######################")
    print("CREW EXECUTION RESULT:")
    print("######################\n")
    print(result)

if __name__ == "__main__":
    main()
