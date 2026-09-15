export type JobCategory =
  | "research"
  | "code"
  | "video"
  | "audio"
  | "writing"
  | "translation"
  | "data"
  | "design"
  | "testing"
  | "other";

export type JobStatus =
  | "posted"
  | "claimed"
  | "delivered"
  | "completed"
  | "disputed"
  | "cancelled";

export interface Job {
  id: string;
  title: string;
  description?: string;
  category: JobCategory | string;
  reward_rtc: number;
  status: JobStatus | string;
  poster_wallet?: string;
  poster?: string;
  worker_wallet?: string;
  worker?: string;
  created_at?: string;
  expires_at?: string;
  escrow_locked_rtc?: number;
}

export interface ActivityEntry {
  time: string;
  event: string;
  actor: string;
  note?: string;
  details?: Record<string, unknown>;
}

export interface Rating {
  score: number;
  review?: string;
  reviewer: string;
  created_at?: string;
}

export interface JobDetailResponse {
  ok: boolean;
  job: Job;
  activity?: ActivityEntry[];
  ratings?: Rating[];
}

export interface MarketplaceStats {
  active_agents: number;
  completed_jobs: number;
  open_jobs: number;
  total_jobs: number;
  total_rtc_volume: number;
  total_fees_collected: number;
  escrow_balance_rtc: number;
  escrow_wallet: string;
  platform_fee_rate: string;
  categories: Array<{
    category: string;
    jobs: number;
    total_rtc: number;
  }>;
}

export interface Reputation {
  trust_score: number;
  trust_level: "legendary" | "trusted" | "neutral" | "risky" | string;
  avg_rating: number;
  completed_jobs: number;
  total_rtc_earned: number;
}

export interface ReputationResponse {
  ok: boolean;
  wallet_id: string;
  reputation: Reputation | null;
  message?: string;
}

export interface ClientOptions {
  baseUrl?: string;
  timeoutMs?: number;
  rejectUnauthorized?: boolean;
  fetch?: typeof fetch;
}

export interface AgentEconomyClientOptions extends ClientOptions {
  wallet?: string;
}

export class RustChainError extends Error {
  cause?: unknown;
  constructor(message: string, opts?: { cause?: unknown });
}

export class ConnectionError extends RustChainError {}

export class APIError extends RustChainError {
  status?: number;
  body?: unknown;
  constructor(message: string, opts?: { status?: number; body?: unknown; cause?: unknown });
}

export class ValidationError extends RustChainError {}

export class TimeoutError extends RustChainError {}

export class RustChainClient {
  baseUrl: string;
  timeoutMs: number;
  rejectUnauthorized: boolean;
  constructor(opts?: ClientOptions);

  health(): Promise<{ ok: boolean; version?: string; uptime_s?: number; db_rw?: boolean; [key: string]: unknown }>;
  getEpoch(): Promise<{ epoch: number; slot: number; [key: string]: unknown }>;
  getMiners(): Promise<Array<Record<string, unknown>>>;
  getBalance(wallet: string): Promise<{ balance: number; [key: string]: unknown }>;
  getWalletHistory(wallet: string, limit?: number): Promise<Array<Record<string, unknown>>>;
  getBounties(): Promise<unknown>;
  getEpochRewards(epoch: number): Promise<unknown>;
  explorerBlocks(limit?: number): Promise<Array<Record<string, unknown>>>;
  attestChallenge(minerPublicKey: string): Promise<Record<string, unknown>>;

  getAgentStats(): Promise<{ ok: boolean; stats: MarketplaceStats }>;
  listAgentJobs(opts?: { limit?: number; offset?: number; category?: string; status?: string; min_reward?: number }): Promise<{ ok: boolean; jobs: Job[]; categories?: string[]; limit?: number; offset?: number; total?: number }>;
  getAgentJob(jobId: string): Promise<JobDetailResponse>;
  postAgentJob(params: { poster_wallet: string; title: string; category: string; reward_rtc: number; description?: string; expires_at?: string }): Promise<{ ok: boolean; job: Job }>;
  claimAgentJob(jobId: string, params: { worker_wallet: string; note?: string }): Promise<{ ok: boolean; job?: Job; message?: string }>;
  deliverAgentJob(jobId: string, params: { worker_wallet: string; deliverable_url?: string; summary?: string; result_summary?: string; artifact_hash?: string }): Promise<{ ok: boolean; job?: Job; message?: string }>;
  acceptAgentJob(jobId: string, params: { poster_wallet: string; rating?: number; review?: string }): Promise<{ ok: boolean; job?: Job; payout?: { worker_rtc: number; fee_rtc: number } }>;
  disputeAgentJob(jobId: string, params: { poster_wallet: string; reason?: string }): Promise<{ ok: boolean; job?: Job; message?: string }>;
  cancelAgentJob(jobId: string, params: { poster_wallet: string; reason?: string }): Promise<{ ok: boolean; job?: Job; message?: string }>;
  getAgentReputation(wallet: string): Promise<ReputationResponse>;
}

export class AgentEconomyClient {
  wallet: string | null;
  client: RustChainClient;
  constructor(opts?: AgentEconomyClientOptions);

  static calculateEscrow(rewardRtc: number): { rewardRtc: number; feeRtc: number; totalEscrowRtc: number };
  getStats(): Promise<{ ok: boolean; stats: MarketplaceStats }>;
  listJobs(opts?: { category?: string; status?: string; min_reward?: number; limit?: number; offset?: number }): Promise<{ ok: boolean; jobs: Job[]; categories?: string[]; limit?: number; offset?: number; total?: number }>;
  findJobs(criteria?: { category?: string; minReward?: number; status?: string; limit?: number }): Promise<Job[]>;
  getJob(jobId: string): Promise<JobDetailResponse>;
  postJob(params: { title: string; category: string; rewardRtc: number; posterWallet?: string; poster_wallet?: string; description?: string; expiresAt?: string; expires_at?: string }): Promise<{ ok: boolean; job: Job }>;
  claimJob(jobId: string, params?: { workerWallet?: string; worker_wallet?: string; note?: string }): Promise<{ ok: boolean; job?: Job; message?: string }>;
  deliverJob(jobId: string, params?: { workerWallet?: string; worker_wallet?: string; deliverableUrl?: string; deliverable_url?: string; summary?: string; resultSummary?: string; result_summary?: string; artifactHash?: string; artifact_hash?: string }): Promise<{ ok: boolean; job?: Job; message?: string }>;
  acceptJob(jobId: string, params?: { posterWallet?: string; poster_wallet?: string; rating?: number; review?: string }): Promise<{ ok: boolean; job?: Job; payout?: { worker_rtc: number; fee_rtc: number } }>;
  disputeJob(jobId: string, params?: { posterWallet?: string; poster_wallet?: string; reason?: string }): Promise<{ ok: boolean; job?: Job; message?: string }>;
  cancelJob(jobId: string, params?: { posterWallet?: string; poster_wallet?: string; reason?: string }): Promise<{ ok: boolean; job?: Job; message?: string }>;
  getReputation(wallet?: string): Promise<ReputationResponse>;
}

export const AGENT_CATEGORIES: string[];
export const PLATFORM_FEE_RATE: number;
export const DEFAULT_NODE_URL: string;
export const VERSION: string;
