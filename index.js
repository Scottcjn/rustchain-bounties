// File: index.js
const core = require('@actions/core');
const github = require('@actions/github');
const axios = require('axios');

async function run() {
  try {
    const nodeUrl = core.getInput('node-url', { required: true });
    const amount = core.getInput('amount', { required: true });
    const walletFrom = core.getInput('wallet-from', { required: true });
    const adminKey = core.getInput('admin-key', { required: true });
    const dryRun = core.getInput('dry-run') === 'true';

    const context = github.context;
    const payload = context.payload;
    const pr = payload.pull_request;

    if (!pr) {
      core.info('No pull_request payload found. Exiting.');
      return;
    }

    if (!pr.merged) {
      core.info('PR is not merged. Exiting.');
      return;
    }

    const prNumber = pr.number;
    const repo = context.repo;
    const prBody = pr.body || '';
    const prHeadSha = pr.head.sha;

    let contributorWallet = extractWalletFromBody(prBody);
    if (!contributorWallet) {
      contributorWallet = await getWalletFromFile(
        nodeUrl,
        repo.owner,
        repo.repo,
        prHeadSha,
        adminKey
      );
    }

    if (!contributorWallet) {
      core.setFailed('Could not determine contributor wallet from PR body or .rtc-wallet file');
      return;
    }

    core.info(`Awarding ${amount} RTC to wallet: ${contributorWallet}`);

    if (dryRun) {
      core.info('DRY RUN: No transaction sent');
      await commentOnPR(
        github.getOctokit(process.env.GITHUB_TOKEN),
        repo.owner,
        repo.repo,
        prNumber,
        `💰 DRY RUN: Would award ${amount} RTC to \`${contributorWallet}\` for merged PR #${prNumber}`
      );
      return;
    }

    const txHash = await sendRtcTransaction(
      nodeUrl,
      walletFrom,
      contributorWallet,
      amount,
      adminKey
    );

    await commentOnPR(
      github.getOctokit(process.env.GITHUB_TOKEN),
      repo.owner,
      repo.repo,
      prNumber,
      `💰 Successfully awarded ${amount} RTC to \`${contributorWallet}\` for merged PR #${prNumber}\nTransaction: \`${txHash}\``
    );

    core.setOutput('transaction-hash', txHash);
  } catch (error) {
    core.setFailed(`Action failed: ${error.message}`);
  }
}

function extractWalletFromBody(body) {
  const walletMatch = body.match(/Wallet:\s*(\S+)/i);
  return walletMatch ? walletMatch[1].trim() : null;
}

async function getWalletFromFile(nodeUrl, owner, repo, ref, adminKey) {
  try {
    const url = `${nodeUrl}/api/v1/repos/${owner}/${repo}/contents/.rtc-wallet?ref=${ref}`;
    const response = await axios.get(url, {
      headers: {
        Authorization: `token ${process.env.GITHUB_TOKEN}`,
        'X-Gitea-Admin': adminKey
      }
    });

    const content = Buffer.from(response.data.content, 'base64').toString('utf8');
    const wallet = content.trim();
    return wallet;
  } catch (error) {
    if (error.response && error.response.status === 404) {
      core.info('.rtc-wallet file not found in PR branch');
      return null;
    }
    core.warning(`Failed to fetch .rtc-wallet: ${error.message}`);
    return null;
  }
}

async function sendRtcTransaction(nodeUrl, fromWallet, toWallet, amount, adminKey) {
  try {
    const url = `${nodeUrl}/api/v1/transactions/send`;
    const response = await axios.post(
      url,
      {
        from: fromWallet,
        to: toWallet,
        amount: parseFloat(amount)
      },
      {
        headers: {
          'Content-Type': 'application/json',
          Authorization: `Bearer ${adminKey}`
        }
      }
    );

    if (response.data && response.data.hash) {
      return response.data.hash;
    } else {
      throw new Error('No transaction hash returned from node');
    }
  } catch (error) {
    throw new Error(`Transaction failed: ${error.response?.data?.message || error.message}`);
  }
}

async function commentOnPR(octokit, owner, repo, prNumber, body) {
  try {
    await octokit.rest.issues.createComment({
      owner,
      repo,
      issue_number: prNumber,
      body
    });
  } catch (error) {
    core.warning(`Failed to comment on PR: ${error.message}`);
  }
}

run();