const express = require('express');
const axios = require('axios');
const cors = require('cors');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

const RTC_WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const GITHUB_USER = 'Scottcjn';
const RUSTCHAIN_REPO = 'Rustchain';
const RTC_API_URL = 'https://api.rustchain.io/v1/transfer';

let bountyStats = {
  totalStars: 0,
  totalFollows: 0,
  totalRewards: 0,
  starKingCount: 0
};

function verifyGitHubToken(token) {
  return token && token.length > 0;
}

async function checkGitHubStars(username, token) {
  try {
    const response = await axios.get(`https://api.github.com/users/${username}/repos?per_page=100`, {
      headers: { Authorization: `token ${token}` }
    });
    const repos = response.data;
    const starredRepos = repos.filter(repo => repo.stargazers_count > 0);
    return starredRepos.length;
  } catch (error) {
    console.error('Error checking GitHub stars:', error);
    return 0;
  }
}

async function checkGitHubFollow(username, token) {
  try {
    const response = await axios.get(`https://api.github.com/users/${username}/followers?per_page=100`, {
      headers: { Authorization: `token ${token}` }
    });
    const followers = response.data;
    return followers.some(follower => follower.login === username);
  } catch (error) {
    console.error('Error checking GitHub follow:', error);
    return false;
  }
}

async function sendRTC(wallet, amount, memo) {
  try {
    const response = await axios.post(RTC_API_URL, {
      from: RTC_WALLET,
      to: wallet,
      amount: amount,
      memo: memo
    });
    return response.data;
  } catch (error) {
    console.error('Error sending RTC:', error);
    return null;
  }
}

app.post('/api/claim', async (req, res) => {
  const { githubToken, wallet } = req.body;

  if (!verifyGitHubToken(githubToken)) {
    return res.status(400).json({ error: 'Invalid GitHub token' });
  }

  if (!wallet || wallet.length < 10) {
    return res.status(400).json({ error: 'Invalid wallet address' });
  }

  try {
    let totalReward = 0;
    let rewards = [];

    // Check Rustchain star
    const rustchainStarred = await checkGitHubStars(GITHUB_USER, githubToken);
    if (rustchainStarred > 0) {
      totalReward += 1;
      rewards.push({ action: 'Star Rustchain', reward: 1 });
    }

    // Check Scottcjn repos stars
    const scottcjnStars = await checkGitHubStars(GITHUB_USER, githubToken);
    if (scottcjnStars >= 10) {
      totalReward += scottcjnStars;
      rewards.push({ action: `Star ${scottcjnStars} Scottcjn repos`, reward: scottcjnStars });
    }

    // Check follow
    const isFollowing = await checkGitHubFollow(GITHUB_USER, githubToken);
    if (isFollowing) {
      totalReward += 1;
      rewards.push({ action: 'Follow @Scottcjn', reward: 1 });
    }

    // Check Star King bonus
    if (scottcjnStars >= 100 && isFollowing) {
      totalReward += 25;
      rewards.push({ action: 'Star King badge + 25 RTC bonus', reward: 25 });
      bountyStats.starKingCount++;
    }

    if (totalReward > 0) {
      const result = await sendRTC(wallet, totalReward, 'GitHub Star & Follow Bounty');
      if (result) {
        bountyStats.totalStars += scottcjnStars;
        bountyStats.totalFollows += isFollowing ? 1 : 0;
        bountyStats.totalRewards += totalReward;

        return res.json({
          success: true,
          wallet: wallet,
          totalReward: totalReward,
          rewards: rewards,
          transaction: result
        });
      } else {
        return res.status(500).json({ error: 'Failed to send RTC' });
      }
    } else {
      return res.json({
        success: false,
        message: 'No eligible actions found. Please star repos and follow @Scottcjn.',
        wallet: wallet
      });
    }
  } catch (error) {
    console.error('Error processing claim:', error);
    return res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/api/stats', (req, res) => {
  res.json(bountyStats);
});

app.get('/api/health', (req, res) => {
  res.json({ status: 'ok', wallet: RTC_WALLET });
});

app.listen(PORT, () => {
  console.log(`Bounty server running on port ${PORT}`);
  console.log(`RTC Wallet: ${RTC_WALLET}`);
});