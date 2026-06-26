export interface StakingConfig {
    rpcUrl: string;
    wallet?: string;
    maxRetries?: number;
    timeout?: number;
}

export interface StakeParams {
    amount: number;
    agentId: string;
    metadata?: Record<string, unknown>;
}

export interface StakingResult {
    success: boolean;
    txHash?: string;
    amount?: number;
    error?: string;
}

export interface BalanceResult {
    staked: number;
    available: number;
    pending: number;
}

export interface StatusResult {
    agentId: string;
    isStaked: boolean;
    stakedAmount: number;
    rewards: number;
    lastClaim: string;
}
