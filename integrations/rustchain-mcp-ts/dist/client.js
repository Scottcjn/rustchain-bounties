/**
 * RustChain API client with automatic failover across multiple node URLs.
 */
import { z } from "zod";
const DEFAULT_PRIMARY = "https://50.28.86.131";
const DEFAULT_TIMEOUT_MS = 10_000;
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
    primaryUrl;
    fallbackUrls;
    timeoutMs;
    constructor(primaryUrl = DEFAULT_PRIMARY, fallbackUrls = [], timeoutMs = DEFAULT_TIMEOUT_MS) {
        this.primaryUrl = primaryUrl.replace(/\/$/, "");
        this.fallbackUrls = fallbackUrls
            .map((u) => u.replace(/\/$/, ""))
            .filter((u) => u && u !== this.primaryUrl);
        this.timeoutMs = timeoutMs;
    }
    /** Read configuration from environment variables. */
    static fromEnv() {
        const primary = (process.env.RUSTCHAIN_PRIMARY_URL ?? DEFAULT_PRIMARY).trim().replace(/\/$/, "") ||
            DEFAULT_PRIMARY;
        const fallbacksRaw = process.env.RUSTCHAIN_FALLBACK_URLS ?? "";
        const fallbacks = fallbacksRaw
            .split(",")
            .map((u) => u.trim().replace(/\/$/, ""))
            .filter(Boolean);
        const timeoutMs = parseInt(process.env.RUSTCHAIN_TIMEOUT_MS ?? String(DEFAULT_TIMEOUT_MS), 10);
        return new RustChainClient(primary, fallbacks, timeoutMs);
    }
    allUrls() {
        return [this.primaryUrl, ...this.fallbackUrls].filter(Boolean);
    }
    async getJson(path, params) {
        const qs = params ? "?" + new URLSearchParams(params).toString() : "";
        const lastErrors = [];
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
                    const json = (await res.json());
                    return json;
                }
                catch (rawErr) {
                    clearTimeout(timer);
                    const msg = rawErr instanceof Error ? rawErr.message : String(rawErr);
                    lastErrors.push(`${msg} from ${url}`);
                    continue;
                }
            }
            catch {
                lastErrors.push(`Unexpected error from ${url}`);
                continue;
            }
        }
        throw new Error(`All RustChain nodes failed for GET ${path}. Errors: ${lastErrors.join(" | ")}`);
    }
    // -------------------------------------------------------------------------
    // Public API methods
    // -------------------------------------------------------------------------
    async health() {
        return this.getJson("/health");
    }
    async miners() {
        return this.getJson("/api/miners");
    }
    async epoch() {
        return this.getJson("/epoch");
    }
    async balance(walletId) {
        return this.getJson("/wallet/balance", { wallet_id: walletId });
    }
    /** Register a new wallet on the RustChain network. */
    async createWallet(walletName) {
        return this.getJson("/wallet/create", { wallet_name: walletName });
    }
    /** Submit a hardware attestation for a miner. */
    async submitAttestation(walletId, hardwareFingerprint) {
        return this.getJson("/attestation/submit", {
            wallet_id: walletId,
            hardware_fingerprint: hardwareFingerprint,
        });
    }
}
//# sourceMappingURL=client.js.map