#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
RustChain load-test graph reporter.

Reads Locust CSV stats, k6 JSON summary, or Artillery JSON report and
produces a single self-contained HTML file with interactive charts
(no external CDN — the page uses inline SVG rendering).

Usage:
    # From Locust CSV prefix:
    python load_tests/graph_reporter.py load_tests/results/locust_report

    # From k6 summary JSON:
    python load_tests/graph_reporter.py --format k6 \
        load_tests/results/k6_summary.json

    # From Artillery JSON:
    python load_tests/graph_reporter.py --format artillery \
        load_tests/results/artillery_report.json

    # Custom output path:
    python load_tests/graph_reporter.py --output my_report.html \
        load_tests/results/locust_report
"""

import argparse
import csv
import html
import json
import math
import os
import sys
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple


# ---------------------------------------------------------------------------
# Data ingestion helpers
# ---------------------------------------------------------------------------

def load_locust_stats(prefix: str) -> Dict[str, Any]:
    """Parse Locust *_stats.csv and *_stats_history.csv into a dict."""
    stats_file = f"{prefix}_stats.csv"
    history_file = f"{prefix}_stats_history.csv"

    if not os.path.isfile(stats_file):
        raise FileNotFoundError(f"Locust stats file not found: {stats_file}")

    endpoints: List[Dict[str, Any]] = []
    with open(stats_file, newline="") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            # skip the "Aggregated" summary row
            if row.get("Name", "").strip().lower() == "aggregated":
                continue
            endpoints.append({
                "name": row.get("Name", ""),
                "method": row.get("Type", ""),
                "requests": int(row.get("Request Count", 0) or 0),
                "failures": int(row.get("Failure Count", 0) or 0),
                "median": float(row.get("Median Response Time", 0) or 0),
                "p95": float(row.get("95%", 0) or 0),
                "p99": float(row.get("99%", 0) or 0),
                "avg": float(row.get("Average Response Time", 0) or 0),
                "min": float(row.get("Min Response Time", 0) or 0),
                "max": float(row.get("Max Response Time", 0) or 0),
                "rps": float(row.get("Requests/s", 0) or 0),
            })

    # Optional time-series from history file
    timeseries: List[Dict[str, Any]] = []
    if os.path.isfile(history_file):
        with open(history_file, newline="") as fh:
            reader = csv.DictReader(fh)
            for row in reader:
                if row.get("Name", "").strip().lower() == "aggregated":
                    continue
                timeseries.append({
                    "timestamp": row.get("Timestamp", ""),
                    "name": row.get("Name", ""),
                    "users": int(row.get("User Count", 0) or 0),
                    "rps": float(row.get("Requests/s", 0) or 0),
                    "failures_per_s": float(row.get("Failures/s", 0) or 0),
                    "p50": float(row.get("50%", 0) or 0),
                    "p95": float(row.get("95%", 0) or 0),
                })

    return {"source": "locust", "endpoints": endpoints, "timeseries": timeseries}


def load_k6_summary(path: str) -> Dict[str, Any]:
    """Parse k6 --out json summary."""
    with open(path) as fh:
        data = json.load(fh)

    metrics = data.get("metrics", {})
    endpoints: List[Dict[str, Any]] = []

    # k6 metrics are flat; extract per-tag-group info if present
    for name, vals in metrics.items():
        if not isinstance(vals, dict) or "values" not in vals:
            continue
        v = vals["values"]
        if "avg" in v:
            endpoints.append({
                "name": name,
                "avg": v.get("avg", 0),
                "min": v.get("min", 0),
                "max": v.get("max", 0),
                "p90": v.get("p(90)", 0),
                "p95": v.get("p(95)", 0),
                "p99": v.get("p(99)", 0),
                "count": v.get("count", 0),
                "rate": v.get("rate", 0),
            })

    return {"source": "k6", "endpoints": endpoints, "timeseries": []}


def load_artillery_report(path: str) -> Dict[str, Any]:
    """Parse Artillery JSON report."""
    with open(path) as fh:
        data = json.load(fh)

    aggregate = data.get("aggregate", {})
    latency = aggregate.get("latency", {})
    codes = aggregate.get("codes", {})
    counters = aggregate.get("counters", {})

    endpoints = [{
        "name": "aggregate",
        "requests": counters.get("http.requests", 0),
        "responses": counters.get("http.responses", 0),
        "min": latency.get("min", 0),
        "max": latency.get("max", 0),
        "median": latency.get("median", 0),
        "p95": latency.get("p95", 0),
        "p99": latency.get("p99", 0),
        "codes": codes,
    }]

    timeseries: List[Dict[str, Any]] = []
    for interval in data.get("intermediate", []):
        ts = interval.get("timestamp", "")
        il = interval.get("latency", {})
        timeseries.append({
            "timestamp": ts,
            "p50": il.get("median", 0),
            "p95": il.get("p95", 0),
            "rps": interval.get("rps", {}).get("mean", 0),
        })

    return {"source": "artillery", "endpoints": endpoints, "timeseries": timeseries}


# ---------------------------------------------------------------------------
# SVG chart builder (zero dependencies)
# ---------------------------------------------------------------------------

def _svg_bar_chart(
    title: str,
    labels: List[str],
    values: List[float],
    color: str = "#4a90d9",
    width: int = 600,
    bar_height: int = 28,
) -> str:
    """Produce an inline SVG horizontal bar chart."""
    margin_left = 180
    margin_top = 40
    margin_right = 80
    chart_width = width - margin_left - margin_right
    height = margin_top + len(labels) * (bar_height + 6) + 20

    max_val = max(values) if values else 1
    if max_val == 0:
        max_val = 1

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'style="font-family:monospace;font-size:13px;background:#fafafa;border:1px solid #ddd;border-radius:6px;">',
        f'<text x="{width // 2}" y="24" text-anchor="middle" font-size="15" '
        f'font-weight="bold" fill="#333">{html.escape(title)}</text>',
    ]

    for i, (label, val) in enumerate(zip(labels, values)):
        y = margin_top + i * (bar_height + 6)
        bw = max(1, int((val / max_val) * chart_width))
        lines.append(
            f'<text x="{margin_left - 8}" y="{y + bar_height // 2 + 4}" '
            f'text-anchor="end" fill="#555">{html.escape(label[:22])}</text>'
        )
        lines.append(
            f'<rect x="{margin_left}" y="{y}" width="{bw}" height="{bar_height}" '
            f'rx="3" fill="{color}" opacity="0.85"/>'
        )
        lines.append(
            f'<text x="{margin_left + bw + 6}" y="{y + bar_height // 2 + 4}" '
            f'fill="#333">{val:.1f}</text>'
        )

    lines.append("</svg>")
    return "\n".join(lines)


def _svg_line_chart(
    title: str,
    x_labels: List[str],
    series: Dict[str, List[float]],
    width: int = 700,
    height: int = 300,
) -> str:
    """Produce an inline SVG line chart with multiple series."""
    margin = {"top": 50, "right": 120, "bottom": 40, "left": 60}
    cw = width - margin["left"] - margin["right"]
    ch = height - margin["top"] - margin["bottom"]

    if not x_labels or not series:
        return f"<p><em>No time-series data for {html.escape(title)}</em></p>"

    all_vals = [v for vs in series.values() for v in vs]
    y_min = 0
    y_max = max(all_vals) if all_vals else 1
    if y_max == 0:
        y_max = 1

    colors = ["#4a90d9", "#e74c3c", "#2ecc71", "#f39c12", "#9b59b6"]

    lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" '
        f'style="font-family:monospace;font-size:12px;background:#fafafa;border:1px solid #ddd;border-radius:6px;">',
        f'<text x="{width // 2}" y="28" text-anchor="middle" font-size="14" '
        f'font-weight="bold" fill="#333">{html.escape(title)}</text>',
    ]

    # axes
    ox, oy = margin["left"], margin["top"]
    lines.append(
        f'<line x1="{ox}" y1="{oy}" x2="{ox}" y2="{oy + ch}" stroke="#aaa"/>'
    )
    lines.append(
        f'<line x1="{ox}" y1="{oy + ch}" x2="{ox + cw}" y2="{oy + ch}" stroke="#aaa"/>'
    )

    n = len(x_labels)
    # x tick labels (show at most 8)
    step = max(1, n // 8)
    for i in range(0, n, step):
        x = ox + int(i / max(1, n - 1) * cw) if n > 1 else ox
        label = x_labels[i][-8:]  # last 8 chars (time portion)
        lines.append(
            f'<text x="{x}" y="{oy + ch + 16}" text-anchor="middle" fill="#777" '
            f'font-size="10">{html.escape(label)}</text>'
        )

    for si, (sname, svals) in enumerate(series.items()):
        col = colors[si % len(colors)]
        points = []
        for i, v in enumerate(svals):
            x = ox + int(i / max(1, n - 1) * cw) if n > 1 else ox
            y = oy + ch - int((v - y_min) / (y_max - y_min) * ch)
            points.append(f"{x},{y}")
        if points:
            lines.append(
                f'<polyline points="{" ".join(points)}" fill="none" '
                f'stroke="{col}" stroke-width="2"/>'
            )
        # legend
        ly = margin["top"] + si * 18
        lx = ox + cw + 12
        lines.append(f'<rect x="{lx}" y="{ly}" width="12" height="12" fill="{col}"/>')
        lines.append(
            f'<text x="{lx + 16}" y="{ly + 10}" fill="#555">{html.escape(sname)}</text>'
        )

    lines.append("</svg>")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# HTML report assembly
# ---------------------------------------------------------------------------

def build_html_report(data: Dict[str, Any], output_path: str) -> str:
    """Build a self-contained HTML report with embedded SVG charts."""
    source = data["source"]
    endpoints = data["endpoints"]
    timeseries = data.get("timeseries", [])
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    charts: List[str] = []

    # --- Bar charts from endpoint summary ---
    if source == "locust":
        names = [ep["name"] for ep in endpoints]
        charts.append(_svg_bar_chart(
            "Median Response Time (ms)", names,
            [ep["median"] for ep in endpoints], color="#4a90d9",
        ))
        charts.append(_svg_bar_chart(
            "P95 Response Time (ms)", names,
            [ep["p95"] for ep in endpoints], color="#e67e22",
        ))
        charts.append(_svg_bar_chart(
            "P99 Response Time (ms)", names,
            [ep["p99"] for ep in endpoints], color="#e74c3c",
        ))
        charts.append(_svg_bar_chart(
            "Requests / second", names,
            [ep["rps"] for ep in endpoints], color="#2ecc71",
        ))
        charts.append(_svg_bar_chart(
            "Failure Count", names,
            [ep["failures"] for ep in endpoints], color="#c0392b",
        ))
    elif source == "k6":
        names = [ep["name"] for ep in endpoints]
        avgs = [ep.get("avg", 0) for ep in endpoints]
        if any(a > 0 for a in avgs):
            charts.append(_svg_bar_chart(
                "Average Duration (ms)", names, avgs, color="#4a90d9",
            ))
        p95s = [ep.get("p95", 0) for ep in endpoints]
        if any(p > 0 for p in p95s):
            charts.append(_svg_bar_chart(
                "P95 Duration (ms)", names, p95s, color="#e67e22",
            ))
    elif source == "artillery":
        for ep in endpoints:
            vals = [
                ep.get("min", 0), ep.get("median", 0),
                ep.get("p95", 0), ep.get("p99", 0), ep.get("max", 0),
            ]
            charts.append(_svg_bar_chart(
                "Latency Distribution (ms)",
                ["Min", "Median", "P95", "P99", "Max"],
                vals, color="#4a90d9",
            ))
            codes = ep.get("codes", {})
            if codes:
                charts.append(_svg_bar_chart(
                    "HTTP Status Codes",
                    list(codes.keys()),
                    [float(v) for v in codes.values()],
                    color="#2ecc71",
                ))

    # --- Line charts from time-series ---
    if timeseries:
        ts_labels = [str(t.get("timestamp", "")) for t in timeseries]
        series_p50 = [t.get("p50", 0) for t in timeseries]
        series_p95 = [t.get("p95", 0) for t in timeseries]
        series_rps = [t.get("rps", 0) for t in timeseries]

        if any(v > 0 for v in series_p50 + series_p95):
            charts.append(_svg_line_chart(
                "Latency Over Time (ms)", ts_labels,
                {"P50": series_p50, "P95": series_p95},
            ))
        if any(v > 0 for v in series_rps):
            charts.append(_svg_line_chart(
                "Throughput Over Time (req/s)", ts_labels,
                {"RPS": series_rps},
            ))

    # --- Summary table ---
    table_rows = ""
    for ep in endpoints:
        row_cells = "".join(
            f"<td>{html.escape(str(v))}</td>" for v in ep.values()
        )
        table_rows += f"<tr>{row_cells}</tr>\n"
    headers = "".join(
        f"<th>{html.escape(k)}</th>" for k in (endpoints[0].keys() if endpoints else [])
    )

    report_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8"/>
<title>RustChain Load Test Report – {html.escape(source)}</title>
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
         Helvetica, Arial, sans-serif; margin: 2rem; background: #fff; color: #333; }}
  h1 {{ border-bottom: 2px solid #4a90d9; padding-bottom: .4rem; }}
  h2 {{ color: #4a90d9; margin-top: 2rem; }}
  .meta {{ color: #888; font-size: .9rem; }}
  .charts {{ display: flex; flex-wrap: wrap; gap: 1.5rem; margin: 1rem 0; }}
  .charts svg {{ flex: 1 1 auto; max-width: 100%; }}
  table {{ border-collapse: collapse; width: 100%; margin: 1rem 0; font-size: .85rem; }}
  th, td {{ border: 1px solid #ddd; padding: .45rem .7rem; text-align: left; }}
  th {{ background: #f5f5f5; }}
  tr:nth-child(even) {{ background: #fafafa; }}
  footer {{ margin-top: 2rem; color: #aaa; font-size: .8rem; }}
</style>
</head>
<body>
<h1>RustChain API – Load Test Report</h1>
<p class="meta">Source: <strong>{html.escape(source)}</strong> &middot;
Generated: <code>{html.escape(now)}</code></p>

<h2>Charts</h2>
<div class="charts">
{"".join(charts) if charts else "<p><em>No chart data available.</em></p>"}
</div>

<h2>Raw Metrics</h2>
<table>
<thead><tr>{headers}</tr></thead>
<tbody>
{table_rows}
</tbody>
</table>

<footer>
Report generated by <code>load_tests/graph_reporter.py</code> &mdash;
RustChain Stress Test Harness v2.0
</footer>
</body>
</html>"""

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as fh:
        fh.write(report_html)

    return output_path


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(
        description="Generate HTML charts from load-test results."
    )
    parser.add_argument(
        "input",
        help=(
            "Input file path: Locust CSV prefix (e.g. results/locust), "
            "k6 summary JSON, or Artillery JSON report."
        ),
    )
    parser.add_argument(
        "--format", "-f",
        choices=["locust", "k6", "artillery"],
        default="locust",
        help="Input format (default: locust).",
    )
    parser.add_argument(
        "--output", "-o",
        default=None,
        help="Output HTML file path (default: <input>_report.html).",
    )
    args = parser.parse_args(argv)

    loaders = {
        "locust": load_locust_stats,
        "k6": load_k6_summary,
        "artillery": load_artillery_report,
    }

    try:
        data = loaders[args.format](args.input)
    except FileNotFoundError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    except (json.JSONDecodeError, KeyError) as exc:
        print(f"Error parsing input: {exc}", file=sys.stderr)
        return 1

    output = args.output or f"{os.path.splitext(args.input)[0]}_report.html"
    path = build_html_report(data, output)
    print(f"✅  Report saved to {path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
