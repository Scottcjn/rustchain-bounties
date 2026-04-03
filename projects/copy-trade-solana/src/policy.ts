import { Trade } from "./types";

/** Per-follower state tracked across trades */
export interface FollowerState {
  /** Total lamports already spent by this follower */
  totalSpentLamports: number;
}

/** Policy configuration — all amounts in lamports */
export interface PolicyConfig {
  /** Minimum trade size to copy (ignore dust) */
  minTradeLamports: number;
  /** Maximum cumulative spend per follower wallet */
  maxPerWalletLamports: number;
  /** Maximum allowed slippage percentage (0-100) */
  slippagePct: number;
}

export const DEFAULT_POLICY: PolicyConfig = {
  minTradeLamports: 1_000_000, // 0.001 SOL
  maxPerWalletLamports: 500_000_000, // 0.5 SOL
  slippagePct: 2,
};

export interface PolicyResult {
  allowed: boolean;
  reason?: string;
}

/** Decide whether a trade should be copied for a given follower */
export function shouldCopy(
  trade: Trade,
  followerState: FollowerState,
  config: PolicyConfig = DEFAULT_POLICY
): PolicyResult {
  if (trade.amount < config.minTradeLamports) {
    return {
      allowed: false,
      reason: `Trade amount ${trade.amount} below minimum ${config.minTradeLamports} lamports`,
    };
  }

  const projectedTotal = followerState.totalSpentLamports + trade.amount;
  if (projectedTotal > config.maxPerWalletLamports) {
    return {
      allowed: false,
      reason: `Would exceed per-wallet cap: ${projectedTotal} > ${config.maxPerWalletLamports} lamports`,
    };
  }

  return { allowed: true };
}
