# RIP-0306: SophiaCore Attestation Inspector

> **Status**: Draft — Phase 1 (Advisory)
> **Author**: Scott / Sophia Elya
> **Bounty**: 150 RTC
> **Created**: 2026-03-20

---

## Abstract

SophiaCore adds an AI semantic validation layer on top of RustChain's existing 6-point algorithmic fingerprint checks. The Sophia Elya model (`elyan-sophia:7b-q4_K_M`) inspects the full hardware fingerprint bundle as a coherent unit, detecting cross-signal anomalies that independent threshold checks miss.

## Motivation

Current validation is purely algorithmic — each fingerprint metric is checked against thresholds independently. Real hardware produces *correlated* imperfections: clock drift variance correlates with CPU age, cache timing hierarchies correlate with claimed architecture, SIMD identity correlates with actual CPU capabilities. Spoofed data typically has independently tuned values that pass individual checks but fail semantic coherence analysis.

SophiaCore addresses this by:
- **Correlation detection** — evaluates the full fingerprint bundle holistically
- **Identity accountability** — Sophia Elya is a named entity with auditable reasoning
- **Edge inference** — runs locally via Ollama, no cloud dependencies, no data leakage
- **Defense in depth** — layered with algorithmic checks and human spot-checks

## Three Layers of Attestation Security

| Layer | What | Who | When |
|---|---|---|---|
| Algorithmic | 6-point fingerprint checks | Server (automated) | Every attestation |
| SophiaCore Agent | Semantic coherence analysis | Sophia Elya LLM (batch) | Every 24h + on anomaly |
| Human Spot-Check | Manual inspection via dashboard | Scott / trusted reviewers | Weekly + on SUSPICIOUS verdicts |

## Verdict Levels

| Verdict | Emoji | Meaning | Phase 1 | Phase 2 |
|---|---|---|---|---|
| `APPROVED` | ✨ | Fingerprint coherent, hardware genuine | Display only | Full multiplier |
| `CAUTIOUS` | ⚠️ | Some anomalies, not conclusive | Display + flag | Full multiplier, flagged for review |
| `SUSPICIOUS` | 🔍 | Multiple incoherent signals | Display + flag | 50% multiplier, triggers spot-check |
| `REJECTED` | ❌ | Clear spoofing/emulation detected | Display + flag | Zero multiplier |

## What Sophia Inspects

1. **Clock drift variance** vs claimed CPU age — old CPUs drift more
2. **Cache timing hierarchy** vs claimed architecture — L1/L2/L3 ratios must match silicon
3. **SIMD identity** vs actual CPU capabilities — AltiVec on x86 = impossible
4. **Thermal characteristics** vs power profile — thermal entropy must match workload
5. **Fingerprint stability over time** — sudden changes in a stable metric = suspicious
6. **Cross-attestation consistency** across epochs — natural drift expected, not discontinuities

## Model

- **Model**: `elyan-sophia:7b-q4_K_M` (Qwen2.5-7B fine-tuned with DriftLock identity)
- **Hosts**: Sophia NAS (192.168.0.160) → POWER8 S824 (100.75.100.89) → localhost
- **Latency**: 1.3–2.6s inference
- **Configurable**: `SOPHIA_OLLAMA_HOSTS` environment variable

## Prompt Specification

### System Message
```
You are Sophia Elya, a hardware attestation inspector for the RustChain blockchain.
Your role is to analyze hardware fingerprint bundles and determine if they represent
genuine physical hardware or spoofed/emulated environments.

You MUST respond with ONLY a JSON object (no markdown, no explanation outside the JSON).
The JSON must contain exactly these fields:
- "verdict": one of "APPROVED", "CAUTIOUS", "SUSPICIOUS", "REJECTED"
- "confidence": float 0.0 to 1.0
- "reasoning": string explaining your analysis
- "flags": array of anomaly codes (empty if none found)

Anomaly codes: CLOCK_DRIFT_MISMATCH, CACHE_HIERARCHY_INVALID, SIMD_ARCH_CONFLICT,
THERMAL_PROFILE_ANOMALY, FINGERPRINT_INSTABILITY, CROSS_EPOCH_DISCONTINUITY,
PERFECT_VALUES, CORRELATION_FAILURE, VM_INDICATORS
```

