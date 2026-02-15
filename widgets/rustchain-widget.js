/**
 * RustChain Dashboard Widget
 * Embeddable widget showing live RustChain network stats
 * 
 * Usage:
 *   <div id="rustchain-widget"></div>
 *   <script src="rustchain-widget.js"></script>
 * 
 * Or with custom container:
 *   <script>
 *     RustChainWidget.init({ container: '#my-container' });
 *   </script>
 */

(function(global) {
  'use strict';

  const CONFIG = {
    API_BASE: 'https://50.28.86.131',
    EXPLORER_URL: 'https://rustchain.org/explorer',
    REFRESH_INTERVAL: 60000,
    CONTAINER_ID: 'rustchain-widget'
  };

  const STYLES = `
    .rustchain-widget{font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif;background:linear-gradient(135deg,#1a1a2e 0%,#16213e 100%);border-radius:16px;padding:24px;max-width:400px;color:#fff;box-shadow:0 10px 40px rgba(0,0,0,.3)}
    .rcw-header{display:flex;align-items:center;justify-content:space-between;margin-bottom:20px;padding-bottom:16px;border-bottom:1px solid rgba(255,255,255,.1)}
    .rcw-logo{display:flex;align-items:center;gap:10px}
    .rcw-logo svg{width:32px;height:32px}
    .rcw-title{font-size:18px;font-weight:700;background:linear-gradient(90deg,#f39c12,#e74c3c);-webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text}
    .rcw-status{display:flex;align-items:center;gap:6px;font-size:12px;padding:4px 10px;border-radius:20px;background:rgba(46,204,113,.2);color:#2ecc71}
    .rcw-status.offline{background:rgba(231,76,60,.2);color:#e74c3c}
    .rcw-dot{width:8px;height:8px;border-radius:50%;background:#2ecc71;animation:rcw-pulse 2s infinite}
    .rcw-status.offline .rcw-dot{background:#e74c3c;animation:none}
    @keyframes rcw-pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.5;transform:scale(1.2)}}
    .rcw-grid{display:grid;grid-template-columns:repeat(2,1fr);gap:16px;margin-bottom:20px}
    .rcw-card{background:rgba(255,255,255,.05);border-radius:12px;padding:16px;cursor:pointer;transition:transform .2s,background .2s}
    .rcw-card:hover{transform:translateY(-2px);background:rgba(255,255,255,.08)}
    .rcw-label{font-size:11px;text-transform:uppercase;letter-spacing:1px;color:rgba(255,255,255,.5);margin-bottom:8px}
    .rcw-value{font-size:24px;font-weight:700;color:#fff}
    .rcw-value.highlight{color:#f39c12}
    .rcw-miners{background:rgba(255,255,255,.05);border-radius:12px;padding:16px;margin-bottom:16px}
    .rcw-miners-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:12px}
    .rcw-miners-title{font-size:13px;text-transform:uppercase;letter-spacing:1px;color:rgba(255,255,255,.5)}
    .rcw-activity{display:flex;gap:3px;height:30px;align-items:flex-end}
    .rcw-bar{width:6px;background:linear-gradient(to top,#f39c12,#e74c3c);border-radius:3px;animation:rcw-bar 1.5s ease-in-out infinite}
    @keyframes rcw-bar{0%,100%{opacity:.4}50%{opacity:1}}
    .rcw-chips{display:flex;flex-wrap:wrap;gap:8px}
    .rcw-chip{font-size:11px;padding:4px 10px;background:rgba(243,156,18,.2);color:#f39c12;border-radius:12px}
    .rcw-footer{display:flex;justify-content:space-between;align-items:center;font-size:11px;color:rgba(255,255,255,.4)}
    .rcw-link{color:#3498db;text-decoration:none;display:flex;align-items:center;gap:4px}
    .rcw-link:hover{color:#5dade2}
    .rcw-timer{display:flex;align-items:center;gap:4px}
    .rcw-loading{display:flex;justify-content:center;align-items:center;height:200px}
    .rcw-spinner{width:40px;height:40px;border:3px solid rgba(255,255,255,.1);border-top-color:#f39c12;border-radius:50%;animation:rcw-spin 1s linear infinite}
    @keyframes rcw-spin{to{transform:rotate(360deg)}}
    @media(max-width:420px){.rustchain-widget{padding:16px;border-radius:12px}.rcw-value{font-size:20px}.rcw-grid{gap:12px}}
  `;

  function injectStyles() {
    if (document.getElementById('rcw-styles')) return;
    const style = document.createElement('style');
    style.id = 'rcw-styles';
    style.textContent = STYLES;
    document.head.appendChild(style);
  }

  async function fetchData() {
    try {
      const [health, epoch, miners] = await Promise.allSettled([
        fetch(`${CONFIG.API_BASE}/health`).then(r => r.json()),
        fetch(`${CONFIG.API_BASE}/epoch`).then(r => r.json()),
        fetch(`${CONFIG.API_BASE}/api/miners`).then(r => r.json())
      ]);
      return {
        health: health.status === 'fulfilled' ? health.value : null,
        epoch: epoch.status === 'fulfilled' ? epoch.value : null,
        miners: miners.status === 'fulfilled' ? miners.value : null
      };
    } catch (e) {
      return { health: null, epoch: null, miners: null, error: e.message };
    }
  }

  function activityBars() {
    return Array.from({ length: 12 }, (_, i) => 
      `<div class="rcw-bar" style="height:${Math.random()*20+10}px;animation-delay:${i*.1}s"></div>`
    ).join('');
  }

  function render(container, data, countdown) {
    const online = data.health && !data.error;
    const epoch = data.epoch?.epoch || data.epoch?.current_epoch || '—';
    const list = Array.isArray(data.miners) ? data.miners : (data.miners?.miners || []);
    const count = list.length || (data.miners?.count || 0);
    const dist = data.epoch?.total_distributed || data.epoch?.rtc_distributed || '—';

    container.innerHTML = `
      <div class="rcw-header">
        <div class="rcw-logo">
          <svg viewBox="0 0 32 32" fill="none"><rect width="32" height="32" rx="8" fill="#f39c12"/><path d="M8 12h16M8 16h12M8 20h14" stroke="#1a1a2e" stroke-width="2.5" stroke-linecap="round"/></svg>
          <span class="rcw-title">RustChain</span>
        </div>
        <div class="rcw-status ${online ? '' : 'offline'}"><div class="rcw-dot"></div>${online ? 'Online' : 'Offline'}</div>
      </div>
      <div class="rcw-grid">
        <div class="rcw-card" onclick="window.open('${CONFIG.EXPLORER_URL}','_blank')">
          <div class="rcw-label">Current Epoch</div><div class="rcw-value highlight">${epoch}</div>
        </div>
        <div class="rcw-card" onclick="window.open('${CONFIG.EXPLORER_URL}/miners','_blank')">
          <div class="rcw-label">Active Miners</div><div class="rcw-value">${count}</div>
        </div>
        <div class="rcw-card" onclick="window.open('${CONFIG.EXPLORER_URL}','_blank')">
          <div class="rcw-label">Network Health</div><div class="rcw-value" style="color:${online?'#2ecc71':'#e74c3c'}">${online?'✓ Healthy':'✗ Down'}</div>
        </div>
        <div class="rcw-card" onclick="window.open('${CONFIG.EXPLORER_URL}/stats','_blank')">
          <div class="rcw-label">RTC Distributed</div><div class="rcw-value">${typeof dist==='number'?dist.toLocaleString():dist}</div>
        </div>
      </div>
      ${list.length ? `<div class="rcw-miners"><div class="rcw-miners-header"><span class="rcw-miners-title">Mining Activity</span><div class="rcw-activity">${activityBars()}</div></div><div class="rcw-chips">${list.slice(0,6).map(m=>`<span class="rcw-chip">${typeof m==='string'?m:(m.miner_id||m.name||'?')}</span>`).join('')}${list.length>6?`<span class="rcw-chip">+${list.length-6}</span>`:''}</div></div>` : ''}
      <div class="rcw-footer">
        <a href="${CONFIG.EXPLORER_URL}" target="_blank" class="rcw-link">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/><polyline points="15 3 21 3 21 9"/><line x1="10" y1="14" x2="21" y2="3"/></svg>
          Block Explorer
        </a>
        <div class="rcw-timer">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"/><path d="M20.49 15a9 9 0 1 1-2.12-9.36L23 10"/></svg>
          <span id="rcw-countdown">${countdown}s</span>
        </div>
      </div>
    `;
  }

  function init(options = {}) {
    injectStyles();
    
    const containerId = options.container || `#${CONFIG.CONTAINER_ID}`;
    const container = document.querySelector(containerId);
    if (!container) {
      console.error('RustChain Widget: Container not found:', containerId);
      return;
    }
    
    container.classList.add('rustchain-widget');
    container.innerHTML = '<div class="rcw-loading"><div class="rcw-spinner"></div></div>';

    let countdown = 60;
    let interval;

    async function refresh() {
      const data = await fetchData();
      render(container, data, countdown);
      countdown = 60;
      
      if (interval) clearInterval(interval);
      interval = setInterval(() => {
        countdown--;
        const el = document.getElementById('rcw-countdown');
        if (el) el.textContent = `${countdown}s`;
        if (countdown <= 0) refresh();
      }, 1000);
    }

    refresh();
  }

  // Auto-init if default container exists
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
      if (document.getElementById(CONFIG.CONTAINER_ID)) init();
    });
  } else {
    if (document.getElementById(CONFIG.CONTAINER_ID)) init();
  }

  // Export for manual init
  global.RustChainWidget = { init };

})(typeof window !== 'undefined' ? window : this);
