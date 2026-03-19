# Import only what's actually available to avoid import errors
try:
    from .client import RustChainClient as APIClient
except ImportError:
    APIClient = None

# Placeholder imports until modules are fully implemented
AgentEconomy = None
Agent = None
Task = None
Transaction = None
EconomyMetrics = None
RustChainSDKError = Exception
APIError = Exception
ValidationError = ValueError

__version__ = "0.1.0"
__all__ = [
    "AgentEconomy",
    "APIClient", 
    "Agent",
    "Task",
    "Transaction",
    "EconomyMetrics",
    "RustChainSDKError",
    "APIError",
    "ValidationError"
]