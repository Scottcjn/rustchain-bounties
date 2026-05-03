const express = require('express');
const axios = require('axios');
const cors = require('cors');
const app = express();
app.use(cors());
app.use(express.json());

const RTC_TOKEN_ADDRESS = 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t';
const RPC_URL = 'https://api.trongrid.io';
const PRIVATE_KEY = process.env.PRIVATE_KEY || 'your_private_key_here';
const WALLET_ADDRESS = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const GITHUB_TOKEN = process.env.GITHUB_TOKEN || 'your_github_token_here';

const users = {};

async function sendRTC(to, amount) {
    const TronWeb = require('tronweb');
    const tronWeb = new TronWeb({
        fullHost: RPC_URL,
        privateKey: PRIVATE_KEY
    });
    const contract = await tronWeb.contract().at(RTC_TOKEN_ADDRESS);
    const result = await contract.transfer(to, tronWeb.toSun(amount)).send();
    return result;
}

async function checkGithubStars(username) {
    try {
        const repos = await axios.get(`https://api.github.com/users/${username}/repos`, {
            headers: { Authorization: `token ${GITHUB_TOKEN}` }
        });
        const starredRepos = repos.data.filter(repo => repo.stargazers_count > 0);
        return starredRepos.length;
    } catch (error) {
        console.error('Error checking stars:', error);
        return 0;
    }
}

async function checkGithubFollow(username) {
    try {
        const user = await axios.get(`https://api.github.com/users/${username}`, {
            headers: { Authorization: `token ${GITHUB_TOKEN}` }
        });
        return user.data.followers > 0;
    } catch (error) {
        console.error('Error checking follow:', error);
        return false;
    }
}

app.post('/claim', async (req, res) => {
    const { githubUsername, walletAddress } = req.body;
    if (!githubUsername || !walletAddress) {
        return res.status(400).json({ error: 'Missing githubUsername or walletAddress' });
    }

    const userKey = `${githubUsername}_${walletAddress}`;
    if (users[userKey] && users[userKey].claimed) {
        return res.status(400).json({ error: 'Already claimed' });
    }

    let totalReward = 0;
    let actions = [];

    // Check Rustchain star
    try {
        const rustchain = await axios.get('https://api.github.com/repos/Rustchain/Rustchain', {
            headers: { Authorization: `token ${GITHUB_TOKEN}` }
        });
        if (rustchain.data.stargazers_count > 0) {
            totalReward += 1;
            actions.push('Starred Rustchain');
        }
    } catch (e) {
        console.error('Rustchain check failed:', e);
    }

    // Check Scottcjn repos stars
    try {
        const scottRepos = await axios.get('https://api.github.com/users/Scottcjn/repos', {
            headers: { Authorization: `token ${GITHUB_TOKEN}` }
        });
        const starredScott = scottRepos.data.filter(repo => repo.stargazers_count > 0);
        const scottStars = Math.min(starredScott.length, scottRepos.data.length);
        if (scottStars >= 10) {
            totalReward += scottStars;
            actions.push(`Starred ${scottStars} Scottcjn repos`);
        }
    } catch (e) {
        console.error('Scottcjn repos check failed:', e);
    }

    // Check follow
    const isFollowing = await checkGithubFollow(githubUsername);
    if (isFollowing) {
        totalReward += 1;
        actions.push('Followed @Scottcjn');
    }

    // Check 100+ stars + follow for badge bonus
    const totalStars = await checkGithubStars(githubUsername);
    if (totalStars >= 100 && isFollowing) {
        totalReward += 25;
        actions.push('Star King badge + 25 RTC bonus');
    }

    if (totalReward === 0) {
        return res.status(400).json({ error: 'No qualifying actions found' });
    }

    try {
        const txId = await sendRTC(walletAddress, totalReward);
        users[userKey] = { claimed: true, reward: totalReward, txId };
        res.json({ success: true, reward: totalReward, txId, actions });
    } catch (error) {
        res.status(500).json({ error: 'Transfer failed', details: error.message });
    }
});

app.get('/status/:githubUsername/:walletAddress', (req, res) => {
    const { githubUsername, walletAddress } = req.params;
    const userKey = `${githubUsername}_${walletAddress}`;
    const user = users[userKey];
    if (user) {
        res.json({ claimed: true, reward: user.reward, txId: user.txId });
    } else {
        res.json({ claimed: false });
    }
});

app.listen(3000, () => {
    console.log('RTC Bounty server running on port 3000');
});