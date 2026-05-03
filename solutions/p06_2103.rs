const express = require('express');
const axios = require('axios');
const cors = require('cors');
const app = express();
const PORT = process.env.PORT || 3000;

app.use(cors());
app.use(express.json());

const RTC_TOKEN = process.env.RTC_TOKEN || 'your-rtc-token-here';
const RTC_API_URL = 'https://api.rtc.network/v1/transactions';
const GITHUB_TOKEN = process.env.GITHUB_TOKEN || 'your-github-token-here';
const GITHUB_USERNAME = 'Scottcjn';
const WALLET_ADDRESS = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';

const REWARDS = {
    STAR_RUSTCHAIN: 1,
    STAR_SCOTTCJN: 1,
    FOLLOW_SCOTTCJN: 1,
    STAR_KING_BONUS: 25
};

const STAR_KING_THRESHOLD = 100;

app.post('/verify-and-reward', async (req, res) => {
    const { githubUsername } = req.body;
    
    if (!githubUsername) {
        return res.status(400).json({ error: 'GitHub username required' });
    }

    try {
        const rewards = [];
        let totalStars = 0;

        // Check if user starred Rustchain repo
        const rustchainStarred = await checkStarredRepo(githubUsername, 'Rustchain');
        if (rustchainStarred) {
            rewards.push({ action: 'Star Rustchain repo', reward: REWARDS.STAR_RUSTCHAIN });
        }

        // Get all repos for Scottcjn
        const repos = await getAllRepos(GITHUB_USERNAME);
        let scottcjnStars = 0;

        for (const repo of repos) {
            const starred = await checkStarredRepo(githubUsername, repo.name);
            if (starred) {
                scottcjnStars++;
                totalStars++;
            }
        }

        if (scottcjnStars >= 10) {
            rewards.push({ action: `Star ${scottcjnStars} Scottcjn repos`, reward: scottcjnStars * REWARDS.STAR_SCOTTCJN });
        }

        // Check if user followed Scottcjn
        const followed = await checkFollow(githubUsername, GITHUB_USERNAME);
        if (followed) {
            rewards.push({ action: 'Follow @Scottcjn', reward: REWARDS.FOLLOW_SCOTTCJN });
        }

        // Check Star King badge
        if (totalStars >= STAR_KING_THRESHOLD && followed) {
            rewards.push({ action: 'Star King badge + bonus', reward: REWARDS.STAR_KING_BONUS });
        }

        if (rewards.length === 0) {
            return res.status(200).json({ message: 'No rewards earned. Complete the required actions.', rewards: [] });
        }

        // Calculate total RTC reward
        const totalReward = rewards.reduce((sum, r) => sum + r.reward, 0);

        // Send RTC transaction
        const txResult = await sendRTCReward(githubUsername, totalReward);

        res.status(200).json({
            message: `Reward of ${totalReward} RTC sent to ${WALLET_ADDRESS}`,
            rewards,
            totalReward,
            transaction: txResult
        });

    } catch (error) {
        console.error('Error processing rewards:', error);
        res.status(500).json({ error: 'Internal server error' });
    }
});

async function checkStarredRepo(username, repoName) {
    try {
        const response = await axios.get(
            `https://api.github.com/users/${username}/starred`,
            {
                headers: {
                    Authorization: `token ${GITHUB_TOKEN}`,
                    Accept: 'application/vnd.github.v3+json'
                },
                params: { per_page: 100 }
            }
        );

        return response.data.some(repo => repo.name === repoName && repo.owner.login === GITHUB_USERNAME);
    } catch (error) {
        console.error(`Error checking starred repo ${repoName}:`, error);
        return false;
    }
}

async function getAllRepos(username) {
    try {
        const response = await axios.get(
            `https://api.github.com/users/${username}/repos`,
            {
                headers: {
                    Authorization: `token ${GITHUB_TOKEN}`,
                    Accept: 'application/vnd.github.v3+json'
                },
                params: { per_page: 100, type: 'owner' }
            }
        );
        return response.data;
    } catch (error) {
        console.error('Error fetching repos:', error);
        return [];
    }
}

async function checkFollow(follower, following) {
    try {
        const response = await axios.get(
            `https://api.github.com/users/${follower}/following`,
            {
                headers: {
                    Authorization: `token ${GITHUB_TOKEN}`,
                    Accept: 'application/vnd.github.v3+json'
                },
                params: { per_page: 100 }
            }
        );

        return response.data.some(user => user.login === following);
    } catch (error) {
        console.error(`Error checking follow status:`, error);
        return false;
    }
}

async function sendRTCReward(username, amount) {
    try {
        const response = await axios.post(
            RTC_API_URL,
            {
                to: WALLET_ADDRESS,
                amount: amount,
                token: RTC_TOKEN,
                memo: `Reward for ${username} - Star & Follow bounty`
            },
            {
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${RTC_TOKEN}`
                }
            }
        );
        return response.data;
    } catch (error) {
        console.error('Error sending RTC reward:', error);
        throw new Error('Failed to send RTC reward');
    }
}

app.listen(PORT, () => {
    console.log(`Star & Follow Bounty server running on port ${PORT}`);
});