// SPDX-License-Identifier: MIT

export class StakingError extends Error {
  constructor(message: string) {
    super(message);
    this.name = "StakingError";
  }
}

export class UnauthorizedError extends StakingError {
  constructor(message = "unauthorized: bad API key") {
    super(message);
    this.name = "UnauthorizedError";
  }
}

export class SignatureError extends StakingError {
  constructor(message = "verdict signature verification failed") {
    super(message);
    this.name = "SignatureError";
  }
}

export class AttestationError extends StakingError {
  constructor(message = "on-chain attestation verification failed") {
    super(message);
    this.name = "AttestationError";
  }
}

export class GateUnavailableError extends StakingError {
  constructor(message = "staking gate unavailable") {
    super(message);
    this.name = "GateUnavailableError";
  }
}
