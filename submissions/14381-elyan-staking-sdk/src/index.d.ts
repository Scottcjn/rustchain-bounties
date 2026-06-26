export interface StakeInput {
  skill: string;
  bondRtc?: number;
  bond_rtc?: number;
  agent?: string;
  nonce?: string;
  createdAt?: string;
  metadata?: Record<string, unknown>;
}

export interface SignedVerdictEnvelope {
  verdict: Record<string, unknown>;
  public_key_pem?: string;
  signature_algorithm?: "Ed25519";
  signature: string;
  attestation?: Attestation;
}

export interface Attestation {
  status: "confirmed" | "finalized" | "success" | string;
  request_hash: string;
  verdict_hash: string;
  tx_id?: string;
  transaction_id?: string;
  block_height?: number;
}

export interface GateResponse {
  verdict: SignedVerdictEnvelope;
  attestation: Attestation;
}

export interface ElyanStakingClientOptions {
  gateUrl: string;
  gatePath?: string;
  apiKey?: string;
  gatePublicKeyPem: string;
  fetch?: typeof fetch;
}

export interface VerificationResult {
  signature: true;
  attestation: true;
  request_hash: string;
  verdict_hash: string;
}

export class StakingError extends Error {
  details: Record<string, unknown>;
}

export class AuthError extends StakingError {}
export class GateUnavailableError extends StakingError {}
export class VerificationError extends StakingError {}

export function canonicalize<T>(value: T): T;
export function canonicalJson(value: unknown): string;
export function sha256Hex(value: string): string;
export function buildCanonicalStakeRequest(input: StakeInput): Record<string, unknown>;
export function verifyEd25519Envelope(envelope: SignedVerdictEnvelope, expectedPubkeyPem?: string): true;
export function verifyAttestation(attestation: Attestation, hashes?: { requestHash?: string; verdictHash?: string }): true;

export class ElyanStakingClient {
  constructor(options: ElyanStakingClientOptions);
  stake(input: StakeInput): Promise<{
    ok: true;
    request: Record<string, unknown>;
    request_hash: string;
    response: GateResponse;
    verified: VerificationResult;
  }>;
  submit(request: Record<string, unknown>): Promise<GateResponse>;
  poll(attestationUrl: string, options?: { timeoutMs?: number; intervalMs?: number }): Promise<Attestation>;
  verify(response: GateResponse, request: Record<string, unknown>): Promise<VerificationResult>;
}

export default ElyanStakingClient;
