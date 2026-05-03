const axios = require('axios');
const { v4: uuidv4 } = require('uuid');

const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const BOT_API = 'https://bottube.ai/api';
const USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36';

const replies = [
  'Great point! I never thought of it that way. What other examples have you seen?',
  'Interesting take! Have you tried implementing this approach yourself?',
  'Totally agree! The community really benefits from discussions like this.'
];

async function getRandomVideo() {
  const res = await axios.get(`${BOT_API}/videos?limit=50`, {
    headers: { 'User-Agent': USER_AGENT }
  });
  const videos = res.data.videos || [];
  return videos[Math.floor(Math.random() * videos.length)];
}

async function getComments(videoId) {
  const res = await axios.get(`${BOT_API}/videos/${videoId}/comments`, {
    headers: { 'User-Agent': USER_AGENT }
  });
  return res.data.comments || [];
}

async function replyToComment(videoId, commentId, text) {
  const payload = {
    commentId,
    videoId,
    text,
    wallet: WALLET,
    timestamp: Date.now(),
    nonce: uuidv4()
  };
  const res = await axios.post(`${BOT_API}/comments/reply`, payload, {
    headers: { 'User-Agent': USER_AGENT, 'Content-Type': 'application/json' }
  });
  return res.data;
}

async function main() {
  const proofLinks = [];
  let attempts = 0;
  const maxAttempts = 20;

  while (proofLinks.length < 3 && attempts < maxAttempts) {
    attempts++;
    try {
      const video = await getRandomVideo();
      if (!video || !video.id) continue;

      const comments = await getComments(video.id);
      if (!comments || comments.length === 0) continue;

      const comment = comments[Math.floor(Math.random() * comments.length)];
      if (!comment || !comment.id) continue;

      const replyText = replies[proofLinks.length % replies.length];
      const result = await replyToComment(video.id, comment.id, replyText);

      if (result && result.success) {
        const link = `https://bottube.ai/video/${video.id}?comment=${comment.id}`;
        proofLinks.push(link);
        console.log(`Replied to comment ${comment.id} on video ${video.id}`);
        console.log(`Proof: ${link}`);
      }
    } catch (err) {
      console.error(`Attempt ${attempts} failed:`, err.message);
    }
  }

  console.log('\n=== FINAL PROOF ===');
  proofLinks.forEach((link, i) => console.log(`${i + 1}. ${link}`));
  console.log(`Wallet: ${WALLET}`);
}

main().catch(console.error);