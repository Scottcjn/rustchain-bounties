// SPDX-License-Identifier: MIT
/**
 * RustChain Development Tools — VS Code Extension
 *
 * Provides:
 * - RTC balance display in the status bar
 * - RustChain config file syntax highlighting
 * - Code snippets for RustChain development
 *
 * Bounty: #1619
 */

import * as vscode from "vscode";
import { BalanceStatusBar } from "./balanceStatusBar";
import { NodeHealthChecker } from "./nodeHealth";

let balanceStatusBar: BalanceStatusBar | undefined;
let nodeHealthChecker: NodeHealthChecker | undefined;

export function activate(context: vscode.ExtensionContext): void {
    const config = vscode.workspace.getConfiguration("rustchain");

    // --- Status bar: RTC balance ---
    balanceStatusBar = new BalanceStatusBar(context);

    // --- Node health checker ---
    nodeHealthChecker = new NodeHealthChecker();

    // --- Commands ---
    context.subscriptions.push(
        vscode.commands.registerCommand("rustchain.refreshBalance", () => {
            balanceStatusBar?.refresh();
        }),
    );

    context.subscriptions.push(
        vscode.commands.registerCommand("rustchain.setMinerId", async () => {
            const current = config.get<string>("minerId", "");
            const minerId = await vscode.window.showInputBox({
                prompt: "Enter your RustChain miner/wallet ID",
                placeHolder: "e.g. my-miner-name",
                value: current,
            });
            if (minerId !== undefined) {
                await vscode.workspace
                    .getConfiguration("rustchain")
                    .update("minerId", minerId, vscode.ConfigurationTarget.Global);
                balanceStatusBar?.refresh();
            }
        }),
    );

    context.subscriptions.push(
        vscode.commands.registerCommand("rustchain.checkNodeHealth", async () => {
            await nodeHealthChecker?.showHealth();
        }),
    );

    // React to configuration changes.
    context.subscriptions.push(
        vscode.workspace.onDidChangeConfiguration((e) => {
            if (e.affectsConfiguration("rustchain")) {
                balanceStatusBar?.onConfigChange();
            }
        }),
    );
}

export function deactivate(): void {
    balanceStatusBar?.dispose();
    balanceStatusBar = undefined;
    nodeHealthChecker = undefined;
}
