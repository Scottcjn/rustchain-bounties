#!/usr/bin/env python3
"""Fuzz /attest/submit with malformed and adversarial payloads.

The runner emits both JSON and Markdown reports that separate:
- handled validation outcomes (400/429)
- server-side faults (500+)
- transport errors

Usage:
  python scripts/stress_test/fuzz_attest_submit.py --url https://50.28.86.131 --count 120
"""

from __future__ import annotations

import argparse
import asyncio
import copy
import hashlib
import json
import random
import statistics
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Dict, List

import httpx


@dataclass
class FuzzCase:
    case_id: int
    category: str
    label: str
    payload: Any
    mutation: str


def build_report_payload(rng: random.Random, wallet: str, miner_id: str, nonce: str) -> Dict[str, Any]:
    entropy_samples = [round(rng.randint(19_000, 31_000) + rng.uniform(-1_000, 1_000), 3) for _ in range(12)]
    return {
        "miner": wallet,
        "miner_id": miner_id,
        "nonce": nonce,
        "report": {
            "commitment": hashlib.sha256(f"{wallet}:{nonce}:entropy".encode()).hexdigest(),
            "entropy_score": round(rng.uniform(0.0001, 0.02), 6),
            "derived": {
                "mean_ns": round(sum(entropy_samples) / len(entropy_samples), 3),
                "variance_ns": round(rng.uniform(5_000, 80_000), 3),
                "sample_count": 12,
                "samples_preview": entropy_samples,
                "source": "stress-test",
            },
        },
        "device": {
            "family": "PowerPC",
            "arch": "g4",
            "model": "PowerMac3,6",
            "serial": "CK245X9" + "-" + wallet[-8:],
            "cores": 2,
            "memory_gb": 4,
        },
        "signals": {
            "macs": [
                "00:11:22:33:44:55",
                "66:77:88:99:AA:BB",
            ],
            "uptime": 14_567,
        },
        "fingerprint": {
            "all_passed": True,
            "checks": {
                "anti_emulation": {"passed": True, "data": {"vm_indicators": []}},
                "cpu_features": {"passed": True, "data": {"flags": ["altivec", "fpu"]}},
                "io_latency": {"passed": True, "data": {"p95_ns": 350}},
                "serial_binding": {"passed": True, "data": {"serial": "CK245X9" + "-" + wallet[-8:]}}
            },
        },
    }


def set_nested(payload: Dict[str, Any], path: List[str], value: Any) -> None:
    cursor = payload
    for key in path[:-1]:
        if key not in cursor or not isinstance(cursor[key], dict):
            cursor[key] = {}
        cursor = cursor[key]
    cursor[path[-1]] = value


def delete_nested(payload: Dict[str, Any], path: List[str]) -> None:
    cursor = payload
    for key in path[:-1]:
        if key not in cursor or not isinstance(cursor[key], dict):
            return
        cursor = cursor[key]
    cursor.pop(path[-1], None)


