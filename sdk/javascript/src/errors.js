/**
 * Custom error types for the RustChain SDK.
 *
 * Mirrors the Python SDK exception hierarchy in
 * `sdk/python/rustchain_sdk/exceptions.py` so error-handling code can
 * be ported 1:1 between the two SDKs.
 */

export class RustChainError extends Error {
  constructor(message, opts = {}) {
    super(message);
    this.name = "RustChainError";
    if (opts.cause !== undefined) this.cause = opts.cause;
  }
}

export class ConnectionError extends RustChainError {
  constructor(message, opts) {
    super(message, opts);
    this.name = "ConnectionError";
  }
}

export class APIError extends RustChainError {
  /**
   * @param {string} message
   * @param {{ status?: number, body?: unknown, cause?: unknown }} [opts]
   */
  constructor(message, opts = {}) {
    super(message, opts);
    this.name = "APIError";
    this.status = opts.status;
    this.body = opts.body;
  }
}

export class ValidationError extends RustChainError {
  constructor(message, opts) {
    super(message, opts);
    this.name = "ValidationError";
  }
}

export class TimeoutError extends RustChainError {
  constructor(message, opts) {
    super(message, opts);
    this.name = "TimeoutError";
  }
}
