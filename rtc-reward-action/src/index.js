const core = require('@actions/core');
const axios = require('axios');

async function run() {
  try {
    const nodeUrl = core.getInput('node-url');
    const amount = parseInt(core.getInput('amount'));
    const walletFrom = core.getInput('wallet-from');
    const adminKey = core.getInput('admin-key');
    const dryRun = core.getInput('dry-run') === 'true';

    const eventPath = process.env.GITHUB_EVENT_PATH;
    const event = require(eventPath);
    const pr = event.pull_request;

    if (!pr.merged) {
      core.info('PR was not merged, skipping reward');
      return;
    }

    let recipient = pr.user.login;
    const bodyMatch = pr.body?.match(/wallet[:\s]+([a-zA-Z0-9_-]+)/i);
    if (bodyMatch) {
      recipient = bodyMatch[1];
    }

    core.info(`Awarding ${amount} RTC to ${recipient}`);

    if (dryRun) {
      core.info('Dry-run mode: skipping actual transfer');
      core.setOutput('recipient', recipient);
      core.setOutput('amount', amount.toString());
      return;
    }

    const response = await axios.post(`${nodeUrl}/wallet/transfer`, {
      from: walletFrom,
      to: recipient,
      amount: amount
    }, {
      headers: {
        'Authorization': `Bearer ${adminKey}`,
        'Content-Type': 'application/json'
      }
    });

    core.info(`Transfer successful: ${JSON.stringify(response.data)}`);
    core.setOutput('recipient', recipient);
    core.setOutput('amount', amount.toString());

  } catch (error) {
    core.setFailed(error.message);
  }
}

run();
