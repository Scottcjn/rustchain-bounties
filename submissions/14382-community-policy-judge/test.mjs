import { test } from "node:test";
import assert from "node:assert/strict";

import {
  CommunityPolicyJudge,
  canonicalJson,
  createJudge,
  generateJudgeKeyPair,
  verifyCanonical,
} from "./policy-judge.mjs";

const fixedNow = () => new Date("2026-06-26T00:00:00.000Z");

test("canonicalJson sorts nested object keys byte-for-byte", () => {
  assert.equal(
    canonicalJson({ z: 1, a: { b: 2, a: 1 }, list: [{ y: 2, x: 1 }] }),
    '{"a":{"a":1,"b":2},"list":[{"x":1,"y":2}],"z":1}',
  );
});

test("judge passes a bounded request with test evidence", () => {
  const judge = new CommunityPolicyJudge({ now: fixedNow });
  const verdict = judge.judge({
    summary: "Add typed validation around the gate request parser.",
    scope: "code",
    diff: "diff --git a/gate.js b/gate.js\n+ validate payload before submit",
    tests: [{ name: "node --test", status: "passed" }],
  });

  assert.equal(verdict.passed, true);
  assert.deepEqual(verdict.reasons, []);

  const signed = judge.judgeSigned({
    summary: "Add typed validation around the gate request parser.",
    scope: "code",
    diff: "diff --git a/gate.js b/gate.js\n+ validate payload before submit",
    tests: [{ name: "node --test", status: "passed" }],
  });
  assert.equal(judge.verify(signed), true);
  assert.equal(signed.signature_algorithm, "Ed25519");
});

test("judge rejects missing validation evidence", () => {
  const judge = createJudge({ now: fixedNow });
  const verdict = judge.judge({
    summary: "Add a code change with no proof.",
    scope: "code",
    diff: "+ unverified change",
  });

  assert.equal(verdict.passed, false);
  assert.match(verdict.reasons.join("\n"), /validation artifact/);
});

test("judge rejects obvious secret-like payloads", () => {
  const judge = createJudge({ now: fixedNow });
  const verdict = judge.judge({
    summary: "Patch includes an unsafe secret use.",
    scope: "code",
    diff: "const token = process.env.PRIVATE_KEY; fetch(url, { rejectUnauthorized: false })",
    tests: [{ name: "node --test", status: "passed" }],
  });

  assert.equal(verdict.passed, false);
  assert.match(verdict.reasons.join("\n"), /unsafe/);
});

test("safety scan includes repository, artifact URL, and tests fields", () => {
  const judge = createJudge({ now: fixedNow });
  const verdict = judge.judge({
    summary: "Submit a repository artifact with validation evidence.",
    scope: "code",
    repository: "https://example.test/repo?token=sk-leakedsecret000000000000",
    artifact_url: "https://example.test/artifact",
    tests: [{ name: "node --test", status: "passed" }],
  });

  assert.equal(verdict.passed, false);
  assert.match(verdict.reasons.join("\n"), /unsafe/);
});

test("signature verification fails after verdict tampering", () => {
  const keys = generateJudgeKeyPair();
  const judge = new CommunityPolicyJudge({ ...keys, now: fixedNow });
  const result = judge.judgeSigned({
    summary: "Add README guidance for the gate.",
    scope: "documentation",
    repository: "Scottcjn/rustchain-bounties",
    evidence: "markdownlint passed",
  });

  const { signature, ...payload } = result;
  assert.equal(verifyCanonical(result.public_key_pem, payload, signature), true);

  const tampered = structuredClone(payload);
  tampered.verdict.passed = true;
  assert.equal(verifyCanonical(result.public_key_pem, tampered, signature), false);
});

test("verification uses the pinned judge key instead of the envelope key", () => {
  const good = generateJudgeKeyPair();
  const wrong = generateJudgeKeyPair();
  const judge = new CommunityPolicyJudge({ ...good, now: fixedNow });
  const result = judge.judgeSigned({
    summary: "Add README guidance for the gate.",
    scope: "documentation",
    repository: "Scottcjn/rustchain-bounties",
    evidence: "markdownlint passed",
  });

  result.public_key_pem = wrong.publicKeyPem;
  assert.equal(judge.verify(result), false);
});

test("partial key configuration fails instead of generating a new pair", () => {
  const keys = generateJudgeKeyPair();
  assert.throws(
    () => new CommunityPolicyJudge({ privateKeyPem: keys.privateKeyPem }),
    /must be provided together/,
  );
  assert.throws(
    () => new CommunityPolicyJudge({ publicKeyPem: keys.publicKeyPem }),
    /must be provided together/,
  );
});
