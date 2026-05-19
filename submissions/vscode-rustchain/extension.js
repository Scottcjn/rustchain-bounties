const vscode = require('vscode');
const { StatusBar } = require('./src/statusBar');
const { ApiClient } = require('./src/apiClient');
const { WalletPanel } = require('./src/walletPanel');

let statusBar;
let apiClient;
let refreshTimer;

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
  const config = vscode.workspace.getConfiguration('rustchain');
  apiClient = new ApiClient(config.get('apiUrl'), config.get('walletAddress'));
  statusBar = new StatusBar(apiClient);

  // Register commands
  context.subscriptions.push(
    vscode.commands.registerCommand('rustchain.showBalance', async () => {
      try {
        const balance = await apiClient.getBalance();
        vscode.window.showInformationMessage(
          `RustChain Balance: ${balance.amount} RTC`
        );
      } catch (err) {
        vscode.window.showErrorMessage(`Failed to fetch balance: ${err.message}`);
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('rustchain.showNetworkStatus', async () => {
      try {
        const status = await apiClient.getNetworkStatus();
        vscode.window.showInformationMessage(
          `RustChain Network — Epoch: ${status.epoch} | Peers: ${status.peers} | Block Height: ${status.blockHeight}`
        );
      } catch (err) {
        vscode.window.showErrorMessage(`Failed to fetch network status: ${err.message}`);
      }
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('rustchain.openDashboard', () => {
      WalletPanel.createOrShow(context.extensionUri, apiClient);
    })
  );

  context.subscriptions.push(
    vscode.commands.registerCommand('rustchain.refreshData', async () => {
      try {
        await statusBar.refresh();
        vscode.window.showInformationMessage('RustChain data refreshed.');
      } catch (err) {
        vscode.window.showErrorMessage(`Refresh failed: ${err.message}`);
      }
    })
  );

  // Start status bar
  statusBar.activate(context.subscriptions);

  // Auto-refresh
  setupAutoRefresh(context);

  vscode.window.showInformationMessage('RustChain Wallet & Miner Dashboard activated ⛏️');
}

function setupAutoRefresh(context) {
  if (refreshTimer) {
    clearInterval(refreshTimer);
  }
  const config = vscode.workspace.getConfiguration('rustchain');
  const interval = config.get('refreshInterval', 60);
  if (interval > 0) {
    refreshTimer = setInterval(() => {
      statusBar.refresh().catch(() => {});
      if (WalletPanel.currentPanel) {
        WalletPanel.currentPanel.refresh().catch(() => {});
      }
    }, interval * 1000);
    context.subscriptions.push({ dispose: () => clearInterval(refreshTimer) });
  }
}

function deactivate() {
  if (refreshTimer) {
    clearInterval(refreshTimer);
  }
}

module.exports = { activate, deactivate };
