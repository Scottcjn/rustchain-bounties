import { test } from "node:test";
import assert from "node:assert/strict";

import {
  StaticAnalysisJudge,
  canonicalJson,
  createJudge,
  generateJudgeKeyPair,
  verifyCanonical,
} from "./static-judge.mjs";

const fixedNow = () => new Date("2026-06-26T00:00:00.000Z");

// ---------------------------------------------------------------------------
// Canonical JSON tests
// ---------------------------------------------------------------------------

test("canonicalJson sorts nested object keys byte-for-byte", () => {
  assert.equal(
    canonicalJson({ z: 1, a: { b: 2, a: 1 }, list: [{ y: 2, x: 1 }] }),
    '{"a":{"a":1,"b":2},"list":[{"x":1,"y":2}],"z":1}',
  );
});

// ---------------------------------------------------------------------------
// Language detection tests
// ---------------------------------------------------------------------------

test("detects Python from explicit language field", () => {
  const judge = new StaticAnalysisJudge({ now: fixedNow });
  const result = judge.detectLanguage({ language: "python", code: "x = 1" });
  assert.equal(result, "python");
});

test("detects Python from .py filename", () => {
  const judge = new StaticAnalysisJudge({ now: fixedNow });
  const result = judge.detectLanguage({ filename: "main.py", code: "import os\nprint(os.getcwd())" });
  assert.equal(result, "python");
});

test("detects JavaScript from code patterns", () => {
  const judge = new StaticAnalysisJudge({ now: fixedNow });
  const result = judge.detectLanguage({ code: "const x = 1;\nconsole.log(x);" });
  assert.equal(result, "javascript");
});

test("detects Rust from code patterns", () => {
  const judge = new StaticAnalysisJudge({ now: fixedNow });
  const result = judge.detectLanguage({ code: "fn main() { println!(); }" });
  assert.equal(result, "rust");
});

// ---------------------------------------------------------------------------
// Passing verdict tests
// ---------------------------------------------------------------------------

test("judge passes well-formed Python with docstring and tests", () => {
  const judge = new StaticAnalysisJudge({ now: fixedNow });
  const code = `def add(a, b):
    """Add two numbers."""
    return a + b
`;
  const result = judge.judge({
    summary: "Implement addition function with proper documentation.",
    language: "python",
    code,
    tests: [{ name: "pytest", status: "passed" }],
  });

  assert.equal(result.verdict.passed, true);
  assert.deepEqual(result.verdict.reasons, []);
  assert.equal(result.verdict.judge_type, "static-analysis");
  assert.equal(result.verdict.language_detected, "python");
  assert.equal(judge.verify(result), true);
  assert.equal(result.signature_algorithm, "Ed25519");
  assert.ok(result.signature.length > 0);
  assert.ok(result.public_key_pem.length > 0);
});

test("judge passes well-formed JavaScript with JSDoc", () => {
  const judge = new StaticAnalysisJudge({ now: fixedNow });
  const code = `/**
 * Multiply two numbers.
 */
export function multiply(a, b) {
  return a * b;
}
`;
  const result = judge.judge({
    summary: "Implement multiplication with JSDoc comments.",
    language: "javascript",
    code,
    tests: [{ name: "node --test", status: "passed" }],
  });

  assert.equal(result.verdict.passed, true);
  assert.deepEqual(result.verdict.reasons, []);
  assert.equal(judge.verify(result), true);
});

// ---------------------------------------------------------------------------
// Failing verdict tests
// ---------------------------------------------------------------------------

test("judge rejects Python with syntax error", () => {
  const judge = createJudge({ now: fixedNow });
  const code = `def broken(
  # missing closing paren and body
`;
  const result = judge.judge({
    summary: "Submit broken Python code as proof of effort.",
    language: "python",
    code,
  });

  assert.equal(result.verdict.passed, false);
  assert.match(result.verdict.reasons.join("\n"), /syntax error/);
  assert.equal(judge.verify(result), true);
});

test("judge rejects code with excessive line length", () => {
  const judge = new StaticAnalysisJudge({ now: fixedNow, config: { maxLineLength: 80 } });
  const longLine = "a = '" + "x".repeat(100) + "'";
  const code = `${longLine}\n`;
  const result = judge.judge({
    summary: "This code has a very long line that exceeds limits.",
    language: "python",
    code,
  });

  assert.equal(result.verdict.passed, false);
  assert.match(result.verdict.reasons.join("\n"), /line/);
  assert.equal(judge.verify(result), true);
});

