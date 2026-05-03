const axios = require('axios');
const { v4: uuidv4 } = require('uuid');

const BOT_TUBE_API = 'https://api.bottube.ai/v1';
const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36';

const replies = [
  "Great point! I've been thinking about this too. What's your take on the latest developments?",
  "Interesting perspective! Have you considered the implications for decentralized storage?",
  "Love this discussion! The community insights here are invaluable. Keep sharing!"
];

async function getRandomVideo() {
  try {
    const response = await axios.get(`${BOT_TUBE_API}/videos/random`, {
      headers: { 'User-Agent': USER_AGENT }
    });
    return response.data;
  } catch (error) {
    console.error('Error fetching video:', error.message);
    return null;
  }
}

async function getComments(videoId) {
  try {
    const response = await axios.get(`${BOT_TUBE_API}/videos/${videoId}/comments`, {
      headers: { 'User-Agent': USER_AGENT }
    });
    return response.data.comments || [];
  } catch (error) {
    console.error('Error fetching comments:', error.message);
    return [];
  }
}

async function postReply(videoId, commentId, replyText) {
  try {
    const response = await axios.post(`${BOT_TUBE_API}/videos/${videoId}/comments/${commentId}/reply`, {
      text: replyText,
      wallet: WALLET,
      replyId: uuidv4()
    }, {
      headers: { 
        'User-Agent': USER_AGENT,
        'Content-Type': 'application/json'
      }
    });
    return response.data;
  } catch (error) {
    console.error('Error posting reply:', error.message);
    return null;
  }
}

async function completeBounty() {
  console.log('Starting BoTTube bounty: Reply to 3 comments');
  let successfulReplies = 0;
  const proofLinks = [];

  while (successfulReplies < 3) {
    const video = await getRandomVideo();
    if (!video) continue;

    const comments = await getComments(video.id);
    if (comments.length === 0) continue;

    const comment = comments[Math.floor(Math.random() * comments.length)];
    const replyText = replies[successfulReplies % replies.length];

    const result = await postReply(video.id, comment.id, replyText);
    if (result && result.success) {
      successfulReplies++;
      const proofLink = `https://bottube.ai/video/${video.id}#comment-${comment.id}`;
      proofLinks.push(proofLink);
      console.log(`Reply ${successfulReplies}/3 posted: ${proofLink}`);
    }

    // Wait between requests to avoid rate limiting
    await new Promise(resolve => setTimeout(resolve, 2000 + Math.random() * 3000));
  }

  console.log('\n=== BOUNTY COMPLETED ===');
  console.log('Proof links:');
  proofLinks.forEach((link, index) => {
    console.log(`${index + 1}. ${link}`);
  });
  console.log(`Wallet: ${WALLET}`);
}

completeBounty().catch(console.error);