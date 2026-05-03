const express = require('express');
const axios = require('axios');
const { TronWeb } = require('tronweb');
const app = express();
const PORT = process.env.PORT || 3000;

// Tron configuration
const tronWeb = new TronWeb({
    fullNode: 'https://api.trongrid.io',
    solidityNode: 'https://api.trongrid.io',
    eventServer: 'https://api.trongrid.io',
    privateKey: process.env.TRON_PRIVATE_KEY
});

// Reward wallet address
const REWARD_WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';

// GitHub API configuration
const GITHUB_TOKEN = process.env.GITHUB_TOKEN;
const GITHUB_USERNAME = 'Scottcjn';
const RUSTCHAIN_REPO = 'Rustchain';

// In-memory tracking (replace with DB in production)
const userActions = {};

// Middleware
app.use(express.json());

// Verify GitHub action
async function verifyGitHubAction(username, actionType) {
    try {
        const headers = { Authorization: `token ${GITHUB_TOKEN}` };
        
        if (actionType === 'star_rustchain') {
            const response = await axios.get(
                `https://api.github.com/repos/${GITHUB_USERNAME}/${RUSTCHAIN_REPO}/stargazers`,
                { headers }
            );
            return response.data.some(user => user.login === username);
        }
        
        if (actionType === 'star_scottcjn') {
            const reposResponse = await axios.get(
                `https://api.github.com/users/${GITHUB_USERNAME}/repos?per_page=100`,
                { headers }
            );
            const starredCount = await Promise.all(
                reposResponse.data.map(repo =>
                    axios.get(
                        `https://api.github.com/repos/${GITHUB_USERNAME}/${repo.name}/stargazers`,
                        { headers }
                    ).then(res => res.data.some(user => user.login === username))
                )
            );
            return starredCount.filter(Boolean).length;
        }
        
        if (actionType === 'follow') {
            const response = await axios.get(
                `https://api.github.com/users/${GITHUB_USERNAME}/followers`,
                { headers }
            );
            return response.data.some(user => user.login === username);
        }
        
        return false;
    } catch (error) {
        console.error('GitHub verification error:', error);
        return false;
    }
}

// Send RTC reward
async function sendRTC(toAddress, amount) {
    try {
        const contract = await tronWeb.contract().at(process.env.RTC_CONTRACT_ADDRESS);
        const result = await contract.transfer(toAddress, tronWeb.toSun(amount)).send();
        return result;
    } catch (error) {
        console.error('RTC transfer error:', error);
        throw error;
    }
}

// Claim reward endpoint
app.post('/claim', async (req, res) => {
    const { username, walletAddress, actionType } = req.body;
    
    if (!username || !walletAddress || !actionType) {
        return res.status(400).json({ error: 'Missing required fields' });
    }
    
    // Check if already claimed
    const userKey = `${username}_${actionType}`;
    if (userActions[userKey]) {
        return res.status(400).json({ error: 'Already claimed this reward' });
    }
    
    try {
        let rewardAmount = 0;
        let actionVerified = false;
        
        switch(actionType) {
            case 'star_rustchain':
                actionVerified = await verifyGitHubAction(username, 'star_rustchain');
                rewardAmount = actionVerified ? 1 : 0;
                break;
                
            case 'star_scottcjn':
                const starredCount = await verifyGitHubAction(username, 'star_scottcjn');
                if (starredCount >= 10) {
                    rewardAmount = starredCount;
                    actionVerified = true;
                }
                break;
                
            case 'follow':
                actionVerified = await verifyGitHubAction(username, 'follow');
                rewardAmount = actionVerified ? 1 : 0;
                break;
                
            case 'star_king':
                const starredRepos = await verifyGitHubAction(username, 'star_scottcjn');
                const followed = await verifyGitHubAction(username, 'follow');
                if (starredRepos >= 100 && followed) {
                    rewardAmount = 25;
                    actionVerified = true;
                }
                break;
                
            default:
                return res.status(400).json({ error: 'Invalid action type' });
        }
        
        if (!actionVerified || rewardAmount === 0) {
            return res.status(400).json({ error: 'Action not verified' });
        }
        
        // Send reward
        const txId = await sendRTC(walletAddress, rewardAmount);
        
        // Record action
        userActions[userKey] = {
            timestamp: Date.now(),
            rewardAmount,
            txId
        };
        
        res.json({
            success: true,
            reward: rewardAmount,
            txId,
            message: `Successfully claimed ${rewardAmount} RTC`
        });
        
    } catch (error) {
        console.error('Claim error:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

// Check reward status
app.get('/status/:username', (req, res) => {
    const { username } = req.params;
    const userRewards = {};
    
    Object.keys(userActions).forEach(key => {
        if (key.startsWith(username)) {
            const actionType = key.replace(`${username}_`, '');
            userRewards[actionType] = userActions[key];
        }
    });
    
    res.json({ username, rewards: userRewards });
});

// Health check
app.get('/health', (req, res) => {
    res.json({ status: 'ok', timestamp: Date.now() });
});

app.listen(PORT, () => {
    console.log(`RTC Bounty Server running on port ${PORT}`);
});