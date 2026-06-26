import crypto from "node:crypto";

export class StakeToolError extends Error {
  constructor(message, details = {}) {
    super(message);
    this.name = this.constructor.name;
    this.details = details;
  }
}

export class StakeInputError extends StakeToolError {}
export class StakeVerificationError extends StakeToolError {}

export function canonicalize(value) {
  if (Array.isArray(value)) return value.map(canonicalize);
  if (value && typeof value === "object" && value.constructor === Object) {
    return Object.fromEntries(
      Object.keys(value).sort().map((key) => [key, canonicalize(value[key])]),
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

export function normalizeStakeInput(input = {}) {
  const skill = String(input.skill || "").trim();
  if (!skill) throw new StakeInputError("skill is required");

  const bondRtc = Number(input.bondRtc ?? input.bond_rtc);
  if (!Number.isFinite(bondRtc) || bondRtc <= 0) {
    throw new StakeInputError("bond_rtc must be a positive number");
  }

  return canonicalize({
    version: 1,
    skill,
    bond_rtc: bondRtc,
    agent: input.agent || process.env.ELYAN_AGENT_ID || "langchain-mcp-agent",
    nonce: input.nonce || crypto.randomUUID(),
    created_at: input.createdAt || input.created_at || new Date().toISOString(),
    metadata: input.metadata || {},
  });
}

export function verifyEd25519Envelope(envelope, expectedPublicKeyPem = "") {
  if (!envelope || typeof envelope !== "object") {
    throw new StakeVerificationError("missing signed verdict envelope");
  }

  const publicKeyPem = expectedPublicKeyPem || envelope.public_key_pem;
  if (!publicKeyPem) throw new StakeVerificationError("missing gate public key");
  if (expectedPublicKeyPem && envelope.public_key_pem && envelope.public_key_pem !== expectedPublicKeyPem) {
    throw new StakeVerificationError("verdict public key does not match configured key");
  }

  const { signature, ...payload } = envelope;
  if (!signature) throw new StakeVerificationError("missing verdict signature");

  const ok = crypto.verify(
    null,
    Buffer.from(canonicalJson(payload)),
    publicKeyPem,
    Buffer.from(signature, "base64"),
  );

  if (!ok) throw new StakeVerificationError("invalid verdict signature");
  return true;
}

export function verifyAttestation(attestation, { requestHash, verdictHash } = {}) {
  if (!attestation || typeof attestation !== "object") {
    throw new StakeVerificationError("missing on-chain attestation");
  }

  const status = String(attestation.status || "").toLowerCase();
  if (!["confirmed", "finalized", "success"].includes(status)) {
    throw new StakeVerificationError("attestation is not confirmed");
  }
  if (requestHash && attestation.request_hash !== requestHash) {
    throw new StakeVerificationError("attestation request hash mismatch");
  }
  if (verdictHash && attestation.verdict_hash !== verdictHash) {
    throw new StakeVerificationError("attestation verdict hash mismatch");
  }
  if (!attestation.tx_id && !attestation.transaction_id) {
    throw new StakeVerificationError("attestation missing transaction id");
  }

  return true;
}

export function verifiedResult(response, request, gatePublicKeyPem = "") {
  const envelope = response.verdict || response;
  verifyEd25519Envelope(envelope, gatePublicKeyPem);

  const requestHash = sha256Hex(canonicalJson(request));
  const verdictPayload = envelope.verdict || {};
  const verdictHash = sha256Hex(canonicalJson(verdictPayload));
  const attestation = response.attestation || envelope.attestation;

  verifyAttestation(attestation, { requestHash, verdictHash });

  return {
    ok: true,
    refunded: false,
    request,
    request_hash: requestHash,
    verdict: envelope,
    attestation,
    verification: {
      signature: true,
      attestation: true,
      verdict_hash: verdictHash,
    },
  };
}

export function refundedResult(request, reason, details = {}) {
  return {
    ok: false,
    refunded: true,
    refund_reason: reason,
    request,
    request_hash: sha256Hex(canonicalJson(request)),
    details,
  };
}

export class StakeAndAcquireClient {
  constructor(options = {}) {
    this.gateUrl = String(options.gateUrl || process.env.ELYAN_GATE_URL || "").replace(/\/$/, "");
    this.gatePath = options.gatePath || process.env.ELYAN_GATE_PATH || "/stake";
    this.apiKey = options.apiKey || process.env.ELYAN_GATE_API_KEY || "";
    this.gatePublicKeyPem = options.gatePublicKeyPem || process.env.ELYAN_GATE_PUBLIC_KEY_PEM || "";
    this.fetch = options.fetch || globalThis.fetch;
    if (!this.fetch) throw new StakeInputError("fetch is not available; pass fetch in options");
  }

  async stakeAndAcquire(input) {
    const request = normalizeStakeInput(input);
    if (!this.gateUrl) return refundedResult(request, "gate_not_configured");

    let response;
    try {
      response = await this.submit(request);
    } catch (error) {
      return refundedResult(request, "gate_unavailable", {
        error: error.message,
        status: error.details?.status,
        body: error.details?.body,
      });
    }

    const passed = response?.verdict?.verdict?.passed ?? response?.verdict?.passed;
    if (passed === false) {
      return refundedResult(request, "gate_denied", {
        verdict: response.verdict,
        attestation: response.attestation,
      });
    }

    try {
      return verifiedResult(response, request, this.gatePublicKeyPem);
    } catch (error) {
      return refundedResult(request, "verification_failed", {
        error: error.message,
      });
    }
  }

  async submit(request) {
    const res = await this.fetch(`${this.gateUrl}${this.gatePath}`, {
      method: "POST",
      headers: {
        "accept": "application/json",
        "content-type": "application/json",
        ...(this.apiKey ? { "authorization": `Bearer ${this.apiKey}` } : {}),
      },
      body: canonicalJson(request),
    });

    const text = await res.text();
    const body = text ? JSON.parse(text) : {};
    if (!res.ok) {
      throw new StakeToolError("gate returned non-success status", {
        status: res.status,
        body,
      });
    }
    return body;
  }
}
