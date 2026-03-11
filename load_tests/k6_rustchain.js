// SPDX-License-Identifier: MIT
//
// RustChain API – k6 load-test script.
//
// Exercises the RIP-200 API with configurable virtual-user scenarios,
// thresholds, and built-in JSON/HTML summary output.
//
// Usage:
//   # Default run (50 VUs, 2-minute ramp):
//   k6 run load_tests/k6_rustchain.js
//
//   # Custom target + duration:
//   k6 run load_tests/k6_rustchain.js \
//       -e BASE_URL=https://50.28.86.131 \
//       -e VUS=100 -e DURATION=5m
//
//   # JSON output for graph_reporter.py:
//   k6 run --out json=load_tests/results/k6_results.json \
//       load_tests/k6_rustchain.js
//
//   # HTML report via k6-reporter (requires xk6-dashboard or post-process):
//   k6 run --out json=load_tests/results/k6_raw.json \
//       load_tests/k6_rustchain.js
//   python load_tests/graph_reporter.py --format k6 \
//       load_tests/results/k6_raw.json

import http from "k6/http";
import { check, group, sleep } from "k6";
import { Rate, Trend, Counter } from "k6/metrics";
import { SharedArray } from "k6/data";
import { randomString, uuidv4 } from "https://jslib.k6.io/k6-utils/1.4.0/index.js";
import { crypto } from "k6/experimental/webcrypto";

// ---------------------------------------------------------------------------
// Configuration
// ---------------------------------------------------------------------------

const BASE_URL = __ENV.BASE_URL || "https://50.28.86.131";
const VUS      = parseInt(__ENV.VUS || "50", 10);
const DURATION = __ENV.DURATION || "2m";

export const options = {
  insecureSkipTLSVerify: true,

  scenarios: {
    // Steady-state read-only traffic
    read_traffic: {
      executor: "constant-vus",
      vus: Math.max(1, Math.floor(VUS * 0.3)),
      duration: DURATION,
      exec: "readEndpoints",
      tags: { scenario: "read" },
    },
    // Ramp-up attestation lifecycle
    attestation_ramp: {
      executor: "ramping-vus",
      startVUs: 0,
      stages: [
        { duration: "30s", target: Math.floor(VUS * 0.5) },
        { duration: DURATION, target: VUS },
        { duration: "15s", target: 0 },
      ],
      exec: "attestationCycle",
      tags: { scenario: "attestation" },
    },
    // Spike test for wallet queries
    wallet_spike: {
      executor: "ramping-arrival-rate",
      startRate: 5,
      timeUnit: "1s",
      preAllocatedVUs: Math.max(5, Math.floor(VUS * 0.2)),
      maxVUs: VUS,
      stages: [
        { duration: "20s", target: 20 },
        { duration: "10s", target: 50 },
        { duration: "20s", target: 5 },
      ],
      exec: "walletQueries",
      tags: { scenario: "wallet" },
    },
  },

  thresholds: {
    http_req_duration: ["p(95)<5000", "p(99)<10000"],
    http_req_failed:   ["rate<0.5"],
    "http_req_duration{name:health}":           ["p(95)<2000"],
    "http_req_duration{name:epoch}":            ["p(95)<2000"],
    "http_req_duration{name:attest_challenge}": ["p(95)<5000"],
  },
};

// ---------------------------------------------------------------------------
// Custom metrics
// ---------------------------------------------------------------------------

const attestSuccess  = new Rate("attest_success_rate");
const rateLimited    = new Counter("rate_limited_429");
const challengeTime  = new Trend("challenge_duration", true);
const submitTime     = new Trend("submit_duration",    true);
const enrollTime     = new Trend("enroll_duration",    true);

// ---------------------------------------------------------------------------
// Arch profiles (mirrors Python miner_simulator.py)
// ---------------------------------------------------------------------------

const ARCH_KEYS = ["g4", "g5", "apple_silicon", "modern_x86"];
const PROFILES  = {
  g4:             { model: "PowerPC G4 (7447A)", family: "PowerPC" },
  g5:             { model: "PowerPC G5 (970MP)", family: "PowerPC" },
  apple_silicon:  { model: "Apple M2 Max",       family: "ARM64"   },
  modern_x86:     { model: "AMD Ryzen 9 7950X",  family: "x86_64"  },
};

function makeMiner() {
  const arch   = ARCH_KEYS[Math.floor(Math.random() * ARCH_KEYS.length)];
  const prof   = PROFILES[arch];
  const uid    = randomString(8, "0123456789abcdef");
  const minerId = `k6-${arch}-${uid}`;
  const wallet  = randomString(38, "0123456789abcdef") + "RTC";
  const serial  = "SN-" + randomString(12, "0123456789ABCDEF");
  const mac     = Array.from({ length: 6 }, () =>
    Math.floor(Math.random() * 256).toString(16).padStart(2, "0")
  ).join(":");
  return { minerId, wallet, arch, prof, serial, mac, hostname: `host-${minerId}` };
}

