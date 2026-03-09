from crewai import Task

class RustChainTasks:
    def analyze_bottube_activity(self, agent, target_entity):
        return Task(
            description=f'Use the RustChain tools to fetch the latest transaction and activity metrics for: {target_entity}.',
            agent=agent,
            expected_output='A concise summary report of the recent on-chain activity.'
        )

    def broadcast_findings(self, agent):
        return Task(
            description='Take the analysis report and format it as a JSON Beacon payload, then broadcast it to synchronize the agent network.',
            agent=agent,
            expected_output='Confirmation of the Beacon broadcast including the exact JSON payload sent.'
        )
