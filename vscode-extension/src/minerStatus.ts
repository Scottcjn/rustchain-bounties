// SPDX-License-Identifier: MIT
/**
 * Status-bar item that shows whether the configured miner is actively attesting.
 *
 * Polls /api/miners and shows:
 *   🟢 Attesting   — miner appears in the active list
 *   🔴 Idle        — miner not found in active list
 *   ⚠️ Node offline — request failed
 */

import * as vscode from "vscode";
import { fetchMiners } from "./rustchainApi";

const POLL_INTERVAL_MS = 60_000; // 1 minute

export class MinerStatusBar implements vscode.Disposable {
    private readonly item: vscode.StatusBarItem;
    private timer: ReturnType<typeof setInterval> | undefined;

    constructor(context: vscode.ExtensionContext) {
        this.item = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            49, // Just left of the balance item
        );
        this.item.command = "rustchain.checkNodeHealth";
        context.subscriptions.push(this.item);
        this.startPolling();
        this.refresh();
    }

    async refresh(): Promise<void> {
        const config = vscode.workspace.getConfiguration("rustchain");
        const minerId = config.get<string>("minerId", "");
        if (!minerId) {
            this.item.text = "$(circle-slash) RTC miner";
            this.item.tooltip = "Configure your miner ID to see attestation status";
            this.item.show();
            return;
        }

        try {
            const miners = await fetchMiners();
            const activeIds = new Set(
                miners.map((m) => m.miner_id || m.wallet_id || "")
            );
            const isActive = activeIds.has(minerId);
            if (isActive) {
                this.item.text = "$(circle-filled) Attesting";
                this.item.color = new vscode.ThemeColor("testing.iconPassed");
                this.item.tooltip = `Miner ${minerId} is actively attesting\nActive miners: ${miners.length}`;
            } else {
                this.item.text = "$(circle-slash) Idle";
                this.item.color = new vscode.ThemeColor("testing.iconFailed");
                this.item.tooltip = `Miner ${minerId} is NOT in the active attestation set\nActive miners: ${miners.length}`;
            }
        } catch {
            this.item.text = "$(warning) Node offline";
            this.item.color = new vscode.ThemeColor("editorWarning.foreground");
            this.item.tooltip = "Could not reach the RustChain node";
        }

        this.item.show();
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
        this.timer = setInterval(() => this.refresh(), POLL_INTERVAL_MS);
    }

    private stopPolling(): void {
        if (this.timer !== undefined) {
            clearInterval(this.timer);
            this.timer = undefined;
        }
    }
}
