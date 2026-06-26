import test from "node:test";
import assert from "node:assert/strict";
import crypto from "node:crypto";

import {
  createJudge,
  generateJudgeKeyPair,
  parseUnifiedDiff,
  verifyCanonical,
  canonicalJson,
} from "./diff-bounds-judge.mjs";

// Fixed key pair so verdicts are reproducible across instances.
const KEYS = generateJudgeKeyPair();
const fixedNow = () => new Date("2026-06-26T00:00:00.000Z");

function makeJudge(limits = {}) {
  return createJudge({ ...KEYS, limits, now: fixedNow });
}

const SMALL_CLEAN_DIFF = `diff --git a/src/util.js b/src/util.js
--- a/src/util.js
+++ b/src/util.js
@@ -1,3 +1,4 @@
 export function add(a, b) {
-  return a + b;
+  return Number(a) + Number(b);
 }
+export const VERSION = "1.1.0";
diff --git a/tests/util.test.js b/tests/util.test.js
--- a/tests/util.test.js
+++ b/tests/util.test.js
@@ -1,2 +1,4 @@
 import { add } from "../src/util.js";
+test("coerces strings", () => { expect(add("1", "2")).toBe(3); });
+test("adds numbers", () => { expect(add(1, 2)).toBe(3); });
`;

test("happy path: small, test-positive diff passes", () => {
  const v = makeJudge().judge({ summary: "harden add()", diff: SMALL_CLEAN_DIFF });
  assert.equal(v.verdict.passed, true, JSON.stringify(v.verdict.reasons));
  assert.equal(v.verdict.stats.files, 2);
  assert.ok(v.verdict.stats.added > 0);
});

test("signed verdict verifies, and tampering breaks verification", () => {
  const judge = makeJudge();
  const v = judge.judge({ summary: "x", diff: SMALL_CLEAN_DIFF });
  assert.equal(judge.verify(v), true);

  // Tamper with the verdict body -> signature no longer matches.
  const tampered = structuredClone(v);
  tampered.verdict.passed = !tampered.verdict.passed;
  assert.equal(judge.verify(tampered), false);
});

test("forged / mismatched public key fails verification (MITM / forgery)", () => {
  const judge = makeJudge();
  const v = judge.judge({ summary: "x", diff: SMALL_CLEAN_DIFF });
  const attacker = generateJudgeKeyPair();
  const { signature, ...payload } = { ...v, public_key_pem: attacker.publicKeyPem };
  // Verifying the real signature against the attacker's key must fail.
  assert.equal(verifyCanonical(attacker.publicKeyPem, payload, signature), false);
});

test("empty / gate-down request fails parseable check", () => {
  const v = makeJudge().judge({ summary: "nothing here" });
  assert.equal(v.verdict.passed, false);
  assert.ok(v.verdict.checks.find((c) => c.id === "parseable").passed === false);
});

test("oversized change exceeds size bounds", () => {
  const body = Array.from({ length: 50 }, (_, i) => `+line ${i}`).join("\n");
  const big = `diff --git a/src/big.js b/src/big.js
--- a/src/big.js
+++ b/src/big.js
@@ -0,0 +1,50 @@
${body}
`;
  const v = makeJudge({ maxAddedLines: 10 }).judge({ summary: "huge", diff: big });
  assert.equal(v.verdict.passed, false);
  assert.equal(v.verdict.checks.find((c) => c.id === "size").passed, false);
});

test("too many files exceeds size bounds", () => {
  const diff = Array.from({ length: 5 }, (_, i) =>
    `diff --git a/src/f${i}.js b/src/f${i}.js\n--- a/src/f${i}.js\n+++ b/src/f${i}.js\n@@ -0,0 +1 @@\n+const x = ${i};`,
  ).join("\n");
  const v = makeJudge({ maxFiles: 3 }).judge({ summary: "many", diff });
  assert.equal(v.verdict.checks.find((c) => c.id === "size").passed, false);
});

