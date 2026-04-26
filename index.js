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
    const url = `https://api.github.com/repos/${owner}/${repo}/contents/.rtc-wallet?ref=${ref}`;
    const headers = {
      'Authorization': `Bearer ${process.env.GITHUB_TOKEN}`,
      'Accept': 'application/vnd.github.v3.raw'
    };

    const response = await axios.get(url, { headers });
    const wallet = response.data.trim();

    if (!wallet) {
      core.warning('.rtc-wallet file found but empty or invalid');
      return null;
    }

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
  const payload = {
    method: 'sendtoaddress',
    params: [toWallet, parseFloat(amount), '', '', false, false, 1, 'UNSET', fromWallet],
    id: 1
  };

  const config = {
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Basic ${Buffer.from(`admin:${adminKey}`).toString('base64')}`
    }
  };

  try {
    const response = await axios.post(nodeUrl, payload, config);
    if (response.data.error) {
      throw new Error(`Node error: ${response.data.error.message}`);
    }
    return response.data.result;
  } catch (error) {
    throw new Error(`Transaction failed: ${error.response?.data?.error?.message || error.message}`);
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