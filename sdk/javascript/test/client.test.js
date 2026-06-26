/**
 * Tests for RustChainClient using Node's built-in test runner.
 *
 * No third-party deps. We inject a fake `fetch` so tests are hermetic and
 * never hit the live node — but the response shapes used are the same ones
 * documented by the Python SDK (`sdk/python/rustchain_sdk/client.py`) and
 * confirmed against `curl https://50.28.86.131/health`.
 */

import { test } from "node:test";
import assert from "node:assert/strict";

import {
  RustChainClient,
  APIError,
  ConnectionError,
  ValidationError,
  TimeoutError,
  DEFAULT_NODE_URL,
} from "../src/index.js";

// ── tiny helper: build a fake fetch ────────────────────────────────

/**
 * @param {(url: string, init: RequestInit) => { status?: number, body?: any }} handler
 */
function fakeFetch(handler) {
  const calls = [];
  const fn = async (url, init) => {
    calls.push({ url, init });
    const { status = 200, body = null } = handler(url, init) ?? {};
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

// ── construction ──────────────────────────────────────────────────

test("uses the real RustChain node URL by default", () => {
  const c = new RustChainClient({ fetch: fakeFetch(() => ({ body: {} })) });
  assert.equal(c.baseUrl, DEFAULT_NODE_URL);
  assert.equal(DEFAULT_NODE_URL, "https://50.28.86.131"); // pin
});

test("strips a trailing slash from baseUrl", () => {
  const c = new RustChainClient({
    baseUrl: "https://example.test/",
    fetch: fakeFetch(() => ({ body: {} })),
  });
  assert.equal(c.baseUrl, "https://example.test");
});

test("throws if no global fetch and none injected", () => {
  const originalFetch = globalThis.fetch;
  // @ts-expect-error
  delete globalThis.fetch;
  try {
    assert.throws(() => new RustChainClient(), /global fetch is not available/);
  } finally {
    globalThis.fetch = originalFetch;
  }
});

// ── health / epoch / miners ────────────────────────────────────────

test("health() hits GET /health and returns parsed JSON", async () => {
  const fetchFn = fakeFetch(() => ({
    body: { ok: true, version: "2.2.1-rip200", uptime_s: 77, db_rw: true },
  }));
  const c = new RustChainClient({ fetch: fetchFn });
  const res = await c.health();
  assert.equal(res.ok, true);
  assert.equal(res.version, "2.2.1-rip200");
  assert.equal(fetchFn.calls.length, 1);
  assert.match(fetchFn.calls[0].url, /\/health$/);
  assert.equal(fetchFn.calls[0].init.method, "GET");
});

test("getEpoch() returns {epoch, slot}", async () => {
  const c = new RustChainClient({
    fetch: fakeFetch(() => ({ body: { epoch: 1847, slot: 42 } })),
  });
  const res = await c.getEpoch();
  assert.equal(res.epoch, 1847);
  assert.equal(res.slot, 42);
});

test("getMiners() returns an array", async () => {
  const c = new RustChainClient({
    fetch: fakeFetch(() => ({ body: [{ id: "m1" }, { id: "m2" }] })),
  });
  const res = await c.getMiners();
  assert.equal(Array.isArray(res), true);
  assert.equal(res.length, 2);
});

// ── balance / history ──────────────────────────────────────────────

test("getBalance() encodes the wallet as miner_id query param", async () => {
  const fetchFn = fakeFetch(() => ({ body: { balance: 42.5 } }));
  const c = new RustChainClient({ fetch: fetchFn });
  await c.getBalance("zxy0314-work");
  const url = new URL(fetchFn.calls[0].url);
  assert.equal(url.pathname, "/wallet/balance");
  assert.equal(url.searchParams.get("miner_id"), "zxy0314-work");
});

test("getBalance() validates the wallet arg", async () => {
  const c = new RustChainClient({ fetch: fakeFetch(() => ({ body: {} })) });
  await assert.rejects(() => c.getBalance(""), ValidationError);
  await assert.rejects(() => c.getBalance(null), ValidationError);
  await assert.rejects(() => c.getBalance(123), ValidationError);
});

test("getWalletHistory() validates limit range", async () => {
  const c = new RustChainClient({ fetch: fakeFetch(() => ({ body: [] })) });
  await assert.rejects(() => c.getWalletHistory("x", 0), ValidationError);
  await assert.rejects(() => c.getWalletHistory("x", 501), ValidationError);
  await assert.rejects(() => c.getWalletHistory("x", 1.5), ValidationError);
});

// ── epoch rewards / explorer / attest ──────────────────────────────

test("getEpochRewards() rejects negative / non-integer epoch", async () => {
  const c = new RustChainClient({ fetch: fakeFetch(() => ({ body: {} })) });
  await assert.rejects(() => c.getEpochRewards(-1), ValidationError);
  await assert.rejects(() => c.getEpochRewards(1.5), ValidationError);
});

test("attestChallenge() POSTs the miner public key", async () => {
  const fetchFn = fakeFetch(() => ({ body: { nonce: "abc", expires_at: 1 } }));
  const c = new RustChainClient({ fetch: fetchFn });
  await c.attestChallenge("pk-deadbeef");
  const call = fetchFn.calls[0];
  assert.equal(call.init.method, "POST");
  assert.deepEqual(JSON.parse(call.init.body), {
    miner_public_key: "pk-deadbeef",
  });
});

// ── errors ────────────────────────────────────────────────────────

test("non-2xx response raises APIError with status + body", async () => {
  const c = new RustChainClient({
    fetch: fakeFetch(() => ({ status: 404, body: { message: "not found" } })),
  });
  await assert.rejects(
    () => c.getBalance("ghost"),
    (err) => {
      assert.ok(err instanceof APIError);
      assert.equal(err.status, 404);
      assert.equal(err.body.message, "not found");
      assert.match(err.message, /404/);
      return true;
    },
  );
});

test("network failure raises ConnectionError", async () => {
  const c = new RustChainClient({
    fetch: async () => {
      throw new TypeError("fetch failed");
    },
  });
  await assert.rejects(() => c.health(), ConnectionError);
});

test("aborted request raises TimeoutError", async () => {
  const c = new RustChainClient({
    timeoutMs: 1,
    fetch: async (_url, init) => {
      // Simulate the abort-controller path: throw an AbortError on signal.
      await new Promise((resolve, reject) => {
        init.signal.addEventListener("abort", () => {
          const err = new Error("aborted");
          err.name = "AbortError";
          reject(err);
        });
      });
    },
  });
  await assert.rejects(() => c.health(), TimeoutError);
});

// ── error class hierarchy ──────────────────────────────────────────

test("all SDK errors extend RustChainError", async () => {
  const { RustChainError } = await import("../src/errors.js");
  assert.ok(new APIError("x") instanceof RustChainError);
  assert.ok(new ConnectionError("x") instanceof RustChainError);
  assert.ok(new ValidationError("x") instanceof RustChainError);
  assert.ok(new TimeoutError("x") instanceof RustChainError);
});
