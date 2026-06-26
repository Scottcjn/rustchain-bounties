import crypto from "node:crypto";

export class StakingError extends Error {
  constructor(message, details = {}) {
    super(message);
    this.name = this.constructor.name;
    this.details = details;
  }
}

export class AuthError extends StakingError {}
export class GateUnavailableError extends StakingError {}
export class VerificationError extends StakingError {}

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

export function verifyEd25519Envelope(envelope, expectedPubkeyPem) {
  if (!expectedPubkeyPem) throw new VerificationError("missing pinned gate public key");
  if (envelope.public_key_pem && envelope.public_key_pem !== expectedPubkeyPem) {
    throw new VerificationError("verdict public key does not match configured gate key");
  }
  const { signature, ...payload } = envelope;
  if (!signature) throw new VerificationError("missing verdict signature");
  const ok = crypto.verify(
    null,
    Buffer.from(canonicalJson(payload)),
    expectedPubkeyPem,
    Buffer.from(signature, "base64"),
  );
  if (!ok) throw new VerificationError("invalid Ed25519 verdict signature");
  return true;
}

export function buildCanonicalStakeRequest(input) {
  if (!input || typeof input !== "object") {
    throw new StakingError("stake request must be an object");
  }
  if (!input.skill || typeof input.skill !== "string") {
    throw new StakingError("skill is required");
  }
  const bondRtc = Number(input.bondRtc ?? input.bond_rtc);
  if (!Number.isFinite(bondRtc) || bondRtc <= 0) {
    throw new StakingError("bondRtc must be a positive number");
  }
  return canonicalize({
    version: 1,
    skill: input.skill,
    bond_rtc: bondRtc,
    agent: input.agent || "anonymous-js-agent",
    nonce: input.nonce || crypto.randomUUID(),
    created_at: input.createdAt || new Date().toISOString(),
    metadata: input.metadata || {},
  });
}

export function verifyAttestation(attestation, { requestHash, verdictHash } = {}) {
  if (!attestation || typeof attestation !== "object") {
    throw new VerificationError("missing on-chain attestation");
  }
  if (!["confirmed", "finalized", "success"].includes(String(attestation.status || "").toLowerCase())) {
    throw new VerificationError("attestation is not confirmed");
  }
  if (requestHash && attestation.request_hash !== requestHash) {
    throw new VerificationError("attestation request hash mismatch");
  }
  if (verdictHash && attestation.verdict_hash !== verdictHash) {
    throw new VerificationError("attestation verdict hash mismatch");
  }
  if (!attestation.tx_id && !attestation.transaction_id) {
    throw new VerificationError("attestation missing transaction id");
  }
  return true;
}

export class ElyanStakingClient {
  constructor(options = {}) {
    this.gateUrl = String(options.gateUrl || "").replace(/\/$/, "");
    this.gatePath = options.gatePath || "/stake";
    this.apiKey = options.apiKey || "";
    this.gatePublicKeyPem = options.gatePublicKeyPem || "";
    this.fetch = options.fetch || globalThis.fetch;
    if (!this.fetch) throw new StakingError("fetch is not available; pass one in options");
  }

  async stake(input) {
    const request = buildCanonicalStakeRequest(input);
    const response = await this.submit(request);
    const verified = await this.verify(response, request);
    return {
      ok: true,
      request,
      request_hash: sha256Hex(canonicalJson(request)),
      response,
      verified,
    };
  }

  async submit(request) {
    if (!this.gateUrl) throw new StakingError("gateUrl is required");
    const url = `${this.gateUrl}${this.gatePath}`;
    let res;
    try {
      res = await this.fetch(url, {
        method: "POST",
        headers: {
          "content-type": "application/json",
          "accept": "application/json",
          ...(this.apiKey ? { "authorization": `Bearer ${this.apiKey}` } : {}),
        },
        body: canonicalJson(request),
      });
    } catch (error) {
      throw new GateUnavailableError("gate unavailable", { cause: error.message });
    }
    const text = await res.text();
    if (res.status === 401 || res.status === 403) {
      throw new AuthError("gate rejected API key", { status: res.status, body: text });
    }
    if (!res.ok) {
      throw new GateUnavailableError("gate returned unavailable status", { status: res.status, body: text });
    }

    let body;
    try {
      body = text ? JSON.parse(text) : {};
    } catch (error) {
      throw new GateUnavailableError("gate returned invalid JSON", { error: error.message, body: text });
    }
    return body;
  }

  async poll(attestationUrl, { timeoutMs = 30000, intervalMs = 1000 } = {}) {
    const deadline = Date.now() + timeoutMs;
    while (Date.now() <= deadline) {
      const res = await this.fetch(attestationUrl, { headers: { accept: "application/json" } });
      const body = JSON.parse(await res.text());
      if (body.status && String(body.status).toLowerCase() !== "pending") return body;
      await new Promise((resolve) => setTimeout(resolve, intervalMs));
    }
    throw new GateUnavailableError("attestation polling timed out");
  }

  async verify(response, request) {
    const envelope = response.verdict || response;
    verifyEd25519Envelope(envelope, this.gatePublicKeyPem);
    const requestHash = sha256Hex(canonicalJson(request));
    if (envelope.verdict?.request_hash !== requestHash) {
      throw new VerificationError("verdict request hash mismatch");
    }
    const verdictHash = sha256Hex(canonicalJson(envelope.verdict));
    const attestation = response.attestation || envelope.attestation;
    verifyAttestation(attestation, { requestHash, verdictHash });
    return {
      signature: true,
      attestation: true,
      request_hash: requestHash,
      verdict_hash: verdictHash,
    };
  }
}

export default ElyanStakingClient;
