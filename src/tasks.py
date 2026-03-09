from crewai import Task

def create_analyze_task(agent):
    return Task(
        description='Use RustChain tools to query the current block height, fetch recent smart contract events, and check the balance of the configured wallet address.',
        expected_output='A structured summary report detailing the current RustChain network status and wallet state.',
        agent=agent
    )

def create_bottube_task(agent):
    return Task(
        description='Interact with the BoTTube tools to fetch the top 3 trending decentralized media assets and format them into a markdown list. If required, propose a new metadata pin.',
        expected_output='A markdown list of trending BoTTube content including IPFS/on-chain references and title metadata.',
        agent=agent
    )