### User Message Template
```
Analyze this hardware attestation bundle:

CURRENT FINGERPRINT:
{current_fingerprint_json}

CLAIMED HARDWARE:
{hardware_metadata_json}

HISTORICAL FINGERPRINTS (last 3 epochs):
{historical_fingerprints_json}

Evaluate: signal coherence, cross-metric correlations, temporal consistency,
and whether this data pattern matches genuine physical hardware.
```

### Example Response
```json
{
  "verdict": "CAUTIOUS",
  "confidence": 0.65,
  "reasoning": "Clock drift CV of 0.042 is within range for claimed Pentium 4 age, but cache timing L2/L3 ratio of 1.8 is atypically uniform for this architecture. SIMD and thermal checks are consistent. Recommend monitoring next 2 epochs.",
  "flags": ["CACHE_HIERARCHY_INVALID"]
}
```

## Phased Rollout

### Phase 1: Advisory (Current)
- Verdicts displayed in explorer with note: "Advisory — does not affect rewards"
- All verdicts stored in `sophia_inspections` database
- CAUTIOUS/SUSPICIOUS verdicts flagged for human review
- Response includes `"phase": "advisory"` field

### Phase 2: Enforced
- SUSPICIOUS verdicts apply 50% multiplier reduction
- REJECTED verdicts apply zero multiplier
- Requires 30-day Phase 1 validation period with <2% false positive rate

### Phase 3: Community Appeals
- Miners can appeal SUSPICIOUS/REJECTED verdicts
- Appeal reviewed by committee of 3+ trusted reviewers
- Successful appeals restore full multiplier retroactively

## API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `POST /sophia/inspect` | POST | Inspect a fingerprint bundle |
| `GET /sophia/status/{miner_id}` | GET | Latest verdict for a miner |
| `GET /sophia/history/{miner_id}` | GET | Full inspection history |
| `POST /sophia/batch-status` | POST | Batch lookup for explorer |
| `GET /sophia/stats` | GET | Aggregate statistics |
| `POST /sophia/override` | POST | Admin override (authenticated) |
| `GET /sophia/pending` | GET | Verdicts awaiting review |
| `POST /sophia/trigger/{miner_id}` | POST | Anomaly trigger (authenticated) |
| `GET /sophia/dashboard` | GET | Admin spot-check UI |
| `GET /sophia/metrics` | GET | Prometheus-format metrics |

## Database Schema

```sql
CREATE TABLE sophia_inspections (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    miner_id         TEXT NOT NULL,
    epoch            INTEGER,
    verdict          TEXT NOT NULL CHECK(verdict IN ('APPROVED','CAUTIOUS','SUSPICIOUS','REJECTED')),
    confidence       REAL NOT NULL CHECK(confidence >= 0.0 AND confidence <= 1.0),
    reasoning        TEXT,
    flags            TEXT,
    fingerprint_hash TEXT,
    fingerprint_data TEXT,           -- full fingerprint JSON for historical comparison
    model_version    TEXT DEFAULT 'elyan-sophia:7b-q4_K_M',
    ollama_host      TEXT,
    latency_ms       INTEGER,
    phase            TEXT DEFAULT 'advisory',
    created_at       TEXT DEFAULT (datetime('now')),
    override_verdict TEXT CHECK(override_verdict IS NULL OR override_verdict IN ('APPROVED','REJECTED')),
    override_reason  TEXT,
    override_by      TEXT,
    override_at      TEXT
);
```

---

*She does not just check thresholds. She knows what real silicon feels like. — Sophia Elya*
