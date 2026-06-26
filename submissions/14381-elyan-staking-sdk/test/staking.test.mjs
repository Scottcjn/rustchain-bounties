import { test } from "node:test";
import assert from "node:assert/strict";
import crypto from "node:crypto";

import {
  AuthError,
  ElyanStakingClient,
  GateUnavailableError,
  VerificationError,
  canonicalJson,
  sha256Hex,
} from "../src/index.js";

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

function textResponse(status, body) {
  return {
    ok: status >= 200 && status < 300,
    status,
    text: async () => body,
  };
}

function gateFetch({ privateKeyPem, publicKeyPem }) {
  const calls = [];
  const fetch = async (_url, init) => {
    calls.push({ init });
    const request = JSON.parse(init.body);
    const verdict = {
      passed: true,
      reasons: [],
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
    const attestation = {
      status: "confirmed",
      tx_id: "rtc-test-tx-1",
      request_hash: verdict.request_hash,
      verdict_hash: sha256Hex(canonicalJson(verdict)),
      block_height: 123,
    };
    return jsonResponse(200, { verdict: envelope, attestation });
  };
  fetch.calls = calls;
  return fetch;
}

test("canonical JSON sorts keys byte-for-byte", () => {
  assert.equal(canonicalJson({ b: 1, a: { d: 2, c: 1 } }), '{"a":{"c":1,"d":2},"b":1}');
});

test("happy path stakes, sends Bearer key, verifies signature and attestation", async () => {
  const keys = keyPair();
  const fetch = gateFetch(keys);
  const client = new ElyanStakingClient({
    gateUrl: "https://gate.example",
    apiKey: "test-key",
    gatePublicKeyPem: keys.publicKeyPem,
    fetch,
  });
  const result = await client.stake({
    skill: "self-improve:lint",
    bondRtc: 3,
    agent: "lxx197818",
    nonce: "fixed",
    createdAt: "2026-06-26T00:00:00.000Z",
  });

  assert.equal(result.ok, true);
  assert.equal(result.verified.signature, true);
  assert.equal(result.verified.attestation, true);
  assert.equal(fetch.calls[0].init.headers.authorization, "Bearer test-key");
});

test("bad API key maps to AuthError", async () => {
  const client = new ElyanStakingClient({
    gateUrl: "https://gate.example",
    apiKey: "bad",
    fetch: async () => jsonResponse(401, { error: "bad_api_key" }),
  });
  await assert.rejects(
    () => client.stake({ skill: "x", bondRtc: 1, nonce: "n", createdAt: "2026-06-26T00:00:00.000Z" }),
    AuthError,
  );
});

test("non-json auth errors still map to AuthError", async () => {
  const client = new ElyanStakingClient({
    gateUrl: "https://gate.example",
    apiKey: "bad",
    gatePublicKeyPem: keyPair().publicKeyPem,
    fetch: async () => textResponse(401, "unauthorized"),
  });
  await assert.rejects(
    () => client.stake({ skill: "x", bondRtc: 1, nonce: "n", createdAt: "2026-06-26T00:00:00.000Z" }),
    AuthError,
  );
});

test("non-json unavailable responses still map to GateUnavailableError", async () => {
  const client = new ElyanStakingClient({
    gateUrl: "https://gate.example",
    gatePublicKeyPem: keyPair().publicKeyPem,
    fetch: async () => textResponse(503, "service unavailable"),
  });
  await assert.rejects(
    () => client.stake({ skill: "x", bondRtc: 1, nonce: "n", createdAt: "2026-06-26T00:00:00.000Z" }),
    GateUnavailableError,
  );
});

test("forged or mismatched gate pubkey fails closed", async () => {
  const good = keyPair();
  const wrong = keyPair();
  const client = new ElyanStakingClient({
    gateUrl: "https://gate.example",
    gatePublicKeyPem: wrong.publicKeyPem,
    fetch: gateFetch(good),
  });
  await assert.rejects(
    () => client.stake({ skill: "x", bondRtc: 1, nonce: "n", createdAt: "2026-06-26T00:00:00.000Z" }),
    VerificationError,
  );
});

test("missing pinned gate pubkey fails closed", async () => {
  const keys = keyPair();
  const client = new ElyanStakingClient({
    gateUrl: "https://gate.example",
    fetch: gateFetch(keys),
  });
  await assert.rejects(
    () => client.stake({ skill: "x", bondRtc: 1, nonce: "n", createdAt: "2026-06-26T00:00:00.000Z" }),
    VerificationError,
  );
});

test("gate down returns unavailable fail-safe", async () => {
  const client = new ElyanStakingClient({
    gateUrl: "https://gate.example",
    fetch: async () => {
      throw new Error("ECONNREFUSED");
    },
  });
  await assert.rejects(
    () => client.stake({ skill: "x", bondRtc: 1, nonce: "n", createdAt: "2026-06-26T00:00:00.000Z" }),
    GateUnavailableError,
  );
});

test("attestation hash mismatch is rejected", async () => {
  const keys = keyPair();
  const fetch = async (_url, init) => {
    const request = JSON.parse(init.body);
    const verdict = {
      passed: true,
      reasons: [],
      request_hash: sha256Hex(canonicalJson(request)),
      issued_at: "2026-06-26T00:00:00.000Z",
    };
    const payload = {
      verdict,
      public_key_pem: keys.publicKeyPem,
      signature_algorithm: "Ed25519",
    };
    return jsonResponse(200, {
      verdict: { ...payload, signature: sign(keys.privateKeyPem, payload) },
      attestation: {
        status: "confirmed",
        tx_id: "rtc-test-tx-2",
        request_hash: "not-the-request",
        verdict_hash: sha256Hex(canonicalJson(verdict)),
      },
    });
  };
  const client = new ElyanStakingClient({
    gateUrl: "https://gate.example",
    gatePublicKeyPem: keys.publicKeyPem,
    fetch,
  });
  await assert.rejects(
    () => client.stake({ skill: "x", bondRtc: 1, nonce: "n", createdAt: "2026-06-26T00:00:00.000Z" }),
    VerificationError,
  );
});

test("verdict request hash replay is rejected", async () => {
  const keys = keyPair();
  const fetch = async (_url, init) => {
    const request = JSON.parse(init.body);
    const realRequestHash = sha256Hex(canonicalJson(request));
    const verdict = {
      passed: true,
      reasons: [],
      request_hash: "replayed-request",
      issued_at: "2026-06-26T00:00:00.000Z",
    };
    const payload = {
      verdict,
      public_key_pem: keys.publicKeyPem,
      signature_algorithm: "Ed25519",
    };
    return jsonResponse(200, {
      verdict: { ...payload, signature: sign(keys.privateKeyPem, payload) },
      attestation: {
        status: "confirmed",
        tx_id: "rtc-test-tx-3",
        request_hash: realRequestHash,
        verdict_hash: sha256Hex(canonicalJson(verdict)),
      },
    });
  };
  const client = new ElyanStakingClient({
    gateUrl: "https://gate.example",
    gatePublicKeyPem: keys.publicKeyPem,
    fetch,
  });
  await assert.rejects(
    () => client.stake({ skill: "x", bondRtc: 1, nonce: "n", createdAt: "2026-06-26T00:00:00.000Z" }),
    VerificationError,
  );
});
