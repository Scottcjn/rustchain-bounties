from crewai import Task

def analyze_chain_task(agent):
    return Task(
        description='Query the current block height of RustChain using your tools and execute a routine BoTTube check-in action.',
        expected_output='A brief summary report of the chain status and BoTTube action result.',
        agent=agent
    )

def broadcast_status_task(agent):
    return Task(
        description='Take the summary report from the blockchain analyst and broadcast it to the broader network using the Beacon coordination tool.',
        expected_output='Confirmation string of the Beacon broadcast.',
        agent=agent
    )
