// SPDX-License-Identifier: MIT
/**
 * Quick command to check RustChain node health and epoch info.
 */

import * as vscode from "vscode";
import { fetchHealth, fetchEpoch } from "./rustchainApi";

export class NodeHealthChecker {
    async showHealth(): Promise<void> {
        try {
            const [health, epoch] = await Promise.all([
                fetchHealth(),
                fetchEpoch(),
            ]);

            const uptimeHours = (health.uptime_s / 3600).toFixed(1);
            const lines = [
                `Node: ${health.ok ? "✅ Healthy" : "❌ Unhealthy"}`,
                `Version: ${health.version}`,
                `Uptime: ${uptimeHours} hours`,
                `Database R/W: ${health.db_rw ? "OK" : "Error"}`,
                `Tip age: ${health.tip_age_slots} slots`,
                "",
                `Epoch: ${epoch.epoch}  |  Slot: ${epoch.slot}`,
                `Enrolled miners: ${epoch.enrolled_miners}`,
                `Epoch pot: ${epoch.epoch_pot} RTC`,
                `Blocks/epoch: ${epoch.blocks_per_epoch}`,
            ];

            void vscode.window.showInformationMessage(
                lines.join("\n"),
                { modal: true },
            );
        } catch (err) {
            const message = err instanceof Error ? err.message : String(err);
            void vscode.window.showErrorMessage(
                `RustChain node unreachable: ${message}`,
            );
        }
    }
}
