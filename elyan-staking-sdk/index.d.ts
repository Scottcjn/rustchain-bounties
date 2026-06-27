export declare class StakingClient {
    private apiKey;
    private gatePubkey;
    private gateEndpoint;
    constructor(apiKey: string, gatePubkeyHex: string, gateEndpoint?: string);
    stake(amount: number, wallet: string): Promise<any>;
    submit(proof: string, txId: string): Promise<any>;
    poll(txId: string): Promise<any>;
    verify(verdict: any): Promise<boolean>;
    private verifyOnChain;
}
//# sourceMappingURL=index.d.ts.map