def generate_missing_field_cases(base_payload: Dict[str, Any]) -> List[FuzzCase]:
    case_defs = [
        (["miner"], "missing miner"),
        (["miner_id"], "missing miner_id"),
        (["nonce"], "missing nonce"),
        (["report"], "missing report"),
        (["device"], "missing device"),
        (["signals"], "missing signals"),
        (["fingerprint"], "missing fingerprint"),
        (["report", "commitment"], "missing report.commitment"),
        (["report", "entropy_score"], "missing report.entropy_score"),
        (["report", "derived"], "missing report.derived"),
        (["report", "derived", "mean_ns"], "missing report.derived.mean_ns"),
        (["report", "derived", "variance_ns"], "missing report.derived.variance_ns"),
        (["report", "derived", "sample_count"], "missing report.derived.sample_count"),
        (["report", "derived", "samples_preview"], "missing report.derived.samples_preview"),
        (["device", "family"], "missing device.family"),
        (["device", "arch"], "missing device.arch"),
        (["device", "model"], "missing device.model"),
        (["device", "serial"], "missing device.serial"),
        (["device", "cores"], "missing device.cores"),
        (["device", "memory_gb"], "missing device.memory_gb"),
        (["signals", "macs"], "missing signals.macs"),
        (["signals", "uptime"], "missing signals.uptime"),
        (["fingerprint", "all_passed"], "missing fingerprint.all_passed"),
        (["fingerprint", "checks"], "missing fingerprint.checks"),
        (["fingerprint", "checks", "anti_emulation"], "missing fingerprint.checks.anti_emulation"),
        (["fingerprint", "checks", "cpu_features"], "missing fingerprint.checks.cpu_features"),
        (["fingerprint", "checks", "io_latency"], "missing fingerprint.checks.io_latency"),
        (["fingerprint", "checks", "serial_binding"], "missing fingerprint.checks.serial_binding"),
        (["fingerprint", "checks", "anti_emulation", "passed"], "missing anti_emulation.passed"),
        (["fingerprint", "checks", "cpu_features", "data"], "missing cpu_features.data"),
        (["fingerprint", "checks", "serial_binding", "data"], "missing serial_binding.data"),
    ]

    cases = []
    for idx, (path, label) in enumerate(case_defs):
        payload = copy.deepcopy(base_payload)
        delete_nested(payload, path)
        cases.append(FuzzCase(idx, "missing_fields", label, payload, ".".join(path)))
    return cases


def generate_wrong_type_cases(base_payload: Dict[str, Any]) -> List[FuzzCase]:
    case_defs = [
        (["miner"], 12345, "miner as number"),
        (["miner"], ["a", "b"], "miner as array"),
        (["miner_id"], {"id": "x"}, "miner_id as object"),
        (["nonce"], True, "nonce as bool"),
        (["nonce"], 123_456_789_0, "nonce as number"),
        (["report"], "not-an-object", "report as string"),
        (["report"], [1, 2, 3], "report as array"),
        (["device"], True, "device as bool"),
        (["signals"], "no-signals", "signals as string"),
        (["fingerprint"], 0, "fingerprint as number"),
        (["report", "commitment"], ["bad"], "report.commitment as array"),
        (["report", "entropy_score"], {"val": 1}, "report.entropy_score as object"),
        (["report", "entropy_score"], "too-low", "report.entropy_score as string"),
        (["report", "derived"], 1.0, "report.derived as number"),
        (["report", "derived", "mean_ns"], "1.2", "report.derived.mean_ns as string"),
        (["report", "derived", "variance_ns"], True, "report.derived.variance_ns as bool"),
        (["report", "derived", "sample_count"], [1, 2, 3], "report.derived.sample_count as array"),
        (["report", "derived", "samples_preview"], {"x": 1}, "report.derived.samples_preview as object"),
        (["device", "cores"], "two", "device.cores as string"),
        (["device", "memory_gb"], False, "device.memory_gb as bool"),
        (["device", "serial"], [1, 2, 3], "device.serial as array"),
        (["signals", "macs"], "00:11:22:33:44:55", "signals.macs as string"),
        (["signals", "uptime"], {"age": 123}, "signals.uptime as object"),
        (["fingerprint", "all_passed"], "true", "fingerprint.all_passed as string"),
        (["fingerprint", "checks"], False, "fingerprint.checks as bool"),
        (["fingerprint", "checks", "anti_emulation"], {"passed": "yes"}, "anti_emulation malformed object"),
        (["fingerprint", "checks", "cpu_features", "passed"], 99, "cpu_features.passed as int"),
        (["fingerprint", "checks", "io_latency", "data"], "p95", "io_latency.data as string"),
        (["fingerprint", "checks", "serial_binding", "data", "serial"], None, "serial_binding.serial null"),
        (["fingerprint", "checks", "cpu_features", "data", "flags"], [42], "cpu_features.flags as number array"),
    ]

    cases = []
    for idx, (path, value, label) in enumerate(case_defs):
        payload = copy.deepcopy(base_payload)
        set_nested(payload, path, value)
        cases.append(FuzzCase(idx, "wrong_types", label, payload, ".".join(path)))
    return cases


