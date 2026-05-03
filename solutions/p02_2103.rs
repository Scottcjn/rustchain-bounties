const express = require('express');
const axios = require('axios');
const cors = require('cors');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

const GITHUB_TOKEN = process.env.GITHUB_TOKEN || 'your_github_token_here';
const RTC_WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const RUSTCHAIN_REPO = 'Scottcjn/Rustchain';
const SCOTTCJN_USERNAME = 'Scottcjn';
const MIN_STARS_FOR_BADGE = 100;

// In-memory store for bounty claims (replace with DB in production)
const bountyClaims = {};

async function verifyStar(username, repo) {
    try {
        const response = await axios.get(`https://api.github.com/repos/${repo}/stargazers`, {
            headers: { Authorization: `token ${GITHUB_TOKEN}` },
            params: { per_page: 100 }
        });
        return response.data.some(user => user.login === username);
    } catch (error) {
        console.error(`Error verifying star for ${repo}:`, error.message);
        return false;
    }
}

async function verifyFollow(follower, target) {
    try {
        const response = await axios.get(`https://api.github.com/users/${target}/followers`, {
            headers: { Authorization: `token ${GITHUB_TOKEN}` },
            params: { per_page: 100 }
        });
        return response.data.some(user => user.login === follower);
    } catch (error) {
        console.error(`Error verifying follow:`, error.message);
        return false;
    }
}

async function getUserStarCount(username) {
    try {
        let page = 1;
        let totalStars = 0;
        while (true) {
            const response = await axios.get(`https://api.github.com/users/${username}/starred`, {
                headers: { Authorization: `token ${GITHUB_TOKEN}` },
                params: { per_page: 100, page }
            });
            totalStars += response.data.length;
            if (response.data.length < 100) break;
            page++;
        }
        return totalStars;
    } catch (error) {
        console.error(`Error getting star count:`, error.message);
        return 0;
    }
}

async function getScottcjnRepos() {
    try {
        let page = 1;
        let allRepos = [];
        while (true) {
            const response = await axios.get(`https://api.github.com/users/${SCOTTCJN_USERNAME}/repos`, {
                headers: { Authorization: `token ${GITHUB_TOKEN}` },
                params: { per_page: 100, page }
            });
            allRepos = allRepos.concat(response.data);
            if (response.data.length < 100) break;
            page++;
        }
        return allRepos.map(repo => repo.full_name);
    } catch (error) {
        console.error(`Error fetching repos:`, error.message);
        return [];
    }
}

async function verifyScottcjnStars(username) {
    const repos = await getScottcjnRepos();
    let starredCount = 0;
    for (const repo of repos) {
        if (await verifyStar(username, repo)) {
            starredCount++;
        }
    }
    return starredCount;
}

app.post('/claim-bounty', async (req, res) => {
    const { githubUsername, walletAddress } = req.body;
    
    if (!githubUsername || !walletAddress) {
        return res.status(400).json({ error: 'Missing githubUsername or walletAddress' });
    }

    if (walletAddress !== RTC_WALLET) {
        return res.status(400).json({ error: 'Invalid wallet address' });
    }

    if (bountyClaims[githubUsername]) {
        return res.status(400).json({ error: 'Bounty already claimed for this user' });
    }

    let totalReward = 0;
    const rewards = [];

    // Check Rustchain star
    const rustchainStarred = await verifyStar(githubUsername, RUSTCHAIN_REPO);
    if (rustchainStarred) {
        totalReward += 1;
        rewards.push({ action: 'Star Rustchain', reward: 1 });
    }

    // Check Scottcjn repos stars
    const scottcjnStars = await verifyScottcjnStars(githubUsername);
    if (scottcjnStars >= 10) {
        totalReward += scottcjnStars;
        rewards.push({ action: `Star ${scottcjnStars} Scottcjn repos`, reward: scottcjnStars });
    }

    // Check follow
    const isFollowing = await verifyFollow(githubUsername, SCOTTCJN_USERNAME);
    if (isFollowing) {
        totalReward += 1;
        rewards.push({ action: 'Follow @Scottcjn', reward: 1 });
    }

    // Check Star King badge
    const totalStars = await getUserStarCount(githubUsername);
    if (totalStars >= MIN_STARS_FOR_BADGE && isFollowing) {
        totalReward += 25;
        rewards.push({ action: 'Star King badge + 25 RTC bonus', reward: 25 });
    }

    if (totalReward === 0) {
        return res.status(400).json({ error: 'No eligible bounty actions found' });
    }

    // Record claim
    bountyClaims[githubUsername] = {
        claimedAt: new Date().toISOString(),
        totalReward,
        rewards
    };

    // Simulate RTC transfer (replace with actual blockchain transaction)
    console.log(`Transferring ${totalReward} RTC to ${walletAddress} for user ${githubUsername}`);

    res.json({
        success: true,
        githubUsername,
        walletAddress,
        totalReward,
        rewards,
        message: `Successfully claimed ${totalReward} RTC!`
    });
});

app.get('/bounty-status/:githubUsername', (req, res) => {
    const { githubUsername } = req.params;
    const claim = bountyClaims[githubUsername];
    if (!claim) {
        return res.json({ claimed: false, message: 'No bounty claimed yet' });
    }
    res.json({
        claimed: true,
        githubUsername,
        ...claim
    });
});

app.get('/repos', async (req, res) => {
    const repos = await getScottcjnRepos();
    res.json({ repos, count: repos.length });
});

app.listen(PORT, () => {
    console.log(`Bounty server running on port ${PORT}`);
    console.log(`RTC Wallet: ${RTC_WALLET}`);
});