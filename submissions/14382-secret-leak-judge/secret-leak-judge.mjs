import crypto from "node:crypto";

// Secret-Leak Judge — a distinct, non-overlapping community gate for the open
// Judge interface (`judge(request) -> (passed, reasons)`).
//
// It judges ONLY one thing: whether a self-improvement diff *introduces
// hardcoded secrets / credentials* in its ADDED lines. An autonomous agent that
// edits its own code to "improve" is one slip away from committing a private
// key, an AWS secret, a vendor token or a password literal straight into the
// repository — and from there into history forever. This judge fails such a
// change fail-safe.
//
// It deliberately does NOT bound diff size (that is a diff-bounds judge), does
// NOT run the test suite (a test-runner judge), and does NOT do lint/AST
// analysis (a static-analysis judge). Those are separate, complementary gates.

export const JUDGE_ID = "secret-leak-judge-v1";

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
// Unified-diff parser (dependency-free). We only care about ADDED content:
// removing a secret is fine, introducing one is not.
// ---------------------------------------------------------------------------

export function parseAddedLines(diffText) {
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
      const match = line.match(/^diff --git a\/(.+?) b\/(.+)$/);
      const path = match ? match[2] : line.slice("diff --git ".length).trim();
      current = { path, hunks: 0, added: [] };
      continue;
    }
    if (!current) continue;

    if (line.startsWith("@@")) current.hunks += 1;
    else if (line.startsWith("rename to ")) current.path = line.slice("rename to ".length).trim();
    else if (line.startsWith("+++ ")) {
      const p = line.slice(4).trim();
      if (p.startsWith("b/")) current.path = p.slice(2);
    } else if (line.startsWith("+") && !line.startsWith("+++")) {
      // Added line. Track 1-based added-line ordinal within the file for
      // human-readable offender locations.
      current.added.push({ text: line.slice(1), n: current.added.length + 1 });
    }
  }
  push();
  return files;
}

// ---------------------------------------------------------------------------
// Secret detectors. Each rule is high-confidence and vendor-anchored or
// structurally specific to keep false positives low. Rules run only against
// ADDED lines.
// ---------------------------------------------------------------------------

// A value that is obviously a placeholder, not a live secret.
const PLACEHOLDER = /^(?:x{3,}|\.{3,}|\*{3,}|<[^>]*>|\$\{[^}]*\}|changeme|your[_-]?\w*|example|placeholder|dummy|test|fake|redacted|none|null|nil|todo|tbd|insert[_-]?\w*|replace[_-]?\w*|\{\{[^}]*\}\})$/i;