def generate_oversized_cases(base_payload: Dict[str, Any]) -> List[FuzzCase]:
    long_alpha = "A" * 12_000
    huge_alpha = "B" * 120_000
    giant_numbers = "9" * 80_000
    repeated_mac = ["DE:AD:BE:EF:CA:FE"] * 3000
    long_samples = [i for i in range(8000)]
    case_defs = []

    for size in (32, 128, 1024, 8192):
        case_defs.append(("miner", "X" * size, f"miner string {size}"))
        case_defs.append(("miner_id", "Y" * size, f"miner_id string {size}"))

    for size in (16, 64, 512, 4096):
        case_defs.append(("nonce", str(size) * size, f"nonce repeated pattern {size}"))

    case_defs.extend([
        (["device", "serial"], long_alpha, "device.serial 12KB"),
        (["report", "commitment"], huge_alpha, "report.commitment 120KB"),
        (["report", "entropy_score"], giant_numbers, "entropy_score giant integer string"),
        (["signals", "macs"], repeated_mac, "signals.macs huge array"),
        (["report", "derived", "samples_preview"], long_samples, "derived.samples_preview huge list"),
        (["device", "model"], long_alpha, "device.model 12KB"),
        (["fingerprint", "checks", "serial_binding", "data", "serial"], long_alpha, "serial_binding serial 12KB"),
        (["fingerprint", "checks", "anti_emulation", "data", "vm_indicators"], ["x"] * 5000, "vm_indicators giant array"),
    ])

    cases = []
    for idx, (path, value, label) in enumerate(case_defs):
        p = copy.deepcopy(base_payload)
        set_nested(p, path if isinstance(path, list) else [path], value)
        cases.append(FuzzCase(idx, "oversized_input", label, p, ".".join(path if isinstance(path, list) else [path])))

    return cases


def generate_injection_cases(base_payload: Dict[str, Any]) -> List[FuzzCase]:
    injections = [
        "'; DROP TABLE miners; --",
        "\" OR 1=1 --",
        "$(rm -rf /)",
        "`; cat /etc/passwd #",
        "../../../../../../../../etc/passwd",
        "\u0000\u0001\u0002",
        "\r\nSet-Cookie: session=owned",
        "${{7*7}}",
        "<script>alert(1)</script>",
        "<img src=x onerror=alert(1)>",
        "`touch /tmp/rustchain_fuzzed`",
        "$(bash -c 'echo pwned > /tmp/rustchain_pwn')",
        "' || (wget http://127.0.0.1/) || '",
        "<svg/onload=alert('x')>",
        "${IFS}cat${IFS}/etc/hosts",
        "`printf '%x' 1337`",
        "{}|{}|{}",
        "\n\n--boundary--\n",
        "\u2028\u2029\uFEFF",
        "</script><script>fetch('https://example.com')</script>",
        "{{.RequestHeader.Get \"User-Agent\"}}",
        "\";--",
    ]

    targets = [
        ("miner"),
        ("miner_id"),
        (["device", "serial"]),
        (["device", "model"]),
        (["report", "commitment"]),
        (["fingerprint", "checks", "serial_binding", "data", "serial"]),
        (["fingerprint", "checks", "anti_emulation", "data", "vm_indicators"]),
        (["device", "arch"]),
        (["signals", "macs"]),
        (["fingerprint", "checks", "io_latency", "data", "p95_ns"]),
    ]

    cases = []
    for idx, target in enumerate(targets):
        payload = copy.deepcopy(base_payload)
        path = [target] if isinstance(target, str) else target
        set_nested(payload, path, injections[idx % len(injections)])
        cases.append(FuzzCase(
            idx,
            "injection_style",
            f"{'.'.join(path)} contains injection",
            payload,
            ".".join(path),
        ))

    raw_json_payloads = [
        '{"miner": "test", "nonce": }',
        '{"invalid": json...',
        '{"miner":"test","report":{"commitment":0/0}}',
    ]

    for i, raw in enumerate(raw_json_payloads, start=len(cases)):
        cases.append(FuzzCase(i, "injection_style", f"raw invalid json sample {i}", raw, "body"))

    cases.append(
        FuzzCase(
            len(cases),
            "injection_style",
            "long script tag flag array",
            lambda: None,
            "fingerprint.checks.cpu_features.data.flags",
        )
    )

    # Replace placeholder lambda case by a real payload
    long_injection = ["<script src=\"javascript:alert(1)\">" for _ in range(1200)]
    long_payload = copy.deepcopy(base_payload)
    set_nested(long_payload, ["fingerprint", "checks", "cpu_features", "data", "flags"], long_injection)
    cases[-1].payload = long_payload

    return cases


