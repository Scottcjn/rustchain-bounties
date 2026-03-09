import os
from dotenv import load_dotenv
from crewai import Crew, Process
from agents import RustChainAgents
from tasks import RustChainTasks

def main():
    load_dotenv()
    print("Initializing RustChain CrewAI Template with Beacon Integration...")

    agents_config = RustChainAgents()
    tasks_config = RustChainTasks()

    # Instantiate agents
    analyst = agents_config.onchain_analyst()
    coordinator = agents_config.beacon_coordinator()

    # Instantiate tasks
    analyze_task = tasks_config.analyze_bottube_activity(analyst, "BoTTube_Channel_Alpha")
    broadcast_task = tasks_config.broadcast_findings(coordinator)

    # Assemble the crew
    rustchain_crew = Crew(
        agents=[analyst, coordinator],
        tasks=[analyze_task, broadcast_task],
        process=Process.sequential,
        verbose=True
    )

    # Kickoff the agent workflow
    result = rustchain_crew.kickoff()

    print("\n=========================================")
    print("CREW EXECUTION RESULT")
    print("=========================================")
    print(result)

if __name__ == "__main__":
    main()
