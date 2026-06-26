import { test } from "node:test";
import assert from "node:assert/strict";
import crypto from "node:crypto";

import {
  ElyanStakeAndAcquireTool,
  StakeAndAcquireClient,
  canonicalJson,
  createLangChainTool,
  sha256Hex,
} from "../src/index.js";
import { handleMcpMessage } from "../src/mcp-server.mjs";

function keyPair() {
  const { privateKey, publicKey } = crypto.generateKeyPairSync("ed25519");
  return {
    privateKeyPem: privateKey.export({ type: "pkcs8", format: "pem" }),
    publicKeyPem: publicKey.export({ type: "spki", format: "pem" }),
  };
}

function sign(privateKeyPem, payload) {
  return crypto.sign(null, Buffer.from(canonicalJson(payload)), privateKeyPem).toString("base64");
}

function jsonResponse(status, body) {
  return {
    ok: status >= 200 && status < 300,
    status,
    text: async () => JSON.stringify(body),
  };
}

function gateFetch({ privateKeyPem, publicKeyPem, passed = true }) {
  return async (_url, init) => {
    const request = JSON.parse(init.body);
    const verdict = {
      passed,
      reasons: passed ? [] : ["skill_not_available"],
      request_hash: sha256Hex(canonicalJson(request)),
      issued_at: "2026-06-26T00:00:00.000Z",
    };
    const envelopePayload = {
      verdict,
      public_key_pem: publicKeyPem,
      signature_algorithm: "Ed25519",
    };
    const envelope = {
      ...envelopePayload,
      signature: sign(privateKeyPem, envelopePayload),
    };
    return jsonResponse(200, {
      verdict: envelope,
      attestation: {
        status: "confirmed",
        tx_id: "rtc-test-tx",
        request_hash: verdict.request_hash,
        verdict_hash: sha256Hex(canonicalJson(verdict)),
      },
    });
  };
}

test("client returns verified result and signed attestation on success", async () => {
  const keys = keyPair();
  const client = new StakeAndAcquireClient({
    gateUrl: "https://gate.example",
    gatePublicKeyPem: keys.publicKeyPem,
    fetch: gateFetch(keys),
  });

  const result = await client.stakeAndAcquire({
    skill: "self-improve:tests",
    bond_rtc: 2,
    agent: "lxx197818",
    nonce: "fixed",
    createdAt: "2026-06-26T00:00:00.000Z",
  });

  assert.equal(result.ok, true);
  assert.equal(result.refunded, false);
  assert.equal(result.verification.signature, true);
  assert.equal(result.verification.attestation, true);
});

test("gate unavailable is surfaced as refunded fail-safe", async () => {
  const client = new StakeAndAcquireClient({
    gateUrl: "https://gate.example",
    fetch: async () => jsonResponse(503, { error: "down" }),
  });
  const result = await client.stakeAndAcquire({ skill: "x", bond_rtc: 1, nonce: "n" });

  assert.equal(result.ok, false);
  assert.equal(result.refunded, true);
  assert.equal(result.refund_reason, "gate_unavailable");
});

test("gate denial is surfaced as refunded fail-safe", async () => {
  const keys = keyPair();
  const client = new StakeAndAcquireClient({
    gateUrl: "https://gate.example",
    gatePublicKeyPem: keys.publicKeyPem,
    fetch: gateFetch({ ...keys, passed: false }),
  });
  const result = await client.stakeAndAcquire({ skill: "not-ready", bond_rtc: 1, nonce: "n" });

  assert.equal(result.ok, false);
  assert.equal(result.refunded, true);
  assert.equal(result.refund_reason, "gate_denied");
});

test("invalid signature fails closed with refunded verification_failed", async () => {
  const good = keyPair();
  const wrong = keyPair();
  const client = new StakeAndAcquireClient({
    gateUrl: "https://gate.example",
    gatePublicKeyPem: wrong.publicKeyPem,
    fetch: gateFetch(good),
  });
  const result = await client.stakeAndAcquire({ skill: "x", bond_rtc: 1, nonce: "n" });

  assert.equal(result.ok, false);
  assert.equal(result.refunded, true);
  assert.equal(result.refund_reason, "verification_failed");
});

test("LangChain-compatible fallback tool invokes the same client", async () => {
  const keys = keyPair();
  const tool = await createLangChainTool({
    gateUrl: "https://gate.example",
    gatePublicKeyPem: keys.publicKeyPem,
    fetch: gateFetch(keys),
  });

  assert.ok(tool instanceof ElyanStakeAndAcquireTool || tool.name === "stake_and_acquire");
  const text = await tool.call({ skill: "self-improve:lint", bond_rtc: 1, nonce: "n" });
  const result = JSON.parse(text);
  assert.equal(result.ok, true);
});

test("MCP server lists and calls stake_and_acquire", async () => {
  const keys = keyPair();
  const client = new StakeAndAcquireClient({
    gateUrl: "https://gate.example",
    gatePublicKeyPem: keys.publicKeyPem,
    fetch: gateFetch(keys),
  });

  const listed = await handleMcpMessage({ jsonrpc: "2.0", id: 1, method: "tools/list" }, { client });
  assert.equal(listed.result.tools[0].name, "stake_and_acquire");

  const called = await handleMcpMessage({
    jsonrpc: "2.0",
    id: 2,
    method: "tools/call",
    params: {
      name: "stake_and_acquire",
      arguments: { skill: "self-improve:review", bond_rtc: 3, nonce: "n" },
    },
  }, { client });

  const result = JSON.parse(called.result.content[0].text);
  assert.equal(result.ok, true);
  assert.equal(result.refunded, false);
});
