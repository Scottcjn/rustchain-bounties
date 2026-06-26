// SPDX-License-Identifier: MIT
export { StakingClient } from "./client.js";
export type {
  StakingClientOptions,
  StakeRequest,
  SubmitResponse,
  PollResponse,
  SignedVerdict,
  VerifiedVerdict,
  AttestationVerifier,
  JobStatus,
} from "./client.js";
export { canonicalize, canonicalBytes } from "./canonical.js";
export { verifyEd25519, hexToBytes, bytesToHex } from "./verify.js";
export {
  StakingError,
  UnauthorizedError,
  SignatureError,
  AttestationError,
  GateUnavailableError,
} from "./errors.js";
