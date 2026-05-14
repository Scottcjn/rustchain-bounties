const vscode = require('vscode');

/**
 * Manages the RustChain status bar item.
 */
class StatusBar {
  /**
   * @param {import('./apiClient').ApiClient} apiClient
   */
  constructor(apiClient) {
    this.apiClient = apiClient;
    this._statusBarItem = vscode.window.createStatusBarItem(
      vscode.StatusBarAlignment.Left,
      50
    );
    this._statusBarItem.command = 'rustchain.openDashboard';
    this._statusBarItem.tooltip = 'RustChain — Click to open Dashboard';
  }

  activate(subscriptions) {
    subscriptions.push(this._statusBarItem);
    this.refresh().catch(() => {});
  }

  async refresh() {
    try {
      const [balance, network] = await Promise.all([
        this.apiClient.getBalance(),
        this.apiClient.getNetworkStatus(),
      ]);
      this._statusBarItem.text = `$(diamond) ${balance.amount} RTC | Epoch ${network.epoch}`;
      this._statusBarItem.show();
    } catch (err) {
      this._statusBarItem.text = '$(warning) RTC: offline';
      this._statusBarItem.show();
    }
  }
}

module.exports = { StatusBar };
