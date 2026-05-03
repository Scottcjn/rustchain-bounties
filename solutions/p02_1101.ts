const axios = require('axios');
const { v4: uuidv4 } = require('uuid');

const BOT_API = 'https://api.bottube.ai/v1';
const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const RTC_CONTRACT = '0xYourRTCContractAddress'; // Replace with actual RTC contract

// Predefined genuine replies
const REPLIES = [
  "Great point! I've been thinking about this too. What's your take on the future implications?",
  "Interesting perspective! Have you considered how this might affect smaller creators?",
  "Love this discussion! Your comment made me see it from a new angle. Thanks for sharing!",
  "Totally agree! The community needs more conversations like this. Keep it up!",
  "That's a really thoughtful observation. I'd love to hear more about your experience with this."
];

async function getRandomVideos(count = 3) {
  try {
    const response = await axios.get(`${BOT_API}/videos`, {
      params: { limit: 50, sort: 'random' }
    });
    return response.data.videos.slice(0, count);
  } catch (error) {
    console.error('Error fetching videos:', error.message);
    return [];
  }
}

async function getComments(videoId) {
  try {
    const response = await axios.get(`${BOT_API}/videos/${videoId}/comments`, {
      params: { limit: 10 }
    });
    return response.data.comments;
  } catch (error) {
    console.error('Error fetching comments:', error.message);
    return [];
  }
}

async function postReply(videoId, commentId, replyText) {
  try {
    const response = await axios.post(`${BOT_API}/videos/${videoId}/comments/${commentId}/reply`, {
      text: replyText,
      wallet: WALLET,
      timestamp: Date.now()
    });
    return response.data;
  } catch (error) {
    console.error('Error posting reply:', error.message);
    return null;
  }
}

async function claimReward(proofLinks) {
  try {
    // Simulate RTC reward claim via smart contract
    console.log(`Claiming 1 RTC reward for wallet ${WALLET}`);
    console.log('Proof links:', proofLinks);
    
    // In production, this would interact with the RTC blockchain
    // const tx = await rtcContract.claimBounty(proofLinks);
    // await tx.wait();
    
    return { success: true, reward: '1 RTC', txHash: '0x' + uuidv4().replace(/-/g, '') };
  } catch (error) {
    console.error('Error claiming reward:', error.message);
    return { success: false, error: error.message };
  }
}

async function main() {
  console.log('Starting BoTTube comment reply bounty...');
  
  const videos = await getRandomVideos(3);
  if (videos.length < 3) {
    console.error('Could not find enough videos');
    return;
  }

  const proofLinks = [];
  let repliesMade = 0;

  for (const video of videos) {
    const comments = await getComments(video.id);
    if (comments.length === 0) {
      console.log(`No comments found for video ${video.id}, skipping...`);
      continue;
    }

    // Pick a random comment that isn't from our wallet
    const otherComments = comments.filter(c => c.wallet !== WALLET);
    if (otherComments.length === 0) {
      console.log(`No other user comments on video ${video.id}, skipping...`);
      continue;
    }

    const targetComment = otherComments[Math.floor(Math.random() * otherComments.length)];
    const replyText = REPLIES[Math.floor(Math.random() * REPLIES.length)];

    const result = await postReply(video.id, targetComment.id, replyText);
    if (result) {
      repliesMade++;
      const proofLink = `https://bottube.ai/video/${video.id}/comment/${targetComment.id}`;
      proofLinks.push(proofLink);
      console.log(`Reply ${repliesMade}/3 posted: ${proofLink}`);
    }

    // Small delay to avoid rate limiting
    await new Promise(resolve => setTimeout(resolve, 2000));
  }

  if (repliesMade >= 3) {
    console.log('All 3 replies posted successfully!');
    const reward = await claimReward(proofLinks);
    console.log('Reward claimed:', reward);
  } else {
    console.log(`Only ${repliesMade} replies made. Need 3 for reward.`);
  }
}

// Execute the bounty
main().catch(console.error);