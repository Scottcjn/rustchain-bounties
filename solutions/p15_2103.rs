const express = require('express');
const axios = require('axios');
const { TronWeb } = require('tronweb');
const app = express();
app.use(express.json());

const tronWeb = new TronWeb({
    fullHost: 'https://api.trongrid.io',
    privateKey: process.env.PRIVATE_KEY
});

const RTC_CONTRACT = 'TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t';
const BOUNTY_WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const TARGET_USER = 'Scottcjn';

async function verifyStar(username, repo) {
    try {
        const res = await axios.get(`https://api.github.com/repos/${username}/${repo}/stargazers`, {
            headers: { Authorization: `token ${GITHUB_TOKEN}` }
        });
        return res.data.some(u => u.login === username);
    } catch { return false; }
}

async function verifyFollow(follower, target) {
    try {
        const res = await axios.get(`https://api.github.com/users/${target}/followers`, {
            headers: { Authorization: `token ${GITHUB_TOKEN}` }
        });
        return res.data.some(u => u.login === follower);
    } catch { return false; }
}

async function sendRTC(to, amount) {
    const contract = await tronWeb.contract().at(RTC_CONTRACT);
    const decimals = await contract.decimals().call();
    const adjusted = amount * Math.pow(10, decimals);
    await contract.transfer(to, adjusted).send();
}

app.post('/claim', async (req, res) => {
    const { githubUser, wallet, action } = req.body;
    if (!githubUser || !wallet || !action) return res.status(400).json({ error: 'Missing fields' });

    let reward = 0;
    try {
        if (action === 'star_rustchain') {
            const starred = await verifyStar(githubUser, 'Rustchain');
            if (starred) reward = 1;
        } else if (action === 'star_scottcjn') {
            const reposRes = await axios.get(`https://api.github.com/users/${TARGET_USER}/repos?per_page=100`, {
                headers: { Authorization: `token ${GITHUB_TOKEN}` }
            });
            const repos = reposRes.data.map(r => r.name);
            let starredCount = 0;
            for (const repo of repos) {
                if (await verifyStar(githubUser, repo)) starredCount++;
            }
            reward = Math.min(starredCount, repos.length);
        } else if (action === 'follow') {
            const following = await verifyFollow(githubUser, TARGET_USER);
            if (following) reward = 1;
        } else if (action === 'star_king') {
            const reposRes = await axios.get(`https://api.github.com/users/${TARGET_USER}/repos?per_page=100`, {
                headers: { Authorization: `token ${GITHUB_TOKEN}` }
            });
            const repos = reposRes.data.map(r => r.name);
            let starredCount = 0;
            for (const repo of repos) {
                if (await verifyStar(githubUser, repo)) starredCount++;
            }
            const following = await verifyFollow(githubUser, TARGET_USER);
            if (starredCount >= 100 && following) reward = 25;
        }

        if (reward > 0) {
            await sendRTC(wallet, reward);
            res.json({ success: true, reward });
        } else {
            res.status(400).json({ error: 'Action not verified' });
        }
    } catch (err) {
        res.status(500).json({ error: err.message });
    }
});

app.listen(3000, () => console.log('Bounty server running on port 3000'));