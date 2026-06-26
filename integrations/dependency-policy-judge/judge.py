# SPDX-License-Identifier: MIT
"""Dependency Policy Judge for the open Judge interface.

Implements:

    judge(request) -> (passed: bool, reasons: list[str])

This gate inspects dependency manifests without installing or executing
submitted code. It is intended for self-improvement flows where dependency
changes should be pinned and should avoid install-time execution, URL/VCS
dependencies, or alternate package indexes unless another gate explicitly
allows them.
"""

from __future__ import annotations

import base64
import hashlib
import json
import re
import time
from dataclasses import dataclass, field
from pathlib import PurePosixPath
from typing import Any, Iterable, Mapping

try:
    import tomllib
except ModuleNotFoundError:  # pragma: no cover - Python < 3.11 fallback
    tomllib = None

from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)
from cryptography.hazmat.primitives.serialization import (
    Encoding,
    PublicFormat,
)


INSTALL_SCRIPT_NAMES = frozenset({"preinstall", "install", "postinstall", "prepare"})
NPM_DEPENDENCY_SECTIONS = (
    "dependencies",
    "devDependencies",
    "optionalDependencies",
    "peerDependencies",
)
PYPROJECT_TOOL_DEPENDENCY_PATHS = (
    ("tool", "poetry", "dependencies"),
    ("tool", "poetry", "dev-dependencies"),
    ("tool", "pdm", "dev-dependencies"),
    ("tool", "pdm", "dependencies"),
    ("tool", "uv", "dev-dependencies"),
    ("tool", "uv", "override-dependencies"),
    ("tool", "uv", "constraint-dependencies"),
)
PYPROJECT_DIRECT_REF_KEYS = frozenset({"path", "url", "git"})


