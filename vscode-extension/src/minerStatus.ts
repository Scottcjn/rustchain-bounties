// SPDX-License-Identifier: MIT
/**
 * Checks whether the configured wallet/miner is in the active miners list.
 * Shows a green/red indicator in the status bar.
 */

import * as vscode from "vscode";
import { fetchMiners } from "./rustchainApi";

export class MinerStatus implements vscode.Disposable {
    private readonly item: vscode.StatusBarItem;
    private timer: ReturnType<typeof setInterval> | undefined;

    constructor(context: vscode.ExtensionContext) {
        this.item = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            48,
        );
        this.item.command = "rustchain.checkNodeHealth";
        context.subscriptions.push(this.item);
        this.refresh();
        this.startPolling();
    }

    async refresh(): Promise<void> {
        const config = vscode.workspace.getConfiguration("rustchain");
        const minerId = config.get<string>("minerId", "");
        if (!minerId) {
            this.item.hide();
            return;
        }

        try {
            const data = await fetchMiners();
            const miners: Array<{ miner_id?: string }> = data?.miners ?? [];
            const isActive = miners.some(
                (m) => m.miner_id === minerId,
            );

            this.item.text = isActive
                ? "$(circle-filled) Mining"
                : "$(circle-slash) Idle";
            this.item.color = isActive
                ? new vscode.ThemeColor("charts.green")
                : new vscode.ThemeColor("charts.yellow");
            this.item.tooltip = isActive
                ? `Miner "${minerId}" is actively attesting`
                : `Miner "${minerId}" is not in the current active set`;
            this.item.show();
        } catch {
            this.item.text = "$(circle-slash) Offline";
            this.item.color = new vscode.ThemeColor("charts.red");
            this.item.tooltip = "Could not reach RustChain node";
            this.item.show();
        }
    }

    onConfigChange(): void {
        this.refresh();
    }

    dispose(): void {
        this.stopPolling();
        this.item.dispose();
    }

    private startPolling(): void {
        this.timer = setInterval(() => void this.refresh(), 3 * 60 * 1000);
    }

    private stopPolling(): void {
        if (this.timer !== undefined) {
            clearInterval(this.timer);
            this.timer = undefined;
        }
    }
}
