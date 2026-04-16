// SPDX-License-Identifier: MIT
/**
 * Thin wrapper around the RustChain node REST API.
 *
 * Uses the built-in Node.js `https` module so the extension has
 * zero runtime dependencies beyond VS Code itself.
 *
 * Includes a mock/stub API layer for development/demo when the
 * actual node (https://50.28.86.131:8099) is unreachable.
 */

import * as https from "https";
import * as vscode from "vscode";

// ---------------------------------------------------------------------------
// Types (match API response shapes from docs/API_REFERENCE.md)
// ---------------------------------------------------------------------------

export interface WalletBalance {
    amount_i64: number;
    amount_rtc: number;
    miner_id: string;
}

export interface NodeHealth {
    backup_age_hours: number;
    db_rw: boolean;
    ok: boolean;
    tip_age_slots: number;
    uptime_s: number;
    version: string;
}

export interface EpochInfo {
    blocks_per_epoch: number;
    enrolled_miners: number;
    epoch: number;
    epoch_pot: number;
    slot: number;
}

export interface MinerInfo {
    miner: string;
    antiquity_multiplier: number;
    last_attestation_s: number;
    is_enrolled: boolean;
}

export interface Transaction {
    tx_hash: string;
    from: string;
    to: string;
    amount_rtc: number;
    timestamp: number;
    confirmed: boolean;
}

export interface TransferRequest {
    to: string;
    amount: number;
    from_miner_id?: string;
}

export interface TransferResult {
    success: boolean;
    tx_hash?: string;
    message: string;
}

// ---------------------------------------------------------------------------
// Mock data for development/demo when node is unreachable
// ---------------------------------------------------------------------------

const MOCK_MINERS: MinerInfo[] = [
    { miner: "retro-pc-386", antiquity_multiplier: 4.2, last_attestation_s: 162000, is_enrolled: true },
    { miner: "mac-classic-se", antiquity_multiplier: 3.8, last_attestation_s: 158000, is_enrolled: true },
    { miner: "sun-workstation", antiquity_multiplier: 3.5, last_attestation_s: 155000, is_enrolled: true },
    { miner: "commodore-64", antiquity_multiplier: 3.1, last_attestation_s: 152000, is_enrolled: true },
    { miner: "ibm-5150", antiquity_multiplier: 2.9, last_attestation_s: 149000, is_enrolled: true },
];

const MOCK_TRANSACTIONS: Transaction[] = [
    { tx_hash: "0xabc123...", from: "founder_community", to: "demo-miner-1", amount_rtc: 25.0, timestamp: 1713000000, confirmed: true },
    { tx_hash: "0xdef456...", from: "founder_team_bounty", to: "demo-miner-1", amount_rtc: 10.0, timestamp: 1712900000, confirmed: true },
    { tx_hash: "0xghi789...", from: "founder_dev_fund", to: "demo-miner-1", amount_rtc: 5.0, timestamp: 1712800000, confirmed: false },
];

// ---------------------------------------------------------------------------
// Configuration helper
// ---------------------------------------------------------------------------

function getConfig(): { nodeUrl: string; rejectUnauthorized: boolean; useMockApi: boolean } {
    const config = vscode.workspace.getConfiguration("rustchain");
    return {
        nodeUrl: config.get<string>("nodeUrl", "https://50.28.86.131"),
        rejectUnauthorized: config.get<boolean>("rejectUnauthorized", false),
        useMockApi: config.get<boolean>("useMockApi", true),
    };
}

// ---------------------------------------------------------------------------
// HTTPS request helper
// ---------------------------------------------------------------------------

/**
 * Perform an HTTPS GET request against the configured RustChain node.
 *
 * The default node uses a self-signed certificate, so we allow disabling
 * TLS verification via the `rustchain.rejectUnauthorized` setting.
 */
function httpGet<T>(path: string, timeoutMs: number = 10_000): Promise<T> {
    const { nodeUrl, rejectUnauthorized } = getConfig();
    const url = new URL(path, nodeUrl);

    return new Promise((resolve, reject) => {
        const req = https.get(
            url,
            { rejectUnauthorized, timeout: timeoutMs },
            (res) => {
                if (res.statusCode === 429) {
                    reject(new Error("Rate limited (HTTP 429) — try again later."));
                    return;
                }
                if (res.statusCode && (res.statusCode < 200 || res.statusCode >= 300)) {
                    reject(new Error(`HTTP ${res.statusCode} from ${url.pathname}`));
                    return;
                }

                const chunks: Buffer[] = [];
                res.on("data", (chunk: Buffer) => chunks.push(chunk));
                res.on("end", () => {
                    try {
                        const body = Buffer.concat(chunks).toString("utf-8");
                        resolve(JSON.parse(body) as T);
                    } catch {
                        reject(new Error(`Failed to parse response from ${url.pathname}`));
                    }
                });
            },
        );

        req.on("error", (err) => reject(err));
        req.on("timeout", () => {
            req.destroy();
            reject(new Error(`Request to ${url.pathname} timed out after ${timeoutMs}ms`));
        });
    });
}

