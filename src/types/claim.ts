export type ChainType = 'Solana' | 'Base';

export interface ClaimState {
  isEligible: boolean;
  tier: number;
  amount: number;
  hasClaimed: boolean;
  sybilCleared: boolean;
}

export interface IdentityData {
  githubId: string;
  githubUsername: string;
  accountCreatedAt: string;
  contributionCount: number;
}