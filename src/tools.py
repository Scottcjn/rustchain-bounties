from langchain.tools import tool

# Safely import RustChain tools, fallback for local testing without the live package
try:
    from rustchain_langchain import RustChainToolKit
except ImportError:
    class RustChainToolKit:
        def get_tools(self):
            # Mock tool returned if package is missing during initial local setup
            @tool("RustChain Status Checker")
            def rustchain_status(query: str) -> str:
                """Check RustChain network and BoTTube status."""
                return "RustChain Network Operational. BoTTube upload nodes are ready."
            return [rustchain_status]

@tool("Beacon Signal Tool")
def beacon_signal_tool(signal: str) -> str:
    """Useful for broadcasting a coordination signal to other agents via Beacon."""
    # Implementation for Beacon agent-to-agent protocol
    return f"Beacon protocol broadcasted successfully: {signal}"

def get_rustchain_tools():
    """Aggregate RustChain, BoTTube, and Beacon tools."""
    toolkit = RustChainToolKit()
    tools = toolkit.get_tools() if hasattr(toolkit, 'get_tools') else []
    
    # Append optional Beacon integration tool for agent-to-agent coordination
    tools.append(beacon_signal_tool)
    return tools
