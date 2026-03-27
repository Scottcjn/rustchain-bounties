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

// ---------------------------------------------------------------------------
// API client
// ---------------------------------------------------------------------------

function getConfig(): { nodeUrl: string; rejectUnauthorized: boolean } {
    const config = vscode.workspace.getConfiguration("rustchain");
    return {
        nodeUrl: config.get<string>("nodeUrl", "https://50.28.86.131"),
        rejectUnauthorized: config.get<boolean>("rejectUnauthorized", false),
    };
}

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
                    } catch (err) {
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
// Public API functions
// ---------------------------------------------------------------------------

export async function fetchBalance(minerId: string): Promise<WalletBalance> {
    if (!minerId) {
        throw new Error("No miner ID configured.");
    }
    return httpGet<WalletBalance>(
        `/wallet/balance?miner_id=${encodeURIComponent(minerId)}`,
    );
}

export async function fetchHealth(): Promise<NodeHealth> {
    return httpGet<NodeHealth>("/health");
}

export async function fetchEpoch(): Promise<EpochInfo> {
    return httpGet<EpochInfo>("/epoch");
}
