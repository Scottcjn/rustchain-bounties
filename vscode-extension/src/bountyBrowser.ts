// SPDX-License-Identifier: MIT
/**
 * Sidebar tree view: browse open RustChain bounties from GitHub.
 */

import * as https from "https";
import * as vscode from "vscode";

const BOUNTIES_URL =
    "https://api.github.com/repos/Scottcjn/rustchain-bounties/issues?state=open&labels=bounty&per_page=30";

interface BountyIssue {
    number: number;
    title: string;
    html_url: string;
    rtc: number;
}

function extractRtc(title: string): number {
    const m = title.match(/(\d+)\s*RTC/);
    return m ? parseInt(m[1], 10) : 0;
}

function fetchBounties(): Promise<BountyIssue[]> {
    return new Promise((resolve, reject) => {
        https.get(
            BOUNTIES_URL,
            {
                rejectUnauthorized: false,
                headers: { "User-Agent": "rustchain-vscode/1.0" },
                timeout: 10_000,
            },
            (res) => {
                const chunks: Buffer[] = [];
                res.on("data", (c: Buffer) => chunks.push(c));
                res.on("end", () => {
                    try {
                        const raw = JSON.parse(Buffer.concat(chunks).toString()) as Array<{
                            number: number;
                            title: string;
                            html_url: string;
                        }>;
                        const bounties = raw
                            .map((i) => ({
                                number: i.number,
                                title: i.title,
                                html_url: i.html_url,
                                rtc: extractRtc(i.title),
                            }))
                            .sort((a, b) => b.rtc - a.rtc);
                        resolve(bounties);
                    } catch (e) {
                        reject(e);
                    }
                });
            },
        ).on("error", reject);
    });
}

class BountyItem extends vscode.TreeItem {
    constructor(public readonly bounty: BountyIssue) {
        super(`${bounty.rtc} RTC — #${bounty.number}`, vscode.TreeItemCollapsibleState.None);
        this.description = bounty.title.replace(/\[BOUNTY[^\]]*\]/i, "").trim();
        this.tooltip = `${bounty.title}\n\nClick to open in browser`;
        this.command = {
            command: "vscode.open",
            title: "Open Bounty",
            arguments: [vscode.Uri.parse(bounty.html_url)],
        };
        this.iconPath = new vscode.ThemeIcon(
            bounty.rtc >= 50 ? "star-full" : bounty.rtc >= 20 ? "star-half" : "circle-small-filled",
        );
        this.contextValue = "bounty";
    }
}

export class BountyBrowserProvider
    implements vscode.TreeDataProvider<BountyItem>
{
    private _onDidChangeTreeData = new vscode.EventEmitter<BountyItem | undefined>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    private bounties: BountyIssue[] = [];
    private loading = false;
    private error: string | undefined;

    constructor(context: vscode.ExtensionContext) {
        context.subscriptions.push(
            vscode.commands.registerCommand("rustchain.refreshBounties", () =>
                this.refresh()
            ),
            vscode.commands.registerCommand("rustchain.claimBounty", (item: BountyItem) => {
                void vscode.env.openExternal(vscode.Uri.parse(item.bounty.html_url));
            }),
        );
        void this.refresh();
    }

    async refresh(): Promise<void> {
        this.loading = true;
        this.error = undefined;
        this._onDidChangeTreeData.fire(undefined);
        try {
            this.bounties = await fetchBounties();
        } catch (e) {
            this.error = e instanceof Error ? e.message : String(e);
            this.bounties = [];
        } finally {
            this.loading = false;
            this._onDidChangeTreeData.fire(undefined);
        }
    }

    getTreeItem(element: BountyItem): vscode.TreeItem {
        return element;
    }

    getChildren(): BountyItem[] {
        if (this.loading) {
            return [new BountyItem({ number: 0, title: "Loading bounties…", html_url: "", rtc: 0 })];
        }
        if (this.error) {
            return [new BountyItem({ number: 0, title: `Error: ${this.error}`, html_url: "", rtc: 0 })];
        }
        return this.bounties.map((b) => new BountyItem(b));
    }
}
