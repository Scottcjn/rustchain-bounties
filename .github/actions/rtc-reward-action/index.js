const core = require('@actions/core');
const github = require('@actions/github');
const https = require('https');
const fs = require('fs');
const path = require('path');

// Wallet address patterns to match
const WALLET_PATTERNS = {
  // Match wallet field in PR body: "wallet: 0x..." or "**Wallet:** 0x..."
  field: (fieldName) => new RegExp(
    `(?:^|\\n)\\s*(?:\\*\\*)?${fieldName}(?:\\*\\*)?\\s*[:=]\\s*([a-zA-Z0-9]{32,64})`,
    'im'
  ),
  // Generic hex wallet address
  hex: /\b(0x[a-fA-F0-9]{40})\b/,
  // Generic base58-style address (32-64 alphanumeric)
  generic: /\b([a-zA-Z0-9]{32,64})\b/
};

/**
 * Extract wallet address from PR body using the specified field name
 */
function extractWalletFromPRBody(prBody, fieldName) {
  if (!prBody) return null;

  // Try field-specific match first
  const fieldRegex = WALLET_PATTERNS.field(fieldName);
  const fieldMatch = prBody.match(fieldRegex);
  if (fieldMatch) {
    return fieldMatch[1].trim();
  }

  // Try hex address pattern
  const hexMatch = prBody.match(WALLET_PATTERNS.hex);
  if (hexMatch) {
    return hexMatch[1].trim();
  }

  return null;
}

/**
 * Try to read wallet address from .rtc-wallet file in the repo
 */
function readWalletFile(workspace) {
  const walletPath = path.join(workspace, '.rtc-wallet');
  try {
    if (fs.existsSync(walletPath)) {
      const content = fs.readFileSync(walletPath, 'utf8').trim();
      if (content && content.length >= 32) {
        return content;
      }
    }
  } catch (error) {
    core.debug(`Could not read .rtc-wallet file: ${error.message}`);
  }
  return null;
}

/**
 * Call RustChain API to transfer RTC tokens
 */
async function transferRTC(nodeUrl, fromAddress, toAddress, amount, adminKey) {
  return new Promise((resolve, reject) => {
    const url = new URL('/wallet/transfer/signed', nodeUrl);
    const postData = JSON.stringify({
      from_address: fromAddress,
      to_address: toAddress,
      amount: parseInt(amount, 10),
      admin_key: adminKey
    });

    const options = {
      hostname: url.hostname,
      port: url.port || (url.protocol === 'https:' ? 443 : 80),
      path: url.pathname,
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData)
      }
    };

    const client = url.protocol === 'https:' ? https : require('http');
    const req = client.request(options, (res) => {
      let data = '';
      res.on('data', (chunk) => { data += chunk; });
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          try {
            resolve(JSON.parse(data));
          } catch {
            resolve({ status: 'ok', raw: data });
          }
        } else {
          reject(new Error(`API returned ${res.statusCode}: ${data}`));
        }
      });
    });

    req.on('error', reject);
    req.write(postData);
    req.end();
  });
}

/**
 * Post a comment on the PR
 */
async function postComment(octokit, owner, repo, prNumber, body) {
  await octokit.rest.issues.createComment({
    owner,
    repo,
    issue_number: prNumber,
    body
  });
}

/**
 * Main action logic
 */
async function run() {
  try {
    // Validate event type
    const { context } = github;
    if (context.eventName !== 'pull_request') {
      core.warning('This action only works on pull_request events');
      return;
    }

    // Check if PR was merged
    const payload = context.payload;
    if (!payload.pull_request) {
      core.warning('No pull_request data in payload');
      return;
    }

    const action = payload.action;
    const pr = payload.pull_request;

    if (action !== 'closed' || !pr.merged) {
      core.info(`PR #${pr.number} was closed but not merged. Skipping reward.`);
      core.setOutput('tx-status', 'skipped');
      return;
    }

    // Get inputs
    const nodeUrl = core.getInput('node-url', { required: true });
    const amount = core.getInput('amount', { required: true });
    const walletFrom = core.getInput('wallet-from', { required: true });
    const adminKey = core.getInput('admin-key', { required: true });
    const walletField = core.getInput('wallet-field') || 'wallet';
    const dryRun = core.getInput('dry-run').toLowerCase() === 'true';

    // Find contributor wallet
    const prBody = pr.body || '';
    let recipientWallet = extractWalletFromPRBody(prBody, walletField);

    if (!recipientWallet) {
      core.info('Wallet not found in PR body, checking .rtc-wallet file...');
      recipientWallet = readWalletFile(process.env.GITHUB_WORKSPACE || process.cwd());
    }

    if (!recipientWallet) {
      const msg = `No wallet address found. Add \`${walletField}: <your-wallet>\` to PR body or create .rtc-wallet file.`;
      core.warning(msg);
      core.setOutput('tx-status', 'skipped');
      return;
    }

    core.info(`Recipient wallet: ${recipientWallet}`);
    core.setOutput('recipient', recipientWallet);
    core.setOutput('amount', amount);

    // Build comment
    const repo = `${context.repo.owner}/${context.repo.repo}`;
    const prLink = `https://github.com/${repo}/pull/${pr.number}`;

    if (dryRun) {
      core.info(`[DRY RUN] Would transfer ${amount} RTC from ${walletFrom} to ${recipientWallet}`);
      core.setOutput('tx-status', 'dry-run');

      const octokit = github.getOctokit(core.getInput('github-token') || process.env.GITHUB_TOKEN);
      await postComment(
        octokit,
        context.repo.owner,
        context.repo.repo,
        pr.number,
        `### 🎁 RTC Reward (Dry Run)\n\n` +
        `| Field | Value |\n|---|---|\n` +
        `| Recipient | \`${recipientWallet}\` |\n` +
        `| Amount | **${amount} RTC** |\n` +
        `| PR | [#${pr.number}](${prLink}) |\n\n` +
        `> ⚠️ Dry run mode — no tokens were sent.`
      );
      return;
    }

    // Execute transfer
    core.info(`Transferring ${amount} RTC to ${recipientWallet}...`);
    const result = await transferRTC(nodeUrl, walletFrom, recipientWallet, amount, adminKey);

    core.info(`Transfer result: ${JSON.stringify(result)}`);
    core.setOutput('tx-status', 'sent');

    // Post confirmation comment
    const octokit = github.getOctokit(core.getInput('github-token') || process.env.GITHUB_TOKEN);
    await postComment(
      octokit,
      context.repo.owner,
      context.repo.repo,
      pr.number,
      `### 🎁 RTC Reward Sent!\n\n` +
      `| Field | Value |\n|---|---|\n` +
      `| Recipient | \`${recipientWallet}\` |\n` +
      `| Amount | **${amount} RTC** |\n` +
      `| PR | [#${pr.number}](${prLink}) |\n\n` +
      `✅ Tokens have been transferred successfully.`
    );

  } catch (error) {
    core.setFailed(`Action failed: ${error.message}`);
    core.setOutput('tx-status', 'error');
  }
}

run();

// Export for testing
module.exports = { extractWalletFromPRBody, readWalletFile, transferRTC };
