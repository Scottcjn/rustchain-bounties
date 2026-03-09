from crewai import Task

def create_ecosystem_sync_task(agent):
    """
    Creates a task for the agent to utilize RustChain, BoTTube, and Beacon.
    """
    return Task(
        description=(
            '1. Analyze the current RustChain ecosystem state using your RustChain tools.\n'
            '2. Format the insights and interact with the BoTTube network.\n'
            '3. Finally, broadcast a synchronization signal to peer agents using the Beacon coordination tool.'
        ),
        expected_output='A detailed execution log confirming the RustChain state query, BoTTube interaction, and the Beacon broadcast payload.',
        agent=agent
    )
