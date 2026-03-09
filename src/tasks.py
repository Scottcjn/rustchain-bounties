from crewai import Task

def build_onchain_coordination_task(agent):
    return Task(
        description='Use RustChain tools to query the current network status. Then, use the Beacon Signal Tool to broadcast this status to other agents. Finally, formulate a summary for a potential BoTTube upload.',
        expected_output='A final status report detailing the RustChain query results, the BoTTube summary, and the Beacon broadcast confirmation.',
        agent=agent
    )
