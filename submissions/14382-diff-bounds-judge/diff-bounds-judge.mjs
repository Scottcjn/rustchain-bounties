import crypto from "node:crypto";

// Diff-Bounds Judge — a distinct, non-overlapping community gate for the open
// Judge interface (`judge(request) -> (passed, reasons)`).
//
// It judges ONLY the *geometry and containment* of a self-improvement diff:
//   - the change stays within size bounds (files / added / removed lines),
//   - it does not delete test files or strip test assertions (anti-gaming),
//   - it does not silently edit protected paths (CI config, lockfiles),
//   - the diff is well-formed and parseable.
//
// It deliberately does NOT run tests (that is a test-runner judge), does NOT do
// lint/AST analysis (a static-analysis judge), and does NOT apply a generic
// content policy (a policy judge). Those are separate, complementary gates.

export const JUDGE_ID = "diff-bounds-judge-v1";

// ---------------------------------------------------------------------------
// Canonical JSON + Ed25519 envelope — byte-for-byte compatible with the open
// SDK and the reference gate server (sorted keys, no whitespace).
// ---------------------------------------------------------------------------

export function canonicalize(value) {
  if (Array.isArray(value)) {
    return value.map(canonicalize);
  }
  if (value && typeof value === "object" && value.constructor === Object) {
    return Object.fromEntries(
      Object.keys(value)
        .sort()
        .map((key) => [key, canonicalize(value[key])]),
    );
  }
  return value;
}

export function canonicalJson(value) {
  return JSON.stringify(canonicalize(value));
}

export function sha256Hex(value) {
  return crypto.createHash("sha256").update(value).digest("hex");
}

export function generateJudgeKeyPair() {
  const { privateKey, publicKey } = crypto.generateKeyPairSync("ed25519");
  return {
    privateKeyPem: privateKey.export({ type: "pkcs8", format: "pem" }),
    publicKeyPem: publicKey.export({ type: "spki", format: "pem" }),
  };
}

// Derive the spki public-key PEM from an Ed25519 private-key PEM so that a judge
// configured with only JUDGE_PRIVATE_KEY_PEM advertises the public key that
// actually verifies its signatures (no fresh/unrelated key).
export function derivePublicKeyPem(privateKeyPem) {
  return crypto
    .createPublicKey(privateKeyPem)
    .export({ type: "spki", format: "pem" });
}

export function signCanonical(privateKeyPem, payload) {
  return crypto
    .sign(null, Buffer.from(canonicalJson(payload)), privateKeyPem)
    .toString("base64");
}

export function verifyCanonical(publicKeyPem, payload, signatureBase64) {
  return crypto.verify(
    null,
    Buffer.from(canonicalJson(payload)),
    publicKeyPem,
    Buffer.from(signatureBase64, "base64"),
  );
}

// ---------------------------------------------------------------------------
// Unified-diff parser (dependency-free). Returns per-file stats.
// ---------------------------------------------------------------------------

function isTestPath(path) {
  return (
    /(^|\/)(tests?|spec|__tests__)\//i.test(path) ||
    /\.(test|spec)\.[a-z0-9]+$/i.test(path) ||
    /(^|\/)test_[^/]+\.py$/i.test(path) ||
    /_test\.[a-z0-9]+$/i.test(path)
  );
}

