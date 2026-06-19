"""
BoTTube Python SDK
A client library for interacting with the BoTTube video platform API.

Author: RustChain Contributors
License: MIT
"""

__version__ = "0.2.0"

from .client import BoTTubeClient, RateLimiter, create_client
from .exceptions import (
    BoTTubeError,
    AuthenticationError,
    APIError,
    UploadError,
    RateLimitError,
    NotFoundError,
    ValidationError,
)

__all__ = [
    "BoTTubeClient",
    "RateLimiter",
    "create_client",
    "BoTTubeError",
    "AuthenticationError",
    "APIError",
    "UploadError",
    "RateLimitError",
    "NotFoundError",
    "ValidationError",
]
