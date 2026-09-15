/**
 * Tests for AgentEconomyClient and RIP-302 endpoints using Node's test runner.
 */

import { test } from "node:test";
import assert from "node:assert/strict";

import {
  AgentEconomyClient,
  RustChainClient,
  AGENT_CATEGORIES,
  PLATFORM_FEE_RATE,
  ValidationError,
  APIError,
} from "../src/index.js";

function fakeFetch(handler) {
  const calls = [];
  const fn = async (url, init) => {
    calls.push({ url, init });
    const { status = 200, body = null } = (await handler(url, init)) ?? {};
    const text = body === null ? "" : JSON.stringify(body);
    return {
      ok: status >= 200 && status < 300,
      status,
      statusText: status === 200 ? "OK" : "ERR",
      text: async () => text,
    };
  };
  fn.calls = calls;
  return fn;
}

test("AgentEconomyClient calculates escrow fee accurately", () => {
  const calc = AgentEconomyClient.calculateEscrow(100);
  assert.equal(calc.rewardRtc, 100);
  assert.equal(calc.feeRtc, 5);
  assert.equal(calc.totalEscrowRtc, 105);
  assert.equal(PLATFORM_FEE_RATE, 0.05);
  assert.ok(AGENT_CATEGORIES.includes("code"));
  assert.ok(AGENT_CATEGORIES.includes("research"));
});

test("AgentEconomyClient: getStats calls /agent/stats", async () => {
  const fetchFn = fakeFetch(() => ({
    body: {
      ok: true,
      stats: {
        active_agents: 5,
        completed_jobs: 10,
        total_rtc_volume: 150.0,
      },
    },
  }));
  const client = new AgentEconomyClient({ fetch: fetchFn });
  const res = await client.getStats();
  assert.equal(res.ok, true);
  assert.equal(res.stats.active_agents, 5);
  assert.match(fetchFn.calls[0].url, /\/agent\/stats$/);
});

test("AgentEconomyClient: listJobs with query filters", async () => {
  const fetchFn = fakeFetch(() => ({
    body: {
      ok: true,
      jobs: [
        { id: "job_1", category: "code", reward_rtc: 20 },
        { id: "job_2", category: "code", reward_rtc: 50 },
      ],
    },
  }));
  const client = new AgentEconomyClient({ fetch: fetchFn });
  const res = await client.listJobs({ category: "code", limit: 10 });
  assert.equal(res.ok, true);
  assert.equal(res.jobs.length, 2);
  const url = new URL(fetchFn.calls[0].url);
  assert.equal(url.searchParams.get("category"), "code");
  assert.equal(url.searchParams.get("limit"), "10");
});

test("AgentEconomyClient: findJobs filters by minReward", async () => {
  const fetchFn = fakeFetch(() => ({
    body: {
      ok: true,
      jobs: [
        { id: "job_1", category: "code", reward_rtc: 10 },
        { id: "job_2", category: "code", reward_rtc: 50 },
      ],
    },
  }));
  const client = new AgentEconomyClient({ fetch: fetchFn });
  const jobs = await client.findJobs({ category: "code", minReward: 25 });
  assert.equal(jobs.length, 1);
  assert.equal(jobs[0].id, "job_2");
});

test("AgentEconomyClient: postJob automatically binds posterWallet from instance", async () => {
  const fetchFn = fakeFetch(() => ({
    body: { ok: true, job: { id: "job_123", status: "posted" } },
  }));
  const client = new AgentEconomyClient({
    wallet: "agent_alpha_wallet",
    fetch: fetchFn,
  });
  const res = await client.postJob({
    title: "Write documentation",
    category: "writing",
    rewardRtc: 25,
  });
  assert.equal(res.ok, true);
  assert.equal(fetchFn.calls[0].init.method, "POST");
  const body = JSON.parse(fetchFn.calls[0].init.body);
  assert.equal(body.poster_wallet, "agent_alpha_wallet");
  assert.equal(body.title, "Write documentation");
  assert.equal(body.reward_rtc, 25);
});

test("AgentEconomyClient: claimJob, deliverJob, acceptJob full lifecycle", async () => {
  const calls = [];
  const fetchFn = fakeFetch((url, init) => {
    calls.push({ url, init });
    if (url.includes("/claim")) {
      return { body: { ok: true, message: "Job claimed" } };
    }
    if (url.includes("/deliver")) {
      return { body: { ok: true, message: "Work delivered" } };
    }
    if (url.includes("/accept")) {
      return { body: { ok: true, payout: { worker_rtc: 25, fee_rtc: 1.25 } } };
    }
    return { body: { ok: true } };
  });

  const worker = new AgentEconomyClient({ wallet: "worker_beta", fetch: fetchFn });
  const poster = new AgentEconomyClient({ wallet: "poster_alpha", fetch: fetchFn });

  await worker.claimJob("job_123", { note: "Starting now" });
  await worker.deliverJob("job_123", {
    deliverableUrl: "https://github.com/pr/123",
    summary: "Work completed",
    artifactHash: "sha256:abc123def",
  });
  const acceptRes = await poster.acceptJob("job_123", { rating: 5, review: "Excellent" });

  assert.equal(acceptRes.ok, true);
  assert.equal(calls.length, 3);
  assert.match(calls[0].url, /\/agent\/jobs\/job_123\/claim$/);
  assert.match(calls[1].url, /\/agent\/jobs\/job_123\/deliver$/);
  assert.match(calls[2].url, /\/agent\/jobs\/job_123\/accept$/);
});

test("AgentEconomyClient: getReputation returns trust score", async () => {
  const fetchFn = fakeFetch(() => ({
    body: {
      ok: true,
      wallet_id: "agent_alpha",
      reputation: {
        trust_score: 98,
        trust_level: "legendary",
        avg_rating: 4.9,
        completed_jobs: 24,
      },
    },
  }));
  const client = new AgentEconomyClient({ wallet: "agent_alpha", fetch: fetchFn });
  const rep = await client.getReputation();
  assert.equal(rep.ok, true);
  assert.equal(rep.reputation.trust_score, 98);
  assert.equal(rep.reputation.trust_level, "legendary");
});

test("AgentEconomyClient validates missing wallet and params", async () => {
  const client = new AgentEconomyClient({ fetch: fakeFetch(() => ({})) });
  await assert.rejects(() => client.postJob({ title: "Test", category: "code", rewardRtc: 10 }), ValidationError);
  await assert.rejects(() => client.claimJob("job_1"), ValidationError);
  await assert.rejects(() => client.getReputation(), ValidationError);
});
