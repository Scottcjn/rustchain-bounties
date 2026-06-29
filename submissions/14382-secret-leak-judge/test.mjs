import test from "node:test";
import assert from "node:assert/strict";
import crypto from "node:crypto";

import {
  createJudge,
  generateJudgeKeyPair,
  parseAddedLines,
  verifyCanonical,
  canonicalJson,
  redact,
} from "./secret-leak-judge.mjs";

// Fixed key pair so verdicts are reproducible across instances.
const KEYS = generateJudgeKeyPair();
const fixedNow = () => new Date("2026-06-27T00:00:00.000Z");

function makeJudge() {
  return createJudge({ ...KEYS, now: fixedNow });
}

// A clean change that reads its secret from the environment — must pass.
const CLEAN_DIFF = `diff --git a/src/client.js b/src/client.js
--- a/src/client.js
+++ b/src/client.js
@@ -1,3 +1,5 @@
 export function makeClient() {
-  return connect();
+  const apiKey = process.env.API_KEY;
+  return connect({ apiKey });
 }
+export const VERSION = "1.2.0";
`;

test("happy path: env-sourced secret passes", () => {
  const v = makeJudge().judge({ summary: "wire api key from env", diff: CLEAN_DIFF });
  assert.equal(v.verdict.passed, true, JSON.stringify(v.verdict.reasons));
  assert.equal(v.verdict.stats.secrets_found, 0);
});

test("PEM private key in added lines fails", () => {
  const diff = `diff --git a/config/key.pem b/config/key.pem
new file mode 100644
--- /dev/null
+++ b/config/key.pem
@@ -0,0 +1,2 @@
+-----BEGIN OPENSSH PRIVATE KEY-----
+b3BlbnNzaC1rZXktdjEAAAAABG5vbmUAAAAEbm9uZQ
`;
  const v = makeJudge().judge({ summary: "add key", diff });
  assert.equal(v.verdict.passed, false);
  assert.ok(v.verdict.findings.some((f) => f.rule === "private_key_block"));
});

test("AWS access key id in added lines fails", () => {
  const diff = `diff --git a/deploy.sh b/deploy.sh
--- a/deploy.sh
+++ b/deploy.sh
@@ -1,1 +1,2 @@
 #!/bin/sh
+export AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
`;
  const v = makeJudge().judge({ summary: "deploy", diff });
  assert.equal(v.verdict.passed, false);
  assert.ok(v.verdict.findings.some((f) => f.rule === "aws_access_key_id"));
});

test("GitHub token in added lines fails", () => {
  const diff = `diff --git a/ci/env b/ci/env
--- a/ci/env
+++ b/ci/env
@@ -1,1 +1,2 @@
 NAME=ci
+GITHUB_TOKEN=ghp_0123456789abcdefABCDEF0123456789abcd
`;
  const v = makeJudge().judge({ summary: "ci", diff });
  assert.equal(v.verdict.passed, false);
  assert.ok(v.verdict.findings.some((f) => f.rule === "github_token"));
});

test("hardcoded password literal fails", () => {
  const diff = `diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1,1 +1,2 @@
 import db
+DB_PASSWORD = "S3cretSummer2026!"
`;
  const v = makeJudge().judge({ summary: "db creds", diff });
  assert.equal(v.verdict.passed, false);
  assert.ok(v.verdict.findings.some((f) => f.rule === "hardcoded_credential_assignment"));
});

test("credentials embedded in a URL fail", () => {
  const diff = `diff --git a/fetch.js b/fetch.js
--- a/fetch.js
+++ b/fetch.js
@@ -1,1 +1,2 @@
 // fetch
+const u = "https://admin:Hunter2Pass@internal.example.com/db";
`;
  const v = makeJudge().judge({ summary: "fetch", diff });
  assert.equal(v.verdict.passed, false);
  assert.ok(v.verdict.findings.some((f) => f.rule === "basic_auth_url"));
});

test("placeholder and env-reference assignments do NOT false-positive", () => {
  const diff = `diff --git a/conf.py b/conf.py
--- a/conf.py
+++ b/conf.py
@@ -1,1 +1,5 @@
 import os
+PASSWORD = "changeme"
+API_KEY = "<your-api-key>"
+SECRET = "\${VAULT_SECRET}"
+TOKEN = "xxxxxxxx"
`;
  const v = makeJudge().judge({ summary: "config template", diff });
  assert.equal(v.verdict.passed, true, JSON.stringify(v.verdict.findings));
});

