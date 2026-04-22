import * as vscode from 'vscode';
import * as https from 'https';

export interface Bounty {
    title: string;
    number: number;
    url: string;
    labels: string[];
}

export class BountyBrowserProvider implements vscode.TreeDataProvider<BountyItem> {
    private _onDidChangeTreeData: vscode.EventEmitter<BountyItem | undefined | null | void> = new vscode.EventEmitter<BountyItem | undefined | null | void>();
    readonly onDidChangeTreeData: vscode.Event<BountyItem | undefined | null | void> = this._onDidChangeTreeData.event;

    constructor() {}

    refresh(): void {
        this._onDidChangeTreeData.fire();
    }

    getTreeItem(element: BountyItem): vscode.TreeItem {
        return element;
    }

    async getChildren(element?: BountyItem): Promise<BountyItem[]> {
        if (element) {
            return [];
        } else {
            const bounties = await this.fetchBounties();
            return bounties.map(b => new BountyItem(b.title, b.number, b.url, vscode.TreeItemCollapsibleState.None));
        }
    }

    private async fetchBounties(): Promise<Bounty[]> {
        return new Promise((resolve, reject) => {
            const options = {
                hostname: 'api.github.com',
                path: '/repos/Scottcjn/rustchain-bounties/issues?labels=bounty&state=open',
                headers: { 'User-Agent': 'VSCode-RustChain-Extension' }
            };

            https.get(options, (res) => {
                let data = '';
                res.on('data', (chunk) => data += chunk);
                res.on('end', () => {
                    try {
                        const issues = JSON.parse(data);
                        resolve(issues.map((i: any) => ({
                            title: i.title,
                            number: i.number,
                            url: i.html_url,
                            labels: i.labels.map((l: any) => l.name)
                        })));
                    } catch (e) {
                        reject(e);
                    }
                });
            }).on('error', reject);
        });
    }
}

class BountyItem extends vscode.TreeItem {
    constructor(
        public readonly label: string,
        public readonly number: number,
        public readonly url: string,
        public readonly collapsibleState: vscode.TreeItemCollapsibleState
    ) {
        super(label, collapsibleState);
        this.tooltip = `#${this.number}: ${this.label}`;
        this.description = `#${this.number}`;
        this.command = {
            command: 'rustchain.openBounty',
            title: 'Open Bounty',
            arguments: [this.url]
        };
        this.iconPath = new vscode.ThemeIcon('gift');
    }
}
