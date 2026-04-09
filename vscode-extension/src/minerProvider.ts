import * as vscode from "vscode";

export class MinerStatusProvider implements vscode.TreeDataProvider<MinerItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<MinerItem | undefined>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    constructor(private readonly context: vscode.ExtensionContext) {
        this.refresh();
    }

    refresh(): void {
        this._onDidChangeTreeData.fire(undefined);
    }

    getTreeItem(element: MinerItem): vscode.TreeItem {
        return element;
    }

    async getChildren(): Promise<MinerItem[]> {
        const config = vscode.workspace.getConfiguration("rustchain");
        const address = config.get<string>("walletAddress", "");
        if (!address) {
            return [new MinerItem("⚠️ Set wallet address in settings", vscode.TreeItemCollapsibleState.None)];
        }
        try {
            const resp = await fetch(`${config.get("nodeUrl", "https://api.rustchain.io")}/v1/miner/${address}/status`);
            const data = await resp.json();
            const attesting = data.attesting ?? false;
            return [
                new MinerItem(attesting ? "🟢 Attesting" : "🔴 Offline", vscode.TreeItemCollapsibleState.None),
                new MinerItem(`Miner: ${address.slice(0, 10)}...`, vscode.TreeItemCollapsibleState.None),
                new MinerItem(`Last Attestation: ${data.last_attestation || "N/A"}`, vscode.TreeItemCollapsibleState.None),
                new MinerItem(`Uptime: ${data.uptime || "N/A"}`, vscode.TreeItemCollapsibleState.None),
            ];
        } catch {
            return [new MinerItem("❌ Cannot reach node", vscode.TreeItemCollapsibleState.None)];
        }
    }
}

class MinerItem extends vscode.TreeItem {
    constructor(label: string, collapsible: vscode.TreeItemCollapsibleState) {
        super(label, collapsible);
    }
}