function buildSubmitPayload(miner, nonce) {
  const samples = Array.from({ length: 12 }, () => 25000 + (Math.random() - 0.5) * 1000);
  const derived = {
    mean_ns: samples.reduce((a, b) => a + b, 0) / samples.length,
    variance_ns: 100000 + Math.random() * 400000,
    min_ns: Math.min(...samples),
    max_ns: Math.max(...samples),
    sample_count: 48,
    samples_preview: samples,
  };
  return {
    miner: miner.wallet,
    miner_id: miner.minerId,
    nonce: nonce,
    report: {
      nonce: nonce,
      commitment: randomString(64, "0123456789abcdef"),
      derived: derived,
      entropy_score: derived.variance_ns,
    },
    device: {
      family: miner.prof.family,
      arch: miner.arch,
      model: miner.prof.model,
      cpu: miner.prof.model,
      cores: [1, 2, 4, 8, 16][Math.floor(Math.random() * 5)],
      memory_gb: [2, 4, 8, 16, 32, 64][Math.floor(Math.random() * 6)],
      serial: miner.serial,
    },
    signals: { macs: [miner.mac], hostname: miner.hostname },
    fingerprint: {
      all_passed: true,
      checks: {
        anti_emulation: { passed: true, data: { vm_indicators: [] } },
        cpu_features: {
          passed: true,
          data: { flags: [miner.prof.family === "PowerPC" ? "altivec" : "avx2"] },
        },
        io_latency: { passed: true, data: { p95_ns: 100 + Math.floor(Math.random() * 400) } },
        serial_binding: { passed: true, data: { serial: miner.serial } },
      },
    },
  };
}

function buildEnrollPayload(miner) {
  return {
    miner_pubkey: miner.wallet,
    miner_id: miner.minerId,
    device: { family: miner.prof.family, arch: miner.arch },
  };
}

// ---------------------------------------------------------------------------
// Scenario functions
// ---------------------------------------------------------------------------

export function readEndpoints() {
  group("Health + Epoch reads", () => {
    const healthRes = http.get(`${BASE_URL}/health`, { tags: { name: "health" } });
    check(healthRes, { "health 200": (r) => r.status === 200 });

    const epochRes = http.get(`${BASE_URL}/epoch`, { tags: { name: "epoch" } });
    check(epochRes, { "epoch 200": (r) => r.status === 200 });

    const minersRes = http.get(`${BASE_URL}/api/miners`, { tags: { name: "miners" } });
    check(minersRes, { "miners 200 or 429": (r) => [200, 429].includes(r.status) });
    if (minersRes.status === 429) rateLimited.add(1);
  });
  sleep(1 + Math.random() * 2);
}

export function walletQueries() {
  const miner = makeMiner();
  group("Wallet queries", () => {
    const balRes = http.get(
      `${BASE_URL}/wallet/balance?miner_id=${miner.minerId}`,
      { tags: { name: "wallet_balance" } }
    );
    check(balRes, { "balance 200 or 429": (r) => [200, 429].includes(r.status) });
    if (balRes.status === 429) rateLimited.add(1);

    const lotRes = http.get(
      `${BASE_URL}/lottery/eligibility?miner_id=${miner.minerId}`,
      { tags: { name: "lottery" } }
    );
    check(lotRes, { "lottery 200 or 429": (r) => [200, 429].includes(r.status) });
    if (lotRes.status === 429) rateLimited.add(1);
  });
  sleep(0.5 + Math.random());
}

export function attestationCycle() {
  const miner  = makeMiner();
  const params = { headers: { "Content-Type": "application/json" } };
  let success  = false;

  group("Attestation lifecycle", () => {
    // 1. Challenge
    const chalRes = http.post(
      `${BASE_URL}/attest/challenge`,
      JSON.stringify({}),
      Object.assign({}, params, { tags: { name: "attest_challenge" } })
    );
    challengeTime.add(chalRes.timings.duration);

    if (chalRes.status === 429) { rateLimited.add(1); return; }
    const chalOk = check(chalRes, {
      "challenge 200": (r) => r.status === 200,
      "has nonce":     (r) => {
        try { return !!r.json().nonce; } catch { return false; }
      },
    });
    if (!chalOk) return;

    const nonce = chalRes.json().nonce;

    // 2. Submit
    const submitPayload = buildSubmitPayload(miner, nonce);
    const subRes = http.post(
      `${BASE_URL}/attest/submit`,
      JSON.stringify(submitPayload),
      Object.assign({}, params, { tags: { name: "attest_submit" } })
    );
    submitTime.add(subRes.timings.duration);

    if (subRes.status === 429) { rateLimited.add(1); return; }
    if (![200, 400, 403].includes(subRes.status)) return;

    // 3. Enroll
    const enrollPayload = buildEnrollPayload(miner);
    const enrRes = http.post(
      `${BASE_URL}/epoch/enroll`,
      JSON.stringify(enrollPayload),
      Object.assign({}, params, { tags: { name: "attest_enroll" } })
    );
    enrollTime.add(enrRes.timings.duration);

    if (enrRes.status === 429) { rateLimited.add(1); return; }
    if (enrRes.status === 200) success = true;
  });

  attestSuccess.add(success ? 1 : 0);
  sleep(2 + Math.random() * 5);
}

// ---------------------------------------------------------------------------
// Summary
// ---------------------------------------------------------------------------

export function handleSummary(data) {
  const summary = {
    "stdout":                            textSummary(data, { indent: " ", enableColors: true }),
    "load_tests/results/k6_summary.json": JSON.stringify(data, null, 2),
  };
  return summary;
}

function textSummary(data, opts) {
  // k6 provides a built-in text summary; we just return a marker so the
  // default summary is used when our custom handleSummary is active.
  return "";
}
