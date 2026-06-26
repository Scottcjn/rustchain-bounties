import crypto from "node:crypto";

export const JUDGE_ID = "lxx197818-community-policy-judge-v1";

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

function asText(request) {
  return [
    request.summary,
    request.diff,
    request.patch,
    request.readme,
    request.evidence,
    request.artifact_url,
    request.repository,
    JSON.stringify(request.tests || []),
    JSON.stringify(request.metadata || {}),
  ]
    .filter(Boolean)
    .join("\n");
}

function hasAny(text, patterns) {
  return patterns.some((pattern) => pattern.test(text));
}

export class CommunityPolicyJudge {
  constructor({ privateKeyPem, publicKeyPem, now = () => new Date() } = {}) {
    if ((privateKeyPem && !publicKeyPem) || (!privateKeyPem && publicKeyPem)) {
      throw new Error("JUDGE_PRIVATE_KEY_PEM and JUDGE_PUBLIC_KEY_PEM must be provided together");
    }
    const generated = privateKeyPem && publicKeyPem ? null : generateJudgeKeyPair();
    this.privateKeyPem = privateKeyPem || generated.privateKeyPem;
    this.publicKeyPem = publicKeyPem || generated.publicKeyPem;
    this.now = now;
  }

  judge(request) {
    const normalized = canonicalize(request || {});
    const text = asText(normalized);
    const checks = [
      this.checkShape(normalized),
      this.checkEvidence(normalized, text),
      this.checkSafety(text),
      this.checkScope(normalized, text),
    ];
    const passed = checks.every((check) => check.passed);
    const verdict = {
      judge_id: JUDGE_ID,
      interface: "Judge.judge(request)->(passed,reasons)",
      passed,
      reasons: checks.filter((check) => !check.passed).map((check) => check.reason),
      checks,
      request_hash: sha256Hex(canonicalJson(normalized)),
      issued_at: this.now().toISOString(),
    };
    return verdict;
  }

  judgeSigned(request) {
    return this.signVerdict(this.judge(request));
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

  verify(signedVerdict, expectedPublicKeyPem = this.publicKeyPem) {
    if (!expectedPublicKeyPem) throw new Error("missing pinned judge public key");
    if (signedVerdict.public_key_pem && signedVerdict.public_key_pem !== expectedPublicKeyPem) {
      return false;
    }
    const { signature, ...payload } = signedVerdict;
    return verifyCanonical(expectedPublicKeyPem, payload, signature);
  }

  checkShape(request) {
    const hasSummary = typeof request.summary === "string" && request.summary.trim().length >= 12;
    const hasArtifact =
      typeof request.diff === "string" ||
      typeof request.patch === "string" ||
      typeof request.artifact_url === "string" ||
      typeof request.repository === "string";
    return {
      id: "shape",
      passed: hasSummary && hasArtifact,
      reason: hasSummary && hasArtifact
        ? "request includes a reviewable summary and artifact"
        : "request must include a non-trivial summary and a diff/patch/repository artifact",
    };
  }

  checkEvidence(request, text) {
    const tests = Array.isArray(request.tests) ? request.tests : [];
    const passedTest = tests.some((test) => {
      const status = String(test.status || test.result || "").toLowerCase();
      return status === "pass" || status === "passed" || status === "success";
    });
    const textualProof = /\b(test|pytest|npm test|cargo test|go test|node --test)\b/i.test(text)
      && /\b(pass|passed|success|green|0 failed)\b/i.test(text);
    const passed = passedTest || textualProof;
    return {
      id: "evidence",
      passed,
      reason: passed
        ? "request contains test or validation evidence"
        : "request needs at least one passing test or validation artifact",
    };
  }

  checkSafety(text) {
    const dangerous = [
      /BEGIN (RSA|OPENSSH|EC|DSA) PRIVATE KEY/i,
      /sk-[a-z0-9_-]{20,}/i,
      /process\.env\.[A-Z0-9_]*(SECRET|TOKEN|PRIVATE|KEY)/i,
      /rejectUnauthorized\s*:\s*false/i,
      /curl\s+[^|]*\|\s*(sh|bash)/i,
      /rm\s+-rf\s+(\/|\$HOME|~)/i,
    ];
    const passed = !hasAny(text, dangerous);
    return {
      id: "safety",
      passed,
      reason: passed
        ? "no obvious secret leakage or unsafe execution pattern detected"
        : "request contains a secret-like or unsafe execution pattern",
    };
  }

  checkScope(request, text) {
    const scope = String(request.scope || request.category || "").toLowerCase();
    const declared = ["code", "test", "policy", "documentation", "integration"].includes(scope);
    const contextual = /\b(fix|feature|test|policy|integration|docs|readme|sdk|gate)\b/i.test(text);
    const passed = declared || contextual;
    return {
      id: "scope",
      passed,
      reason: passed
        ? "request declares or implies a bounded improvement scope"
        : "request needs a bounded improvement scope",
    };
  }
}

export function createJudge(options = {}) {
  return new CommunityPolicyJudge(options);
}