test("judge rejects code with trailing whitespace", () => {
  const judge = createJudge({ now: fixedNow });
  // Use explicit spaces/tabs at end of lines
  const code = "x = 1   \ny = 2\t\n";
  const result = judge.judge({
    summary: "Code has trailing whitespace on multiple lines.",
    language: "python",
    code,
  });

  assert.equal(result.verdict.passed, false);
  assert.match(result.verdict.reasons.join("\n"), /trailing whitespace/);
  assert.equal(judge.verify(result), true);
});

test("judge rejects code with missing docstrings", () => {
  const judge = createJudge({ now: fixedNow });
  const code = `def undocumented_function(x):
    return x + 1

class UndocumentedClass:
    pass
`;
  const result = judge.judge({
    summary: "Function and class without docstrings submitted for review.",
    language: "python",
    code,
  });

  assert.equal(result.verdict.passed, false);
  assert.match(result.verdict.reasons.join("\n"), /missing docstring|documentation/);
  assert.equal(judge.verify(result), true);
});

test("judge rejects code with unused imports", () => {
  const judge = createJudge({ now: fixedNow });
  const code = `import os
import sys
print(sys.argv)
`;
  const result = judge.judge({
    summary: "Code imports os but never uses it.",
    language: "python",
    code,
  });

  assert.equal(result.verdict.passed, false);
  assert.match(result.verdict.reasons.join("\n"), /unused import/);
  assert.equal(judge.verify(result), true);
});

test("judge rejects code with hardcoded secrets", () => {
  const judge = createJudge({ now: fixedNow });
  const code = `password = "super_secret_value_12345"
api_key = "AKIAIOSFODNN7EXAMPLE"
`;
  const result = judge.judge({
    summary: "Code contains hardcoded credentials for authentication.",
    language: "python",
    code,
  });

  assert.equal(result.verdict.passed, false);
  assert.match(result.verdict.reasons.join("\n"), /hardcoded secret/);
  assert.equal(judge.verify(result), true);
});

// ---------------------------------------------------------------------------
// Tampering detection test
// ---------------------------------------------------------------------------

test("signature verification fails after verdict tampering", () => {
  const keys = generateJudgeKeyPair();
  const judge = new StaticAnalysisJudge({ ...keys, now: fixedNow });
  const code = `def good():
    """A good function."""
    return True
`;
  const result = judge.judge({
    summary: "Submit clean code for static analysis review.",
    language: "python",
    code,
  });

  const { signature, ...payload } = result;
  assert.equal(verifyCanonical(result.public_key_pem, payload, signature), true);

  const tampered = structuredClone(payload);
  tampered.verdict.passed = false;
  tampered.verdict.reasons = ["tampered"];
  assert.equal(verifyCanonical(result.public_key_pem, tampered, signature), false);
});

// ---------------------------------------------------------------------------
// Request normalization test
// ---------------------------------------------------------------------------

test("judge handles diff field as code source", () => {
  const judge = createJudge({ now: fixedNow });
  const diff = `diff --git a/main.py b/main.py
--- a/main.py
+++ b/main.py
@@ -1,3 +1,6 @@
+def greet():
+    """Greet the user."""
+    print("Hello")
`;
  const result = judge.judge({
    summary: "Add greet function to main.py",
    language: "python",
    diff,
  });

  assert.equal(result.verdict.passed, true);
  assert.equal(result.verdict.language_detected, "python");
  assert.equal(judge.verify(result), true);
});

// ---------------------------------------------------------------------------
// Config override test
// ---------------------------------------------------------------------------

test("config can disable checks", () => {
  const judge = new StaticAnalysisJudge({
    now: fixedNow,
    config: {
      checkSecrets: false,
      checkUnusedImports: false,
      checkTrailingWhitespace: false,
    },
  });
  const code = `password = "not_really_checked"\nimport os\n`;
  const result = judge.judge({
    summary: "Check disabled judges do not flag known patterns.",
    language: "python",
    code,
  });

  // With secrets, unused_imports, trailing_whitespace disabled,
  // and no functions/classes to document, the code should pass.
  assert.equal(result.verdict.passed, true);
  assert.deepEqual(result.verdict.reasons, []);
});

test("config disables docstring requirement", () => {
  const judge = new StaticAnalysisJudge({
    now: fixedNow,
    config: {
      requireDocstrings: false,
      checkUnusedImports: false,
      checkSecrets: false,
      checkTrailingWhitespace: false,
    },
  });
  const code = `x = 1\nprint(x)\n`;
  const result = judge.judge({
    summary: "Simple assignment passes when checks are relaxed.",
    language: "python",
    code,
  });

  assert.equal(result.verdict.passed, true);
  assert.deepEqual(result.verdict.reasons, []);
});
