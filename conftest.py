"""Root pytest configuration for the rustchain-bounties test suite.

``ai_agent.py`` imports the optional third-party ``PyGithub`` package at
module scope.  When that package is absent from the test environment the
whole module fails to import, which takes down every test in
``tests/test_ai_agent.py`` with ``ModuleNotFoundError: No module named
'github'``.

Instead of making ``PyGithub`` a hard requirement, install a tiny stand-in
module into ``sys.modules`` only when the real package cannot be imported.
The stub exposes just enough surface (``Github``, ``Auth``,
``GithubException``) for imports to succeed; tests that need real behaviour
patch these attributes explicitly.
"""

import sys
import types


def _real_github_available():
    try:
        import github  # noqa: F401
    except Exception:
        return False
    return True


def _install_github_stub():
    class GithubException(Exception):
        def __init__(self, status=None, data=None, headers=None):
            self.status = status
            self.data = data
            self.headers = headers
            super().__init__("status={0} data={1!r}".format(status, data))

    class BadCredentialsException(GithubException):
        pass

    class UnknownObjectException(GithubException):
        pass

    class Github:
        def __init__(self, *args, **kwargs):
            self._args = args
            self._kwargs = kwargs

        def get_user(self, *args, **kwargs):
            raise GithubException(501, "PyGithub stub: get_user is unavailable")

        def get_repo(self, *args, **kwargs):
            raise GithubException(501, "PyGithub stub: get_repo is unavailable")

        def get_rate_limit(self, *args, **kwargs):
            raise GithubException(501, "PyGithub stub: rate limit unavailable")

    class Auth:
        def __init__(self, token=None):
            self.token = token

        @classmethod
        def Token(cls, token):
            return cls(token)

    github_mod = types.ModuleType("github")
    github_mod.__version__ = "0.0.0-pygithub-stub"
    github_mod.Github = Github
    github_mod.Auth = Auth
    github_mod.GithubException = GithubException

    exceptions_mod = types.ModuleType("github.GithubException")
    exceptions_mod.GithubException = GithubException
    exceptions_mod.BadCredentialsException = BadCredentialsException
    exceptions_mod.UnknownObjectException = UnknownObjectException
    exceptions_mod.GithubException = GithubException

    sys.modules.setdefault("github", github_mod)
    sys.modules.setdefault("github.GithubException", exceptions_mod)


if not _real_github_available():
    _install_github_stub()
