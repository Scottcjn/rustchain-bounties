# SPDX-License-Identifier: MIT
"""Static-analysis Judge — community gate for the open Judge interface.

Implements the open ``Judge`` interface:

    judge(request) -> (passed: bool, reasons: list[str])

This is an *alternative* gate to SophiaCore. It runs purely on the
Python source carried in ``request`` and produces a deterministic
verdict based on AST-level static analysis. No code is executed.

Each verdict is signed with the judge's own Ed25519 key so any SDK
that verifies signed envelopes can confirm authorship.

Bounty: Scottcjn/rustchain-bounties#14382 (75 RTC)
"""

from __future__ import annotations

import ast
import base64
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Mapping, Tuple

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.ed25519 import (
    Ed25519PrivateKey,
    Ed25519PublicKey,
)


# ─── Open Judge interface ───────────────────────────────────────────

class Judge:
    """Open Judge interface.

    Any concrete judge must implement :meth:`judge` with the signature
    ``judge(request) -> (passed, reasons)``. Implementations are free
    to add extra methods (e.g. signing) so long as this contract holds.
    """

    judge_id: str = "judge.base"

    def judge(self, request: Mapping[str, Any]) -> Tuple[bool, List[str]]:
        raise NotImplementedError


# ─── Static-analysis Judge ──────────────────────────────────────────

# Default rules — chosen to be cheap, deterministic, and stable across
# Python versions. They flag the cheap-and-obvious foot-guns we don't
# want code self-improvements to introduce.

DEFAULT_BANNED_CALLS = frozenset({"eval", "exec", "compile", "__import__"})
DEFAULT_BANNED_MODULES = frozenset({"os.system", "subprocess", "pickle", "marshal"})
DEFAULT_MAX_FUNCTION_LINES = 200
DEFAULT_MAX_FILE_LINES = 2000


@dataclass
class StaticAnalysisJudge(Judge):
    """A judge that runs AST-level static analysis on submitted code.

    The judge passes a request iff every source file:

    1. Parses as valid Python.
    2. Contains no calls to ``eval``/``exec``/``compile``/``__import__``.
    3. Imports no banned modules (e.g. ``subprocess``, ``pickle``).
    4. Stays under the configured per-function and per-file line caps.

    Configuration is intentionally limited — this is a *gate*, not a
    full linter. For richer policy, compose multiple judges.
    """

    judge_id: str = "judge.static-analysis.v1"
    banned_calls: frozenset = field(default_factory=lambda: DEFAULT_BANNED_CALLS)
    banned_modules: frozenset = field(default_factory=lambda: DEFAULT_BANNED_MODULES)
    max_function_lines: int = DEFAULT_MAX_FUNCTION_LINES
    max_file_lines: int = DEFAULT_MAX_FILE_LINES
    private_key: Ed25519PrivateKey = field(default=None, repr=False)

    def __post_init__(self) -> None:
        if self.private_key is None:
            self.private_key = Ed25519PrivateKey.generate()

    # ── Interface ──────────────────────────────────────────────────

    def judge(self, request: Mapping[str, Any]) -> Tuple[bool, List[str]]:
        """Run the gate on ``request``.

        ``request`` is expected to look like::

            {
                "files": {
                    "path/to/file.py": "<source>",
                    ...
                }
            }

        Returns ``(passed, reasons)``. ``reasons`` is non-empty on
        failure and may be empty on success.
        """
        files = self._extract_files(request)
        if not files:
            return False, ["no source files provided"]

        reasons: List[str] = []
        for path, source in files.items():
            reasons.extend(self._check_file(path, source))

        return (not reasons), reasons

    # ── Signing ────────────────────────────────────────────────────

    def public_key_bytes(self) -> bytes:
        """Return the raw 32-byte Ed25519 public key."""
        return self.private_key.public_key().public_bytes(
            encoding=serialization.Encoding.Raw,
            format=serialization.PublicFormat.Raw,
        )

    def sign_verdict(self, request: Mapping[str, Any]) -> Dict[str, Any]:
        """Return a signed verdict envelope.

        The envelope is JSON-serialisable and contains the public key,
        the verdict, and an Ed25519 signature over a canonical
        encoding of ``(judge_id, passed, reasons, ts)``.
        """
        passed, reasons = self.judge(request)
        verdict = {
            "judge_id": self.judge_id,
            "passed": passed,
            "reasons": reasons,
            "ts": int(time.time()),
        }
        message = _canonical(verdict)
        signature = self.private_key.sign(message)
        return {
            "verdict": verdict,
            "public_key": base64.b64encode(self.public_key_bytes()).decode("ascii"),
            "signature": base64.b64encode(signature).decode("ascii"),
        }

    @staticmethod
    def verify(envelope: Mapping[str, Any]) -> bool:
        """Verify a signed verdict envelope. Returns True iff valid."""
        try:
            verdict = envelope["verdict"]
            pk_bytes = base64.b64decode(envelope["public_key"])
            sig = base64.b64decode(envelope["signature"])
        except (KeyError, ValueError, TypeError):
            return False
        try:
            pk = Ed25519PublicKey.from_public_bytes(pk_bytes)
            pk.verify(sig, _canonical(verdict))
            return True
        except Exception:
            return False

    # ── Internals ──────────────────────────────────────────────────

    @staticmethod
    def _extract_files(request: Mapping[str, Any]) -> Dict[str, str]:
        files = request.get("files") if isinstance(request, Mapping) else None
        if not isinstance(files, Mapping):
            return {}
        return {str(k): str(v) for k, v in files.items() if v is not None}

    def _check_file(self, path: str, source: str) -> List[str]:
        reasons: List[str] = []
        lines = source.count("\n") + 1
        if lines > self.max_file_lines:
            reasons.append(
                f"{path}: file too large ({lines} > {self.max_file_lines} lines)"
            )

        try:
            tree = ast.parse(source, filename=path)
        except SyntaxError as exc:
            reasons.append(f"{path}: syntax error at line {exc.lineno}: {exc.msg}")
            return reasons

        for node in ast.walk(tree):
            reasons.extend(self._check_node(path, node))
        return reasons

    def _check_node(self, path: str, node: ast.AST) -> Iterable[str]:
        # Banned bare calls: eval(...), exec(...), etc.
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in self.banned_calls:
                yield f"{path}:{node.lineno}: banned call to {node.func.id}()"

        # Banned imports.
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name in self.banned_modules:
                    yield f"{path}:{node.lineno}: banned import '{alias.name}'"
        if isinstance(node, ast.ImportFrom):
            mod = node.module or ""
            if mod in self.banned_modules:
                yield f"{path}:{node.lineno}: banned import-from '{mod}'"

        # Oversized functions.
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            end = getattr(node, "end_lineno", node.lineno)
            span = (end or node.lineno) - node.lineno + 1
            if span > self.max_function_lines:
                yield (
                    f"{path}:{node.lineno}: function '{node.name}' too long "
                    f"({span} > {self.max_function_lines} lines)"
                )


def _canonical(verdict: Mapping[str, Any]) -> bytes:
    """Deterministic JSON encoding used for signing/verification."""
    return json.dumps(verdict, sort_keys=True, separators=(",", ":")).encode("utf-8")


__all__ = ["Judge", "StaticAnalysisJudge"]
