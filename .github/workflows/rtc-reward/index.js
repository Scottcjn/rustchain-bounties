const core = require('@actions/core');

async function run() {
  try {
    const nodeUrl = core.getInput('node-url');
    const amount = core.getInput('amount');
    const walletFrom = core.getInput('wallet-from');
    const adminKey = core.getInput('admin-key');
    const dryRun = core.getInput('dry-run') === 'true';
    
    // Get PR info
    const pr = process.env.GITHUB_EVENT_PATH ? require(process.env.GITHUB_EVENT_PATH) : {};
    
    // Check if PR was merged
    if (!pr.pull_request || pr.pull_request.merged !== true) {
      console.log('PR not merged, skipping');
      return;
    }
    
    const contributorWallet = pr.pull_request.user?.login || 'contributor';
    
    if (dryRun) {
      console.log(`DRY RUN: Would award ${amount} RTC to ${contributorWallet}`);
      core.notice(`DRY RUN: Would award ${amount} RTC to ${contributorWallet}`);
      return;
    }
    
    // Call RustChain API to transfer RTC
    const response = await fetch(`${nodeUrl}/wallet/transfer`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        from: walletFrom,
        to: contributorWallet,
        amount: parseInt(amount),
        key: adminKey
      })
    });
    
    const result = await response.json();
    
    console.log(`Awarded ${amount} RTC to ${contributorWallet}`);
    core.notice(`Successfully awarded ${amount} RTC to ${contributorWallet}`);
    
  } catch (error) {
    core.setFailed(error.message);
  }
}

run();
