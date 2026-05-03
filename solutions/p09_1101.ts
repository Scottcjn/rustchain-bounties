const axios = require('axios');
const { v4: uuidv4 } = require('uuid');

const BOT_API = 'https://bottube.ai/api';
const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';

const replies = [
  'Great point! I never thought about it that way. What inspired you to comment?',
  'Interesting take! Have you tried applying this in a real project?',
  'Totally agree! This is exactly what the community needs more of.'
];

async function getRandomVideos() {
  const res = await axios.get(`${BOT_API}/videos?limit=10`);
  return res.data.videos;
}

async function getComments(videoId) {
  const res = await axios.get(`${BOT_API}/videos/${videoId}/comments`);
  return res.data.comments;
}

async function postReply(videoId, commentId, text) {
  const payload = {
    wallet: WALLET,
    commentId,
    text,
    timestamp: Date.now(),
    nonce: uuidv4()
  };
  const res = await axios.post(`${BOT_API}/videos/${videoId}/comments/${commentId}/reply`, payload);
  return res.data;
}

async function main() {
  const videos = await getRandomVideos();
  let replied = 0;

  for (const video of videos) {
    if (replied >= 3) break;
    const comments = await getComments(video.id);
    const externalComments = comments.filter(c => c.wallet !== WALLET);
    if (externalComments.length === 0) continue;

    const targetComment = externalComments[0];
    const replyText = replies[replied % replies.length];
    const result = await postReply(video.id, targetComment.id, replyText);
    console.log(`Replied to ${targetComment.id} on video ${video.id}: ${result.status}`);
    replied++;
  }

  if (replied === 3) {
    console.log('Bounty completed! Proof links:');
    // In production, you'd store and output the actual links
  } else {
    console.log('Could not find enough comments to reply to.');
  }
}

main().catch(console.error);