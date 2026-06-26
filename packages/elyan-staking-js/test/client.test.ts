// SPDX-License-Identifier: MIT
import { test } from "node:test";
import assert from "node:assert/strict";
import { generateKeyPairSync, sign as nodeSign } from "node:crypto";
import { StakingClient } from "../src/client.js";
import {
  AttestationError,
  GateUnavailableError,
  SignatureError,
  UnauthorizedError,
} from "../src/errors.js";
import { canonicalBytes, bytesToHex } from "../src/index.js";

function makeKeypair() {
  const { publicKey, privateKey } = generateKeyPairSync("ed25519");
  // Extract raw 32-byte public key from SPKI DER: last 32 bytes.
  const spki = publicKey.export({ format: "der", type: "spki" });
  const rawPub = spki.subarray(spki.length - 32);
  return { privateKey, publicKeyHex: bytesToHex(rawPub) };
}

function signPayload(privateKey: any, payload: unknown): string {
  const sig = nodeSign(null, canonicalBytes(payload), privateKey);
  return bytesToHex(sig);
}

function mockFetch(handler: (url: string, init: RequestInit) => Response | Promise<Response>) {
  return async (input: any, init: any) => handler(String(input), init);
}

test("happy path: submit → poll → verify returns trusted payload", async () => {
  const { privateKey, publicKeyHex } = makeKeypair();
  const payload = { agentId: "a1", amount: 10, verdict: "accepted" };
  const signature = signPayload(privateKey, payload);
  const verdict = { payload, signature, attestation: { txHash: "0xdead", chain: "rtc" } };

  let step = 0;
  const client = new StakingClient({
    gateUrl: "https://gate.test",
    apiKey: "k",
    gatePublicKey: publicKeyHex,
    fetchImpl: mockFetch(async (url) => {
      if (url.endsWith("/v1/stake") && step === 0) {
        step = 1;
        return new Response(JSON.stringify({ jobId: "j1", acceptedAt: "now" }), { status: 200 });
      }
      if (url.endsWith("/v1/stake/j1")) {
        return new Response(JSON.stringify({ jobId: "j1", status: "ready", verdict }), {
          status: 200,
        });
      }
      return new Response("nope", { status: 404 });
    }) as any,
  });

  const result = await client.stake({ agentId: "a1", amount: 10, purpose: "train" });
  assert.equal(result.attestationTxHash, "0xdead");
  assert.deepEqual(result.payload, payload);
});

test("bad API key → UnauthorizedError", async () => {
  const { publicKeyHex } = makeKeypair();
  const client = new StakingClient({
    gateUrl: "https://gate.test",
    apiKey: "bad",
    gatePublicKey: publicKeyHex,
    fetchImpl: mockFetch(async () => new Response("nope", { status: 401 })) as any,
  });
  await assert.rejects(client.submit({ agentId: "a", amount: 1, purpose: "p" }), UnauthorizedError);
});

test("forged signature (mismatched pubkey) → SignatureError", async () => {
  const keyA = makeKeypair();
  const keyB = makeKeypair();
  const payload = { agentId: "a1", amount: 10 };
  const signature = signPayload(keyA.privateKey, payload); // signed by A
  const verdict = { payload, signature, attestation: { txHash: "0xabc" } };

  const client = new StakingClient({
    gateUrl: "https://gate.test",
    apiKey: "k",
    gatePublicKey: keyB.publicKeyHex, // verified against B → must fail
    fetchImpl: mockFetch(async () => new Response("", { status: 200 })) as any,
  });
  await assert.rejects(client.verify(verdict as any), SignatureError);
});

test("tampered payload → SignatureError", async () => {
  const { privateKey, publicKeyHex } = makeKeypair();
  const payload = { agentId: "a1", amount: 10 };
  const signature = signPayload(privateKey, payload);
  const tampered = { payload: { agentId: "a1", amount: 999 }, signature, attestation: { txHash: "0xabc" } };

  const client = new StakingClient({
    gateUrl: "https://gate.test",
    apiKey: "k",
    gatePublicKey: publicKeyHex,
    fetchImpl: mockFetch(async () => new Response("", { status: 200 })) as any,
  });
  await assert.rejects(client.verify(tampered as any), SignatureError);
});

test("gate down (network error) → GateUnavailableError", async () => {
  const { publicKeyHex } = makeKeypair();
  const client = new StakingClient({
    gateUrl: "https://gate.test",
    apiKey: "k",
    gatePublicKey: publicKeyHex,
    fetchImpl: mockFetch(async () => {
      throw new Error("ECONNREFUSED");
    }) as any,
  });
  await assert.rejects(
    client.submit({ agentId: "a", amount: 1, purpose: "p" }),
    GateUnavailableError,
  );
});

test("gate 503 → GateUnavailableError", async () => {
  const { publicKeyHex } = makeKeypair();
  const client = new StakingClient({
    gateUrl: "https://gate.test",
    apiKey: "k",
    gatePublicKey: publicKeyHex,
    fetchImpl: mockFetch(async () => new Response("", { status: 503 })) as any,
  });
  await assert.rejects(
    client.submit({ agentId: "a", amount: 1, purpose: "p" }),
    GateUnavailableError,
  );
});

test("failed attestation → AttestationError", async () => {
  const { privateKey, publicKeyHex } = makeKeypair();
  const payload = { agentId: "a1" };
  const verdict = {
    payload,
    signature: signPayload(privateKey, payload),
    attestation: { txHash: "" }, // empty → default verifier rejects
  };
  const client = new StakingClient({
    gateUrl: "https://gate.test",
    apiKey: "k",
    gatePublicKey: publicKeyHex,
    fetchImpl: mockFetch(async () => new Response("", { status: 200 })) as any,
  });
  await assert.rejects(client.verify(verdict as any), AttestationError);
});
