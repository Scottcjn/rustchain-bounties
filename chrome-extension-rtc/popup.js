const BASE_URL = 'https://50.28.86.131';

document.addEventListener('DOMContentLoaded', () => {
  const minerIdInput = document.getElementById('minerId');
  const checkBalanceBtn = document.getElementById('checkBalance');
  const refreshBtn = document.getElementById('refresh');
  const balanceEl = document.getElementById('balance');
  const balanceUsdEl = document.getElementById('balance-usd');
  const statusEl = document.getElementById('status');
  const errorEl = document.getElementById('error');

  // Load saved miner ID
  chrome.storage.local.get(['minerId'], (result) => {
    if (result.minerId) {
      minerIdInput.value = result.minerId;
      fetchBalance(result.minerId);
    }
  });

  // Check balance
  checkBalanceBtn.addEventListener('click', () => {
    const minerId = minerIdInput.value.trim();
    if (!minerId) {
      showError('Please enter your miner ID');
      return;
    }

    // Save miner ID
    chrome.storage.local.set({ minerId });

    fetchBalance(minerId);
  });

  // Refresh
  refreshBtn.addEventListener('click', () => {
    const minerId = minerIdInput.value.trim();
    if (minerId) {
      fetchBalance(minerId);
    }
  });

  async function fetchBalance(minerId) {
    try {
      errorEl.style.display = 'none';
      statusEl.textContent = 'Loading...';

      const response = await fetch(`${BASE_URL}/wallet/balance?miner_id=${encodeURIComponent(minerId)}`);
      const data = await response.json();

      if (data.amount_rtc !== undefined) {
        balanceEl.textContent = `${data.amount_rtc.toFixed(2)} RTC`;
        balanceUsdEl.textContent = `≈ $${(data.amount_rtc * 0.1).toFixed(2)} USD`;
        statusEl.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
      } else {
        showError('Failed to fetch balance');
      }
    } catch (error) {
      showError(`Error: ${error.message}`);
      statusEl.textContent = 'Last updated: Never';
    }
  }

  function showError(message) {
    errorEl.textContent = message;
    errorEl.style.display = 'block';
  }
});