test("removing a secret (a `-` line) does not fail — only added lines are scanned", () => {
  const diff = `diff --git a/app.py b/app.py
--- a/app.py
+++ b/app.py
@@ -1,2 +1,2 @@
 import db
-DB_PASSWORD = "S3cretSummer2026!"
+DB_PASSWORD = os.environ["DB_PASSWORD"]
`;
  const v = makeJudge().judge({ summary: "stop hardcoding", diff });
  assert.equal(v.verdict.passed, true, JSON.stringify(v.verdict.findings));
});

test("allow_secrets whitelists an intended addition (e.g. a public test fixture)", () => {
  const diff = `diff --git a/tests/fixtures/sample.pem b/tests/fixtures/sample.pem
new file mode 100644
--- /dev/null
+++ b/tests/fixtures/sample.pem
@@ -0,0 +1,1 @@
+-----BEGIN PRIVATE KEY-----
`;
  const blocked = makeJudge().judge({ summary: "fixture", diff });
  assert.equal(blocked.verdict.passed, false);

  const allowed = makeJudge().judge({
    summary: "intended test fixture",
    diff,
    allow_secrets: ["tests/fixtures/sample.pem"],
  });
  assert.equal(allowed.verdict.passed, true, JSON.stringify(allowed.verdict.findings));
});

test("findings never echo the raw secret back (redaction)", () => {
  const diff = `diff --git a/ci/env b/ci/env
--- a/ci/env
+++ b/ci/env
@@ -1,1 +1,2 @@
 NAME=ci
+GITHUB_TOKEN=ghp_0123456789abcdefABCDEF0123456789abcd
`;
  const v = makeJudge().judge({ summary: "ci", diff });
  const snippet = v.verdict.findings[0].snippet;
  assert.ok(!snippet.includes("ghp_0123456789abcdefABCDEF0123456789abcd"));
  assert.match(snippet, /redacted/);
});

test("signed verdict verifies, and tampering breaks verification", () => {
  const judge = makeJudge();
  const v = judge.judge({ summary: "x", diff: CLEAN_DIFF });
  assert.equal(judge.verify(v), true);

  const tampered = structuredClone(v);
  tampered.verdict.passed = !tampered.verdict.passed;
  assert.equal(judge.verify(tampered), false);
});

test("forged / mismatched public key fails verification (MITM / forgery)", () => {
  const judge = makeJudge();
  const v = judge.judge({ summary: "x", diff: CLEAN_DIFF });
  const attacker = generateJudgeKeyPair();
  const { signature, ...payload } = { ...v, public_key_pem: attacker.publicKeyPem };
  assert.equal(verifyCanonical(attacker.publicKeyPem, payload, signature), false);
});

test("empty / gate-down request fails parseable check", () => {
  const v = makeJudge().judge({ summary: "nothing here" });
  assert.equal(v.verdict.passed, false);
  assert.equal(v.verdict.checks.find((c) => c.id === "parseable").passed, false);
});

test("header-only diff (no @@ hunk) fails parseable", () => {
  const v = makeJudge().judge({ summary: "noop", diff: "diff --git a/x b/x\n" });
  assert.equal(v.verdict.passed, false);
  const parseable = v.verdict.checks.find((c) => c.id === "parseable");
  assert.equal(parseable.passed, false);
});

test("private-key-only construction derives a matching public key (documented flow)", () => {
  const judge = createJudge({ privateKeyPem: KEYS.privateKeyPem, now: fixedNow });
  const signed = judge.judge({ summary: "x", diff: CLEAN_DIFF });
  const expectedPub = crypto
    .createPublicKey(KEYS.privateKeyPem)
    .export({ type: "spki", format: "pem" });
  assert.equal(signed.public_key_pem, expectedPub);
  const { signature, ...payload } = signed;
  assert.ok(verifyCanonical(signed.public_key_pem, payload, signature));
});

test("verdict signature is reproducible for identical input", () => {
  const a = createJudge({ ...KEYS, now: fixedNow }).judge({ summary: "x", diff: CLEAN_DIFF });
  const b = createJudge({ ...KEYS, now: fixedNow }).judge({ summary: "x", diff: CLEAN_DIFF });
  assert.equal(a.signature, b.signature);
});

test("canonical JSON sorts keys deterministically", () => {
  assert.equal(canonicalJson({ b: 1, a: 2 }), '{"a":2,"b":1}');
});

test("parseAddedLines collects only added content with file paths", () => {
  const files = parseAddedLines(CLEAN_DIFF);
  assert.equal(files.length, 1);
  assert.equal(files[0].path, "src/client.js");
  assert.ok(files[0].added.length >= 2);
});

test("redact shortens long tokens", () => {
  const out = redact("token=ghp_0123456789abcdefABCDEF0123456789abcd");
  assert.match(out, /redacted/);
});
