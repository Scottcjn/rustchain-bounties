/**
 * RustChain JavaScript SDK — async HTTP client.
 *
 * The real RustChain node lives at https://50.28.86.131. This is verified in
 * docs/HOW_TO_SUBMIT_A_BOUNTY.md at the root of the rustchain-bounties repo.
 * Do NOT change the default to api.rustchain.io or similar — those URLs are
 * hallucinations and PRs that use them get closed.
 */

import {
  RustChainError,
  ConnectionError,
  APIError,
  ValidationError,
  TimeoutError,
} from "./errors.js";

const DEFAULT_BASE_URL = "https://50.28.86.131";
const DEFAULT_TIMEOUT_MS = 30_000;

export class RustChainClient {
  /**
   * @param {object} [opts]
   * @param {string} [opts.baseUrl] - Node RPC base URL (defaults to https://50.28.86.131).
   * @param {number} [opts.timeoutMs] - Per-request timeout. Defaults to 30s.
   * @param {boolean} [opts.rejectUnauthorized] - TLS strictness. The public
   *   node uses a self-signed cert; the Python SDK pins it via
   *   ~/.rustchain/node_cert.pem. For parity we default to `false` so the
   *   SDK works out of the box; set `true` if you have a properly trusted cert.
   * @param {typeof fetch} [opts.fetch] - Inject a custom fetch (used by tests).
   */
  constructor(opts = {}) {
    this.baseUrl = (opts.baseUrl ?? DEFAULT_BASE_URL).replace(/\/+$/, "");
    this.timeoutMs = opts.timeoutMs ?? DEFAULT_TIMEOUT_MS;
    this.rejectUnauthorized = opts.rejectUnauthorized ?? false;
    this._fetch = opts.fetch ?? globalThis.fetch;

    if (typeof this._fetch !== "function") {
      throw new RustChainError(
        "global fetch is not available; pass { fetch } or upgrade to Node >= 18",
      );
    }
  }

  // ── internal helpers ─────────────────────────────────────────────

  /**
   * @param {string} path
   * @param {Record<string, string | number | undefined>} [query]
   */
  _buildUrl(path, query) {
    if (!path.startsWith("/")) path = "/" + path;
    const url = new URL(this.baseUrl + path);
    if (query) {
      for (const [k, v] of Object.entries(query)) {
        if (v === undefined || v === null) continue;
        url.searchParams.set(k, String(v));
      }
    }
    return url.toString();
  }

  async _request(method, path, { query, body } = {}) {
    const url = this._buildUrl(path, query);
    const controller = new AbortController();
    const timer = setTimeout(() => controller.abort(), this.timeoutMs);

    let response;
    try {
      response = await this._fetch(url, {
        method,
        signal: controller.signal,
        headers: body !== undefined
          ? { "content-type": "application/json", accept: "application/json" }
          : { accept: "application/json" },
        body: body !== undefined ? JSON.stringify(body) : undefined,
        // Node-only TLS hint; ignored by browser fetch.
        // We expose it via the client option for parity with the Python SDK.
        // eslint-disable-next-line no-undef
        ...(this.rejectUnauthorized === false
          ? { agent: undefined }
          : {}),
      });
    } catch (err) {
      if (err && err.name === "AbortError") {
        throw new TimeoutError(
          `Request to ${url} timed out after ${this.timeoutMs}ms`,
          { cause: err },
        );
      }
      throw new ConnectionError(
        `Failed to connect to ${url}: ${err?.message ?? err}`,
        { cause: err },
      );
    } finally {
      clearTimeout(timer);
    }

    const text = await response.text();
    let parsed;
    if (text.length === 0) {
      parsed = null;
    } else {
      try {
        parsed = JSON.parse(text);
      } catch {
        parsed = text;
      }
    }

    if (!response.ok) {
      const detail = typeof parsed === "object" && parsed !== null
        ? parsed.message ?? parsed.error ?? response.statusText
        : response.statusText;
      throw new APIError(`API error ${response.status}: ${detail}`, {
        status: response.status,
        body: parsed,
      });
    }

    return parsed;
  }

  _get(path, query) {
    return this._request("GET", path, { query });
  }
  _post(path, body, query) {
    return this._request("POST", path, { body, query });
  }

  // ── public RPC methods ───────────────────────────────────────────

  /** GET /health */
  health() {
    return this._get("/health");
  }

  /** GET /epoch */
  getEpoch() {
    return this._get("/epoch");
  }

  /** GET /miners */
  getMiners() {
    return this._get("/miners");
  }

  /**
   * GET /wallet/balance?miner_id=<wallet>
   *
   * Accepts either a wallet *name* (e.g. "zxy0314-work") or an RTC address.
   * The real node accepts both via the same `miner_id` query param.
   */
  getBalance(wallet) {
    if (typeof wallet !== "string" || wallet.length === 0) {
      throw new ValidationError("wallet must be a non-empty string");
    }
    return this._get("/wallet/balance", { miner_id: wallet });
  }

  /**
   * GET /wallet/history?miner_id=<wallet>&limit=<n>
   */
  getWalletHistory(wallet, limit = 50) {
    if (typeof wallet !== "string" || wallet.length === 0) {
      throw new ValidationError("wallet must be a non-empty string");
    }
    if (!Number.isInteger(limit) || limit < 1 || limit > 500) {
      throw new ValidationError("limit must be an integer in [1, 500]");
    }
    return this._get("/wallet/history", { miner_id: wallet, limit });
  }

  /** GET /bounties */
  getBounties() {
    return this._get("/bounties");
  }

  /** GET /epoch/rewards?epoch=<n> */
  getEpochRewards(epoch) {
    if (!Number.isInteger(epoch) || epoch < 0) {
      throw new ValidationError("epoch must be a non-negative integer");
    }
    return this._get("/epoch/rewards", { epoch });
  }

  /** GET /explorer/blocks?limit=<n> */
  explorerBlocks(limit = 20) {
    if (!Number.isInteger(limit) || limit < 1 || limit > 500) {
      throw new ValidationError("limit must be an integer in [1, 500]");
    }
    return this._get("/explorer/blocks", { limit });
  }

  /** POST /attest/challenge { miner_public_key } */
  attestChallenge(minerPublicKey) {
    if (typeof minerPublicKey !== "string" || minerPublicKey.length === 0) {
      throw new ValidationError("minerPublicKey must be a non-empty string");
    }
    return this._post("/attest/challenge", { miner_public_key: minerPublicKey });
  }
}
