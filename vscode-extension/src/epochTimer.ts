// SPDX-License-Identifier: MIT
/**
 * Status-bar item showing epoch progress and countdown to next settlement.
 */

import * as vscode from "vscode";
import { fetchEpoch, EpochInfo } from "./rustchainApi";

const BLOCK_TIME_S = 600; // 10 minutes per slot

export class EpochTimer implements vscode.Disposable {
    private readonly item: vscode.StatusBarItem;
    private timer: ReturnType<typeof setInterval> | undefined;
    private lastEpoch: EpochInfo | undefined;

    constructor(context: vscode.ExtensionContext) {
        this.item = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            49, // just left of balance
        );
        this.item.command = "rustchain.checkNodeHealth";
        context.subscriptions.push(this.item);
        this.refresh();
        this.startPolling();
    }

    async refresh(): Promise<void> {
        try {
            const epoch = await fetchEpoch();
            this.lastEpoch = epoch;
            this.render(epoch);
        } catch {
            this.item.text = "$(clock) RTC: epoch?";
            this.item.tooltip = "Could not fetch epoch info";
            this.item.show();
        }
    }

    private render(epoch: EpochInfo): void {
        const slotsLeft = epoch.blocks_per_epoch - epoch.slot;
        const secsLeft = slotsLeft * BLOCK_TIME_S;
        const hoursLeft = Math.floor(secsLeft / 3600);
        const minsLeft = Math.floor((secsLeft % 3600) / 60);

        const timeStr =
            hoursLeft > 0
                ? `${hoursLeft}h ${minsLeft}m`
                : `${minsLeft}m`;

        this.item.text = `$(clock) E${epoch.epoch} ${timeStr}`;
        this.item.tooltip =
            `Epoch ${epoch.epoch}  |  Slot ${epoch.slot}/${epoch.blocks_per_epoch}\n` +
            `Next settlement in ~${timeStr}\n` +
            `Pot: ${epoch.epoch_pot.toFixed(2)} RTC  |  Miners: ${epoch.enrolled_miners}\n` +
            `Click to check node health`;
        this.item.show();
    }

    dispose(): void {
        this.stopPolling();
        this.item.dispose();
    }

    private startPolling(): void {
        this.timer = setInterval(() => void this.refresh(), 5 * 60 * 1000);
    }

    private stopPolling(): void {
        if (this.timer !== undefined) {
            clearInterval(this.timer);
            this.timer = undefined;
        }
    }
}
