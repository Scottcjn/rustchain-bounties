// SPDX-License-Identifier: MIT
import { canonicalize } from "./canonical.js";
import { verifyEd25519, hexToBytes } from "./verify.js";
import {
  AttestationError,
  GateUnavailableError,
  SignatureError,
  StakingError,
  UnauthorizedError,
} from "./errors.js";

export interface StakingClientOptions {
  /** Base URL of the staking gate, e.g. "https://gate.elyan.example". */
  gateUrl: string;
  /** Bearer API key issued by the gate. */
  apiKey: string;
  /** Gate's Ed25519 public key (hex, 32 bytes / 64 hex chars). */
  gatePublicKey: string;
  /** Optional fetch override (defaults to global fetch). */
  fetchImpl?: typeof fetch;
  /** Optional on-chain attestation verifier; defaults to a no-op that requires a non-empty txHash. */
  attestationVerifier?: AttestationVerifier;
  /** Request timeout in ms (default 15000). */
  timeoutMs?: number;
}

export interface StakeRequest {
  agentId: string;
  amount: string | number;
  purpose: string;
  nonce?: string;
  [k: string]: unknown;
}

export interface SubmitResponse {
  jobId: string;
  acceptedAt: string;
}

export type JobStatus = "pending" | "ready" | "rejected";

export interface PollResponse {
  jobId: string;
  status: JobStatus;
  verdict?: SignedVerdict;
}

export interface SignedVerdict {
  /** The verdict payload — canonicalized and signed by the gate. */
  payload: Record<string, unknown>;
  /** Ed25519 signature over canonical(payload), hex-encoded (128 chars). */
  signature: string;
  /** On-chain attestation tx hash (chain-specific). */
  attestation: { txHash: string; chain?: string };
}

export interface VerifiedVerdict {
  payload: Record<string, unknown>;
  attestationTxHash: string;
}

export interface AttestationVerifier {
  verify(verdict: SignedVerdict): Promise<boolean>;
}

const defaultAttestationVerifier: AttestationVerifier = {
  async verify(v) {
    return typeof v.attestation?.txHash === "string" && v.attestation.txHash.length > 0;
  },
};

export class StakingClient {
  private readonly gateUrl: string;
  private readonly apiKey: string;
  private readonly gatePubKey: Uint8Array;
  private readonly fetchImpl: typeof fetch;
  private readonly attestation: AttestationVerifier;
  private readonly timeoutMs: number;

  constructor(opts: StakingClientOptions) {
    if (!opts.gateUrl) throw new StakingError("gateUrl required");
    if (!opts.apiKey) throw new StakingError("apiKey required");
    if (!opts.gatePublicKey) throw new StakingError("gatePublicKey required");
    this.gateUrl = opts.gateUrl.replace(/\/+$/, "");
    this.apiKey = opts.apiKey;
    this.gatePubKey = hexToBytes(opts.gatePublicKey);
    if (this.gatePubKey.length !== 32) {
      throw new StakingError("gatePublicKey must be 32 bytes (64 hex chars)");
    }
    this.fetchImpl = opts.fetchImpl ?? globalThis.fetch;
    this.attestation = opts.attestationVerifier ?? defaultAttestationVerifier;
    this.timeoutMs = opts.timeoutMs ?? 15000;
  }

  /** High-level helper: submit → poll → verify. */
  async stake(req: StakeRequest): Promise<VerifiedVerdict> {
    const { jobId } = await this.submit(req);
    let polled: PollResponse;
    // Bounded poll loop.
    const deadline = Date.now() + this.timeoutMs;
    // eslint-disable-next-line no-constant-condition
    while (true) {
      polled = await this.poll(jobId);
      if (polled.status !== "pending") break;
      if (Date.now() > deadline) {
        throw new GateUnavailableError("timed out waiting for verdict");
      }
      await new Promise((r) => setTimeout(r, 500));
    }
    if (polled.status === "rejected" || !polled.verdict) {
      throw new StakingError("stake rejected by gate");
    }
    return this.verify(polled.verdict);
  }

  /** POST /v1/stake — submit a stake request, get a jobId. */
  async submit(req: StakeRequest): Promise<SubmitResponse> {
    const body = canonicalize(req);
    const res = await this.call("/v1/stake", "POST", body);
    const json = (await res.json()) as SubmitResponse;
    if (!json?.jobId) throw new StakingError("malformed submit response");
    return json;
  }

  /** GET /v1/stake/:jobId — poll for verdict. */
  async poll(jobId: string): Promise<PollResponse> {
    const res = await this.call(`/v1/stake/${encodeURIComponent(jobId)}`, "GET");
    const json = (await res.json()) as PollResponse;
    if (!json?.jobId || !json?.status) {
      throw new StakingError("malformed poll response");
    }
    return json;
  }

  /**
   * Verify a signed verdict fail-safe: checks Ed25519 signature first, then on-chain
   * attestation. Throws on any failure; returns the trusted payload on success.
   */
  async verify(verdict: SignedVerdict): Promise<VerifiedVerdict> {
    if (!verdict?.signature || !verdict?.payload) {
      throw new SignatureError("verdict missing signature or payload");
    }
    let sigBytes: Uint8Array;
    try {
      sigBytes = hexToBytes(verdict.signature);
    } catch {
      throw new SignatureError("verdict signature is not valid hex");
    }
    const ok = verifyEd25519(verdict.payload, sigBytes, this.gatePubKey);
    if (!ok) throw new SignatureError();

    const attOk = await this.attestation.verify(verdict);
    if (!attOk) throw new AttestationError();

    return {
      payload: verdict.payload,
      attestationTxHash: verdict.attestation.txHash,
    };
  }

  private async call(path: string, method: "GET" | "POST", body?: string): Promise<Response> {
    const url = this.gateUrl + path;
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeoutMs);
    let res: Response;
    try {
      res = await this.fetchImpl(url, {
        method,
        headers: {
          Authorization: `Bearer ${this.apiKey}`,
          "Content-Type": "application/json",
          Accept: "application/json",
        },
        body,
        signal: controller.signal,
      });
    } catch (err) {
      throw new GateUnavailableError(`gate request failed: ${(err as Error).message}`);
    } finally {
      clearTimeout(timer);
    }
    if (res.status === 401 || res.status === 403) {
      throw new UnauthorizedError();
    }
    if (res.status >= 500 || res.status === 0) {
      throw new GateUnavailableError(`gate returned ${res.status}`);
    }
    if (!res.ok) {
      throw new StakingError(`gate error ${res.status}`);
    }
    return res;
  }
}
