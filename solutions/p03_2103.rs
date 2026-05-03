const express = require('express');
const axios = require('axios');
const cors = require('cors');
const app = express();
app.use(cors());
app.use(express.json());

const RTC_TOKEN = process.env.RTC_TOKEN || 'your-rtc-token';
const RTC_WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const GITHUB_USERNAME = 'Scottcjn';
const REPO_NAME = 'Rustchain';
const MIN_STARS_FOR_BADGE = 100;

const claimedStars = new Map();
const claimedFollows = new Map();

async function checkStar(username, repo) {
  try {
    const res = await axios.get(`https://api.github.com/repos/${username}/${repo}/stargazers`, {
      headers: { Accept: 'application/vnd.github.v3+json' }
    });
    return res.data.some(user => user.login === username);
  } catch {
    return false;
  }
}

async function checkFollow(follower, target) {
  try {
    const res = await axios.get(`https://api.github.com/users/${target}/followers`, {
      headers: { Accept: 'application/vnd.github.v3+json' }
    });
    return res.data.some(user => user.login === follower);
  } catch {
    return false;
  }
}

async function getStarCount(username) {
  try {
    const res = await axios.get(`https://api.github.com/users/${username}/repos?per_page=100`, {
      headers: { Accept: 'application/vnd.github.v3+json' }
    });
    let totalStars = 0;
    for (const repo of res.data) {
      totalStars += repo.stargazers_count;
    }
    return totalStars;
  } catch {
    return 0;
  }
}

app.post('/claim/star', async (req, res) => {
  const { githubUser } = req.body;
  if (!githubUser) return res.status(400).json({ error: 'Missing githubUser' });

  if (claimedStars.has(githubUser)) {
    return res.status(400).json({ error: 'Already claimed' });
  }

  const hasStarred = await checkStar(githubUser, REPO_NAME);
  if (!hasStarred) return res.status(400).json({ error: 'Not starred' });

  claimedStars.set(githubUser, true);
  res.json({ reward: 1, token: RTC_TOKEN, wallet: RTC_WALLET });
});

app.post('/claim/follow', async (req, res) => {
  const { githubUser } = req.body;
  if (!githubUser) return res.status(400).json({ error: 'Missing githubUser' });

  if (claimedFollows.has(githubUser)) {
    return res.status(400).json({ error: 'Already claimed' });
  }

  const isFollowing = await checkFollow(githubUser, GITHUB_USERNAME);
  if (!isFollowing) return res.status(400).json({ error: 'Not following' });

  claimedFollows.set(githubUser, true);
  res.json({ reward: 1, token: RTC_TOKEN, wallet: RTC_WALLET });
});

app.post('/claim/bulk-stars', async (req, res) => {
  const { githubUser } = req.body;
  if (!githubUser) return res.status(400).json({ error: 'Missing githubUser' });

  if (claimedStars.has(githubUser)) {
    return res.status(400).json({ error: 'Already claimed' });
  }

  const repos = await axios.get(`https://api.github.com/users/${GITHUB_USERNAME}/repos?per_page=100`, {
    headers: { Accept: 'application/vnd.github.v3+json' }
  });

  let starredCount = 0;
  for (const repo of repos.data) {
    const hasStarred = await checkStar(githubUser, repo.name);
    if (hasStarred) starredCount++;
  }

  if (starredCount < 10) return res.status(400).json({ error: 'Need 10+ starred repos' });

  claimedStars.set(githubUser, true);
  res.json({ reward: starredCount, token: RTC_TOKEN, wallet: RTC_WALLET });
});

app.post('/claim/star-king', async (req, res) => {
  const { githubUser } = req.body;
  if (!githubUser) return res.status(400).json({ error: 'Missing githubUser' });

  if (claimedStars.has(githubUser)) {
    return res.status(400).json({ error: 'Already claimed' });
  }

  const totalStars = await getStarCount(githubUser);
  if (totalStars < MIN_STARS_FOR_BADGE) return res.status(400).json({ error: 'Need 100+ stars' });

  const isFollowing = await checkFollow(githubUser, GITHUB_USERNAME);
  if (!isFollowing) return res.status(400).json({ error: 'Not following' });

  claimedStars.set(githubUser, true);
  res.json({ reward: 25, badge: 'Star King', token: RTC_TOKEN, wallet: RTC_WALLET });
});

app.listen(3000, () => console.log('Bounty server running on port 3000'));