const core = require('@actions/core');
const github = require('@actions/github');
const fs = require('fs');
const path = require('path');
const https = require('https');
const http = require('http');

/**
 * Resolve the wallet address from (in priority order):
 *   1. action input `wallet-address`
 *   2. `.rtc-wallet` file in the repo root
 *   3. PR body — looks for "RTC Wallet:" or "Wallet:" line
 */
function resolveWalletAddress(inputWallet) {
  // 1. Explicit input
  if (inputWallet && inputWallet.trim().length > 0) {
    core.info(`Wallet resolved from action input: ${inputWallet.trim()}`);
    return inputWallet.trim();
  }

  // 2. .rtc-wallet file
  const walletFile = path.join(process.env.GITHUB_WORKSPACE || '.', '.rtc-wallet');
  if (fs.existsSync(walletFile)) {
    const content = fs.readFileSync(walletFile, 'utf8').trim();
    if (content.length > 0) {
      core.info(`Wallet resolved from .rtc-wallet file: ${content}`);
      return content;
    }
  }

  // 3. PR body
  const prBody = github.context.payload?.pull_request?.body || '';
  const walletMatch = prBody.match(/(?:RTC\s*)?Wallet\s*:\s*([A-Za-z0-9]+)/i);
  if (walletMatch && walletMatch[1]) {
    core.info(`Wallet resolved from PR body: ${walletMatch[1]}`);
    return walletMatch[1];
  }

  return null;
}

/**
 * Perform a GET request (no external deps).
 */
function httpGet(url) {
  return new Promise((resolve, reject) => {
    const mod = url.startsWith('https') ? https : http;
    mod.get(url, { timeout: 15000 }, (res) => {
      let data = '';
      res.on('data', (chunk) => (data += chunk));
      res.on('end', () => {
        resolve({ statusCode: res.statusCode, body: data });
      });
    }).on('error', reject);
  });
}

/**
 * Query RustChain wallet balance (READ-ONLY).
 * GET {apiBase}/wallet/balance?miner_id={wallet}
 */
async function queryBalance(apiBase, walletAddress) {
  const url = `${apiBase.replace(/\/+$/, '')}/wallet/balance?miner_id=${encodeURIComponent(walletAddress)}`;
  core.info(`Querying balance at: ${url}`);

  try {
    const response = await httpGet(url);
    if (response.statusCode === 200) {
      const body = JSON.parse(response.body);
      return {
        success: true,
        balance: body.balance ?? body.Balance ?? body.amount ?? JSON.stringify(body),
        raw: body,
      };
    }
    core.warning(`Balance query returned status ${response.statusCode}: ${response.body}`);
    return { success: false, balance: 'N/A', raw: response.body };
  } catch (err) {
    core.warning(`Balance query failed: ${err.message}`);
    return { success: false, balance: 'N/A', raw: err.message };
  }
}

/**
 * Post a comment on the PR (unless dry-run).
 */
async function postComment(octokit, owner, repo, prNumber, body) {
  await octokit.rest.issues.createComment({ owner, repo, issue_number: prNumber, body });
}

/**
 * Build the markdown comment body.
 */
function buildComment(walletAddress, balanceResult, queryAmount) {
  const statusIcon = balanceResult.success ? '✅' : '⚠️';
  const balance = balanceResult.balance;
  const timestamp = new Date().toISOString();

  let comment = `## ${statusIcon} RTC Balance Query\n\n`;
  comment += `| Field | Value |\n`;
  comment += `|---|---|\n`;
  comment += `| **Wallet** | \`${walletAddress}\` |\n`;
  comment += `| **Balance** | ${balance} RTC |\n`;
  comment += `| **Query Amount** | ${queryAmount} RTC (informational) |\n`;
  comment += `| **Queried at** | ${timestamp} |\n\n`;
  comment += `> **Note:** This action performs **read-only** queries. No transfers or sends are executed.\n`;

  return comment;
}

/* ------------------------------------------------------------------ */
/*  Main                                                               */
/* ------------------------------------------------------------------ */
async function run() {
  try {
    const inputWallet   = core.getInput('wallet-address');
    const queryAmount   = core.getInput('query-amount') || '20';
    const apiBase       = core.getInput('api-base-url') || 'https://rustchain.org';
    const token         = core.getInput('github-token');
    const dryRun        = core.getInput('dry-run') === 'true';

    // Resolve wallet address
    const walletAddress = resolveWalletAddress(inputWallet);
    if (!walletAddress) {
      core.setFailed(
        'Could not resolve wallet address. Provide it via `wallet-address` input, `.rtc-wallet` file, or PR body.'
      );
      return;
    }

    core.setOutput('wallet-address', walletAddress);

    // Query balance (read-only)
    const balanceResult = await queryBalance(apiBase, walletAddress);
    core.setOutput('balance', balanceResult.balance);
    core.setOutput('status', balanceResult.success ? 'success' : 'error');

    core.info(`Wallet: ${walletAddress}`);
    core.info(`Balance: ${balanceResult.balance}`);

    // Post comment unless dry-run
    const pr = github.context.payload?.pull_request;
    if (!dryRun && pr && token) {
      const octokit = github.getOctokit(token);
      const { owner, repo } = github.context.repo;
      const prNumber = pr.number;

      const commentBody = buildComment(walletAddress, balanceResult, queryAmount);
      await postComment(octokit, owner, repo, prNumber, commentBody);
      core.info(`Comment posted on PR #${prNumber}`);
    } else if (dryRun) {
      core.info('Dry-run mode — skipping PR comment.');
      core.info('Would have posted:\n' + buildComment(walletAddress, balanceResult, queryAmount));
    } else {
      core.info('Not in a PR context or no token — skipping comment.');
    }
  } catch (error) {
    core.setFailed(`Action failed: ${error.message}`);
  }
}

run();
