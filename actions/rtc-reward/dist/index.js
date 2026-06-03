// RTC Reward Action — standalone (no external npm deps)
// Uses only Node.js 20 built-ins. Compatible with GitHub Actions node20 runtime.

const fs = require('fs');
const path = require('path');

// ---- helpers ----

function getInput(name, opts = {}) {
  const key = `INPUT_${name.replace(/-/g, '_').toUpperCase()}`;
  const val = process.env[key];
  if (opts.required && (val === undefined || val === '')) {
    throw new Error(`Input required and not supplied: ${name}`);
  }
  return val !== undefined ? val : (opts.default || '');
}

function setOutput(name, value) {
  // Write to GITHUB_OUTPUT file if available (actions/core compatible)
  const outFile = process.env.GITHUB_OUTPUT;
  if (outFile) {
    fs.appendFileSync(outFile, `${name}=${value}\n`);
  }
  // Also print for workflow command compatibility
  process.stdout.write(`::set-output name=${name}::${value}\n`);
}

function setFailed(msg) {
  process.stderr.write(`::error::${msg}\n`);
  process.exit(1);
}

function info(msg) {
  process.stdout.write(`${msg}\n`);
}

function warning(msg) {
  process.stdout.write(`::warning::${msg}\n`);
}

async function octokitRequest(token, method, url, body) {
  const resp = await fetch(url, {
    method,
    headers: {
      Authorization: `Bearer ${token}`,
      'Content-Type': 'application/json',
      Accept: 'application/vnd.github+json',
      'X-GitHub-Api-Version': '2022-11-28',
    },
    body: body ? JSON.stringify(body) : undefined,
  });
  const data = resp.headers.get('content-type')?.includes('json')
    ? await resp.json()
    : await resp.text();
  if (!resp.ok) {
    throw new Error(`GitHub API ${method} ${url} → ${resp.status}: ${JSON.stringify(data)}`);
  }
  return data;
}

// ---- main ----

async function run() {
  const nodeUrl = getInput('node-url', { required: true });
  const amount = parseInt(getInput('amount', { required: true }), 10);
  if (isNaN(amount) || amount <= 0) throw new Error(`Invalid amount: ${getInput('amount')}`);
  const walletFrom = getInput('wallet-from', { required: true });
  const adminKey = getInput('admin-key', { required: true });
  const dryRun = getInput('dry-run') === 'true';
  const walletPattern = getInput('wallet-pattern') || 'RTC[0-9a-fA-F]{36,44}';
  const commentTemplate = getInput('comment-template') || [
    '## RTC Reward',
    '',
    'This merged PR earned **{{amount}} RTC** — sent to `{{wallet}}`.',
    '',
    '[RustChain Bounty Program](https://github.com/Scottcjn/rustchain-bounties)',
  ].join('\n');

  const token = process.env.GITHUB_TOKEN;
  if (!token) throw new Error('GITHUB_TOKEN not set');

  // Read event payload
  const eventPath = process.env.GITHUB_EVENT_PATH;
  if (!eventPath) throw new Error('GITHUB_EVENT_PATH not set');
  const event = JSON.parse(fs.readFileSync(eventPath, 'utf-8'));
  const repoFull = (process.env.GITHUB_REPOSITORY || '').split('/');
  const owner = repoFull[0];
  const repo = repoFull[1];

  const apiBase = 'https://api.github.com';

  // Determine PR number
  let prNumber;
  if (event.pull_request) {
    prNumber = event.pull_request.number;
  } else if (event.after) {
    // Push event — find associated merged PR
    const prs = await octokitRequest(
      token, 'GET',
      `${apiBase}/repos/${owner}/${repo}/commits/${event.after}/pulls`
    );
    const merged = prs.filter(p => p.merged_at);
    if (merged.length > 0) prNumber = merged[0].number;
  }

  if (!prNumber) {
    info('No merged PR found for this event. Skipping.');
    return;
  }

  // Fetch PR
  const pr = await octokitRequest(
    token, 'GET',
    `${apiBase}/repos/${owner}/${repo}/pulls/${prNumber}`
  );

  if (!pr.merged) {
    info(`PR #${prNumber} is not merged. Skipping.`);
    return;
  }

  // Extract wallet
  let wallet = extractWallet(pr.body || '', walletPattern);
  if (!wallet) {
    wallet = await findWalletInRepo(token, apiBase, owner, repo, pr.head.sha, walletPattern);
  }
  if (!wallet) {
    info(`No RTC wallet found in PR #${prNumber}. Skipping reward.`);
    setOutput('wallet-found', 'false');
    return;
  }

  info(`Found wallet: ${wallet}`);
  info(`Awarding ${amount} RTC to @${pr.user.login} for PR #${prNumber}`);

  if (dryRun) {
    info('[DRY RUN] Would call RTC transfer:');
    info(`  From: ${walletFrom}  →  To: ${wallet}`);
    info(`  Amount: ${amount} RTC`);
    info(`  Node: ${nodeUrl}`);
  } else {
    const tx = await sendRTC(nodeUrl, walletFrom, wallet, amount, adminKey, pr.html_url);
    info(`Transfer result: ${JSON.stringify(tx)}`);
  }

  // Post comment
  const comment = commentTemplate
    .replace(/\{\{amount\}\}/g, String(amount))
    .replace(/\{\{wallet\}\}/g, wallet)
    .replace(/\{\{pr_number\}\}/g, String(prNumber))
    .replace(/\{\{author\}\}/g, pr.user.login);

  if (!dryRun) {
    await octokitRequest(token, 'POST',
      `${apiBase}/repos/${owner}/${repo}/issues/${prNumber}/comments`,
      { body: comment }
    );
    info('Reward comment posted.');
  } else {
    info(`[DRY RUN] Would post comment:\n${comment}`);
  }

  setOutput('wallet-found', 'true');
  setOutput('wallet', wallet);
  setOutput('amount', String(amount));
  setOutput('pr-number', String(prNumber));
}

function extractWallet(text, pattern) {
  const re = new RegExp(pattern, 'g');
  const matches = text.match(re);
  return matches ? matches[matches.length - 1] : null;
}

async function findWalletInRepo(token, apiBase, owner, repo, ref, pattern) {
  const paths = ['.rtc-wallet', '.github/rtc-wallet', 'RTC_WALLET', '.rtcwallet'];
  for (const p of paths) {
    try {
      const data = await octokitRequest(
        token, 'GET',
        `${apiBase}/repos/${owner}/${repo}/contents/${p}?ref=${ref}`
      );
      const content = Buffer.from(data.content, 'base64').toString('utf-8').trim();
      const wallet = extractWallet(content, pattern);
      if (wallet) { info(`Found wallet in ${p}: ${wallet}`); return wallet; }
    } catch { /* file not found */ }
  }
  return null;
}

async function sendRTC(nodeUrl, from, to, amount, adminKey, memo) {
  const payload = { from, to, amount, admin_key: adminKey, memo };
  const resp = await fetch(`${nodeUrl.replace(/\/$/, '')}/api/v1/transfer`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  });
  if (!resp.ok) {
    const text = await resp.text();
    throw new Error(`RTC transfer failed (${resp.status}): ${text}`);
  }
  return resp.json();
}

run();
