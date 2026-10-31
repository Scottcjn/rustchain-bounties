"""Pytest bootstrap for the repository root.

Some test modules (e.g. ``tests/test_ai_agent.py``) import ``github``
(PyGithub) at import time.  PyGithub is an optional runtime dependency and
is not always installed in CI or in a bare checkout, which makes the whole
suite fail with ``ModuleNotFoundError: No module named 'github'`` before a
single test can run.

This conftest installs a tiny, side-effect-free placeholder module *only*
when the real PyGithub is genuinely missing.  When PyGithub is installed the
stub is never created, so real behaviour is untouched.  Tests that mock the
GitHub client keep working: they patch attributes on the imported module,
which the stub supports in exactly the same way a real module would.
"""

import sys
import types


def _install_github_stub() -> None:
    """Register a minimal ``github`` module if PyGithub is unavailable."""
    stub = types.ModuleType("github")
    stub.__doc__ = "Minimal in-process stand-in for PyGithub (test bootstrap)."

    class GithubException(Exception):
        """Placeholder mirroring ``github.GithubException``."""

        def __init__(self, status=None, data=None, headers=None):
            self.status = status
            self.data = data
            self.headers = headers
            super().__init__(status, data)

    class Github:
        """Placeholder mirroring ``github.Github``.

        Instances are inert.  Tests are expected to mock this class; any
        unmocked call raises so that accidental network use is obvious
        instead of silently succeeding.
        """

        def __init__(self, *args, **kwargs):
            self.args = args
            self.kwargs = kwargs

        def get_repo(self, *args, **kwargs):
            raise RuntimeError(
                "PyGithub is not installed; 'github.Github.get_repo' is a stub."
            )

        def get_user(self, *args, **kwargs):
            raise RuntimeError(
                "PyGithub is not installed; 'github.Github.get_user' is a stub."
            )

    class _TokenAuth:
        def __init__(self, token=None, *args, **kwargs):
            self.token = token

    stub.Github = Github
    stub.GithubException = GithubException
    stub.Auth = types.SimpleNamespace(Token=_TokenAuth)
    stub.MainClass = Github
    sys.modules["github"] = stub


try:  # pragma: no cover - trivial import guard
    import github  # noqa: F401
    import github.GithubException  # noqa: F401
    import github.Auth  # noqa: F401
    import github.MainClass  # noqa: F401
    import github.Github  # noqa: F401
    import github.GithubIntegration  # noqa: F401
    import github.GithubRetry  # noqa: F401
    import github.Auth  # noqa: F401
    import github.PaginatedList  # noqa: F401
    import github.Repository  # noqa: F401
    import github.Issue  # noqa: F401
    import github.PullRequest  # noqa: F401
    import github.AuthenticatedUser  # noqa: F401
except ImportError:  # pragma: no cover - depends on the environment
    _install_github_stub()
