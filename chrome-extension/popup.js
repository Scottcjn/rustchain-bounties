// RustChain Balance Chrome Extension
// Load saved wallet
chrome.storage.local.get(['walletId'], (result) => {
  if (result.walletId) {
    document.getElementById('walletId').value = result.walletId;
    fetchBalance(result.walletId);
  }
});

// Save wallet and load balance
document.getElementById('saveBtn').addEventListener('click', () => {
  const walletId = document.getElementById('walletId').value;
  chrome.storage.local.set({ walletId }, () => {
    fetchBalance(walletId);
  });
});

// Fetch balance from RustChain API
function fetchBalance(walletId) {
  fetch(`https://50.28.86.131/wallet/balance?miner_id=${walletId}`, {
    method: 'GET',
    headers: { 'Accept': 'application/json' }
  })
  .then(res => res.json())
  .then(data => {
    document.getElementById('balance').textContent = `${data.amount_rtc} RTC`;
    document.getElementById('usd').textContent = `≈ $${(data.amount_rtc * 0.1).toFixed(2)} USD`;
  })
  .catch(err => {
    document.getElementById('balance').textContent = 'Error';
    console.error(err);
  });
}

// Auto-refresh every 30 seconds
chrome.alarms.create('refreshBalance', { periodInMinutes: 0.5 });
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'refreshBalance') {
    chrome.storage.local.get(['walletId'], (result) => {
      if (result.walletId) fetchBalance(result.walletId);
    });
  }
});
