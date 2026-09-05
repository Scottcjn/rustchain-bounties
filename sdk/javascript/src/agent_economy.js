/**
 * RustChain RIP-302 Agent Economy Client.
 *
 * Provides a dedicated, high-level client interface for the Agent-to-Agent
 * job marketplace, escrow lifecycle, reputation management, and automated
 * task distribution.
 */

import { RustChainClient } from "./client.js";
import { ValidationError } from "./errors.js";

export const AGENT_CATEGORIES = [
  "research",
  "code",
  "video",
  "audio",
  "writing",
  "translation",
  "data",
  "design",
  "testing",
  "other",
];

export const PLATFORM_FEE_RATE = 0.05; // 5%

export class AgentEconomyClient {
  /**
   * @param {object} [opts]
   * @param {string} [opts.baseUrl] - Base URL (defaults to https://50.28.86.131)
   * @param {string} [opts.wallet] - Default wallet address for posting/claiming
   * @param {number} [opts.timeoutMs] - Request timeout
   * @param {boolean} [opts.rejectUnauthorized] - TLS strictness
   * @param {typeof fetch} [opts.fetch] - Custom fetch implementation
   */
  constructor(opts = {}) {
    this.wallet = opts.wallet ?? null;
    this.client = new RustChainClient(opts);
  }

  /**
   * Calculate required escrow and platform fee (5%)
   * @param {number} rewardRtc
   * @returns {{ rewardRtc: number, feeRtc: number, totalEscrowRtc: number }}
   */
  static calculateEscrow(rewardRtc) {
    if (typeof rewardRtc !== "number" || rewardRtc <= 0) {
      throw new ValidationError("rewardRtc must be a positive number");
    }
    const feeRtc = Math.round(rewardRtc * PLATFORM_FEE_RATE * 1000) / 1000;
    const totalEscrowRtc = Math.round((rewardRtc + feeRtc) * 1000) / 1000;
    return {
      rewardRtc,
      feeRtc,
      totalEscrowRtc,
    };
  }

  /**
   * Get marketplace-wide Agent Economy statistics
   */
  async getStats() {
    return this.client.getAgentStats();
  }

  /**
   * List open and active jobs with optional filtering
   * @param {object} [opts]
   * @param {string} [opts.category]
   * @param {string} [opts.status]
   * @param {number} [opts.min_reward]
   * @param {number} [opts.limit]
   * @param {number} [opts.offset]
   */
  async listJobs(opts = {}) {
    return this.client.listAgentJobs(opts);
  }

  /**
   * Find matching jobs filtered by criteria
   * @param {object} [criteria]
   * @param {string} [criteria.category]
   * @param {number} [criteria.minReward]
   * @param {string} [criteria.status="posted"]
   * @param {number} [criteria.limit=50]
   */
  async findJobs(criteria = {}) {
    const raw = await this.client.listAgentJobs({
      category: criteria.category,
      min_reward: criteria.minReward,
      status: criteria.status,
      limit: criteria.limit ?? 50,
    });
    const jobs = Array.isArray(raw.jobs) ? raw.jobs : [];
    if (criteria.minReward !== undefined) {
      return jobs.filter((j) => Number(j.reward_rtc || j.reward || 0) >= criteria.minReward);
    }
    return jobs;
  }

  /**
   * Get details and activity log for a specific job
   * @param {string} jobId
   */
  async getJob(jobId) {
    return this.client.getAgentJob(jobId);
  }

  /**
   * Post a new job in the agent marketplace
   * @param {object} params
   * @param {string} [params.posterWallet] - Defaults to client.wallet
   * @param {string} params.title
   * @param {string} [params.description]
   * @param {string} params.category
   * @param {number} params.rewardRtc
   * @param {string} [params.expiresAt]
   */
  async postJob(params) {
    const posterWallet = params.posterWallet || params.poster_wallet || this.wallet;
    if (!posterWallet) {
      throw new ValidationError("posterWallet is required (pass in params or constructor)");
    }
    const rewardRtc = params.rewardRtc ?? params.reward_rtc;

    return this.client.postAgentJob({
      poster_wallet: posterWallet,
      title: params.title,
      description: params.description,
      category: params.category,
      reward_rtc: rewardRtc,
      expires_at: params.expiresAt || params.expires_at,
    });
  }

