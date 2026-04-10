"""
RustChain Python SDK
===================
A full-featured Python SDK for the RustChain node API.

pip install rustchain-sdk

Usage:
    from rustchain import RustChain

    client = RustChain(node_url="https://50.28.86.131")
    print(client.health())
    print(client.get_balance("my-wallet"))
"""

__version__ = "0.1.0"
__author__ = "RustChain"

from rustchain.client import RustChain
from rustchain.exceptions import RustChainError, NodeOfflineError

__all__ = ["RustChain", "RustChainError", "NodeOfflineError", "__version__"]
