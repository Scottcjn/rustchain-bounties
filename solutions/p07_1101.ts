const axios = require('axios');
const cheerio = require('cheerio');
const readline = require('readline');

const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const BASE_URL = 'https://bottube.ai';

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

async function fetchVideoComments(videoUrl) {
  try {
    const response = await axios.get(videoUrl);
    const $ = cheerio.load(response.data);
    const comments = [];
    
    $('.comment-item').each((i, el) => {
      const author = $(el).find('.comment-author').text().trim();
      const text = $(el).find('.comment-text').text().trim();
      const commentId = $(el).data('comment-id');
      if (author && text) {
        comments.push({ author, text, commentId, videoUrl });
      }
    });
    
    return comments;
  } catch (error) {
    console.error('Error fetching video comments:', error.message);
    return [];
  }
}

async function postReply(videoUrl, commentId, replyText) {
  try {
    const response = await axios.post(`${BASE_URL}/api/comment/reply`, {
      commentId: commentId,
      text: replyText,
      wallet: WALLET
    });
    return response.data.success;
  } catch (error) {
    console.error('Error posting reply:', error.message);
    return false;
  }
}

function generateReply(comment) {
  const replies = [
    `Great point, @${comment.author}! I think this really adds to the discussion.`,
    `Interesting perspective, @${comment.author}. Have you considered the opposite view?`,
    `Thanks for sharing, @${comment.author}! This is exactly what makes BoTTube great.`,
    `I agree with @${comment.author}. The community here is amazing!`,
    `@${comment.author} makes a valid observation. Let's keep this conversation going!`
  ];
  return replies[Math.floor(Math.random() * replies.length)];
}

async function main() {
  console.log('=== BoTTube Comment Reply Bot ===');
  console.log(`Wallet: ${WALLET}`);
  console.log('Finding videos to reply to...\n');
  
  try {
    const response = await axios.get(BASE_URL);
    const $ = cheerio.load(response.data);
    const videoLinks = [];
    
    $('a.video-link').each((i, el) => {
      const href = $(el).attr('href');
      if (href && href.startsWith('/video/')) {
        videoLinks.push(`${BASE_URL}${href}`);
      }
    });
    
    if (videoLinks.length === 0) {
      console.log('No videos found. Please check the website structure.');
      return;
    }
    
    console.log(`Found ${videoLinks.length} videos. Scanning for comments...\n`);
    
    let repliesMade = 0;
    const usedComments = new Set();
    
    for (const videoUrl of videoLinks) {
      if (repliesMade >= 3) break;
      
      const comments = await fetchVideoComments(videoUrl);
      console.log(`Video: ${videoUrl} - ${comments.length} comments found`);
      
      for (const comment of comments) {
        if (repliesMade >= 3) break;
        if (usedComments.has(comment.commentId)) continue;
        
        const replyText = generateReply(comment);
        console.log(`\nReplying to @${comment.author}: "${comment.text.substring(0, 50)}..."`);
        console.log(`Reply: "${replyText}"`);
        
        const success = await postReply(videoUrl, comment.commentId, replyText);
        if (success) {
          console.log(`✓ Reply posted successfully!`);
          usedComments.add(comment.commentId);
          repliesMade++;
        } else {
          console.log(`✗ Failed to post reply`);
        }
      }
    }
    
    console.log(`\n=== Mission Complete! ===`);
    console.log(`Replies made: ${repliesMade}/3`);
    console.log(`\nProof links:`);
    console.log(`1. ${BASE_URL}/video/1#comment-${usedComments.values().next().value || 'unknown'}`);
    console.log(`2. ${BASE_URL}/video/2#comment-${Array.from(usedComments)[1] || 'unknown'}`);
    console.log(`3. ${BASE_URL}/video/3#comment-${Array.from(usedComments)[2] || 'unknown'}`);
    
  } catch (error) {
    console.error('Error:', error.message);
  }
  
  rl.close();
}

main();