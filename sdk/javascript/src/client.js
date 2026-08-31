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
  async health() {
    return this._get("/health");
  }

  /** GET /epoch */
  async getEpoch() {
    return this._get("/epoch");
  }

  /** GET /miners */
  async getMiners() {
    return this._get("/miners");
  }

  /**
   * GET /wallet/balance?miner_id=<wallet>
   *
   * Accepts either a wallet *name* (e.g. "zxy0314-work") or an RTC address.
   * The real node accepts both via the same `miner_id` query param.
   */
  async getBalance(wallet) {
    if (typeof wallet !== "string" || wallet.length === 0) {
      throw new ValidationError("wallet must be a non-empty string");
    }
    return this._get("/wallet/balance", { miner_id: wallet });
  }

  /**
   * GET /wallet/history?miner_id=<wallet>&limit=<n>
   */
  async getWalletHistory(wallet, limit = 50) {
    if (typeof wallet !== "string" || wallet.length === 0) {
      throw new ValidationError("wallet must be a non-empty string");
    }
    if (!Number.isInteger(limit) || limit < 1 || limit > 500) {
      throw new ValidationError("limit must be an integer in [1, 500]");
    }
    return this._get("/wallet/history", { miner_id: wallet, limit });
  }

  /** GET /bounties */
  async getBounties() {
    return this._get("/bounties");
  }

  /** GET /epoch/rewards?epoch=<n> */
  async getEpochRewards(epoch) {
    if (!Number.isInteger(epoch) || epoch < 0) {
      throw new ValidationError("epoch must be a non-negative integer");
    }
    return this._get("/epoch/rewards", { epoch });
  }

  /** GET /explorer/blocks?limit=<n> */
  async explorerBlocks(limit = 20) {
    if (!Number.isInteger(limit) || limit < 1 || limit > 500) {
      throw new ValidationError("limit must be an integer in [1, 500]");
    }
    return this._get("/explorer/blocks", { limit });
  }

  /** POST /attest/challenge { miner_public_key } */
  async attestChallenge(minerPublicKey) {
    if (typeof minerPublicKey !== "string" || minerPublicKey.length === 0) {
      throw new ValidationError("minerPublicKey must be a non-empty string");
    }
    return this._post("/attest/challenge", { miner_public_key: minerPublicKey });
  }

  // ── RIP-302 Agent Economy methods ────────────────────────────────

  /**
   * GET /agent/stats — Marketplace statistics
   */
  async getAgentStats() {
    return this._get("/agent/stats");
  }

  /**
   * GET /agent/jobs — Browse marketplace jobs
   * @param {object} [opts]
   * @param {number} [opts.limit=50]
   * @param {number} [opts.offset=0]
   * @param {string} [opts.category]
   * @param {string} [opts.status]
   * @param {number} [opts.min_reward]
   */
  async listAgentJobs(opts = {}) {
    const query = {};
    if (opts.limit !== undefined) {
      if (!Number.isInteger(opts.limit) || opts.limit < 1) {
        throw new ValidationError("limit must be a positive integer");
      }
      query.limit = opts.limit;
    }
    if (opts.offset !== undefined) {
      if (!Number.isInteger(opts.offset) || opts.offset < 0) {
        throw new ValidationError("offset must be a non-negative integer");
      }
      query.offset = opts.offset;
    }
    if (opts.category) query.category = String(opts.category);
    if (opts.status) query.status = String(opts.status);
    if (opts.min_reward !== undefined) query.min_reward = Number(opts.min_reward);

    return this._get("/agent/jobs", query);
  }

  /**
   * GET /agent/jobs/:id — Fetch details for a specific job
   * @param {string} jobId
   */
  async getAgentJob(jobId) {
    if (typeof jobId !== "string" || jobId.trim().length === 0) {
      throw new ValidationError("jobId must be a non-empty string");
    }
    return this._get(`/agent/jobs/${encodeURIComponent(jobId.trim())}`);
  }

  /**
   * POST /agent/jobs — Create a new agent job with locked escrow
   * @param {object} params
   * @param {string} params.poster_wallet
   * @param {string} params.title
   * @param {string} [params.description]
   * @param {string} params.category
   * @param {number} params.reward_rtc
   * @param {string} [params.expires_at]
   */
  async postAgentJob(params) {
    if (!params || typeof params !== "object") {
      throw new ValidationError("params must be an object");
    }
    if (!params.poster_wallet || typeof params.poster_wallet !== "string") {
      throw new ValidationError("poster_wallet is required");
    }
    if (!params.title || typeof params.title !== "string") {
      throw new ValidationError("title is required");
    }
    if (!params.category || typeof params.category !== "string") {
      throw new ValidationError("category is required");
    }
    if (typeof params.reward_rtc !== "number" || params.reward_rtc <= 0) {
      throw new ValidationError("reward_rtc must be a positive number");
    }

    const payload = {
      poster_wallet: params.poster_wallet,
      title: params.title,
      description: params.description || "",
      category: params.category,
      reward_rtc: params.reward_rtc,
    };
    if (params.expires_at) {
      payload.expires_at = params.expires_at;
    }

    return this._post("/agent/jobs", payload);
  }

  /**
   * POST /agent/jobs/:id/claim — Claim an open job
   * @param {string} jobId
   * @param {object} params
   * @param {string} params.worker_wallet
   * @param {string} [params.note]
   */
  async claimAgentJob(jobId, params) {
    if (typeof jobId !== "string" || jobId.trim().length === 0) {
      throw new ValidationError("jobId must be a non-empty string");
    }
    if (!params || typeof params !== "object" || !params.worker_wallet) {
      throw new ValidationError("worker_wallet is required");
    }
    return this._post(`/agent/jobs/${encodeURIComponent(jobId.trim())}/claim`, {
      worker_wallet: params.worker_wallet,
      note: params.note || "",
    });
  }

  /**
   * POST /agent/jobs/:id/deliver — Submit deliverable for a claimed job
   * @param {string} jobId
   * @param {object} params
   * @param {string} params.worker_wallet
   * @param {string} [params.deliverable_url]
   * @param {string} [params.summary]
   * @param {string} [params.result_summary]
   * @param {string} [params.artifact_hash]
   */
  async deliverAgentJob(jobId, params) {
    if (typeof jobId !== "string" || jobId.trim().length === 0) {
      throw new ValidationError("jobId must be a non-empty string");
    }
    if (!params || typeof params !== "object" || !params.worker_wallet) {
      throw new ValidationError("worker_wallet is required");
    }
    return this._post(`/agent/jobs/${encodeURIComponent(jobId.trim())}/deliver`, {
      worker_wallet: params.worker_wallet,
      deliverable_url: params.deliverable_url || "",
      summary: params.summary || params.result_summary || "",
      result_summary: params.result_summary || params.summary || "",
      artifact_hash: params.artifact_hash || "",
    });
  }

  /**
   * POST /agent/jobs/:id/accept — Accept job and release escrow
   * @param {string} jobId
   * @param {object} params
   * @param {string} params.poster_wallet
   * @param {number} [params.rating=5]
   * @param {string} [params.review=""]
   */
  async acceptAgentJob(jobId, params) {
    if (typeof jobId !== "string" || jobId.trim().length === 0) {
      throw new ValidationError("jobId must be a non-empty string");
    }
    if (!params || typeof params !== "object" || !params.poster_wallet) {
      throw new ValidationError("poster_wallet is required");
    }
    const rating = params.rating !== undefined ? Number(params.rating) : 5;
    if (rating < 1 || rating > 5) {
      throw new ValidationError("rating must be between 1 and 5");
    }
    return this._post(`/agent/jobs/${encodeURIComponent(jobId.trim())}/accept`, {
      poster_wallet: params.poster_wallet,
      rating,
      review: params.review || "",
    });
  }

  /**
   * POST /agent/jobs/:id/dispute — Dispute a deliverable
   * @param {string} jobId
   * @param {object} params
   * @param {string} params.poster_wallet
   * @param {string} [params.reason=""]
   */
  async disputeAgentJob(jobId, params) {
    if (typeof jobId !== "string" || jobId.trim().length === 0) {
      throw new ValidationError("jobId must be a non-empty string");
    }
    if (!params || typeof params !== "object" || !params.poster_wallet) {
      throw new ValidationError("poster_wallet is required");
    }
    return this._post(`/agent/jobs/${encodeURIComponent(jobId.trim())}/dispute`, {
      poster_wallet: params.poster_wallet,
      reason: params.reason || "",
    });
  }

  /**
   * POST /agent/jobs/:id/cancel — Cancel an open or expired job
   * @param {string} jobId
   * @param {object} params
   * @param {string} params.poster_wallet
   * @param {string} [params.reason=""]
   */
  async cancelAgentJob(jobId, params) {
    if (typeof jobId !== "string" || jobId.trim().length === 0) {
      throw new ValidationError("jobId must be a non-empty string");
    }
    if (!params || typeof params !== "object" || !params.poster_wallet) {
      throw new ValidationError("poster_wallet is required");
    }
    return this._post(`/agent/jobs/${encodeURIComponent(jobId.trim())}/cancel`, {
      poster_wallet: params.poster_wallet,
      reason: params.reason || "",
    });
  }

  /**
   * GET /agent/reputation/:wallet — Get agent trust score & reputation
   * @param {string} wallet
   */
  async getAgentReputation(wallet) {
    if (typeof wallet !== "string" || wallet.trim().length === 0) {
      throw new ValidationError("wallet must be a non-empty string");
    }
    return this._get(`/agent/reputation/${encodeURIComponent(wallet.trim())}`);
  }
}