test("deleting a test file fails test_integrity", () => {
  const diff = `diff --git a/tests/core.test.js b/tests/core.test.js
deleted file mode 100644
--- a/tests/core.test.js
+++ /dev/null
@@ -1,2 +0,0 @@
-test("keeps working", () => { expect(1).toBe(1); });
-test("still works", () => { expect(2).toBe(2); });
`;
  const v = makeJudge().judge({ summary: "drop tests", diff });
  assert.equal(v.verdict.passed, false);
  assert.equal(v.verdict.checks.find((c) => c.id === "test_integrity").passed, false);
});

test("net removal of assertions fails test_integrity", () => {
  const diff = `diff --git a/tests/core.test.js b/tests/core.test.js
--- a/tests/core.test.js
+++ b/tests/core.test.js
@@ -1,4 +1,2 @@
 import { f } from "../src/f.js";
-test("a", () => { expect(f(1)).toBe(1); });
-test("b", () => { expect(f(2)).toBe(2); });
+// removed the failing tests to make the gate green
`;
  const v = makeJudge().judge({ summary: "gaming", diff });
  assert.equal(v.verdict.checks.find((c) => c.id === "test_integrity").passed, false);
});

test("editing a protected path fails, but allow_protected overrides", () => {
  const diff = `diff --git a/.github/workflows/ci.yml b/.github/workflows/ci.yml
--- a/.github/workflows/ci.yml
+++ b/.github/workflows/ci.yml
@@ -1,1 +1,1 @@
-      run: npm test
+      run: echo skip
`;
  const blocked = makeJudge().judge({ summary: "disable ci", diff });
  assert.equal(blocked.verdict.checks.find((c) => c.id === "protected_paths").passed, false);

  const allowed = makeJudge().judge({
    summary: "intended ci change",
    diff,
    allow_protected: [".github/workflows/ci.yml"],
  });
  assert.equal(allowed.verdict.checks.find((c) => c.id === "protected_paths").passed, true);
});

test("parseUnifiedDiff counts added/removed and flags new/deleted files", () => {
  const files = parseUnifiedDiff(SMALL_CLEAN_DIFF);
  assert.equal(files.length, 2);
  const util = files.find((f) => f.path === "src/util.js");
  assert.equal(util.added, 2);
  assert.equal(util.removed, 1);
});

test("canonical JSON sorts keys deterministically", () => {
  assert.equal(canonicalJson({ b: 1, a: 2 }), canonicalJson({ a: 2, b: 1 }));
  assert.equal(canonicalJson({ b: 1, a: 2 }), '{"a":2,"b":1}');
});

test("verdict signature is reproducible for identical input", () => {
  const a = createJudge({ ...KEYS, now: fixedNow }).judge({ summary: "x", diff: SMALL_CLEAN_DIFF });
  const b = createJudge({ ...KEYS, now: fixedNow }).judge({ summary: "x", diff: SMALL_CLEAN_DIFF });
  assert.equal(a.signature, b.signature);
  assert.equal(
    crypto.createHash("sha256").update(a.signature).digest("hex"),
    crypto.createHash("sha256").update(b.signature).digest("hex"),
  );
});

test("private-key-only construction derives a matching public key (documented flow)", () => {
  // Reproduces the JUDGE_PRIVATE_KEY_PEM-only server command: supply ONLY the
  // private key. The advertised public key must verify the signature.
  const judge = createJudge({ privateKeyPem: KEYS.privateKeyPem, now: fixedNow });
  const signed = judge.judge({ summary: "x", diff: SMALL_CLEAN_DIFF });

  // Advertised key is derived from the supplied private key, not a fresh one.
  const expectedPub = crypto
    .createPublicKey(KEYS.privateKeyPem)
    .export({ type: "spki", format: "pem" });
  assert.equal(signed.public_key_pem, expectedPub);

  // And the verdict actually verifies under the advertised key.
  const { signature, ...payload } = signed;
  assert.ok(verifyCanonical(signed.public_key_pem, payload, signature));
});

test("header-only diff (no @@ hunk) fails parseable", () => {
  const headerOnly = "diff --git a/src/x.js b/src/x.js\n";
  const v = makeJudge().judge({ summary: "noop", diff: headerOnly });
  assert.equal(v.verdict.passed, false);
  const parseable = v.verdict.checks.find((c) => c.id === "parseable");
  assert.equal(parseable.passed, false);
  assert.match(parseable.reason, /no `@@` hunk|header-only/);
});