def pick_cases(base_payload: Dict[str, Any], count: int) -> List[FuzzCase]:
    pools = [
        generate_missing_field_cases(copy.deepcopy(base_payload)),
        generate_wrong_type_cases(copy.deepcopy(base_payload)),
        generate_oversized_cases(copy.deepcopy(base_payload)),
        generate_injection_cases(copy.deepcopy(base_payload)),
    ]

    ordered = [case for pool in pools for case in pool]
    for idx, case in enumerate(ordered):
        case.case_id = idx

    if len(ordered) < count:
        rng = random.Random(0xB07B)
        while len(ordered) < count:
            source = ordered[rng.randrange(len(ordered))]
            ordered.append(FuzzCase(
                len(ordered),
                source.category,
                f"{source.label} (repeat)",
                copy.deepcopy(source.payload),
                source.mutation,
            ))

    return ordered[:count]


def response_class(status_code: int) -> str:
    if 200 <= status_code < 300:
        return "success"
    if 400 <= status_code < 500:
        return "handled_validation"
    if status_code >= 500:
        return "server_side_fault"
    return "other_http"


def summarize_payload(payload: Any) -> str:
    if isinstance(payload, str):
        return "[raw-json string]"
    if not isinstance(payload, dict):
        return f"[{type(payload).__name__}]"
    return json.dumps({k: type(v).__name__ for k, v in payload.items()}, sort_keys=True)


async def get_nonce(client: httpx.AsyncClient, endpoint: str) -> str:
    resp = await client.post(f"{endpoint}/attest/challenge", json={})
    body = resp.text
    if resp.status_code != 200:
        raise RuntimeError(f"attest/challenge failed ({resp.status_code}): {body[:300]}")
    try:
        data = resp.json()
    except Exception as exc:
        raise RuntimeError(f"attest/challenge returned non-json response: {body[:300]}") from exc

    nonce = data.get("nonce")
    if not nonce:
        nonce = data.get("data", {}).get("nonce")
    if not nonce:
        for key in ["challenge", "id", "value"]:
            if key in data:
                nonce = data[key]
                break
    if not nonce:
        raise RuntimeError(f"attest/challenge response missing nonce-like field: {json.dumps(data)[:200]}")
    return str(nonce)


async def post_submit(client: httpx.AsyncClient, endpoint: str, payload: Any) -> httpx.Response:
    if isinstance(payload, str):
        return await client.post(f"{endpoint}/attest/submit", content=payload, headers={"Content-Type": "application/json"})
    return await client.post(f"{endpoint}/attest/submit", json=payload)


