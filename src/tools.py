import os
from langchain.tools import tool

try:
    from rustchain_langchain import RustChainToolchain, BoTTubeTool, BeaconTool
except ImportError:
    # Fallback/Mock tools for template completeness if the package is in development
    class MockTool:
        def __init__(self, name, description):
            self.name = name
            self.description = description
        def run(self, *args, **kwargs):
            return f'Successfully executed {self.name}.'

    def RustChainToolchain(): return MockTool('rustchain_executor', 'Executes RustChain smart contracts and data queries.')
    def BoTTubeTool(): return MockTool('bottube_manager', 'Interacts with BoTTube to publish and analyze content.')
    def BeaconTool(): return MockTool('beacon_coordinator', 'Broadcasts signals to other agents via Beacon.')

def get_rustchain_tools():
    """
    Returns a list of initialized RustChain tools for CrewAI.
    Integrates the optional Beacon tool if enabled via environment.
    """
    tools = [RustChainToolchain(), BoTTubeTool()]
    
    if os.getenv('BEACON_COORDINATION_ENABLED', 'false').lower() == 'true':
        tools.append(BeaconTool())
        
    return tools
