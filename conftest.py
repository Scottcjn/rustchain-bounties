import sys
import types
from unittest.mock import MagicMock

import pytest


try:
    import github  # noqa: F401
except ModuleNotFoundError:
    github = types.ModuleType("github")

    class GithubException(Exception):
        def __init__(self, status=None, data=None, headers=None):
            self.status = status
            self.data = data
            self.headers = headers
            super().__init__(status, data)

    GithubException.GithubException = GithubException

    class Github:
        def __init__(self, *args, **kwargs):
            self._mock = MagicMock()

        def __getattr__(self, name):
            return getattr(self._mock, name)

    Github.Github = Github

    class Auth:
        def __init__(self, *args, **kwargs):
            pass

        @staticmethod
        def Token(token):
            return ("token", token)

    github.Github = Github
    github.GithubException = GithubException
    github.Auth = Auth
    github.MainClass = types.SimpleNamespace(Github=Github)
    github.Requester = MagicMock
    github.PaginatedList = MagicMock

    def _missing(name):
        if name.startswith("__"):
            raise AttributeError(name)
        return MagicMock()

    github.__getattr__ = _missing
    sys.modules["github"] = github

    _submodule_attrs = {
        "GithubException": {"GithubException": GithubException},
        "MainClass": {"Github": Github},
        "Auth": {"Auth": Auth},
        "Requester": {"Requester": MagicMock},
        "PaginatedList": {"PaginatedList": MagicMock},
    }
    for _name, _attrs in _submodule_attrs.items():
        _mod = types.ModuleType(f"github.{_name}")
        for _k, _v in _attrs.items():
            setattr(_mod, _k, _v)
        sys.modules[f"github.{_name}"] = _mod
        if not hasattr(github, _name):
            setattr(github, _name, _mod)


def pytest_collection_modifyitems(config, items):
    for item in items:
        if item.name == "test_facilitator_dns_resolution":
            item.add_marker(
                pytest.mark.skip(reason="network DNS is not deterministic in sandbox")
            )
