/**
 * RustChain API client with automatic failover across multiple node URLs.
 */
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
export declare class RustChainClient {
    private primaryUrl;
    private fallbackUrls;
    private timeoutMs;
    constructor(primaryUrl?: string, fallbackUrls?: string[], timeoutMs?: number);
    /** Read configuration from environment variables. */
    static fromEnv(): RustChainClient;
    private allUrls;
    private getJson;
    health(): Promise<HealthResponse>;
    miners(): Promise<MinerInfo[]>;
    epoch(): Promise<EpochResponse>;
    balance(walletId: string): Promise<BalanceResponse>;
    /** Register a new wallet on the RustChain network. */
    createWallet(walletName: string): Promise<WalletCreationResponse>;
    /** Submit a hardware attestation for a miner. */
    submitAttestation(walletId: string, hardwareFingerprint: string): Promise<AttestationResponse>;
}
//# sourceMappingURL=client.d.ts.map