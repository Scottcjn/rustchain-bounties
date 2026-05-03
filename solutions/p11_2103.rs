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
const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;

async function verifyStars(username) {
    try {
        const repos = await axios.get(`https://api.github.com/users/${username}/repos?per_page=100`, {
            headers: { Authorization: `token ${GITHUB_TOKEN}` }
        });
        
        const starredRepos = repos.data.filter(repo => repo.stargazers_count > 0);
        return starredRepos.length;
    } catch (error) {
        console.error('Error fetching repos:', error);
        return 0;
    }
}

async function verifyFollow(username, targetUsername) {
    try {
        const response = await axios.get(`https://api.github.com/users/${username}/following`, {
            headers: { Authorization: `token ${GITHUB_TOKEN}` }
        });
        return response.data.some(user => user.login === targetUsername);
    } catch (error) {
        console.error('Error checking follow:', error);
        return false;
    }
}

async function sendRTC(to, amount) {
    try {
        const contract = await tronWeb.contract().at(RTC_CONTRACT);
        const result = await contract.transfer(to, tronWeb.toSun(amount)).send();
        return result;
    } catch (error) {
        console.error('Error sending RTC:', error);
        throw error;
    }
}

app.post('/claim', async (req, res) => {
    const { username, wallet } = req.body;
    
    if (!username || !wallet) {
        return res.status(400).json({ error: 'Missing username or wallet' });
    }

    try {
        const starCount = await verifyStars(username);
        const isFollowing = await verifyFollow(username, 'Scottcjn');
        
        let reward = 0;
        let badge = null;

        // Base rewards
        if (starCount >= 1) reward += 1; // Star Rustchain
        if (starCount >= 10) reward += Math.min(starCount, 100); // Star Scottcjn repos
        if (isFollowing) reward += 1; // Follow Scottcjn

        // Star King bonus
        if (starCount >= 100 && isFollowing) {
            reward += 25;
            badge = 'Star King';
        }

        if (reward > 0) {
            await sendRTC(wallet, reward);
            return res.json({ 
                success: true, 
                reward: `${reward} RTC`, 
                badge: badge,
                txHash: 'sent'
            });
        } else {
            return res.json({ 
                success: false, 
                message: 'No qualifying actions found. Please star repos and follow @Scottcjn.'
            });
        }
    } catch (error) {
        console.error('Error processing claim:', error);
        return res.status(500).json({ error: 'Internal server error' });
    }
});

app.get('/check/:username', async (req, res) => {
    const { username } = req.params;
    
    try {
        const starCount = await verifyStars(username);
        const isFollowing = await verifyFollow(username, 'Scottcjn');
        
        let reward = 0;
        let badge = null;

        if (starCount >= 1) reward += 1;
        if (starCount >= 10) reward += Math.min(starCount, 100);
        if (isFollowing) reward += 1;
        if (starCount >= 100 && isFollowing) {
            reward += 25;
            badge = 'Star King';
        }

        return res.json({
            username,
            starCount,
            isFollowing,
            potentialReward: `${reward} RTC`,
            badge: badge
        });
    } catch (error) {
        console.error('Error checking status:', error);
        return res.status(500).json({ error: 'Internal server error' });
    }
});

const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log(`Bounty server running on port ${PORT}`);
});