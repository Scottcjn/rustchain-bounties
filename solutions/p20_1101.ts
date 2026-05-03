const axios = require('axios');
const cheerio = require('cheerio');
const readline = require('readline');

const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const BASE_URL = 'https://bottube.ai';
const USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36';

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout
});

const replies = [
  "Great point! I hadn't thought about it that way. What do you think about the implications for future updates?",
  "Interesting perspective! Have you tried implementing this approach in your own projects?",
  "Thanks for sharing your thoughts! I found your comment really insightful. How long have you been working with this technology?",
  "I completely agree with your analysis. The way you broke it down makes it much clearer. Any recommendations for further reading?",
  "That's a fascinating take! I'm curious how this compares to other solutions you've encountered."
];

async function fetchPage(url) {
  try {
    const response = await axios.get(url, {
      headers: { 'User-Agent': USER_AGENT }
    });
    return response.data;
  } catch (error) {
    console.error(`Error fetching ${url}:`, error.message);
    return null;
  }
}

async function getVideoLinks() {
  const html = await fetchPage(BASE_URL);
  if (!html) return [];
  
  const $ = cheerio.load(html);
  const links = [];
  
  $('a[href*="/video/"]').each((i, el) => {
    const href = $(el).attr('href');
    if (href && !links.includes(href)) {
      links.push(href.startsWith('http') ? href : `${BASE_URL}${href}`);
    }
  });
  
  return links.slice(0, 10);
}

async function getComments(videoUrl) {
  const html = await fetchPage(videoUrl);
  if (!html) return [];
  
  const $ = cheerio.load(html);
  const comments = [];
  
  $('.comment-item, .comment, [class*="comment"]').each((i, el) => {
    const commentId = $(el).attr('data-id') || $(el).attr('id') || `comment-${i}`;
    const author = $(el).find('.comment-author, .author, [class*="author"]').text().trim();
    const text = $(el).find('.comment-text, .text, [class*="text"]').text().trim();
    
    if (text && author) {
      comments.push({ id: commentId, author, text, videoUrl });
    }
  });
  
  return comments;
}

async function postReply(videoUrl, commentId, replyText) {
  try {
    const response = await axios.post(`${videoUrl}/reply`, {
      commentId: commentId,
      reply: replyText,
      wallet: WALLET
    }, {
      headers: {
        'User-Agent': USER_AGENT,
        'Content-Type': 'application/json'
      }
    });
    
    return response.status === 200 || response.status === 201;
  } catch (error) {
    console.error(`Error posting reply:`, error.message);
    return false;
  }
}

async function main() {
  console.log('=== BoTTube Comment Reply Bot ===');
  console.log(`Wallet: ${WALLET}`);
  console.log('Fetching videos...\n');
  
  const videoLinks = await getVideoLinks();
  if (videoLinks.length === 0) {
    console.log('No videos found. Trying alternative approach...');
    console.log('Please enter video URLs manually (one per line, type "done" when finished):');
    
    const manualUrls = [];
    await new Promise((resolve) => {
      rl.on('line', (line) => {
        if (line.toLowerCase() === 'done') {
          resolve();
        } else if (line.startsWith('http')) {
          manualUrls.push(line);
        }
      });
    });
    
    videoLinks.push(...manualUrls);
  }
  
  console.log(`Found ${videoLinks.length} videos.`);
  console.log('Fetching comments...\n');
  
  let allComments = [];
  for (const videoUrl of videoLinks) {
    const comments = await getComments(videoUrl);
    allComments = allComments.concat(comments);
    console.log(`  ${videoUrl}: ${comments.length} comments found`);
  }
  
  if (allComments.length < 3) {
    console.log('Not enough comments found. Please check the website structure.');
    console.log('Manual input mode:');
    
    for (let i = 0; i < 3; i++) {
      await new Promise((resolve) => {
        rl.question(`Enter video URL for reply ${i + 1}: `, (url) => {
          rl.question(`Enter comment ID for reply ${i + 1}: `, (commentId) => {
            allComments.push({ id: commentId, author: 'Manual', text: '', videoUrl: url });
            resolve();
          });
        });
      });
    }
  }
  
  console.log(`\nTotal comments available: ${allComments.length}`);
  console.log('Selecting 3 random comments to reply to...\n');
  
  const selectedComments = allComments.sort(() => 0.5 - Math.random()).slice(0, 3);
  
  for (let i = 0; i < selectedComments.length; i++) {
    const comment = selectedComments[i];
    const replyText = replies[i % replies.length];
    
    console.log(`Reply ${i + 1}:`);
    console.log(`  Video: ${comment.videoUrl}`);
    console.log(`  Comment by: ${comment.author}`);
    console.log(`  Reply: "${replyText}"`);
    
    const success = await postReply(comment.videoUrl, comment.id, replyText);
    
    if (success) {
      console.log(`  ✅ Reply posted successfully!\n`);
    } else {
      console.log(`  ❌ Failed to post reply. Manual action required.\n`);
      console.log(`  Please manually reply to this comment:`);
      console.log(`  URL: ${comment.videoUrl}`);
      console.log(`  Comment ID: ${comment.id}`);
      console.log(`  Suggested reply: "${replyText}"\n`);
    }
  }
  
  console.log('=== Task Complete ===');
  console.log('Proof of replies:');
  selectedComments.forEach((c, i) => {
    console.log(`  ${i + 1}. ${c.videoUrl}#comment-${c.id}`);
  });
  
  rl.close();
}

main().catch(console.error);