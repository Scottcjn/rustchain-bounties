const express = require('express');
const axios = require('axios');
const cors = require('cors');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

const RTC_WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const GITHUB_USER = 'Scottcjn';
const GITHUB_API = 'https://api.github.com';
const RTC_API = 'https://api.rtc.network/v1';

// In-memory store for tracking rewards (use DB in production)
const rewardStore = new Map();

app.post('/api/verify', async (req, res) => {
    const { githubToken, walletAddress } = req.body;
    
    if (!githubToken || !walletAddress) {
        return res.status(400).json({ error: 'Missing required fields' });
    }

    try {
        const headers = { Authorization: `token ${githubToken}` };
        
        // Get user info
        const userResponse = await axios.get(`${GITHUB_API}/user`, { headers });
        const username = userResponse.data.login;

        // Check if already claimed
        if (rewardStore.has(username)) {
            return res.status(400).json({ error: 'Already claimed rewards' });
        }

        // Get starred repos
        const starredResponse = await axios.get(`${GITHUB_API}/users/${username}/starred`, { 
            headers,
            params: { per_page: 100 }
        });
        const starredRepos = starredResponse.data;

        // Get all Scottcjn repos
        const scottReposResponse = await axios.get(`${GITHUB_API}/users/${GITHUB_USER}/repos`, {
            headers,
            params: { per_page: 100 }
        });
        const scottRepos = scottReposResponse.data;
        const scottRepoNames = scottRepos.map(repo => repo.full_name);

        // Check following
        const followingResponse = await axios.get(`${GITHUB_API}/users/${username}/following`, {
            headers,
            params: { per_page: 100 }
        });
        const following = followingResponse.data;
        const isFollowingScott = following.some(user => user.login === GITHUB_USER);

        // Calculate rewards
        let totalRTC = 0;
        let rewards = [];

        // Star Rustchain repo
        const rustchainStarred = starredRepos.some(repo => repo.full_name === `${GITHUB_USER}/Rustchain`);
        if (rustchainStarred) {
            totalRTC += 1;
            rewards.push({ action: 'Star Rustchain repo', reward: 1 });
        }

        // Star Scottcjn repos
        const scottStarredCount = starredRepos.filter(repo => scottRepoNames.includes(repo.full_name)).length;
        if (scottStarredCount >= 10) {
            totalRTC += scottStarredCount;
            rewards.push({ action: `Star ${scottStarredCount} Scottcjn repos`, reward: scottStarredCount });
        }

        // Follow Scottcjn
        if (isFollowingScott) {
            totalRTC += 1;
            rewards.push({ action: 'Follow @Scottcjn', reward: 1 });
        }

        // Star King bonus
        const totalStarredCount = starredRepos.length;
        if (totalStarredCount >= 100 && isFollowingScott) {
            totalRTC += 25;
            rewards.push({ action: 'Star King badge + 25 RTC bonus', reward: 25 });
        }

        if (totalRTC === 0) {
            return res.status(400).json({ error: 'No eligible rewards found. Complete the required actions first.' });
        }

        // Send RTC to wallet
        const transferResponse = await axios.post(`${RTC_API}/transfer`, {
            from: RTC_WALLET,
            to: walletAddress,
            amount: totalRTC,
            memo: `GitHub bounty rewards for ${username}`
        }, {
            headers: { 'Authorization': `Bearer ${process.env.RTC_API_KEY}` }
        });

        // Store reward record
        rewardStore.set(username, {
            wallet: walletAddress,
            amount: totalRTC,
            timestamp: new Date().toISOString(),
            rewards
        });

        res.json({
            success: true,
            username,
            totalRTC,
            rewards,
            transaction: transferResponse.data
        });

    } catch (error) {
        console.error('Verification error:', error);
        res.status(500).json({ 
            error: 'Verification failed',
            details: error.response?.data || error.message
        });
    }
});

app.get('/api/rewards/:username', (req, res) => {
    const { username } = req.params;
    const reward = rewardStore.get(username);
    
    if (!reward) {
        return res.status(404).json({ error: 'No rewards found for this user' });
    }
    
    res.json(reward);
});

app.listen(PORT, () => {
    console.log(`Bounty server running on port ${PORT}`);
});