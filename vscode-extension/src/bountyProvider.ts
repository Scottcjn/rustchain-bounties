import * as vscode from "vscode";

export class BountyProvider implements vscode.TreeDataProvider<BountyItem> {
    private _onDidChangeTreeData = new vscode.EventEmitter<BountyItem | undefined>();
    readonly onDidChangeTreeData = this._onDidChangeTreeData.event;

    refresh(): void {
        this._onDidChangeTreeData.fire(undefined);
    }

    getTreeItem(element: BountyItem): vscode.TreeItem {
        return element;
    }

    async getChildren(): Promise<BountyItem[]> {
        try {
            const config = vscode.workspace.getConfiguration("rustchain");
            const resp = await fetch(`${config.get("nodeUrl", "https://api.rustchain.io")}/v1/bounties?limit=20`);
            const data = await resp.json();
            const bounties = data.bounties || [];
            if (bounties.length === 0) return [new BountyItem("No open bounties", "", vscode.TreeItemCollapsibleState.None)];
            return bounties.map((b: any) => new BountyItem(
                `${b.reward || "?"} RTC — ${b.title || "Untitled"}`,
                b.url || "",
                vscode.TreeItemCollapsibleState.None
            ));
        } catch {
            return [new BountyItem("❌ Cannot load bounties", "", vscode.TreeItemCollapsibleState.None)];
        }
    }
}

class BountyItem extends vscode.TreeItem {
    constructor(label: string, readonly url: string, collapsible: vscode.TreeItemCollapsibleState) {
        super(label, collapsible);
        if (url) {
            this.command = { title: "Open", command: "vscode.open", arguments: [vscode.Uri.parse(url)] };
            this.tooltip = url;
        }
    }
}
