// SPDX-License-Identifier: MIT
/**
 * RustChain Development Tools — VS Code Extension
 *
 * Provides:
 * - RTC balance display in the status bar
 * - RustChain wallet dashboard view
 * - Commands: refresh balance, set miner ID, check node health,
 *   list miners, transfer RTC, view transactions, claim bounty
 * - RustChain config file syntax highlighting
 * - Code snippets for RustChain development
 *
 * Bounty: #2868
 * Wallet: RTCd5fbce79a0e0826d41a3736cfeacd5a5b921e6e5
 */

import * as vscode from "vscode";
import { BalanceStatusBar } from "./balanceStatusBar";
import { NodeHealthChecker } from "./nodeHealth";
import { WalletViewProvider } from "./walletView";
import { fetchMiners, fetchTransactions, submitTransfer, claimBountyOnChain } from "./rustchainApi";

let balanceStatusBar: BalanceStatusBar | undefined;
let nodeHealthChecker: NodeHealthChecker | undefined;
let walletViewProvider: WalletViewProvider | undefined;

export function activate(context: vscode.ExtensionContext): void {
    const config = vscode.workspace.getConfiguration("rustchain");

    // --- Status bar: RTC balance ---
    balanceStatusBar = new BalanceStatusBar(context);

    // --- Node health checker ---
    nodeHealthChecker = new NodeHealthChecker();

    // --- Wallet view provider ---
    walletViewProvider = new WalletViewProvider(context);

    // --- Commands ---

    // rustchain.refreshBalance
    context.subscriptions.push(
        vscode.commands.registerCommand("rustchain.refreshBalance", () => {
            balanceStatusBar?.refresh();
            walletViewProvider?.refresh();
        }),
    );

    // rustchain.setMinerId
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
                walletViewProvider?.refresh();
            }
        }),
    );

    // rustchain.checkNodeHealth
    context.subscriptions.push(
        vscode.commands.registerCommand("rustchain.checkNodeHealth", async () => {
            await nodeHealthChecker?.showHealth();
        }),
    );

    // rustchain.openWalletView
    context.subscriptions.push(
        vscode.commands.registerCommand("rustchain.openWalletView", async () => {
            await walletViewProvider?.show();
        }),
    );

    // rustchain.listMiners
    context.subscriptions.push(
        vscode.commands.registerCommand("rustchain.listMiners", async () => {
            const minerId = config.get<string>("minerId", "");
            if (!minerId) {
                void vscode.window.showWarningMessage(
                    "No miner ID configured. Run 'RustChain: Set Miner/Wallet ID' first.",
                );
                return;
            }

            await vscode.window.withProgress(
                { location: vscode.ProgressLocation.Notification, title: "Fetching miners..." },
                async () => {
                    try {
                        const miners = await fetchMiners();
                        const lines = miners.map(
                            (m) =>
                                `• ${m.miner}  (multiplier: ${m.antiquity_multiplier}x, enrolled: ${m.is_enrolled})`,
                        );
                        const msg = lines.length > 0
                            ? `Active miners (${miners.length}):\n\n${lines.join("\n")}`
                            : "No active miners found.";
                        void vscode.window.showInformationMessage(msg, { modal: true });
                    } catch (err) {
                        const msg = err instanceof Error ? err.message : String(err);
                        void vscode.window.showErrorMessage(`Failed to list miners: ${msg}`);
                    }
                },
            );
        }),
    );

    // rustchain.transfer
    context.subscriptions.push(
        vscode.commands.registerCommand("rustchain.transfer", async () => {
            const minerId = config.get<string>("minerId", "");
            if (!minerId) {
                void vscode.window.showWarningMessage(
                    "No miner ID configured. Run 'RustChain: Set Miner/Wallet ID' first.",
                );
                return;
            }

            const to = await vscode.window.showInputBox({
                prompt: "Recipient wallet address",
                placeHolder: "RTC...",
            });
            if (!to) { return; }

            const amountStr = await vscode.window.showInputBox({
                prompt: "Amount to transfer (RTC)",
                placeHolder: "10.0",
            });
            if (!amountStr) { return; }

            const amount = parseFloat(amountStr);
            if (isNaN(amount) || amount <= 0) {
                void vscode.window.showErrorMessage("Invalid amount.");
                return;
            }

            await vscode.window.withProgress(
                { location: vscode.ProgressLocation.Notification, title: "Submitting transfer..." },
                async () => {
                    try {
                        const result = await submitTransfer({ to, amount, from_miner_id: minerId });
                        if (result.success) {
                            void vscode.window.showInformationMessage(
                                `Transfer successful!\nTx: ${result.tx_hash}`,
                            );
                        } else {
                            void vscode.window.showErrorMessage(`Transfer failed: ${result.message}`);
                        }
                    } catch (err) {
                        const msg = err instanceof Error ? err.message : String(err);
                        void vscode.window.showErrorMessage(`Transfer failed: ${msg}`);
                    }
                },
            );
        }),
    );

    // rustchain.viewTransactions
    context.subscriptions.push(
        vscode.commands.registerCommand("rustchain.viewTransactions", async () => {
            const minerId = config.get<string>("minerId", "");
            if (!minerId) {
                void vscode.window.showWarningMessage(
                    "No miner ID configured. Run 'RustChain: Set Miner/Wallet ID' first.",
                );
                return;
            }

            await vscode.window.withProgress(
                { location: vscode.ProgressLocation.Notification, title: "Fetching transactions..." },
                async () => {
                    try {
                        const txs = await fetchTransactions(minerId);
                        if (txs.length === 0) {
                            void vscode.window.showInformationMessage("No transactions found.");
                            return;
                        }
                        const lines = txs.map(
                            (t) =>
                                `${t.confirmed ? "✅" : "⏳"} ${t.amount_rtc} RTC: ${t.from} → ${t.to} (${t.tx_hash.slice(0, 12)}...)`,
                        );
                        void vscode.window.showInformationMessage(
                            `Transactions (${txs.length}):\n\n${lines.join("\n")}`,
                            { modal: true },
                        );
                    } catch (err) {
                        const msg = err instanceof Error ? err.message : String(err);
                        void vscode.window.showErrorMessage(`Failed to fetch transactions: ${msg}`);
                    }
                },
            );
        }),
    );

    // rustchain.claimBounty
    context.subscriptions.push(
        vscode.commands.registerCommand("rustchain.claimBounty", async () => {
            const minerId = config.get<string>("minerId", "");
            if (!minerId) {
                void vscode.window.showWarningMessage(
                    "No miner ID configured. Run 'RustChain: Set Miner/Wallet ID' first.",
                );
                return;
            }

            const bountyId = await vscode.window.showInputBox({
                prompt: "Bounty issue number to claim",
                placeHolder: "2868",
            });
            if (!bountyId) { return; }

            const numId = parseInt(bountyId, 10);
            if (isNaN(numId) || numId <= 0) {
                void vscode.window.showErrorMessage("Invalid bounty number.");
                return;
            }

            await vscode.window.withProgress(
                { location: vscode.ProgressLocation.Notification, title: `Claiming bounty #${bountyId}...` },
                async () => {
                    try {
                        const result = await claimBountyOnChain(String(numId), minerId);
                        if (result.success) {
                            void vscode.window.showInformationMessage(
                                `Bounty #${bountyId} claimed!\nTx: ${result.tx_hash}\n\nWallet: RTCd5fbce79a0e0826d41a3736cfeacd5a5b921e6e5`,
                            );
                        } else {
                            void vscode.window.showErrorMessage(`Claim failed: ${result.message}`);
                        }
                    } catch (err) {
                        const msg = err instanceof Error ? err.message : String(err);
                        void vscode.window.showErrorMessage(`Claim failed: ${msg}`);
                    }
                },
            );
        }),
    );

    // React to configuration changes.
    context.subscriptions.push(
        vscode.workspace.onDidChangeConfiguration((e) => {
            if (e.affectsConfiguration("rustchain")) {
                balanceStatusBar?.onConfigChange();
                walletViewProvider?.refresh();
            }
        }),
    );
}

export function deactivate(): void {
    balanceStatusBar?.dispose();
    balanceStatusBar = undefined;
    nodeHealthChecker = undefined;
    walletViewProvider = undefined;
}