// A right-hand side that references an environment variable / config lookup
// rather than embedding a literal secret.
const ENV_REFERENCE =
  /(process\.env|os\.environ|getenv|System\.getenv|ENV\[|config\.|settings\.|secrets\.|vault\.|import\.meta\.env|\$\{?[A-Z][A-Z0-9_]*\}?)/;

export const SECRET_RULES = [
  {
    id: "private_key_block",
    label: "PEM private key material",
    // Header line of a PEM private key block of any flavour.
    test: (line) => /-----BEGIN (?:RSA |EC |OPENSSH |DSA |PGP |ENCRYPTED )?PRIVATE KEY-----/.test(line),
  },
  {
    id: "aws_access_key_id",
    label: "AWS access key id",
    test: (line) => /\b(?:AKIA|ASIA|AGPA|AIDA|AROA|ANPA)[0-9A-Z]{16}\b/.test(line),
  },
  {
    id: "github_token",
    label: "GitHub token",
    test: (line) => /\b(?:ghp|gho|ghu|ghs|ghr)_[0-9A-Za-z]{36,}\b|\bgithub_pat_[0-9A-Za-z_]{60,}\b/.test(line),
  },
  {
    id: "slack_token",
    label: "Slack token",
    test: (line) => /\bxox[baprs]-[0-9A-Za-z-]{10,}\b/.test(line),
  },
  {
    id: "google_api_key",
    label: "Google API key",
    test: (line) => /\bAIza[0-9A-Za-z_\-]{35}\b/.test(line),
  },
  {
    id: "stripe_secret_key",
    label: "Stripe secret/restricted key",
    test: (line) => /\b(?:sk|rk)_(?:live|test)_[0-9A-Za-z]{16,}\b/.test(line),
  },
  {
    id: "openai_key",
    label: "OpenAI / Anthropic-style API key",
    test: (line) => /\bsk-(?:proj-|ant-)?[0-9A-Za-z_\-]{20,}\b/.test(line),
  },
  {
    id: "basic_auth_url",
    label: "credentials embedded in URL",
    // scheme://user:password@host — flag only when the password is non-trivial
    // and not an env reference.
    test: (line) => {
      const m = line.match(/\b[a-z][a-z0-9+.\-]*:\/\/[^\s/:@]+:([^\s/@]{4,})@/i);
      if (!m) return false;
      const pw = m[1];
      return !PLACEHOLDER.test(pw) && !ENV_REFERENCE.test(pw);
    },
  },
  {
    id: "hardcoded_credential_assignment",
    label: "hardcoded credential assignment",
    // key = "literal" where key names a secret and the literal is long enough
    // to be a real secret, not a placeholder or an env lookup.
    test: (line) => {
      // Anchor on a non-alphanumeric (or start) and allow a prefix such as
      // `DB_`, `app-` etc. so `DB_PASSWORD`, `clientSecret` and friends match.
      // `\b` cannot be used as the boundary because `_` is itself a word char.
      const m = line.match(
        /(?:^|[^a-z0-9])[a-z0-9_-]*(?:password|passwd|pwd|secret(?:[_-]?key)?|api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|private[_-]?key|encryption[_-]?key)\s*[:=]\s*(['"])([^'"]{8,})\1/i,
      );
      if (!m) return false;
      const value = m[2];
      if (PLACEHOLDER.test(value)) return false;
      if (ENV_REFERENCE.test(value)) return false;
      // Pure references like "process.env.X" captured without quotes won't reach
      // here; quoted values that are themselves an env placeholder are excluded
      // above. Require at least one non-space, non-word-boundary character mix.
      return /[^\s]/.test(value);
    },
  },
];

// ---------------------------------------------------------------------------
// Judge
// ---------------------------------------------------------------------------

export class SecretLeakJudge {
  constructor({ privateKeyPem, publicKeyPem, rules = SECRET_RULES, now = () => new Date() } = {}) {
    if (privateKeyPem) {
      this.privateKeyPem = privateKeyPem;
      // Always derive the advertised key from the signing key so the documented
      // JUDGE_PRIVATE_KEY_PEM-only flow emits self-consistent verdicts.
      this.publicKeyPem = derivePublicKeyPem(privateKeyPem);
    } else if (publicKeyPem) {
      this.publicKeyPem = publicKeyPem;
      this.privateKeyPem = null;
    } else {
      const generated = generateJudgeKeyPair();
      this.privateKeyPem = generated.privateKeyPem;
      this.publicKeyPem = generated.publicKeyPem;
    }
    this.rules = rules;
    this.now = now;
  }

  judge(request) {
    const normalized = canonicalize(request || {});
    const diffText = normalized.diff || normalized.patch || "";
    const files = diffText ? parseAddedLines(diffText) : [];
    const allow = Array.isArray(normalized.allow_secrets) ? normalized.allow_secrets : [];

    const parseable = this.checkParseable(diffText, files);
    const scan = this.checkSecrets(files, allow);

    const checks = [parseable, scan];
    const passed = checks.every((check) => check.passed);
    const verdict = {
      judge_id: JUDGE_ID,
      interface: "Judge.judge(request)->(passed,reasons)",
      passed,
      reasons: checks.filter((check) => !check.passed).map((check) => check.reason),
      checks,
      findings: scan.findings,
      stats: {
        files: files.length,
        added_lines: files.reduce((n, f) => n + f.added.length, 0),
        secrets_found: scan.findings.length,
      },
      request_hash: sha256Hex(canonicalJson(normalized)),
      issued_at: this.now().toISOString(),
    };
    return this.signVerdict(verdict);
  }

  // --- individual checks ---------------------------------------------------

  checkParseable(diffText, files) {
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

  checkSecrets(files, allow) {
    const findings = [];
    for (const file of files) {
      for (const { text, n } of file.added) {
        for (const rule of this.rules) {
          if (!rule.test(text)) continue;
          const snippet = redact(text);
          // An allow-list entry whitelists an intended addition by matching the
          // file path or a substring of the (redacted) offending line.
          const whitelisted = allow.some(
            (a) => a === file.path || (typeof a === "string" && a.length >= 4 && text.includes(a)),
          );
          if (whitelisted) continue;
          findings.push({ rule: rule.id, label: rule.label, path: file.path, added_line: n, snippet });
        }
      }
    }
    const passed = findings.length === 0;
    return {
      id: "no_hardcoded_secrets",
      passed,
      findings,
      reason: passed
        ? "added lines introduce no hardcoded secrets"
        : `added lines introduce ${findings.length} hardcoded secret(s): ` +
          findings.map((f) => `${f.label} in ${f.path} (+line ${f.added_line})`).join("; "),
    };
  }

  // --- signing -------------------------------------------------------------

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
}

// Redact the middle of a long token so the verdict never echoes a live secret
// back to the caller while still leaving enough to locate it.
export function redact(line) {
  return line.replace(/([A-Za-z0-9_\-+/]{12,})/g, (m) =>
    m.length <= 8 ? m : `${m.slice(0, 4)}…${m.slice(-2)}[redacted ${m.length} chars]`,
  ).trim().slice(0, 200);
}

export function createJudge(options = {}) {
  return new SecretLeakJudge(options);
}
