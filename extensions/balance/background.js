// RustChain Balance Extension - Background Service Worker

// Install event
chrome.runtime.onInstalled.addListener(() => {
  console.log('RustChain Balance extension installed');
  
  // Set default refresh interval
  chrome.alarms.create('refreshBalance', { periodInMinutes: 0.5 });
});

// Alarm event for auto-refresh
chrome.alarms.onAlarm.addListener((alarm) => {
  if (alarm.name === 'refreshBalance') {
    // Notify popup to refresh (if open)
    chrome.runtime.sendMessage({ action: 'refreshBalance' });
    
    // Update badge with latest balance (optional)
    updateBadge();
  }
});

// Message listener
chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
  if (request.action === 'getBalance') {
    fetchBalance(request.wallet)
      .then(balance => sendResponse({ balance }))
      .catch(error => sendResponse({ error: error.message }));
    return true; // Keep channel open for async response
  }
});

// Fetch balance from API
async function fetchBalance(wallet) {
  try {
    const response = await fetch('http://localhost:8545/api/v1/balance/' + wallet);
    if (response.ok) {
      const data = await response.json();
      return data.balance;
    }
  } catch (error) {
    console.error('Balance fetch error:', error);
  }
  return null;
}

// Update extension badge
async function updateBadge() {
  const result = await chrome.storage.local.get(['walletAddress']);
  if (result.walletAddress) {
    const balance = await fetchBalance(result.walletAddress);
    if (balance) {
      const display = balance > 999 ? '999+' : balance.toFixed(0);
      chrome.action.setBadgeText({ text: display.toString() });
      chrome.action.setBadgeBackgroundColor({ color: '#667eea' });
    }
  }
}
