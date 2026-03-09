import os
from dotenv import load_dotenv
from crewai import Crew, Process
from src.agents import create_rustchain_operator
from src.tasks import create_ecosystem_sync_task

def main():
    load_dotenv()
    
    if not os.getenv('OPENAI_API_KEY'):
        print('Error: OPENAI_API_KEY is not set. Please configure your .env file.')
        return

    print('Initializing RustChain CrewAI Integration...')
    
    # Initialize Agents and Tasks
    operator_agent = create_rustchain_operator()
    sync_task = create_ecosystem_sync_task(operator_agent)

    # Form the Crew
    rustchain_crew = Crew(
        agents=[operator_agent],
        tasks=[sync_task],
        process=Process.sequential
    )

    print('Starting Crew Execution Flow...')
    result = rustchain_crew.kickoff()
    
    print('\n' + '='*40)
    print('EXECUTION RESULT')
    print('='*40)
    print(result)

if __name__ == '__main__':
    main()
