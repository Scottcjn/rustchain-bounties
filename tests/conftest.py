"""Test bootstrap helpers.

``ai_agent`` imports PyGithub at module import time.  PyGithub is a heavy
optional dependency and is not always installed in the lightweight test
environment, which makes every ``tests/test_ai_agent.py`` test fail with
``ModuleNotFoundError: No module named 'github'`` before any test body runs.

This conftest keeps the real package untouched when it is available, and only
falls back to a tiny attribute-on-demand stand-in module otherwise.  The
stand-in classes are plain placeholders intended for ``unittest.mock.patch``
targets, which is exactly how the tests exercise the GitHub client.
"""

import sys
import types

try:  # pragma: no cover - depends on the environment
    import github  # noqa: F401
    _HAS_GITHUB = True
except ModuleNotFoundError:  # pragma: no cover - depends on the environment
    _HAS_GITHUB = False


if not _HAS_GITHUB:  # pragma: no cover - depends on the environment
    _stub = types.ModuleType("github")
    _stub.__doc__ = "Minimal stand-in for PyGithub used when it is not installed."

    def _make_attr(name):
        """Create (and cache) a placeholder attribute for the stub module."""
        base = Exception if name.endswith(("Exception", "Error")) else object
        value = type(name, (base,), {})
        setattr(_stub, name, value)
        return value

    # PEP 562 module-level __getattr__ keeps the stub permissive for every
    # symbol (``Github``, ``Auth``, ``GithubException``, ``RateLimitExceeded...``)
    # without enumerating them up front.
    _stub.__getattr__ = _make_attr

    sys.modules["github"] = _stub
