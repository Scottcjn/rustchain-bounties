/**
 * RustChain API client with automatic failover across multiple node URLs.
 */

import { z } from "zod";

const DEFAULT_PRIMARY = "https://50.28.86.131";
const DEFAULT_TIMEOUT_MS = 10_000;

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------

export interface HealthResponse {
  status: string;
  peers?: number;
  height?: number;
  timestamp?: number;
  [key: string]: unknown;
}

export interface MinerInfo {
  id: string;
  address: string;
  architecture?: string;
  status?: string;
  [key: string]: unknown;
}

export interface EpochResponse {
  epoch: number;
  slot?: number;
  height?: number;
  rewards?: number;
  miners_online?: number;
  [key: string]: unknown;
}

export interface BalanceResponse {
  wallet_id: string;
  balance: number;
  balance_rtc?: number;
  pending?: number;
  [key: string]: unknown;
}

export interface WalletCreationResponse {
  wallet_id: string;
  address: string;
  created_at?: number;
  [key: string]: unknown;
}

export interface AttestationResponse {
  attestation_id: string;
  status: string;
  submitted_at?: number;
  [key: string]: unknown;
}

// ---------------------------------------------------------------------------
// Schema validation (Zod)
// ---------------------------------------------------------------------------

const HealthSchema = z.object({ status: z.string() }).passthrough();
const MinerListSchema = z.array(z.object({ id: z.string() }).passthrough());
const EpochSchema = z.object({ epoch: z.number() }).passthrough();
const BalanceSchema = z.object({ wallet_id: z.string(), balance: z.number() }).passthrough();
const WalletCreationSchema = z.object({ wallet_id: z.string(), address: z.string() }).passthrough();
const AttestationSchema = z.object({ attestation_id: z.string(), status: z.string() }).passthrough();

// ---------------------------------------------------------------------------
// Client class
// ---------------------------------------------------------------------------

export class RustChainClient {
  private primaryUrl: string;
  private fallbackUrls: string[];
  private timeoutMs: number;

  constructor(
    primaryUrl = DEFAULT_PRIMARY,
    fallbackUrls: string[] = [],
    timeoutMs = DEFAULT_TIMEOUT_MS
  ) {
    this.primaryUrl = primaryUrl.replace(/\/$/, "");
    this.fallbackUrls = fallbackUrls
      .map((u) => u.replace(/\/$/, ""))
      .filter((u) => u && u !== this.primaryUrl);
    this.timeoutMs = timeoutMs;
  }

  /** Read configuration from environment variables. */
  static fromEnv(): RustChainClient {
    const primary =
      (process.env.RUSTCHAIN_PRIMARY_URL ?? DEFAULT_PRIMARY).trim().replace(/\/$/, "") ||
      DEFAULT_PRIMARY;
    const fallbacksRaw = process.env.RUSTCHAIN_FALLBACK_URLS ?? "";
    const fallbacks = fallbacksRaw
      .split(",")
      .map((u) => u.trim().replace(/\/$/, ""))
      .filter(Boolean);
    const timeoutMs = parseInt(process.env.RUSTCHAIN_TIMEOUT_MS ?? String(DEFAULT_TIMEOUT_MS), 10);
    return new RustChainClient(primary, fallbacks, timeoutMs);
  }

  private allUrls(): string[] {
    return [this.primaryUrl, ...this.fallbackUrls].filter(Boolean);
  }

  private async getJson<T>(path: string, params?: Record<string, string>): Promise<T> {
    const qs = params ? "?" + new URLSearchParams(params).toString() : "";
    const lastErrors: string[] = [];

    for (const base of this.allUrls()) {
      const url = `${base}${path}${qs}`;
      try {
        const controller = new AbortController();
        const timer = setTimeout(() => controller.abort(), this.timeoutMs);
        try {
          const res = await fetch(url, {
            signal: controller.signal,
            headers: { Accept: "application/json" },
          });
          clearTimeout(timer);
          if (!res.ok) {
            lastErrors.push(`${res.status} ${res.statusText} from ${url}`);
            continue;
          }
          const json = (await res.json()) as T;
          return json;
        } catch (rawErr: unknown) {
          clearTimeout(timer);
          const msg = rawErr instanceof Error ? rawErr.message : String(rawErr);
          lastErrors.push(`${msg} from ${url}`);
          continue;
        }
      } catch {
        lastErrors.push(`Unexpected error from ${url}`);
        continue;
      }
    }

    throw new Error(
      `All RustChain nodes failed for GET ${path}. Errors: ${lastErrors.join(" | ")}`
    );
  }

  // -------------------------------------------------------------------------
  // Public API methods
  // -------------------------------------------------------------------------

  async health(): Promise<HealthResponse> {
    return this.getJson<HealthResponse>("/health");
  }

  async miners(): Promise<MinerInfo[]> {
    return this.getJson<MinerInfo[]>("/api/miners");
  }

  async epoch(): Promise<EpochResponse> {
    return this.getJson<EpochResponse>("/epoch");
  }

  async balance(walletId: string): Promise<BalanceResponse> {
    return this.getJson<BalanceResponse>("/wallet/balance", { wallet_id: walletId });
  }

  /** Register a new wallet on the RustChain network. */
  async createWallet(walletName: string): Promise<WalletCreationResponse> {
    return this.getJson<WalletCreationResponse>("/wallet/create", { wallet_name: walletName });
  }

  /** Submit a hardware attestation for a miner. */
  async submitAttestation(
    walletId: string,
    hardwareFingerprint: string
  ): Promise<AttestationResponse> {
    return this.getJson<AttestationResponse>("/attestation/submit", {
      wallet_id: walletId,
      hardware_fingerprint: hardwareFingerprint,
    });
  }
}
