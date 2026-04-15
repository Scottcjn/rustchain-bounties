// SPDX-License-Identifier: MIT
/**
 * Status-bar item that shows a countdown to the next RustChain epoch settlement.
 *
 * Displays: "Epoch 42 · 1h 23m"
 * Refreshes epoch data every 5 minutes; the display ticks every second.
 */

import * as vscode from "vscode";
import { fetchEpoch, EpochInfo } from "./rustchainApi";

const FETCH_INTERVAL_MS = 5 * 60 * 1_000;  // re-fetch epoch data every 5 min
const TICK_INTERVAL_MS  = 1_000;            // update countdown every 1 s

// Assume 60 slots/epoch; each slot = ~30 s (tweak via config if needed)
const SLOTS_PER_EPOCH = 60;
const SLOT_DURATION_S = 30;

export class EpochTimer implements vscode.Disposable {
    private readonly item: vscode.StatusBarItem;
    private fetchTimer: ReturnType<typeof setInterval> | undefined;
    private tickTimer:  ReturnType<typeof setInterval> | undefined;

    private epochData: EpochInfo | null = null;
    private fetchedAt: number = 0; // Date.now() when we last fetched

    constructor(context: vscode.ExtensionContext) {
        this.item = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            48,
        );
        this.item.command = "rustchain.checkNodeHealth";
        this.item.tooltip = "Time until next RustChain epoch settlement — click for details";
        context.subscriptions.push(this.item);

        this.startFetching();
        this.startTicking();
        this.fetchNow();
    }

    dispose(): void {
        this.stopFetching();
        this.stopTicking();
        this.item.dispose();
    }

    // -------------------------------------------------------------------------

    private async fetchNow(): Promise<void> {
        try {
            this.epochData = await fetchEpoch();
            this.fetchedAt = Date.now();
        } catch {
            this.epochData = null;
        }
        this.tick();
    }

    private tick(): void {
        if (!this.epochData) {
            this.item.text = "$(clock) Epoch: offline";
            this.item.show();
            return;
        }

        const epoch = this.epochData;
        const slotsPer = epoch.blocks_per_epoch || SLOTS_PER_EPOCH;
        const currentSlot = epoch.slot;
        const slotsLeft = slotsPer - (currentSlot % slotsPer);

        // If the node provides seconds_until_next, use it adjusted for elapsed time.
        let secondsLeft: number;
        if (epoch.seconds_until_next !== undefined) {
            const elapsed = Math.floor((Date.now() - this.fetchedAt) / 1_000);
            secondsLeft = Math.max(0, epoch.seconds_until_next - elapsed);
        } else {
            secondsLeft = slotsLeft * SLOT_DURATION_S;
        }

        const h = Math.floor(secondsLeft / 3600);
        const m = Math.floor((secondsLeft % 3600) / 60);
        const s = secondsLeft % 60;

        let countdown: string;
        if (h > 0) {
            countdown = `${h}h ${m}m`;
        } else if (m > 0) {
            countdown = `${m}m ${s}s`;
        } else {
            countdown = `${s}s`;
        }

        this.item.text = `$(clock) Epoch ${epoch.epoch} · ${countdown}`;
        this.item.tooltip =
            `Epoch: ${epoch.epoch}  |  Slot: ${currentSlot}\n` +
            `Enrolled miners: ${epoch.enrolled_miners}\n` +
            `Next settlement in: ${countdown}\n` +
            `Epoch pot: ${epoch.epoch_pot} RTC`;
        this.item.show();
    }

    private startFetching(): void {
        this.fetchTimer = setInterval(() => this.fetchNow(), FETCH_INTERVAL_MS);
    }
    private stopFetching(): void {
        if (this.fetchTimer !== undefined) { clearInterval(this.fetchTimer); this.fetchTimer = undefined; }
    }
    private startTicking(): void {
        this.tickTimer = setInterval(() => this.tick(), TICK_INTERVAL_MS);
    }
    private stopTicking(): void {
        if (this.tickTimer !== undefined) { clearInterval(this.tickTimer); this.tickTimer = undefined; }
    }
}