  /**
   * Claim an open job
   * @param {string} jobId
   * @param {object} [params]
   * @param {string} [params.workerWallet] - Defaults to client.wallet
   * @param {string} [params.note]
   */
  async claimJob(jobId, params = {}) {
    const workerWallet = params.workerWallet || params.worker_wallet || this.wallet;
    if (!workerWallet) {
      throw new ValidationError("workerWallet is required (pass in params or constructor)");
    }
    return this.client.claimAgentJob(jobId, {
      worker_wallet: workerWallet,
      note: params.note || "",
    });
  }

  /**
   * Deliver work for a claimed job
   * @param {string} jobId
   * @param {object} params
   * @param {string} [params.workerWallet] - Defaults to client.wallet
   * @param {string} [params.deliverableUrl]
   * @param {string} [params.summary]
   * @param {string} [params.artifactHash]
   */
  async deliverJob(jobId, params = {}) {
    const workerWallet = params.workerWallet || params.worker_wallet || this.wallet;
    if (!workerWallet) {
      throw new ValidationError("workerWallet is required (pass in params or constructor)");
    }
    return this.client.deliverAgentJob(jobId, {
      worker_wallet: workerWallet,
      deliverable_url: params.deliverableUrl || params.deliverable_url || "",
      summary: params.summary || params.resultSummary || params.result_summary || "",
      artifact_hash: params.artifactHash || params.artifact_hash || "",
    });
  }

  /**
   * Accept a delivered job and release escrow
   * @param {string} jobId
   * @param {object} [params]
   * @param {string} [params.posterWallet] - Defaults to client.wallet
   * @param {number} [params.rating=5]
   * @param {string} [params.review]
   */
  async acceptJob(jobId, params = {}) {
    const posterWallet = params.posterWallet || params.poster_wallet || this.wallet;
    if (!posterWallet) {
      throw new ValidationError("posterWallet is required (pass in params or constructor)");
    }
    return this.client.acceptAgentJob(jobId, {
      poster_wallet: posterWallet,
      rating: params.rating ?? 5,
      review: params.review || "",
    });
  }

  /**
   * Dispute / reject a delivered job
   * @param {string} jobId
   * @param {object} [params]
   * @param {string} [params.posterWallet] - Defaults to client.wallet
   * @param {string} [params.reason]
   */
  async disputeJob(jobId, params = {}) {
    const posterWallet = params.posterWallet || params.poster_wallet || this.wallet;
    if (!posterWallet) {
      throw new ValidationError("posterWallet is required (pass in params or constructor)");
    }
    return this.client.disputeAgentJob(jobId, {
      poster_wallet: posterWallet,
      reason: params.reason || "",
    });
  }

  /**
   * Cancel an open job and refund escrow
   * @param {string} jobId
   * @param {object} [params]
   * @param {string} [params.posterWallet] - Defaults to client.wallet
   * @param {string} [params.reason]
   */
  async cancelJob(jobId, params = {}) {
    const posterWallet = params.posterWallet || params.poster_wallet || this.wallet;
    if (!posterWallet) {
      throw new ValidationError("posterWallet is required (pass in params or constructor)");
    }
    return this.client.cancelAgentJob(jobId, {
      poster_wallet: posterWallet,
      reason: params.reason || "",
    });
  }

  /**
   * Get reputation and trust score for a wallet
   * @param {string} [wallet] - Defaults to client.wallet
   */
  async getReputation(wallet) {
    const targetWallet = wallet || this.wallet;
    if (!targetWallet) {
      throw new ValidationError("wallet is required (pass as argument or constructor)");
    }
    return this.client.getAgentReputation(targetWallet);
  }
}
