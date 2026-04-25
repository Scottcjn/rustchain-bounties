const core = require('@actions/core');
const github = require('@actions/github');
const axios = require('axios');

async function run() {
  try {
    const nodeUrl = core.getInput('node-url');
    const amount = core.getInput('amount');
    const walletFrom = core.getInput('wallet-from');
    const adminKey = core.getInput('admin-key');
    const dryRun = core.getInput('dry-run') === 'true';

    const context = github.context;
    const pr = context.payload.pull_request;

    if (!pr || !pr.merged) {
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
    const url = `${nodeUrl}/api/v1/contents/.rtc-wallet?ref=${ref}`;
    const response = await axios.get(url, {
      headers: {
        Authorization: `token ${process.env.GITHUB_TOKEN}`,
        Accept: 'application/vnd.github.v3+json'
      }
    });
    const content = Buffer.from(response.data.content, 'base64').toString('utf8');
    return content.trim().split('\n')[0].trim() || null;
  } catch (error) {
    if (error.response && error.response.status === 404) {
      return null;
    }
    throw error;
  }
}

async function sendRtcTransaction(nodeUrl, from, to, amount, privateKey) {
  const url = `${nodeUrl}/api/v1/send_transaction`;
  const data = {
    from,
    to,
    amount: parseFloat(amount),
    privateKey
  };
  const response = await axios.post(url, data);
  return response.data.transaction_hash;
}

async function commentOnPR(octokit, owner, repo, prNumber, body) {
  await octokit.rest.issues.createComment({
    owner,
    repo,
    issue_number: prNumber,
    body
  });
}

run();