import { StakingConfig, StakeParams, StakingResult, BalanceResult, StatusResult } from "./types";

export class StakingClient {
    private config: StakingConfig;
    
    constructor(config: StakingConfig) {
        this.config = {
            maxRetries: 3,
            timeout: 30000,
            ...config
        };
    }
    
    async stake(params: StakeParams): Promise<StakingResult> {
        return this._request("stake", params);
    }
    
    async unstake(params: StakeParams): Promise<StakingResult> {
        return this._request("unstake", params);
    }
    
    async claim(agentId: string): Promise<StakingResult> {
        return this._request("claim", { agentId });
    }
    
    async getBalance(): Promise<BalanceResult> {
        const resp = await this._request("balance", {});
        return resp as BalanceResult;
    }
    
    async getStatus(agentId: string): Promise<StatusResult> {
        const resp = await this._request("status", { agentId });
        return resp as StatusResult;
    }
    
    private async _request(method: string, params: Record<string, unknown>): Promise<unknown> {
        const url = `${this.config.rpcUrl}/api/v1/${method}`;
        let lastError: Error | null = null;
        
        for (let attempt = 0; attempt < (this.config.maxRetries ?? 3); attempt++) {
            try {
                const controller = new AbortController();
                const timeout = setTimeout(() => controller.abort(), this.config.timeout ?? 30000);
                
                const resp = await fetch(url, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(params),
                    signal: controller.signal
                });
                
                clearTimeout(timeout);
                
                if (!resp.ok) {
                    throw new Error(`HTTP ${resp.status}: ${await resp.text()}`);
                }
                
                return await resp.json();
            } catch (err) {
                lastError = err as Error;
                if (attempt < (this.config.maxRetries ?? 3) - 1) {
                    await new Promise(r => setTimeout(r, Math.pow(2, attempt) * 1000));
                }
            }
        }
        
        throw lastError ?? new Error("Request failed");
    }
}
