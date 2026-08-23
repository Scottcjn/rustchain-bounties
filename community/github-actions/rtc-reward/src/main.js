'use strict';

// rtc-reward: parses bounty claim issues and exports payout details.
//
// Fixes #16327 (Claim #696): claimants wrap their wallet in markdown code
// quotes, e.g.
//   **Wallet:** `7doPxSPt1pmbHcUcVzK22FVECDhv8kV6nnd2XMKaFiRd`
// The previous parser expected a bare address and rejected these claims.

const core = require('@actions/core');
const github = require('@actions/github');

// Wallet label followed by an optional code quote and a base58 address.
// Tolerates bold markers: **Wallet:**, Wallet:, wallet :
const WALLET_RE = /wallet\s*\*{0,2}\s*:\s*\*{0,2}\s*`?([1-9A-HJ-NP-Za-km-z]{32,44})`?/i;
const WALLET_VALID_RE = /^[1-9A-HJ-NP-Za-km-z]{32,44}$/;

// "(2 RTC)" anywhere in the title or body.
const AMOUNT_RE = /\(\s*(\d+(?:\.\d+)?)\s*RTC\s*\)/i;

function extractWallet(body) {
  if (!body) {
    return null;
  }
  const match = body.match(WALLET_RE);
  if (!match) {
    return null;
  }
  const candidate = match[1].trim();
  return WALLET_VALID_RE.test(candidate) ? candidate : null;
}

function extractAmount(title, body, fallbackAmount) {
  const fromTitle = title && title.match(AMOUNT_RE);
  if (fromTitle) {
    return Number(fromTitle[1]);
  }
  const fromBody = body && body.match(AMOUNT_RE);
  if (fromBody) {
    return Number(fromBody[1]);
  }
  return fallbackAmount;
}

async function run() {
  try {
    const token = core.getInput('github-token') || process.env.GITHUB_TOKEN || '';
    const fallbackAmount = Number(core.getInput('default-amount') || '0');
    const dryRun = String(core.getInput('dry-run') || '').toLowerCase() === 'true';

    const ctx = github.context;
    const issue = ctx.payload.issue;
    const issueNumber = (issue && issue.number) || Number(core.getInput('issue-number') || '0');

    if (!issueNumber) {
      core.setFailed('rtc-reward: no issue number available');
      return;
    }

    const title = (issue && issue.title) || '';
    const body = (issue && issue.body) || '';

    const wallet = extractWallet(body);
    const amount = extractAmount(title, body, fallbackAmount);
    const valid = Boolean(wallet) && amount > 0;

    core.setOutput('issue-number', String(issueNumber));
    core.setOutput('wallet', wallet || '');
    core.setOutput('amount', String(amount));
    core.setOutput('valid', String(valid));

    if (!wallet) {
      core.warning('rtc-reward: no valid base58 wallet found in claim #' + issueNumber);
    }
    if (!(amount > 0)) {
      core.warning('rtc-reward: no positive RTC amount found in claim #' + issueNumber);
    }

    if (!token || dryRun || !issue) {
      core.info('rtc-reward: dry run - outputs exported, no comment posted');
      return;
    }

    const octokit = github.getOctokit(token);
    const repo = ctx.repo;

    let comment;
    if (valid) {
      comment =
        '✅ Claim #' + issueNumber + ' validated by rtc-reward.\n\n' +
        '- Wallet: `' + wallet + '`\n' +
        '- Amount: ' + amount + ' RTC\n\n' +
        'Payout queued by the rewards bot.';
    } else {
      comment =
        '⚠️ Claim #' + issueNumber + ' could not be validated.\n\n' +
        (wallet ? '' : '- Add a wallet line: Wallet: <your-base58-address>\n') +
        (amount > 0 ? '' : '- Include the amount in the title, e.g. (2 RTC).\n');
    }

    await octokit.rest.issues.createComment({
      owner: repo.owner,
      repo: repo.repo,
      issue_number: issueNumber,
      body: comment,
    });
    core.info('rtc-reward: commented on #' + issueNumber + ' (valid=' + valid + ')');
  } catch (err) {
    core.setFailed('rtc-reward: ' + (err && err.message ? err.message : String(err)));
  }
}

run();
