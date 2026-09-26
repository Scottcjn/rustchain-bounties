"""Minimal local fallback for the ``prometheus_client`` package.

Used when the real ``prometheus_client`` distribution is unavailable.
Implements just enough of the API for ``scripts/prometheus_exporter.py``
and its unit tests: ``CollectorRegistry``, ``REGISTRY``,
``generate_latest``, ``start_http_server`` and the ``core`` metric
families.  When the real package is installed it takes precedence
(the real distribution shadows this fallback if it is importable
earlier on ``sys.path``).
"""

from __future__ import annotations

from typing import Dict, Iterable, List, Sequence


def _format_value(value) -> str:
    return repr(float(value))


def _escape_label_value(value: str) -> str:
    return (
        str(value)
        .replace("\\", "\\\\")
        .replace("\n", "\\n")
        .replace('"', '\\"')
    )


class _MetricFamily:
    _type = "gauge"

    def __init__(self, name, documentation, value=None, labels=None):
        self.name = name
        self.documentation = documentation or ""
        self.labelnames = list(labels or [])
        self.samples: List[tuple] = []
        if value is not None:
            self.samples.append((name, {}, value))

    def add_metric(self, labels, value, *args, **kwargs):
        labeldict = dict(zip(self.labelnames, list(labels or [])))
        extra = getattr(self, "_extra_samples", None)
        if extra is not None:
            # Histogram-style: subclasses override add_metric.
            raise NotImplementedError
        self.samples.append((self.name, labeldict, value))

    def _render_samples(self) -> List[str]:
        lines = []
        for sample_name, labeldict, value in self.samples:
            if labeldict:
                labels = ",".join(
                    f'{k}="{_escape_label_value(v)}"'
                    for k, v in labeldict.items()
                )
                lines.append(
                    f"{sample_name}{{{labels}}} {_format_value(value)}"
                )
            else:
                lines.append(f"{sample_name} {_format_value(value)}")
        return lines

    def render(self) -> List[str]:
        lines = [
            f"# HELP {self.name} {self.documentation}",
            f"# TYPE {self.name} {self._type}",
        ]
        lines.extend(self._render_samples())
        return lines


class CollectorRegistry:
    """Registry holding collectors exposing a ``collect()`` method."""

    def __init__(self):
        self._collectors: List = []

    def register(self, collector) -> None:
        if collector not in self._collectors:
            self._collectors.append(collector)

    def unregister(self, collector) -> None:
        self._collectors = [c for c in self._collectors if c is not collector]


REGISTRY = CollectorRegistry()


def generate_latest(registry: CollectorRegistry = REGISTRY) -> bytes:
    lines: List[str] = []
    for collector in list(registry._collectors):
        try:
            families = collector.collect()
        except Exception:
            continue
        for family in families or ():
            try:
                lines.extend(family.render())
            except Exception:
                continue
    text = "\n".join(lines)
    if text:
        text += "\n"
    return text.encode("utf-8")


def start_http_server(port: int, addr: str = "0.0.0.0") -> None:  # pragma: no cover
    """Fallback no-op stand-in for the real HTTP server."""
    raise RuntimeError(
        "prometheus_client fallback cannot serve metrics "
        "(real prometheus_client is not installed)"
    )


__all__ = [
    "CollectorRegistry",
    "REGISTRY",
    "generate_latest",
    "start_http_server",
]
