const express = require('express');
const axios = require('axios');
const cors = require('cors');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());

// Configuration
const GITHUB_TOKEN = process.env.GITHUB_TOKEN || '';
const RTC_WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const RUSTCHAIN_REPO = 'Scottcjn/Rustchain';
const SCOTTCJN_USER = 'Scottcjn';

// In-memory store for rewards (replace with DB in production)
const rewards = {};

// Helper: GitHub API headers
const githubHeaders = {
  headers: {
    'Authorization': `token ${GITHUB_TOKEN}`,
    'Accept': 'application/vnd.github.v3+json'
  }
};

// Helper: Check if user starred a repo
async function hasStarredRepo(username, repo) {
  try {
    const response = await axios.get(
      `https://api.github.com/user/starred/${repo}`,
      { ...githubHeaders, validateStatus: status => status < 500 }
    );
    return response.status === 204;
  } catch (error) {
    return false;
  }
}

// Helper: Get user's starred repos count
async function getStarredCount(username) {
  try {
    const response = await axios.get(
      `https://api.github.com/users/${username}/starred?per_page=1`,
      githubHeaders
    );
    const linkHeader = response.headers.link;
    if (!linkHeader) return 0;
    const match = linkHeader.match(/page=(\d+)>; rel="last"/);
    return match ? parseInt(match[1]) : 0;
  } catch (error) {
    return 0;
  }
}

// Helper: Check if user follows Scottcjn
async function isFollowing(username) {
  try {
    const response = await axios.get(
      `https://api.github.com/user/following/${SCOTTCJN_USER}`,
      { ...githubHeaders, validateStatus: status => status < 500 }
    );
    return response.status === 204;
  } catch (error) {
    return false;
  }
}

// Helper: Get all Scottcjn repos
async function getScottcjnRepos() {
  try {
    const response = await axios.get(
      `https://api.github.com/users/${SCOTTCJN_USER}/repos?per_page=100`,
      githubHeaders
    );
    return response.data.map(repo => repo.full_name);
  } catch (error) {
    return [];
  }
}

// Helper: Check which Scottcjn repos user starred
async function getStarredScottcjnRepos(username) {
  const allRepos = await getScottcjnRepos();
  const starredRepos = [];
  for (const repo of allRepos) {
    if (await hasStarredRepo(username, repo)) {
      starredRepos.push(repo);
    }
  }
  return starredRepos;
}

// Endpoint: Verify and reward
app.post('/verify', async (req, res) => {
  const { username } = req.body;
  if (!username) {
    return res.status(400).json({ error: 'Username required' });
  }

  try {
    let totalReward = 0;
    const rewardsBreakdown = [];

    // 1. Star Rustchain repo
    if (await hasStarredRepo(username, RUSTCHAIN_REPO)) {
      totalReward += 1;
      rewardsBreakdown.push({ action: 'Star Rustchain repo', reward: 1 });
    }

    // 2. Star Scottcjn repos
    const starredScottcjnRepos = await getStarredScottcjnRepos(username);
    if (starredScottcjnRepos.length >= 10) {
      const repoReward = starredScottcjnRepos.length;
      totalReward += repoReward;
      rewardsBreakdown.push({ action: `Star ${starredScottcjnRepos.length} Scottcjn repos`, reward: repoReward });
    }

    // 3. Follow Scottcjn
    if (await isFollowing(username)) {
      totalReward += 1;
      rewardsBreakdown.push({ action: 'Follow @Scottcjn', reward: 1 });
    }

    // 4. Star King badge (100+ repos + follow)
    const totalStarred = await getStarredCount(username);
    if (totalStarred >= 100 && await isFollowing(username)) {
      totalReward += 25;
      rewardsBreakdown.push({ action: 'Star King badge (100+ repos + follow)', reward: 25 });
    }

    // Store reward (simulate sending RTC)
    if (totalReward > 0) {
      rewards[username] = (rewards[username] || 0) + totalReward;
      console.log(`Rewarded ${username} with ${totalReward} RTC (Total: ${rewards[username]})`);
    }

    res.json({
      username,
      totalReward,
      rewardsBreakdown,
      wallet: RTC_WALLET,
      message: totalReward > 0 ? `Reward of ${totalReward} RTC sent to ${RTC_WALLET}` : 'No rewards earned'
    });

  } catch (error) {
    console.error('Verification error:', error);
    res.status(500).json({ error: 'Verification failed' });
  }
});

// Endpoint: Check balance
app.get('/balance/:username', (req, res) => {
  const { username } = req.params;
  res.json({ username, balance: rewards[username] || 0 });
});

// Start server
app.listen(PORT, () => {
  console.log(`Bounty server running on port ${PORT}`);
  console.log(`RTC Wallet: ${RTC_WALLET}`);
});