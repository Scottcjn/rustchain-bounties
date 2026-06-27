# Community Gate — Open Judge Interface
## Bounty #14382 (75 RTC)

## Implementation
A `Judge` interface and reference implementation for the Elyan community gate.

### Judge Interface
```typescript
interface Judge {
    judge(request: JudgeRequest): JudgeResult;
}

interface JudgeRequest {
    agentId: string;
    action: string;
    context: Record<string, unknown>;
}

interface JudgeResult {
    passed: boolean;
    reasons: string[];
    score: number;
}
```

### Reference Implementation: StakingGate
The `StakingGate` checks:
1. Agent has minimum stake (≥ 10 RTC)
2. Agent is not blacklisted
3. Agent has not exceeded daily action limit
4. Staking rewards are current (not expired)

### Usage
```typescript
import { StakingGate } from "./gate";

const gate = new StakingGate({
    minStake: 10,
    maxActionsPerDay: 100,
    rpcUrl: "https://api.elyan.network"
});

const result = await gate.judge({
    agentId: "agent-123",
    action: "stake",
    context: { amount: 50 }
});

console.log(result.passed); // true/false
console.log(result.reasons); // ["Insufficient stake", ...]
```

### Wallet
ETH: 0xde67FD4b7fC0d02d43AA3A8b5c8c5a80c823d0c6