const ASSERTION_PATTERN =
  /\b(assert\w*|expect|should|t\.(?:is|ok|deepEqual|throws)|self\.assert\w*)\b|\bit\s*\(|\btest\s*\(/;

export function parseUnifiedDiff(diffText) {
  const files = [];
  let current = null;
  const lines = String(diffText).split(/\r?\n/);

  const push = () => {
    if (current) files.push(current);
    current = null;
  };

  for (const line of lines) {
    if (line.startsWith("diff --git ")) {
      push();
      // diff --git a/path b/path
      const match = line.match(/^diff --git a\/(.+?) b\/(.+)$/);
      const path = match ? match[2] : line.slice("diff --git ".length).trim();
      current = {
        path,
        added: 0,
        removed: 0,
        isNew: false,
        isDeleted: false,
        addedAssertions: 0,
        removedAssertions: 0,
        hunks: 0,
      };
      continue;
    }
    if (!current) continue;

    if (line.startsWith("@@")) current.hunks += 1;
    else if (line.startsWith("new file mode")) current.isNew = true;
    else if (line.startsWith("deleted file mode")) current.isDeleted = true;
    else if (line.startsWith("rename to ")) current.path = line.slice("rename to ".length).trim();
    else if (line.startsWith("+++ ")) {
      const p = line.slice(4).trim();
      if (p === "/dev/null") current.isDeleted = true;
      else if (p.startsWith("b/")) current.path = p.slice(2);
    } else if (line.startsWith("--- ")) {
      const p = line.slice(4).trim();
      if (p === "/dev/null") current.isNew = true;
    } else if (line.startsWith("+") && !line.startsWith("+++")) {
      current.added += 1;
      if (ASSERTION_PATTERN.test(line.slice(1))) current.addedAssertions += 1;
    } else if (line.startsWith("-") && !line.startsWith("---")) {
      current.removed += 1;
      if (ASSERTION_PATTERN.test(line.slice(1))) current.removedAssertions += 1;
    }
  }
  push();
  return files;
}

// ---------------------------------------------------------------------------
// Judge
// ---------------------------------------------------------------------------

export const DEFAULT_LIMITS = {
  maxFiles: 25,
  maxAddedLines: 800,
  maxRemovedLines: 600,
  // Paths an autonomous self-improvement may not silently rewrite.
  protectedPaths: [
    /(^|\/)\.github\//i,
    /(^|\/)package-lock\.json$/i,
    /(^|\/)yarn\.lock$/i,
    /(^|\/)pnpm-lock\.yaml$/i,
    /(^|\/)Cargo\.lock$/i,
    /(^|\/)poetry\.lock$/i,
  ],
};

export class DiffBoundsJudge {
  constructor({ privateKeyPem, publicKeyPem, limits = {}, now = () => new Date() } = {}) {
    if (privateKeyPem) {
      this.privateKeyPem = privateKeyPem;
      // Always derive the advertised key from the signing key so the documented
      // JUDGE_PRIVATE_KEY_PEM-only flow emits self-consistent verdicts. An
      // explicit publicKeyPem is honoured only when no private key is supplied
      // (verify-only construction).
      this.publicKeyPem = derivePublicKeyPem(privateKeyPem);
    } else if (publicKeyPem) {
      this.publicKeyPem = publicKeyPem;
      this.privateKeyPem = null;
    } else {
      const generated = generateJudgeKeyPair();
      this.privateKeyPem = generated.privateKeyPem;
      this.publicKeyPem = generated.publicKeyPem;
    }
    this.limits = {
      ...DEFAULT_LIMITS,
      ...limits,
      protectedPaths: limits.protectedPaths || DEFAULT_LIMITS.protectedPaths,
    };
    this.now = now;
  }

  judge(request) {
    const normalized = canonicalize(request || {});
    const diffText = normalized.diff || normalized.patch || "";
    const files = diffText ? parseUnifiedDiff(diffText) : [];

    const checks = [
      this.checkParseable(diffText, files),
      this.checkSize(files),
      this.checkTestIntegrity(files),
      this.checkProtectedPaths(files, normalized),
    ];

    const passed = checks.every((check) => check.passed);
    const verdict = {
      judge_id: JUDGE_ID,
      interface: "Judge.judge(request)->(passed,reasons)",
      passed,
      reasons: checks.filter((check) => !check.passed).map((check) => check.reason),
      checks,
      stats: this.summarize(files),
      limits: {
        maxFiles: this.limits.maxFiles,
        maxAddedLines: this.limits.maxAddedLines,
        maxRemovedLines: this.limits.maxRemovedLines,
      },
      request_hash: sha256Hex(canonicalJson(normalized)),
      issued_at: this.now().toISOString(),
    };
    return this.signVerdict(verdict);
  }

  summarize(files) {
    return {
      files: files.length,
      added: files.reduce((n, f) => n + f.added, 0),
      removed: files.reduce((n, f) => n + f.removed, 0),
    };
  }

  signVerdict(verdict) {
    const envelope = {
      verdict: canonicalize(verdict),
      signature_algorithm: "Ed25519",
      public_key_pem: this.publicKeyPem,
    };
    return {
      ...envelope,
      signature: signCanonical(this.privateKeyPem, envelope),
    };
  }

  verify(signedVerdict) {
    const { signature, ...payload } = signedVerdict;
    return verifyCanonical(signedVerdict.public_key_pem, payload, signature);
  }

  // --- individual checks ---------------------------------------------------

  checkParseable(diffText, files) {
    // A well-formed unified diff needs a file header AND at least one real hunk
    // (`@@`). Header-only/malformed input (a bare `diff --git` line) must NOT
    // pass the parseable guard, otherwise it would slip through every size /
    // integrity bound with zero scrutinised content.
    const hasHunk = files.some((f) => f.hunks > 0);
    const passed =
      typeof diffText === "string" &&
      diffText.trim().length > 0 &&
      files.length > 0 &&
      hasHunk;
    let reason;
    if (passed) reason = "request carries a well-formed unified diff";
    else if (files.length > 0 && !hasHunk)
      reason = "diff has file headers but no `@@` hunk — header-only/malformed patch rejected";
    else
      reason = "request must include a non-empty unified `diff`/`patch` (no parseable file headers found)";
    return { id: "parseable", passed, reason };
  }

  checkSize(files) {
    const { added, removed, files: n } = this.summarize(files);
    const within =
      n <= this.limits.maxFiles &&
      added <= this.limits.maxAddedLines &&
      removed <= this.limits.maxRemovedLines;
    return {
      id: "size",
      passed: within,
      reason: within
        ? `change is within bounds (${n} files, +${added}/-${removed})`
        : `change exceeds bounds: ${n}/${this.limits.maxFiles} files, ` +
          `+${added}/${this.limits.maxAddedLines} added, -${removed}/${this.limits.maxRemovedLines} removed`,
    };
  }

  checkTestIntegrity(files) {
    const offenders = [];
    let netAssertions = 0;
    for (const f of files) {
      if (!isTestPath(f.path)) continue;
      if (f.isDeleted) offenders.push(`deletes test file ${f.path}`);
      netAssertions += f.addedAssertions - f.removedAssertions;
    }
    if (netAssertions < 0) {
      offenders.push(`net removal of ${-netAssertions} test assertion(s)`);
    }
    const passed = offenders.length === 0;
    return {
      id: "test_integrity",
      passed,
      reason: passed
        ? "diff does not delete tests or strip assertions"
        : `diff weakens the test suite: ${offenders.join("; ")}`,
    };
  }

  checkProtectedPaths(files, request) {
    const allow = Array.isArray(request.allow_protected) ? request.allow_protected : [];
    const offenders = files
      .map((f) => f.path)
      .filter((p) => this.limits.protectedPaths.some((re) => re.test(p)))
      .filter((p) => !allow.includes(p));
    const passed = offenders.length === 0;
    return {
      id: "protected_paths",
      passed,
      reason: passed
        ? "diff does not touch protected paths"
        : `diff edits protected paths without allow_protected: ${offenders.join(", ")}`,
    };
  }
}

export function createJudge(options = {}) {
  return new DiffBoundsJudge(options);
}
