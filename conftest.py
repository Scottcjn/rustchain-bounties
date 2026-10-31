"""Pytest bootstrap for the repository root.

Several test modules import ``ai_agent``, which imports PyGithub at module
scope.  In minimal CI images PyGithub is frequently absent, so collection
blows up with ``ModuleNotFoundError: No module named 'github'`` before any
test body (or its ``unittest.mock.patch`` target) ever runs.

Fix: when the real package is missing, register a tiny stand-in module in
``sys.modules``.  The tests that care about behavior patch
``ai_agent.Github`` anyway, so they only need the import to succeed.  When
PyGithub is installed this file does nothing at all.
"""

import sys
import types

try:  # pragma: no cover - depends on the environment
    import github  # noqa: F401

except ImportError:  # pragma: no cover - exercised only without PyGithub
    _stub = types.ModuleType("github")

    class GithubException(Exception):
        """Minimal stand-in for ``github.GithubException``."""

        def __init__(self, status=None, data=None, headers=None):
            super().__init__(status, data)
            self.status = status
            self.data = data
            self.headers = headers

    class _Unavailable:
        """Placeholder for PyGithub objects used only at runtime."""

        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def __getattr__(self, name):
            if name.startswith("__"):
                raise AttributeError(name)
            return _Unavailable()

    class Github(_Unavailable):
        """Stand-in for ``github.Github``."""

        def get_repo(self, *args, **kwargs):
            raise GithubException(503, {"message": "PyGithub is not installed"})

        def get_user(self, *args, **kwargs):
            raise GithubException(503, {"message": "PyGithub is not installed"})

    class Auth(_Unavailable):
        """Stand-in for ``github.Auth``."""

        @classmethod
        def Token(cls, token):
            return cls(token)

    _stub.Github = Github
    _stub.Auth = Auth
    _stub.GithubException = GithubException
    _stub.GithubIntegration = _Unavailable
    _stub.Requester = _Unavailable
    _stub.Consts = _Unavailable
    _stub.__version__ = "0.0.0-stub"

    def _module_getattr(name):
        if name.startswith("__"):
            raise AttributeError(name)
        return type(name, (_Unavailable,), {})

    _stub.__getattr__ = _module_getattr
    sys.modules["github"] = _stub