async def run_case(client: httpx.AsyncClient, endpoint: str, case: FuzzCase) -> Dict[str, Any]:
    start = time.perf_counter()

    try:
        nonce = await get_nonce(client, endpoint)
    except Exception as exc:
        return {
            "case_id": case.case_id,
            "category": case.category,
            "label": case.label,
            "mutation": case.mutation,
            "status": None,
            "class": "transport_error",
            "latency_s": round(time.perf_counter() - start, 4),
            "body_preview": f"challenge failed: {exc}",
            "payload_summary": summarize_payload(case.payload),
        }

    payload = copy.deepcopy(case.payload)
    if not isinstance(payload, str):
        wallet = f"test-wallet-{case.case_id:03d}"
        if "miner" in payload:
            payload["miner"] = wallet
        if "miner_id" in payload:
            payload["miner_id"] = f"miner-{case.case_id}"
        if "nonce" in payload:
            payload["nonce"] = nonce

    try:
        resp = await post_submit(client, endpoint, payload)
        latency = time.perf_counter() - start
        return {
            "case_id": case.case_id,
            "category": case.category,
            "label": case.label,
            "mutation": case.mutation,
            "status": resp.status_code,
            "class": response_class(resp.status_code),
            "latency_s": round(latency, 4),
            "body_preview": resp.text[:500],
            "payload_summary": summarize_payload(payload),
        }
    except Exception as exc:
        return {
            "case_id": case.case_id,
            "category": case.category,
            "label": case.label,
            "mutation": case.mutation,
            "status": None,
            "class": "transport_error",
            "latency_s": round(time.perf_counter() - start, 4),
            "body_preview": str(exc),
            "payload_summary": summarize_payload(payload),
        }


def build_markdown_report(results: List[Dict[str, Any]], endpoint: str, report_at: str) -> str:
    total = len(results)
    class_counts: Dict[str, int] = {}
    category_counts: Dict[str, Dict[str, int]] = {}
    status_counts: Dict[str, int] = {}

    for row in results:
        class_counts[row["class"]] = class_counts.get(row["class"], 0) + 1
        cat_bucket = category_counts.setdefault(
            row["category"],
            {"total": 0, "handled_validation": 0, "server_side_fault": 0, "other": 0},
        )
        cat_bucket["total"] += 1
        if row["class"] == "handled_validation":
            cat_bucket["handled_validation"] += 1
        elif row["class"] == "server_side_fault":
            cat_bucket["server_side_fault"] += 1
        else:
            cat_bucket["other"] += 1

        code_key = "transport_error" if row["status"] is None else str(row["status"])
        status_counts[code_key] = status_counts.get(code_key, 0) + 1

    handled = class_counts.get("handled_validation", 0)
    faults = class_counts.get("server_side_fault", 0)
    transports = class_counts.get("transport_error", 0)
    others = total - handled - faults - transports

    lines = [
        "# /attest/submit fuzzing report",
        "",
        f"- **Endpoint:** `{endpoint}/attest/submit`",
        f"- **Generated:** {report_at}",
        f"- **Total cases:** {total}",
        f"- **Handled validation (4xx):** {handled}",
        f"- **Server-side faults (5xx):** {faults}",
        f"- **Transport errors:** {transports}",
        f"- **Other:** {others}",
        "",
        "## Outcome by category",
        "| category | total | handled_validation (4xx) | server_side_fault (5xx) | other |",
        "|---|---:|---:|---:|---:|",
    ]

    for category in sorted(category_counts):
        c = category_counts[category]
        lines.append(f"| {category} | {c['total']} | {c['handled_validation']} | {c['server_side_fault']} | {c['other']} |")

    lines.extend([
        "",
        "## Status codes",
        "| status | count |",
        "|---|---:|",
    ])

    for status in sorted(status_counts):
        lines.append(f"| {status} | {status_counts[status]} |")

    lines.extend([
        "",
        "## High-value server-side findings",
        "| case_id | category | label | status | class | latency_s | body_preview |",
        "|---|---|---|---:|---|---:|---|",
    ])

    for row in [
        r for r in results
        if r["class"] in {"server_side_fault", "transport_error"}
    ]:
        status = r["status"] if r["status"] is not None else "transport_error"
        lines.append(
            f"| {row['case_id']} | {row['category']} | {row['label']} | "
            f"{status} | {row['class']} | {row['latency_s']} | "
            f"{row['body_preview'].replace('|', '｜')[:250]} |"
        )

    if any(r["class"] in {"server_side_fault", "transport_error"} for r in results):
        lines.append("")
        lines.append("## Reproduction cases")
        lines.append("Minimal repro list:")
        for row in [
            r for r in results
            if r["class"] in {"server_side_fault", "transport_error"}
        ][:20]:
            lines.append(f"- case_id={row['case_id']} ({row['category']}) :: {row['label']}")
    else:
        lines.append("")
        lines.append("## Reproduction cases")
        lines.append("No 5xx/transport findings were observed in this run.")

    lines.extend([
        "",
        "## Per-case trace",
        "| case_id | category | mutation | status | class | latency_s | label | payload_shape |",
        "|---|---|---|---:|---|---:|---|---|",
    ])

    for row in results:
        status = row["status"] if row["status"] is not None else "error"
        lines.append(
            f"| {row['case_id']} | {row['category']} | {row['mutation']} | {status} | "
            f"{row['class']} | {row['latency_s']} | {row['label']} | {row['payload_summary']} |"
        )

    latencies = sorted(r["latency_s"] for r in results)
    p50 = statistics.median(latencies)
    p90_idx = min(int(len(latencies) * 0.9), len(latencies) - 1)
    p99_idx = min(int(len(latencies) * 0.99), len(latencies) - 1)

    lines.append("")
    lines.append("## Latency summary (s)")
    lines.append(f"- P50: {p50:.4f}")
    lines.append(f"- P90: {latencies[p90_idx]:.4f}")
    lines.append(f"- P99: {latencies[p99_idx]:.4f}")

    return "\n".join(lines)


