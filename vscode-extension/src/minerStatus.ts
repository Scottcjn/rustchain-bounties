// SPDX-License-Identifier: MIT
/**
 * RustChain Development Tools — Miner Status
 *
 * Shows a green/red status bar indicator reflecting whether the user's
 * miner is currently active and attesting on the network.
 */

import * as vscode from "vscode";
import * as https from "https";
import { fetchHealth } from "./rustchainApi";

interface MinerInfo {
    miner_id: string;
    is_active: boolean;
    last_attestation_slot: number;
}

export class MinerStatus implements vscode.Disposable {
    private readonly item: vscode.StatusBarItem;
    private timer: ReturnType<typeof setInterval> | undefined;

    constructor(context: vscode.ExtensionContext) {
        this.item = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Left,
            51,
        );
        this.item.command = "rustchain.openMinerStatus";
        this.item.tooltip = "RustChain Miner Status — click for details";
        context.subscriptions.push(this.item);

        this.startPolling();
        this.refresh();
    }

    async refresh(): Promise<void> {
        const config = vscode.workspace.getConfiguration("rustchain");
        const showStatus = config.get<boolean>("showMinerStatus", true);
        if (!showStatus) {
            this.item.hide();
            return;
        }

        const minerId = config.get<string>("minerId", "");
        if (!minerId) {
            this.item.text = "$(chrome-close) Miner: not set";
            this.item.color = undefined;
            this.item.show();
            return;
        }

        try {
            const health = await fetchHealth();
            const isActive = await this.checkMinerAttesting(minerId);

            if (isActive) {
                this.item.text = "$(pass-filled) Miner: active";
                this.item.color = new vscode.ThemeColor("testing.iconPassed");
            } else {
                this.item.text = "$(error) Miner: idle";
                this.item.color = new vscode.ThemeColor("testing.iconFailed");
            }

            const uptime = health.uptime_s;
            const uptimeStr = uptime > 3600
                ? `${Math.floor(uptime / 3600)}h ${Math.floor((uptime % 3600) / 60)}m`
                : uptime > 60
                    ? `${Math.floor(uptime / 60)}m`
                    : `${uptime}s`;

            this.item.tooltip = [
                `Miner: ${minerId}`,
                `Status: ${isActive ? "Attesting" : "Idle"}`,
                `Node uptime: ${uptimeStr}`,
                `Version: ${health.version}`,
                ``,
                `Click to view full status`,
            ].join("\n");

        } catch {
            this.item.text = "$(warning) Miner: offline";
            this.item.color = new vscode.ThemeColor("testing.iconUnset");
            this.item.tooltip = "Could not reach the RustChain node";
        }

        this.item.show();
    }

    private async checkMinerAttesting(minerId: string): Promise<boolean> {
        try {
            const { nodeUrl, rejectUnauthorized } = this.getConfig();
            const url = new URL("/api/miners", nodeUrl);

            const result = await this.httpGet<{ miners: MinerInfo[] }>(
                url.toString(),
                rejectUnauthorized,
            );

            const miner = result.miners?.find(
                (m) => m.miner_id.toLowerCase() === minerId.toLowerCase(),
            );
            return miner?.is_active ?? false;
        } catch {
            return false;
        }
    }

    private httpGet<T>(url: string, rejectUnauthorized: boolean): Promise<T> {
        return new Promise((resolve, reject) => {
            const req = https.get(url, { rejectUnauthorized, timeout: 10_000 }, (res) => {
                if (res.statusCode === 429) {
                    reject(new Error("Rate limited"));
                    return;
                }
                if (res.statusCode && (res.statusCode < 200 || res.statusCode >= 300)) {
                    reject(new Error(`HTTP ${res.statusCode}`));
                    return;
                }
                const chunks: Buffer[] = [];
                res.on("data", (c: Buffer) => chunks.push(c));
                res.on("end", () => {
                    try {
                        resolve(JSON.parse(Buffer.concat(chunks).toString("utf-8")) as T);
                    } catch {
                        reject(new Error("Parse error"));
                    }
                });
            });
            req.on("error", reject);
            req.on("timeout", () => { req.destroy(); reject(new Error("Timeout")); });
        });
    }

    private getConfig(): { nodeUrl: string; rejectUnauthorized: boolean } {
        const config = vscode.workspace.getConfiguration("rustchain");
        return {
            nodeUrl: config.get<string>("nodeUrl", "https://50.28.86.131"),
            rejectUnauthorized: config.get<boolean>("rejectUnauthorized", false),
        };
    }

    onConfigChange(): void {
        this.stopPolling();
        this.startPolling();
        this.refresh();
    }

    dispose(): void {
        this.stopPolling();
        this.item.dispose();
    }

    private startPolling(): void {
        const intervalSec = 60;
        this.timer = setInterval(() => this.refresh(), intervalSec * 1000);
    }

    private stopPolling(): void {
        if (this.timer !== undefined) {
            clearInterval(this.timer);
            this.timer = undefined;
        }
    }
}
