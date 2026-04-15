// SPDX-License-Identifier: MIT
/**
 * Thin wrapper around the RustChain node REST API.
 *
 * Uses the built-in Node.js `https` module so the extension has
 * zero runtime dependencies beyond VS Code itself.
 */

import * as https from "https";
import * as vscode from "vscode";

// ---------------------------------------------------------------------------
// Types
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
    /** Seconds until next epoch settlement (may not be present on all nodes) */
    seconds_until_next?: number;
}

export interface MinerInfo {
    miner_id: string;
    wallet_id?: string;
    last_seen?: number;
    attestations?: number;
    status?: string;
}

export interface GitHubIssue {
    number: number;
    title: string;
    html_url: string;
    labels: Array<{ name: string; color: string }>;
    created_at: string;
    reward?: string;
}

// ---------------------------------------------------------------------------
// Internal HTTP helper
// ---------------------------------------------------------------------------

function getConfig(): { nodeUrl: string; rejectUnauthorized: boolean } {
    const config = vscode.workspace.getConfiguration("rustchain");
    return {
        nodeUrl: config.get<string>("nodeUrl", "https://50.28.86.131"),
        rejectUnauthorized: config.get<boolean>("rejectUnauthorized", false),
    };
}

function httpGet<T>(path: string, timeoutMs: number = 10_000): Promise<T> {
    const { nodeUrl, rejectUnauthorized } = getConfig();
    const url = new URL(path, nodeUrl);

    return new Promise((resolve, reject) => {
        const req = https.get(url, { rejectUnauthorized, timeout: timeoutMs }, (res) => {
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
                    resolve(JSON.parse(Buffer.concat(chunks).toString("utf-8")) as T);
                } catch {
                    reject(new Error(`Failed to parse response from ${url.pathname}`));
                }
            });
        });
        req.on("error", reject);
        req.on("timeout", () => { req.destroy(); reject(new Error(`Timeout: ${url.pathname}`)); });
    });
}

function httpsGet<T>(url: string, timeoutMs: number = 10_000): Promise<T> {
    return new Promise((resolve, reject) => {
        const options = {
            timeout: timeoutMs,
            headers: { "User-Agent": "RustChain-VSCode-Extension/0.2.0" },
        };
        const req = https.get(url, options, (res) => {
            if (res.statusCode && (res.statusCode < 200 || res.statusCode >= 300)) {
                reject(new Error(`GitHub API returned HTTP ${res.statusCode}`));
                return;
            }
            const chunks: Buffer[] = [];
            res.on("data", (chunk: Buffer) => chunks.push(chunk));
            res.on("end", () => {
                try {
                    resolve(JSON.parse(Buffer.concat(chunks).toString("utf-8")) as T);
                } catch {
                    reject(new Error("Failed to parse GitHub response"));
                }
            });
        });
        req.on("error", reject);
        req.on("timeout", () => { req.destroy(); reject(new Error("GitHub request timed out")); });
    });
}

// ---------------------------------------------------------------------------
// Public API
// ---------------------------------------------------------------------------

export async function fetchBalance(minerId: string): Promise<WalletBalance> {
    if (!minerId) throw new Error("No miner ID configured.");
    return httpGet<WalletBalance>(`/wallet/balance?miner_id=${encodeURIComponent(minerId)}`);
}

export async function fetchHealth(): Promise<NodeHealth> {
    return httpGet<NodeHealth>("/health");
}

export async function fetchEpoch(): Promise<EpochInfo> {
    return httpGet<EpochInfo>("/epoch");
}

export async function fetchMiners(): Promise<MinerInfo[]> {
    const result = await httpGet<MinerInfo[] | { miners?: MinerInfo[] }>("/api/miners");
    return Array.isArray(result) ? result : (result.miners ?? []);
}

export async function fetchBounties(): Promise<GitHubIssue[]> {
    const url =
        "https://api.github.com/repos/Scottcjn/rustchain-bounties/issues" +
        "?state=open&labels=bounty&per_page=30&sort=created&direction=desc";
    const issues = await httpsGet<GitHubIssue[]>(url);
    return issues.map((issue) => ({
        ...issue,
        reward: extractReward(issue.title),
    }));
}

function extractReward(title: string): string | undefined {
    const m = title.match(/\[BOUNTY:\s*([^\]]+)\]/i);
    return m ? m[1].trim() : undefined;
}
