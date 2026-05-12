import * as vscode from 'vscode';

// Fetches wallet and miner status information from the RustChain API.
async function fetchWalletInfo(nodeUrl: string, walletId: string) {
  // TODO: Implement API calls to RustChain node for balance, miner status, epoch countdown and bounty list.
  // Placeholder returns dummy data for now.
  return {
    balance: 0,
    minerStatus: 'offline',
    epochCountdown: '00:00:00',
    bounties: [] as string[],
  };
}

export async function activate(context: vscode.ExtensionContext) {
  const configuration = vscode.workspace.getConfiguration();
  const nodeUrl = configuration.get<string>('rustchainWallet.nodeUrl') ?? 'https://api.rustchain.org';
  const walletId = configuration.get<string>('rustchainWallet.walletId') ?? '';

  // Create a status bar item to display the RTC balance, miner status and epoch countdown.
  const statusBarItem = vscode.window.createStatusBarItem(vscode.StatusBarAlignment.Left);
  statusBarItem.text = 'RustChain: Loading...';
  statusBarItem.show();
  context.subscriptions.push(statusBarItem);

  // Updates the status bar with latest information.
  async function updateDashboard() {
    try {
      const info = await fetchWalletInfo(nodeUrl, walletId);
      statusBarItem.text = `RTC ${info.balance} | Miner: ${info.minerStatus} | Next epoch: ${info.epochCountdown}`;
    } catch (err) {
      statusBarItem.text = 'RustChain: Error fetching info';
      console.error(err);
    }
  }

  // Register command to show dashboard; will open an information message for now.
  const showDashboardCommand = vscode.commands.registerCommand('rustchain-wallet-dashboard.showDashboard', async () => {
    await updateDashboard();
    vscode.window.showInformationMessage('RustChain Wallet Dashboard opened (UI under construction).');
  });

  context.subscriptions.push(showDashboardCommand);

  // Periodically refresh dashboard every minute.
  const interval = setInterval(updateDashboard, 60000);
  context.subscriptions.push({ dispose: () => clearInterval(interval) });

  // Perform initial update on activation.
  updateDashboard();
}

export function deactivate() {
  // Clean up resources if necessary.
}
