"""Fallback ``prometheus_client.core`` metric families.

Mirrors the subset of the real API used by ``scripts/prometheus_exporter.py``:
``GaugeMetricFamily``, ``CounterMetricFamily`` and ``HistogramMetricFamily``.
"""

from __future__ import annotations

from typing import List

from . import _escape_label_value, _format_value, _MetricFamily


class GaugeMetricFamily(_MetricFamily):
    _type = "gauge"


class CounterMetricFamily(_MetricFamily):
    _type = "counter"


class HistogramMetricFamily(_MetricFamily):
    _type = "histogram"

    def __init__(self, name, documentation, value=None, labels=None):
        super().__init__(name, documentation, value=value, labels=labels)
        self.samples = []
        self._histograms: List[tuple] = []

    def add_metric(self, labels, buckets, sum_value=None):
        labeldict = dict(zip(self.labelnames, list(labels or [])))
        self._histograms.append((labeldict, list(buckets or []), sum_value))

    def render(self) -> List[str]:
        lines = [
            f"# HELP {self.name} {self.documentation}",
            f"# TYPE {self.name} {self._type}",
        ]
        for labeldict, buckets, sum_value in self._histograms:
            total_count = 0
            for bound, count in buckets:
                try:
                    total_count = int(count)
                except (TypeError, ValueError):
                    total_count = 0
                if labeldict:
                    labels = ",".join(
                        [f'{k}="{_escape_label_value(v)}"'
                         for k, v in labeldict.items()]
                        + [f'le="{_escape_label_value(bound)}"']
                    )
                    lines.append(
                        f"{self.name}_bucket{{{labels}}} "
                        f"{_format_value(count)}"
                    )
                else:
                    lines.append(
                        f'{self.name}_bucket{{le="{_escape_label_value(bound)}"}} '
                        f"{_format_value(count)}"
                    )
            if labeldict:
                labels = ",".join(
                    f'{k}="{_escape_label_value(v)}"'
                    for k, v in labeldict.items()
                )
                lines.append(
                    f"{self.name}_count{{{labels}}} "
                    f"{_format_value(total_count)}"
                )
                if sum_value is not None:
                    lines.append(
                        f"{self.name}_sum{{{labels}}} "
                        f"{_format_value(sum_value)}"
                    )
            else:
                lines.append(
                    f"{self.name}_count {_format_value(total_count)}"
                )
                if sum_value is not None:
                    lines.append(
                        f"{self.name}_sum {_format_value(sum_value)}"
                    )
        return lines


__all__ = [
    "GaugeMetricFamily",
    "CounterMetricFamily",
    "HistogramMetricFamily",
]
