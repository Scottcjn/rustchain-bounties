const API_BASE = "https://explorer.rustchain.org";
const REFRESH_INTERVAL_MS = 30000;
const ONLINE_WINDOW_SECONDS = 180;

const state = {
  miners: [],
  jobs: [],
  stats: null,
  errors: [],
  lastLoadedAt: null,
  timer: null,
};

const els = {
  healthBadge: document.querySelector("#healthBadge"),
  updatedAt: document.querySelector("#updatedAt"),
  refreshBtn: document.querySelector("#refreshBtn"),
  errorPanel: document.querySelector("#errorPanel"),
  minerCount: document.querySelector("#minerCount"),
  onlineCount: document.querySelector("#onlineCount"),
  vintageCount: document.querySelector("#vintageCount"),
  topMultiplier: document.querySelector("#topMultiplier"),
  topMiner: document.querySelector("#topMiner"),
  agentVolume: document.querySelector("#agentVolume"),
  agentJobs: document.querySelector("#agentJobs"),
  minerRows: document.querySelector("#minerRows"),
  minerCaption: document.querySelector("#minerCaption"),
  minerSearch: document.querySelector("#minerSearch"),
  familyFilter: document.querySelector("#familyFilter"),
  statusFilter: document.querySelector("#statusFilter"),
  sortSelect: document.querySelector("#sortSelect"),
  archBars: document.querySelector("#archBars"),
  activeAgents: document.querySelector("#activeAgents"),
  openJobs: document.querySelector("#openJobs"),
  escrowBalance: document.querySelector("#escrowBalance"),
  feeRate: document.querySelector("#feeRate"),
  categoryBars: document.querySelector("#categoryBars"),
  reputationWallet: document.querySelector("#reputationWallet"),
  reputationBtn: document.querySelector("#reputationBtn"),
  reputationResult: document.querySelector("#reputationResult"),
  jobList: document.querySelector("#jobList"),
  jobCaption: document.querySelector("#jobCaption"),
  jobCategoryFilter: document.querySelector("#jobCategoryFilter"),
};

function formatNumber(value, digits = 0) {
  const number = Number(value || 0);
  return new Intl.NumberFormat("en-US", {
    maximumFractionDigits: digits,
    minimumFractionDigits: digits,
  }).format(number);
}

function formatRtc(value) {
  return `${formatNumber(value, 1)} RTC`;
}

function unixToDate(seconds) {
  const value = Number(seconds || 0);
  if (!value) return null;
  return new Date(value * 1000);
}

function relativeTime(seconds) {
  const date = unixToDate(seconds);
  if (!date) return "unknown";

  const diffSeconds = Math.round((date.getTime() - Date.now()) / 1000);
  const abs = Math.abs(diffSeconds);
  const units = [
    ["day", 86400],
    ["hour", 3600],
    ["minute", 60],
    ["second", 1],
  ];

  const [unit, size] = units.find(([, unitSeconds]) => abs >= unitSeconds) || units[3];
  const value = Math.round(diffSeconds / size);
  return new Intl.RelativeTimeFormat("en", { numeric: "auto" }).format(value, unit);
}

function onlineStatus(miner) {
  const last = Number(miner.last_attest || 0);
  if (!last) return "stale";
  const age = Math.max(0, Date.now() / 1000 - last);
  return age <= ONLINE_WINDOW_SECONDS ? "online" : "stale";
}

function shortMiner(id) {
  const value = String(id || "unknown");
  if (value.length <= 28) return value;
  return `${value.slice(0, 14)}...${value.slice(-8)}`;
}

function familyClass(family) {
  const value = String(family || "").toLowerCase();
  if (value.includes("power")) return "power";
  if (value.includes("apple") || value.includes("x86") || value.includes("windows")) return "modern";
  return "";
}

