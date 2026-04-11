// SPDX-License-Identifier: MIT
/**
 * RustChain Development Tools — Epoch Timer
 *
 * Shows a countdown to the next epoch settlement in the status bar.
 * Updates every minute.
 */

import * as vscode from "vscode";
import { fetchEpoch } from "./rustchainApi";

const SECONDS_PER_SLOT = 30; // approximate

export class EpochTimer implements vscode.Disposable {
    private readonly item: vscode.StatusBarItem;
    private timer: ReturnType<typeof setInterval> | undefined;

    constructor(context: vscode.ExtensionContext) {
        this.item = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Left,
            52,
        );
        this.item.command = "rustchain.showEpochInfo";
        this.item.tooltip = "RustChain Epoch — click for details";
        context.subscriptions.push(this.item);

        this.startPolling();
        this.refresh();
    }

    async refresh(): Promise<void> {
        const config = vscode.workspace.getConfiguration("rustchain");
        const showTimer = config.get<boolean>("showEpochTimer", true);
        if (!showTimer) {
            this.item.hide();
            return;
        }

        try {
            const epoch = await fetchEpoch();
            const blocksPerEpoch = epoch.blocks_per_epoch;
            const currentSlot = epoch.slot;
            const slotsRemaining = Math.max(0, blocksPerEpoch - currentSlot);
            const secondsRemaining = slotsRemaining * SECONDS_PER_SLOT;

            const countdown = this.formatCountdown(secondsRemaining);

            this.item.text = `$(clock) Epoch ${epoch.epoch}: ${countdown}`;
            this.item.tooltip = [
                `Current Epoch: ${epoch.epoch}`,
                `Slot: ${currentSlot} / ${blocksPerEpoch}`,
                `Enrolled miners: ${epoch.enrolled_miners}`,
                `Epoch POT: ${epoch.epoch_pot}`,
                ``,
                `Next epoch in: ${countdown}`,
            ].join("\n");

        } catch {
            this.item.text = "$(clock) Epoch: --";
            this.item.tooltip = "Could not fetch epoch info";
        }

        this.item.show();
    }

    private formatCountdown(seconds: number): string {
        if (seconds <= 0) { return "settling..."; }

        const hours = Math.floor(seconds / 3600);
        const minutes = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;

        if (hours > 0) {
            return `${hours}h ${minutes}m`;
        } else if (minutes > 0) {
            return `${minutes}m ${secs}s`;
        } else {
            return `${secs}s`;
        }
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
        this.timer = setInterval(() => this.refresh(), 60_000); // every minute
    }

    private stopPolling(): void {
        if (this.timer !== undefined) {
            clearInterval(this.timer);
            this.timer = undefined;
        }
    }
}
