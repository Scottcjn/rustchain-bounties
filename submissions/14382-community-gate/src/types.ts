export interface JudgeRequest {
    agentId: string;
    action: string;
    context: Record<string, unknown>;
}

export interface JudgeResult {
    passed: boolean;
    reasons: string[];
    score: number;
}

export interface Judge {
    judge(request: JudgeRequest): Promise<JudgeResult>;
}

export interface GateConfig {
    minStake: number;
    maxActionsPerDay: number;
    rpcUrl: string;
    minReputation?: number;
}
