const core = require('@actions/core');
const github = require('@actions/core');
const https = require('https');
const http = require('http');

async function run() {
  try {
    // Only run on merged PRs
    const payload = github.context.payload;
    if (payload.action !== 'closed' || !payload.pull_request?.merged) {
      core.info('PR not merged, skipping reward');
      return;
    }

    const nodeUrl = core.getInput('node-url', { required: true });
    const amount = parseInt(core.getInput('amount', { required: true }));
    const walletFrom = core.getInput('wallet-from', { required: true });
    const walletKey = core.getInput('wallet-key', { required: true });
    const walletTo = core.getInput('wallet-to') || payload.pull_request.user.login;

    const prNumber = payload.pull_request.number;
    const prAuthor = payload.pull_request.user.login;
    const prTitle = payload.pull_request.title;

    core.info(`PR #${prNumber} merged by ${prAuthor}: "${prTitle}"`);
    core.info(`Awarding ${amount} RTC from ${walletFrom} to ${walletTo}`);

    // Build transaction
    const txData = {
      from: walletFrom,
      to: walletTo,
      amount: amount,
      memo: `PR #${prNumber} merged: ${prTitle}`.substring(0, 128),
      timestamp: Date.now()
    };

    // Send to RustChain node
    const url = new URL('/api/transfer', nodeUrl);
    const transport = url.protocol === 'https:' ? https : http;

    const postData = JSON.stringify(txData);

    const req = transport.request(url, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Content-Length': Buffer.byteLength(postData),
        'Authorization': `Bearer ${walletKey}`
      }
    }, (res) => {
      let data = '';
      res.on('data', chunk => data += chunk);
      res.on('end', () => {
        if (res.statusCode >= 200 && res.statusCode < 300) {
          core.info(`✅ Reward sent: ${amount} RTC to ${walletTo}`);
          core.setOutput('tx_hash', data);
          core.setOutput('amount', amount.toString());
          core.setOutput('recipient', walletTo);
        } else {
          core.warning(`Node returned ${res.statusCode}: ${data}`);
          core.setOutput('status', 'pending');
        }
      });
    });

    req.on('error', (e) => {
      core.warning(`Failed to send reward: ${e.message}`);
      core.setOutput('status', 'error');
    });

    req.write(postData);
    req.end();

  } catch (error) {
    core.setFailed(error.message);
  }
}

run();