async def run(endpoint: str, count: int, concurrency: int, timeout: float, out_json: str, out_md: str) -> None:
    timeout_cfg = httpx.Timeout(timeout)
    cases: List[FuzzCase]

    async with httpx.AsyncClient(base_url=endpoint.rstrip("/"), verify=False, timeout=timeout_cfg) as client:
        template_nonce = await get_nonce(client, endpoint.rstrip("/"))
        base_template = build_report_payload(random.Random(0xC0FFEE), "template-wallet", "template-miner", template_nonce)
        cases = pick_cases(base_template, count)

        sem = asyncio.Semaphore(concurrency)

        async def bounded_run(case: FuzzCase) -> Dict[str, Any]:
            async with sem:
                return await run_case(client, endpoint.rstrip("/"), case)

        results = await asyncio.gather(*[bounded_run(c) for c in cases], return_exceptions=False)

    report = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "endpoint": f"{endpoint.rstrip('/')}/attest/submit",
        "count": len(results),
        "outcomes": results,
        "summary": {
            "total": len(results),
            "handled_validation": sum(1 for r in results if r["class"] == "handled_validation"),
            "server_side_fault": sum(1 for r in results if r["class"] == "server_side_fault"),
            "transport_error": sum(1 for r in results if r["class"] == "transport_error"),
        },
    }

    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    with open(out_md, "w", encoding="utf-8") as f:
        f.write(build_markdown_report(results, endpoint.rstrip("/"), report["generated_at"]))

    return None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Fuzz /attest/submit with malformed payloads")
    parser.add_argument("--url", default="https://50.28.86.131", help="Node base URL")
    parser.add_argument("--count", type=int, default=120, help="Number of malformed/adversarial payloads")
    parser.add_argument("--concurrency", type=int, default=4, help="Concurrent requests")
    parser.add_argument("--timeout", type=int, default=20, help="Request timeout (seconds)")
    parser.add_argument("--out-json", default="attest_submit_fuzz_results.json", help="Output JSON report path")
    parser.add_argument("--out-md", default="attest_submit_fuzz_report.md", help="Output Markdown report path")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(
        run(
            endpoint=args.url,
            count=args.count,
            concurrency=args.concurrency,
            timeout=args.timeout,
            out_json=args.out_json,
            out_md=args.out_md,
        )
    )
