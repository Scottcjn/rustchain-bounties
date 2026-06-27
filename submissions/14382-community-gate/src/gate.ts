import { Judge, JudgeRequest, JudgeResult, GateConfig } from "./types";

export class StakingGate implements Judge {
    private config: GateConfig;
    
    constructor(config: GateConfig) {
        this.config = {
            minReputation: 0,
            ...config
        };
    }
    
    async judge(request: JudgeRequest): Promise<JudgeResult> {
        const reasons: string[] = [];
        let passed = true;
        
        // Check 1: Minimum stake
        const stakeOk = request.context.amount ? 
            (request.context.amount as number) >= this.config.minStake : false;
        if (!stakeOk) {
            reasons.push(`Insufficient stake: minimum ${this.config.minStake} RTC required`);
            passed = false;
        }
        
        // Check 2: Action within limits
        const actionCount = request.context.actionCount as number || 0;
        if (actionCount > this.config.maxActionsPerDay) {
            reasons.push(`Daily action limit exceeded: ${this.config.maxActionsPerDay}`);
            passed = false;
        }
        
        // Check 3: Reputation
        const reputation = request.context.reputation as number || 0;
        if (reputation < (this.config.minReputation ?? 0)) {
            reasons.push(`Insufficient reputation: minimum ${this.config.minReputation}`);
            passed = false;
        }
        
        return {
            passed,
            reasons,
            score: passed ? 1.0 : Math.max(0, 1.0 - (reasons.length * 0.25))
        };
    }
    
    async validate(request: JudgeRequest): Promise<string[]> {
        const result = await this.judge(request);
        return result.reasons;
    }
}

export { JudgeRequest, JudgeResult, GateConfig };
