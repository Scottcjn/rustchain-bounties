import os
from dotenv import load_dotenv
from crewai import Crew, Process
from src.agents import get_rustchain_operator
from src.tasks import build_onchain_coordination_task

def run_template():
    load_dotenv()
    if not os.getenv("OPENAI_API_KEY"):
        print("Warning: OPENAI_API_KEY not set. CrewAI requires an LLM provider to run the agents.")

    # 1. Initialize Agents
    operator_agent = get_rustchain_operator()
    
    # 2. Assign Tasks
    coordination_task = build_onchain_coordination_task(operator_agent)

    # 3. Form Crew
    crew = Crew(
        agents=[operator_agent],
        tasks=[coordination_task],
        process=Process.sequential,
        verbose=True
    )

    print("Starting CrewAI RustChain Template Execution...")
    
    # 4. Kickoff Workflow
    result = crew.kickoff()
    
    print("\n===========================")
    print("--- Execution Result ---")
    print("===========================\n")
    print(result)

if __name__ == '__main__':
    run_template()
