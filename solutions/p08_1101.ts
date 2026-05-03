const puppeteer = require('puppeteer');
const fs = require('fs');

const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const BASE_URL = 'https://bottube.ai';
const REPLIES_FILE = 'replies.json';

const replies = [
  "Great point! I hadn't thought of it that way. What other examples come to mind?",
  "Interesting perspective! Have you tried applying this to your own workflow?",
  "Totally agree! The community insights here are gold. Thanks for sharing!",
  "This is exactly what I was looking for. How did you come up with that approach?",
  "Love the discussion! Could you elaborate on the second part?",
  "Solid take. I've been experimenting with similar ideas and it works well.",
  "Thanks for the input! What resources would you recommend for beginners?",
  "That's a clever observation. Do you think it scales to larger projects?",
  "Nice! I'm going to try this out. Any pitfalls to watch for?",
  "Appreciate the detailed comment. It really adds to the conversation."
];

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

function getRandomReply() {
  return replies[Math.floor(Math.random() * replies.length)];
}

async function postReply(page, commentId, replyText) {
  const replyButton = await page.$(`[data-comment-id="${commentId}"] .reply-button`);
  if (!replyButton) {
    console.log(`Reply button not found for comment ${commentId}`);
    return false;
  }
  await replyButton.click();
  await sleep(1000);
  const textarea = await page.$('.reply-textarea');
  if (!textarea) {
    console.log('Reply textarea not found');
    return false;
  }
  await textarea.type(replyText, { delay: 50 });
  await sleep(500);
  const submitButton = await page.$('.submit-reply');
  if (!submitButton) {
    console.log('Submit button not found');
    return false;
  }
  await submitButton.click();
  await sleep(2000);
  return true;
}

async function main() {
  const browser = await puppeteer.launch({ headless: false });
  const page = await browser.newPage();
  await page.goto(BASE_URL, { waitUntil: 'networkidle2' });
  await sleep(3000);

  // Get video links
  const videoLinks = await page.$$eval('a.video-link', links => links.map(link => link.href));
  if (videoLinks.length < 3) {
    console.log('Not enough videos found');
    await browser.close();
    return;
  }

  const selectedVideos = videoLinks.slice(0, 3);
  const postedReplies = [];

  for (let i = 0; i < selectedVideos.length; i++) {
    const videoUrl = selectedVideos[i];
    console.log(`Processing video ${i + 1}: ${videoUrl}`);
    await page.goto(videoUrl, { waitUntil: 'networkidle2' });
    await sleep(3000);

    // Get comments
    const comments = await page.$$eval('.comment', comments => comments.map(comment => ({
      id: comment.getAttribute('data-comment-id'),
      text: comment.querySelector('.comment-text')?.textContent?.trim()
    })));

    if (comments.length === 0) {
      console.log('No comments found on this video');
      continue;
    }

    const comment = comments[0]; // Reply to first comment
    const replyText = getRandomReply();
    const success = await postReply(page, comment.id, replyText);
    if (success) {
      postedReplies.push({
        videoUrl,
        commentId: comment.id,
        replyText,
        timestamp: new Date().toISOString()
      });
      console.log(`Replied to comment ${comment.id} on video ${i + 1}`);
    }
    await sleep(2000);
  }

  // Save proof
  fs.writeFileSync(REPLIES_FILE, JSON.stringify(postedReplies, null, 2));
  console.log(`Posted ${postedReplies.length} replies. Proof saved to ${REPLIES_FILE}`);

  await browser.close();
}

main().catch(console.error);