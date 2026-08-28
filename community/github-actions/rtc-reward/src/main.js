const core = require('@actions/core');
const github = require('@actions/github');
const fetch = require('node-fetch');
const { extractRtcWallet } = require('./wallet');

async function getContributorWallet() {
  const walletFile = core.getInput('wallet-file');
  const prBody = github.context.payload.pull_request?.body || '';
  
  // Try to extract wallet from PR body
  const prWallet = extractRtcWallet(prBody);
  if (prWallet) return prWallet;
  
  // Try to get wallet from file in repo
  try {
    const response = await fetch(
      `https://api.github.com/repos/${github.context.repo.owner}/${github.context.repo.repo}/contents/${walletFile}`,
      {
        headers: {
          'Authorization': `token ${process.env.GITHUB_TOKEN}`,
          'Accept': 'application/vnd.github.v3+json'
        }
      }
    );
    
    if (response.ok) {
      const data = await response.json();
      const wallet = extractRtcWallet(
        Buffer.from(data.content, 'base64').toString().trim()
      );
      if (wallet) return wallet;
    }
  } catch (error) {
    core.info(`Could not read wallet file: ${error.message}`);
  }
  
  // Fallback to PR author
  return github.context.payload.pull_request?.user?.login || 'unknown';
}

async function awardRTC(contributorWallet, amount, nodeUrl, adminKey, dryRun) {
  if (dryRun === 'true') {
    core.info(`DRY RUN: Would award ${amount} RTC to ${contributorWallet}`);
    return { success: true, message: 'Dry run completed' };
  }
  
  try {
    const response = await fetch(`${nodeUrl}/admin/transfer`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-Admin-Key': adminKey
      },
      body: JSON.stringify({
        from_wallet: core.getInput('wallet-from'),
        to_wallet: contributorWallet,
        amount_rtc: parseFloat(amount)
      })
    });
    
    const result = await response.json();
    return { success: response.ok, message: result.message || 'Transfer completed' };
  } catch (error) {
    return { success: false, message: error.message };
  }
}

async function main() {
  try {
    // Verify this is a merged PR
    if (!github.context.payload.pull_request?.merged) {
      core.info('PR not merged, skipping reward');
      return;
    }
    
    const amount = core.getInput('amount');
    const nodeUrl = core.getInput('node-url');
    const adminKey = core.getInput('admin-key');
    const dryRun = core.getInput('dry-run');
    
    const contributorWallet = await getContributorWallet();
    core.info(`Awarding ${amount} RTC to contributor: ${contributorWallet}`);
    
    const result = await awardRTC(contributorWallet, amount, nodeUrl, adminKey, dryRun);
    
    if (result.success) {
      core.info(`Successfully awarded ${amount} RTC to ${contributorWallet}`);
      await core.setOutput('success', 'true');
    } else {
      core.setFailed(`Failed to award RTC: ${result.message}`);
      await core.setOutput('success', 'false');
    }
    
    // Post comment on PR
    const octokit = github.getOctokit(process.env.GITHUB_TOKEN);
    await octokit.rest.issues.createComment({
      owner: github.context.repo.owner,
      repo: github.context.repo.repo,
      issue_number: github.context.issue.number,
      body: result.success 
        ? `✅ **RTC Reward Awarded**\n\n${amount} RTC has been transferred to wallet \`${contributorWallet}\`.\n\nThank you for your contribution! 🌾`
        : `❌ **RTC Reward Failed**\n\nFailed to transfer ${amount} RTC: ${result.message}`
    });
    
  } catch (error) {
    core.setFailed(error.message);
  }
}

main();
