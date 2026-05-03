const express = require('express');
const axios = require('axios');
const cors = require('cors');
const app = express();
app.use(cors());
app.use(express.json());

const RTC_NODE = 'https://rustchain-node.example.com'; // Replace with actual RTC node
const GITHUB_TOKEN = process.env.GITHUB_TOKEN || 'your_github_token_here';
const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';

// In-memory tracking (use DB in production)
const userStars = {};
const userFollows = {};

async function getGitHubUser(username) {
  const res = await axios.get(`https://api.github.com/users/${username}`, {
    headers: { Authorization: `token ${GITHUB_TOKEN}` }
  });
  return res.data;
}

async function getStarredRepos(username) {
  let page = 1;
  let repos = [];
  while (true) {
    const res = await axios.get(`https://api.github.com/users/${username}/starred?per_page=100&page=${page}`, {
      headers: { Authorization: `token ${GITHUB_TOKEN}` }
    });
    repos = repos.concat(res.data);
    if (res.data.length < 100) break;
    page++;
  }
  return repos;
}

async function checkFollow(username) {
  try {
    await axios.get(`https://api.github.com/users/Scottcjn/following/${username}`, {
      headers: { Authorization: `token ${GITHUB_TOKEN}` }
    });
    return true;
  } catch (e) {
    return false;
  }
}

async function sendRTC(to, amount) {
  const tx = {
    from: WALLET,
    to: to,
    amount: amount,
    timestamp: Date.now()
  };
  const res = await axios.post(`${RTC_NODE}/api/transaction`, tx);
  return res.data;
}

app.post('/claim', async (req, res) => {
  const { username, wallet } = req.body;
  if (!username || !wallet) return res.status(400).json({ error: 'username and wallet required' });

  try {
    const user = await getGitHubUser(username);
    const starred = await getStarredRepos(username);
    const following = await checkFollow(username);

    let totalReward = 0;
    let reasons = [];

    // Check Rustchain star
    const hasRustchain = starred.some(r => r.full_name === 'Scottcjn/Rustchain');
    if (hasRustchain && !userStars[username]?.rustchain) {
      totalReward += 1;
      reasons.push('Starred Rustchain: +1 RTC');
      userStars[username] = userStars[username] || {};
      userStars[username].rustchain = true;
    }

    // Check Scottcjn repos stars (up to all)
    const scottcjnRepos = starred.filter(r => r.owner.login === 'Scottcjn');
    const newScottcjnStars = scottcjnRepos.filter(r => !userStars[username]?.scottcjn?.includes(r.name));
    if (newScottcjnStars.length > 0) {
      const reward = newScottcjnStars.length;
      totalReward += reward;
      reasons.push(`Starred ${newScottcjnStars.length} Scottcjn repos: +${reward} RTC`);
      userStars[username] = userStars[username] || {};
      userStars[username].scottcjn = (userStars[username].scottcjn || []).concat(newScottcjnStars.map(r => r.name));
    }

    // Check follow
    if (following && !userFollows[username]) {
      totalReward += 1;
      reasons.push('Followed Scottcjn: +1 RTC');
      userFollows[username] = true;
    }

    // Check Star King badge (100+ repos starred + follow)
    if (starred.length >= 100 && following && !userStars[username]?.starKing) {
      totalReward += 25;
      reasons.push('Star King badge: +25 RTC');
      userStars[username].starKing = true;
    }

    if (totalReward > 0) {
      await sendRTC(wallet, totalReward);
      res.json({ success: true, reward: totalReward, reasons });
    } else {
      res.json({ success: true, reward: 0, reasons: ['No new rewards available'] });
    }
  } catch (err) {
    console.error(err);
    res.status(500).json({ error: 'Internal error' });
  }
});

app.get('/status/:username', async (req, res) => {
  const { username } = req.params;
  const starred = await getStarredRepos(username);
  const following = await checkFollow(username);
  res.json({
    username,
    starredCount: starred.length,
    followingScottcjn: following,
    rustchainStarred: starred.some(r => r.full_name === 'Scottcjn/Rustchain'),
    scottcjnStars: starred.filter(r => r.owner.login === 'Scottcjn').length,
    starKingEligible: starred.length >= 100 && following
  });
});

app.listen(3000, () => console.log('RTC bounty server running on port 3000'));