// ---------------------------------------------------------------------------
// Mock API functions (used when node is unreachable and useMockApi=true)
// ---------------------------------------------------------------------------

function getMockBalance(minerId: string): WalletBalance {
    // Generate a deterministic-ish balance based on miner ID
    const hash = minerId.split("").reduce((acc, c) => acc + c.charCodeAt(0), 0);
    const amount = 100 + (hash % 1000) + Math.random() * 10;
    return {
        amount_i64: Math.floor(amount * 1000000),
        amount_rtc: parseFloat(amount.toFixed(6)),
        miner_id: minerId,
    };
}

function getMockHealth(): NodeHealth {
    return {
        backup_age_hours: 0.5,
        db_rw: true,
        ok: true,
        tip_age_slots: 3,
        uptime_s: 864000,
        version: "1.4.2-mock",
    };
}

function getMockEpoch(): EpochInfo {
    return {
        blocks_per_epoch: 1000,
        enrolled_miners: MOCK_MINERS.length,
        epoch: 42,
        epoch_pot: 5000.0,
        slot: 750,
    };
}

function getMockMiners(): MinerInfo[] {
    return MOCK_MINERS;
}

function getMockTransactions(minerId: string): Transaction[] {
    return MOCK_TRANSACTIONS.map((tx) => ({
        ...tx,
        to: minerId || "demo-miner-1",
    }));
}

function mockTransfer(_req: TransferRequest): TransferResult {
    // Simulate a transfer
    return {
        success: true,
        tx_hash: "0x" + Math.random().toString(16).slice(2, 66),
        message: "Transfer submitted successfully (mock)",
    };
}

// ---------------------------------------------------------------------------
// Public API functions (try real API, fall back to mock if configured)
// ---------------------------------------------------------------------------

export async function fetchBalance(minerId: string): Promise<WalletBalance> {
    if (!minerId) {
        throw new Error("No miner ID configured.");
    }

    const { useMockApi } = getConfig();

    try {
        return await httpGet<WalletBalance>(
            `/wallet/balance?miner_id=${encodeURIComponent(minerId)}`,
        );
    } catch (err) {
        if (useMockApi) {
            console.log(`[RustChain] Using mock balance for ${minerId}`);
            return getMockBalance(minerId);
        }
        throw err;
    }
}

export async function fetchHealth(): Promise<NodeHealth> {
    const { useMockApi } = getConfig();

    try {
        return await httpGet<NodeHealth>("/health");
    } catch {
        if (useMockApi) {
            console.log("[RustChain] Using mock health data");
            return getMockHealth();
        }
        throw new Error("Node unreachable and mock API disabled");
    }
}

export async function fetchEpoch(): Promise<EpochInfo> {
    const { useMockApi } = getConfig();

    try {
        return await httpGet<EpochInfo>("/epoch");
    } catch {
        if (useMockApi) {
            console.log("[RustChain] Using mock epoch data");
            return getMockEpoch();
        }
        throw new Error("Node unreachable and mock API disabled");
    }
}

export async function fetchMiners(): Promise<MinerInfo[]> {
    const { useMockApi } = getConfig();

    try {
        return await httpGet<MinerInfo[]>("/api/miners");
    } catch {
        if (useMockApi) {
            console.log("[RustChain] Using mock miners data");
            return getMockMiners();
        }
        throw new Error("Node unreachable and mock API disabled");
    }
}

export async function fetchTransactions(minerId: string): Promise<Transaction[]> {
    const { useMockApi } = getConfig();

    try {
        return await httpGet<Transaction[]>(
            `/wallet/transactions?miner_id=${encodeURIComponent(minerId)}`,
        );
    } catch {
        if (useMockApi) {
            console.log(`[RustChain] Using mock transactions for ${minerId}`);
            return getMockTransactions(minerId);
        }
        throw new Error("Node unreachable and mock API disabled");
    }
}

export async function submitTransfer(req: TransferRequest): Promise<TransferResult> {
    const { useMockApi } = getConfig();

    // Real node would use POST to /wallet/transfer
    // For now, use mock if configured
    if (useMockApi) {
        console.log(`[RustChain] Mock transfer: ${req.amount} RTC to ${req.to}`);
        return mockTransfer(req);
    }

    throw new Error("Real transfer API not implemented — enable mock API for testing");
}

export async function checkBountyEligibility(bountyId: string, minerId: string): Promise<boolean> {
    // This would check if a miner is eligible to claim a bounty
    // For now, return true if we have a miner ID
    return minerId.length > 0;
}

export async function claimBountyOnChain(bountyId: string, minerId: string): Promise<TransferResult> {
    // This would submit a claim transaction to the RustChain blockchain
    // For now, return a mock success
    return {
        success: true,
        tx_hash: "0x" + Math.random().toString(16).slice(2, 66),
        message: `Bounty #${bountyId} claimed by ${minerId} (mock)`,
    };
}