def _canonical_json(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode()


def _b64(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64decode(data: str) -> bytes:
    padding = "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode((data + padding).encode("ascii"))


def _request_digest(request: Mapping[str, Any]) -> str:
    return hashlib.sha256(_canonical_json(request)).hexdigest()


def _basename(path: str) -> str:
    return PurePosixPath(path.replace("\\", "/")).name


def _is_manifest(path: str) -> bool:
    name = _basename(path)
    return (
        name == "package.json"
        or name == "pyproject.toml"
        or (name.startswith("requirements") and name.endswith(".txt"))
    )


def _iter_pyproject_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, list):
        for item in value:
            yield from _iter_pyproject_strings(item)
    elif isinstance(value, dict):
        for item in value.values():
            yield from _iter_pyproject_strings(item)


def _nested_get(value: Mapping[str, Any], path: tuple[str, ...]) -> Any:
    current: Any = value
    for key in path:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


@dataclass
class DependencyPolicyJudge:
    """Dependency manifest judge with Ed25519 signed verdicts."""

    judge_id: str = "judge.dependency-policy.v1"
    private_key: Ed25519PrivateKey | None = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self.private_key is None:
            self.private_key = Ed25519PrivateKey.generate()

    def judge(self, request: Mapping[str, Any]) -> tuple[bool, list[str]]:
        manifests = self._extract_manifests(request)
        if not manifests:
            return False, ["no supported dependency manifests provided"]

        reasons: list[str] = []
        for path, content in manifests.items():
            if _basename(path) == "package.json":
                reasons.extend(self._check_package_json(path, content))
            elif _basename(path).startswith("requirements"):
                reasons.extend(self._check_requirements(path, content))
            elif _basename(path) == "pyproject.toml":
                reasons.extend(self._check_pyproject(path, content))

        return not reasons, reasons

    def public_key_b64(self) -> str:
        assert self.private_key is not None
        public_key = self.private_key.public_key().public_bytes(
            encoding=Encoding.Raw,
            format=PublicFormat.Raw,
        )
        return _b64(public_key)

    def sign_verdict(
        self,
        request: Mapping[str, Any],
        *,
        issued_at: int | None = None,
    ) -> dict[str, Any]:
        passed, reasons = self.judge(request)
        payload = {
            "judge_id": self.judge_id,
            "passed": passed,
            "reasons": reasons,
            "request_sha256": _request_digest(request),
            "issued_at": int(time.time()) if issued_at is None else issued_at,
        }
        assert self.private_key is not None
        signature = self.private_key.sign(_canonical_json(payload))
        return {
            "payload": payload,
            "signature": _b64(signature),
            "public_key": self.public_key_b64(),
            "signature_algorithm": "Ed25519",
        }

    @staticmethod
    def verify(envelope: Mapping[str, Any]) -> bool:
        try:
            if envelope.get("signature_algorithm") != "Ed25519":
                return False
            payload = envelope["payload"]
            public_key = Ed25519PublicKey.from_public_bytes(_b64decode(envelope["public_key"]))
            public_key.verify(_b64decode(envelope["signature"]), _canonical_json(payload))
            return True
        except (KeyError, TypeError, ValueError, InvalidSignature):
            return False

    def _extract_manifests(self, request: Mapping[str, Any]) -> dict[str, str]:
        raw: dict[str, Any] = {}
        for key in ("manifests", "files"):
            value = request.get(key)
            if isinstance(value, Mapping):
                raw.update(value)

        manifests: dict[str, str] = {}
        for path, content in raw.items():
            if isinstance(path, str) and isinstance(content, str) and _is_manifest(path):
                manifests[path] = content
        return manifests

    def _check_package_json(self, path: str, content: str) -> list[str]:
        try:
            doc = json.loads(content)
        except json.JSONDecodeError as exc:
            return [f"{path}: invalid JSON: {exc.msg}"]

        if not isinstance(doc, dict):
            return [f"{path}: package.json must be an object"]

        reasons: list[str] = []
        scripts = doc.get("scripts")
        if isinstance(scripts, dict):
            for name in sorted(INSTALL_SCRIPT_NAMES & set(scripts)):
                reasons.append(f"{path}: install lifecycle script '{name}' is not allowed")

        for section in NPM_DEPENDENCY_SECTIONS:
            dependencies = doc.get(section)
            if not isinstance(dependencies, dict):
                continue
            for name, spec in sorted(dependencies.items()):
                if not isinstance(spec, str):
                    reasons.append(f"{path}: {section}.{name} version spec must be a string")
                    continue
                reason = self._npm_spec_reason(spec)
                if reason:
                    reasons.append(f"{path}: {section}.{name} uses {reason}: {spec!r}")

        return reasons

    def _check_requirements(self, path: str, content: str) -> list[str]:
        reasons: list[str] = []
        for line_no, raw_line in enumerate(content.splitlines(), start=1):
            line = raw_line.strip()
            if not line or line.startswith("#"):
                continue
            base = line.split("#", 1)[0].strip()
            lower = base.lower()
            if lower.startswith(("-e ", "--editable ")):
                reasons.append(f"{path}:{line_no}: editable installs are not allowed")
            elif lower.startswith(("--extra-index-url", "--index-url", "--find-links")):
                reasons.append(f"{path}:{line_no}: alternate package sources are not allowed")
            elif "://" in lower or lower.startswith("git+"):
                reasons.append(f"{path}:{line_no}: URL or VCS requirements are not allowed")
            elif "==" not in base:
                reasons.append(f"{path}:{line_no}: requirement must be pinned with ==")
        return reasons

    def _check_pyproject(self, path: str, content: str) -> list[str]:
        if tomllib is None:
            return [f"{path}: pyproject.toml requires Python 3.11+ tomllib"]
        try:
            doc = tomllib.loads(content)
        except Exception as exc:
            return [f"{path}: invalid TOML: {exc}"]

        reasons: list[str] = []
        project = doc.get("project")
        if isinstance(project, dict):
            for dep in _iter_pyproject_strings(project.get("dependencies", [])):
                reason = self._python_spec_reason(dep)
                if reason:
                    reasons.append(f"{path}: project dependency uses {reason}: {dep!r}")
            optional = project.get("optional-dependencies")
            if isinstance(optional, dict):
                for group, deps in sorted(optional.items()):
                    for dep in _iter_pyproject_strings(deps):
                        reason = self._python_spec_reason(dep)
                        if reason:
                            reasons.append(
                                f"{path}: optional dependency group {group!r} uses {reason}: {dep!r}"
                            )
        for tool_path in PYPROJECT_TOOL_DEPENDENCY_PATHS:
            section = _nested_get(doc, tool_path)
            if not isinstance(section, (dict, list)):
                continue
            for dep in self._iter_tool_dependency_specs(section):
                reason = self._python_spec_reason(dep)
                if reason:
                    location = ".".join(tool_path)
                    reasons.append(f"{path}: {location} dependency uses {reason}: {dep!r}")
        return reasons

    def _iter_tool_dependency_specs(self, value: Any) -> Iterable[str]:
        if isinstance(value, str):
            yield value
        elif isinstance(value, list):
            for item in value:
                yield from self._iter_tool_dependency_specs(item)
        elif isinstance(value, dict):
            if PYPROJECT_DIRECT_REF_KEYS & set(value):
                yield json.dumps(value, sort_keys=True)
                return
            for name, spec in sorted(value.items()):
                if isinstance(spec, str):
                    yield f"{name}{spec}"
                elif isinstance(spec, dict):
                    if PYPROJECT_DIRECT_REF_KEYS & set(spec):
                        yield f"{name} {json.dumps(spec, sort_keys=True)}"
                    elif "version" in spec:
                        yield f"{name}{spec['version']}"
                    else:
                        yield from self._iter_tool_dependency_specs(spec)
                else:
                    yield from self._iter_tool_dependency_specs(spec)

    @staticmethod
    def _npm_spec_reason(spec: str) -> str | None:
        stripped = spec.strip()
        lower = stripped.lower()
        if lower in {"", "*", "latest"}:
            return "floating dependency"
        if "://" in lower or lower.startswith(("git+", "github:", "gitlab:", "bitbucket:", "file:")):
            return "URL/VCS/local dependency"
        if lower.startswith(("^", "~", ">", "<", ">=", "<=")) or "||" in lower:
            return "range dependency"
        if re.search(r"(^|[.\-])x($|[.\-])", lower):
            return "wildcard dependency"
        return None

    @staticmethod
    def _python_spec_reason(spec: str) -> str | None:
        stripped = spec.strip()
        lower = stripped.lower()
        direct_reference_markers = (
            " @ ",
            "://",
            "git+",
            "file:",
            "path =",
            '"path"',
            "'path'",
            '"url"',
            "'url'",
            '"git"',
            "'git'",
        )
        if any(marker in lower for marker in direct_reference_markers) or lower.startswith(
            ("./", "../", "/", "git+")
        ):
            return "URL/VCS dependency"
        if "==" not in stripped:
            return "unpinned dependency"
        return None
