const core = require('@actions/core');
const github = require('@actions/github');

function findWallet(prBody, walletFile) {
  const body = prBody || '';
  const patterns = [
    /RTC(?: wallet| address)?\s*[:=]\s*([A-Za-z0-9._:-]+)/i,
    /wallet\s*[:=]\s*([A-Za-z0-9._:-]+)/i
  ];
  for (const pattern of patterns) {
    const match = body.match(pattern);
    if (match) return match[1];
  }
  const fileValue = (walletFile || '').trim();
  return fileValue || null;
}

async function reward({ nodeUrl, amount, walletFrom, adminKey, walletTo, dryRun }) {
  if (dryRun) {
    return { ok: true, dryRun: true, message: `Dry run: would send ${amount} RTC to ${walletTo}` };
  }

  const endpoint = new URL('/api/rewards/pr-merge', nodeUrl).toString();
  const response = await fetch(endpoint, {
    method: 'POST',
    headers: {
      'content-type': 'application/json',
      authorization: `Bearer ${adminKey}`
    },
    body: JSON.stringify({ amount: Number(amount), walletFrom, walletTo })
  });

  const text = await response.text();
  if (!response.ok) throw new Error(`RTC reward failed (${response.status}): ${text}`);
  return { ok: true, dryRun: false, message: text || `Sent ${amount} RTC to ${walletTo}` };
}

async function run() {
  const nodeUrl = core.getInput('node-url', { required: true });
  const amount = core.getInput('amount') || '5';
  const walletFrom = core.getInput('wallet-from', { required: true });
  const adminKey = core.getInput('admin-key', { required: true });
  const token = core.getInput('github-token') || process.env.GITHUB_TOKEN;
  const dryRun = core.getBooleanInput('dry-run');

  const { payload, repo } = github.context;
  const pr = payload.pull_request;
  if (!pr || !pr.merged) {
    core.info('No merged pull request found; skipping RTC reward.');
    return;
  }

  const octokit = github.getOctokit(token);
  let walletFile = '';
  try {
    const { data } = await octokit.rest.repos.getContent({
      owner: repo.owner,
      repo: repo.repo,
      path: '.rtc-wallet',
      ref: pr.head.sha
    });
    walletFile = Buffer.from(data.content || '', 'base64').toString('utf8');
  } catch (_) {
    core.info('No .rtc-wallet file found in PR head; checking PR body only.');
  }

  const walletTo = findWallet(pr.body, walletFile);
  if (!walletTo) throw new Error('Contributor RTC wallet not found in PR body or .rtc-wallet file.');

  const result = await reward({ nodeUrl, amount, walletFrom, adminKey, walletTo, dryRun });
  await octokit.rest.issues.createComment({
    owner: repo.owner,
    repo: repo.repo,
    issue_number: pr.number,
    body: `🏆 RTC reward processed for @${pr.user.login}: ${result.message}`
  });
  core.info(result.message);
}

if (require.main === module) {
  run().catch((error) => core.setFailed(error.message));
}

module.exports = { findWallet, reward };