async function fetchJson(path) {
  const response = await fetch(`${API_BASE}${path}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error(`${path} returned ${response.status}`);
  }
  return response.json();
}

async function loadDashboard() {
  els.refreshBtn.disabled = true;
  els.refreshBtn.textContent = "Refreshing";
  state.errors = [];

  const [minersResult, jobsResult, statsResult, healthResult] = await Promise.allSettled([
    fetchJson("/api/miners"),
    fetchJson("/agent/jobs"),
    fetchJson("/agent/stats"),
    fetchJson("/health"),
  ]);

  if (minersResult.status === "fulfilled") {
    state.miners = Array.isArray(minersResult.value.miners) ? minersResult.value.miners : [];
  } else {
    state.errors.push(minersResult.reason.message);
  }

  if (jobsResult.status === "fulfilled") {
    state.jobs = Array.isArray(jobsResult.value.jobs) ? jobsResult.value.jobs : [];
  } else {
    state.errors.push(jobsResult.reason.message);
  }

  if (statsResult.status === "fulfilled") {
    state.stats = statsResult.value.stats || null;
  } else {
    state.errors.push(statsResult.reason.message);
  }

  if (healthResult.status === "rejected") {
    state.errors.push(healthResult.reason.message);
  }

  state.lastLoadedAt = new Date();
  render();
  els.refreshBtn.disabled = false;
  els.refreshBtn.textContent = "Refresh";
  resetRefreshTimer();
}

function resetRefreshTimer() {
  if (state.timer) window.clearTimeout(state.timer);
  state.timer = window.setTimeout(loadDashboard, REFRESH_INTERVAL_MS);
}

function render() {
  renderHealth();
  renderMetrics();
  renderFamilyOptions();
  renderMiners();
  renderArchitectureBars();
  renderAgentEconomy();
  renderJobCategoryOptions();
  renderJobs();
}

function renderHealth() {
  const hasData = state.miners.length > 0 || state.stats;
  els.healthBadge.className = `health-badge ${state.errors.length ? "warn" : "ok"}`;
  els.healthBadge.textContent = state.errors.length ? "Partial data" : hasData ? "Live" : "No data";
  els.updatedAt.textContent = state.lastLoadedAt
    ? `Updated ${state.lastLoadedAt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit", second: "2-digit" })}`
    : "Not loaded";

  if (state.errors.length) {
    els.errorPanel.hidden = false;
    els.errorPanel.textContent = state.errors.join(" | ");
  } else {
    els.errorPanel.hidden = true;
    els.errorPanel.textContent = "";
  }
}

function renderMetrics() {
  const miners = state.miners;
  const online = miners.filter((miner) => onlineStatus(miner) === "online");
  const vintage = miners.filter((miner) => Number(miner.antiquity_multiplier || 0) > 1.2);
  const top = miners.reduce((best, miner) => {
    return Number(miner.antiquity_multiplier || 0) > Number(best?.antiquity_multiplier || 0) ? miner : best;
  }, null);

  els.minerCount.textContent = miners.length;
  els.onlineCount.textContent = `${online.length} online`;
  els.vintageCount.textContent = vintage.length;
  els.topMultiplier.textContent = `${formatNumber(top?.antiquity_multiplier || 0, 2)}x`;
  els.topMiner.textContent = top ? shortMiner(top.miner) : "No miner";

  const stats = state.stats || {};
  els.agentVolume.textContent = formatRtc(stats.total_rtc_volume);
  els.agentJobs.textContent = `${formatNumber(stats.completed_jobs)} completed`;
}

function renderFamilyOptions() {
  const current = els.familyFilter.value;
  const families = [...new Set(state.miners.map((miner) => miner.device_family || "Unknown"))].sort();
  els.familyFilter.innerHTML = [
    `<option value="all">All</option>`,
    ...families.map((family) => `<option value="${escapeHtml(family)}">${escapeHtml(family)}</option>`),
  ].join("");

  if (families.includes(current)) {
    els.familyFilter.value = current;
  }
}

function getFilteredMiners() {
  const search = els.minerSearch.value.trim().toLowerCase();
  const family = els.familyFilter.value;
  const status = els.statusFilter.value;
  const sort = els.sortSelect.value;

  return [...state.miners]
    .filter((miner) => {
      const text = [
        miner.miner,
        miner.device_arch,
        miner.device_family,
        miner.hardware_type,
      ].join(" ").toLowerCase();
      const familyOk = family === "all" || miner.device_family === family;
      const statusOk = status === "all" || onlineStatus(miner) === status;
      return (!search || text.includes(search)) && familyOk && statusOk;
    })
    .sort((a, b) => {
      if (sort === "miner" || sort === "device_family") {
        return String(a[sort] || "").localeCompare(String(b[sort] || ""));
      }
      return Number(b[sort] || 0) - Number(a[sort] || 0);
    });
}

function renderMiners() {
  const miners = getFilteredMiners();
  els.minerCaption.textContent = `${miners.length} of ${state.miners.length} miners shown`;

  if (!miners.length) {
    els.minerRows.innerHTML = `<tr><td colspan="6" class="empty-cell">No miners match the current view.</td></tr>`;
    return;
  }

  const maxMultiplier = Math.max(...state.miners.map((miner) => Number(miner.antiquity_multiplier || 0)), 1);
  els.minerRows.innerHTML = miners.map((miner) => {
    const multiplier = Number(miner.antiquity_multiplier || 0);
    const fill = Math.max(4, Math.min(100, (multiplier / maxMultiplier) * 100));
    const status = onlineStatus(miner);
    const first = relativeTime(miner.first_attest);
    const last = relativeTime(miner.last_attest);
    const family = miner.device_family || "Unknown";

    return `
      <tr>
        <td>
          <span class="miner-id" title="${escapeHtml(miner.miner || "")}">${escapeHtml(shortMiner(miner.miner))}</span>
          <span class="subtle">First seen ${escapeHtml(first)}</span>
        </td>
        <td><span class="badge ${familyClass(family)}">${escapeHtml(family)}</span></td>
        <td>
          ${escapeHtml(miner.hardware_type || "Unknown")}
          <span class="subtle">${escapeHtml(miner.device_arch || "unknown arch")}</span>
        </td>
        <td>
          <span class="multiplier">
            <strong>${formatNumber(multiplier, 2)}x</strong>
            <span class="multiplier-track"><span class="multiplier-fill" style="--fill:${fill}%"></span></span>
          </span>
        </td>
        <td>${escapeHtml(last)}</td>
        <td><span class="status-dot ${status}">${status}</span></td>
      </tr>
    `;
  }).join("");
}

function renderArchitectureBars() {
  const counts = countBy(state.miners, (miner) => miner.device_family || "Unknown");
  const total = Math.max(1, state.miners.length);
  els.archBars.innerHTML = renderBars(counts, total);
}

function renderAgentEconomy() {
  const stats = state.stats || {};
  els.activeAgents.textContent = formatNumber(stats.active_agents);
  els.openJobs.textContent = formatNumber(stats.open_jobs);
  els.escrowBalance.textContent = formatRtc(stats.escrow_balance_rtc);
  els.feeRate.textContent = stats.platform_fee_rate || "0%";

  const categories = {};
  (stats.categories || []).forEach((category) => {
    categories[category.category || "other"] = Number(category.jobs || 0);
  });
  const total = Object.values(categories).reduce((sum, value) => sum + value, 0) || 1;
  els.categoryBars.innerHTML = renderBars(categories, total);
}

function renderJobCategoryOptions() {
  const current = els.jobCategoryFilter.value;
  const statsCategories = ((state.stats || {}).categories || []).map((category) => category.category);
  const jobCategories = state.jobs.map((job) => job.category).filter(Boolean);
  const categories = [...new Set([...statsCategories, ...jobCategories])].filter(Boolean).sort();
  els.jobCategoryFilter.innerHTML = [
    `<option value="all">All</option>`,
    ...categories.map((category) => `<option value="${escapeHtml(category)}">${escapeHtml(category)}</option>`),
  ].join("");

  if (categories.includes(current)) {
    els.jobCategoryFilter.value = current;
  }
}

function renderJobs() {
  const category = els.jobCategoryFilter.value;
  const jobs = state.jobs.filter((job) => category === "all" || job.category === category);
  els.jobCaption.textContent = `${jobs.length} of ${state.jobs.length} open jobs`;

  if (!jobs.length) {
    els.jobList.innerHTML = `<p class="empty-state">No open jobs are currently returned by the API.</p>`;
    return;
  }

  els.jobList.innerHTML = jobs.map((job) => {
    const title = job.title || job.name || `Job ${job.id || ""}`.trim();
    const reward = job.reward_rtc || job.reward || job.amount || "RTC";
    const category = job.category || "uncategorized";
    const status = job.status || "posted";
    return `
      <article class="job-row">
        <div>
          <strong>${escapeHtml(title)}</strong>
          <small>${escapeHtml(category)} | ${escapeHtml(status)}</small>
        </div>
        <span class="badge">${escapeHtml(String(reward))}</span>
        <code>${escapeHtml(job.id || job.job_id || "open")}</code>
      </article>
    `;
  }).join("");
}

async function lookupReputation() {
  const wallet = els.reputationWallet.value.trim();
  if (!wallet) {
    els.reputationResult.textContent = "Enter a wallet or agent id.";
    return;
  }

  els.reputationBtn.disabled = true;
  els.reputationBtn.textContent = "Checking";
  els.reputationResult.textContent = "Loading reputation...";

  try {
    const data = await fetchJson(`/agent/reputation/${encodeURIComponent(wallet)}`);
    if (!data.reputation) {
      els.reputationResult.textContent = `${data.wallet_id || wallet}: no reputation history returned.`;
    } else {
      els.reputationResult.textContent = `${data.wallet_id || wallet}: ${JSON.stringify(data.reputation)}`;
    }
  } catch (error) {
    els.reputationResult.textContent = error.message;
  } finally {
    els.reputationBtn.disabled = false;
    els.reputationBtn.textContent = "Lookup";
  }
}

function countBy(items, selector) {
  return items.reduce((counts, item) => {
    const key = selector(item);
    counts[key] = (counts[key] || 0) + 1;
    return counts;
  }, {});
}

function renderBars(counts, total) {
  const entries = Object.entries(counts).sort((a, b) => b[1] - a[1]);
  if (!entries.length) {
    return `<p class="empty-state">No data available.</p>`;
  }

  return entries.map(([name, count]) => {
    const fill = Math.max(4, Math.round((count / total) * 100));
    return `
      <div class="bar-row">
        <span class="bar-name"><span>${escapeHtml(name)}</span><strong>${formatNumber(count)}</strong></span>
        <span></span>
        <span class="bar-rail"><span class="bar-fill" style="--fill:${fill}%"></span></span>
      </div>
    `;
  }).join("");
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

[
  els.minerSearch,
  els.familyFilter,
  els.statusFilter,
  els.sortSelect,
].forEach((control) => control.addEventListener("input", renderMiners));

els.jobCategoryFilter.addEventListener("change", renderJobs);
els.reputationBtn.addEventListener("click", lookupReputation);
els.reputationWallet.addEventListener("keydown", (event) => {
  if (event.key === "Enter") lookupReputation();
});
els.refreshBtn.addEventListener("click", loadDashboard);
window.addEventListener("visibilitychange", () => {
  if (!document.hidden) loadDashboard();
});

loadDashboard();
