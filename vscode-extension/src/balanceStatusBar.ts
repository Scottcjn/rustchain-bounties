// SPDX-License-Identifier: MIT
/**
 * Status-bar item that shows the user's RTC wallet balance.
 *
 * The balance is fetched periodically from the configured RustChain node
 * and displayed in the VS Code status bar. Clicking the item opens the
 * "Set Miner ID" quick-input.
 */

import * as vscode from "vscode";
import { fetchBalance } from "./rustchainApi";

const DEFAULT_REFRESH_SECONDS = 120;
const MIN_REFRESH_SECONDS = 30;

export class BalanceStatusBar implements vscode.Disposable {
    private readonly item: vscode.StatusBarItem;
    private timer: ReturnType<typeof setInterval> | undefined;

    constructor(context: vscode.ExtensionContext) {
        this.item = vscode.window.createStatusBarItem(
            vscode.StatusBarAlignment.Right,
            50,
        );
        this.item.command = "rustchain.setMinerId";
        this.item.tooltip = "Click to set your RustChain miner/wallet ID";
        context.subscriptions.push(this.item);

        this.startPolling();
        // Immediately try to fetch on activation.
        this.refresh();
    }

    /** Fetch and display the current balance. */
    async refresh(): Promise<void> {
        const config = vscode.workspace.getConfiguration("rustchain");
        const showBalance = config.get<boolean>("showBalance", true);
        if (!showBalance) {
            this.item.hide();
            return;
        }

        const minerId = config.get<string>("minerId", "");
        if (!minerId) {
            this.item.text = "$(wallet) RTC: set wallet";
            this.item.tooltip = "Click to configure your RustChain miner/wallet ID";
            this.item.show();
            return;
        }

        try {
            const balance = await fetchBalance(minerId);
            const formatted = balance.amount_rtc.toLocaleString(undefined, {
                minimumFractionDigits: 2,
                maximumFractionDigits: 6,
            });
            this.item.text = `$(wallet) ${formatted} RTC`;
            this.item.tooltip = `Miner: ${balance.miner_id}\nBalance: ${formatted} RTC\n\nClick to change wallet ID`;
        } catch {
            this.item.text = "$(wallet) RTC: offline";
            this.item.tooltip = "Could not reach the RustChain node — click to configure";
        }

        this.item.show();
    }

    /** Restart the polling timer (called when config changes). */
    onConfigChange(): void {
        this.stopPolling();
        this.startPolling();
        this.refresh();
    }

    dispose(): void {
        this.stopPolling();
        this.item.dispose();
    }

    // ------------------------------------------------------------------

    private startPolling(): void {
        const config = vscode.workspace.getConfiguration("rustchain");
        const showBalance = config.get<boolean>("showBalance", true);
        if (!showBalance) {
            return;
        }

        let intervalSec = config.get<number>(
            "balanceRefreshInterval",
            DEFAULT_REFRESH_SECONDS,
        );
        if (intervalSec < MIN_REFRESH_SECONDS) {
            intervalSec = MIN_REFRESH_SECONDS;
        }

        this.timer = setInterval(() => {
            this.refresh();
        }, intervalSec * 1000);
    }

    private stopPolling(): void {
        if (this.timer !== undefined) {
            clearInterval(this.timer);
            this.timer = undefined;
        }
    }
}
