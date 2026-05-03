const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const WALLET = 'TU8NBT5iGyMNkLwWmWmgy7tFMbKnafLHcu';
const BASE_URL = 'https://bottube.ai';

const replies = [
  'Great point! I think this really adds value to the discussion.',
  'Interesting perspective! Have you considered the opposite view?',
  'Thanks for sharing your thoughts! This is exactly why I love this community.'
];

async function sleep(ms) {
  return new Promise(resolve => setTimeout(resolve, ms));
}

async function getRandomVideoUrl(page) {
  await page.goto(BASE_URL, { waitUntil: 'networkidle2', timeout: 30000 });
  await sleep(2000);
  
  const videoLinks = await page.$$eval('a[href*="/video/"]', links => 
    links.map(link => link.href)
  );
  
  if (videoLinks.length === 0) {
    throw new Error('No video links found on homepage');
  }
  
  const uniqueLinks = [...new Set(videoLinks)];
  return uniqueLinks[Math.floor(Math.random() * uniqueLinks.length)];
}

async function findAndReplyToComment(page, videoUrl, replyText) {
  await page.goto(videoUrl, { waitUntil: 'networkidle2', timeout: 30000 });
  await sleep(3000);
  
  // Find existing comments
  const commentElements = await page.$$('.comment-item, .comment, [class*="comment"]');
  
  if (commentElements.length === 0) {
    throw new Error('No comments found on this video');
  }
  
  // Pick a random comment
  const randomIndex = Math.floor(Math.random() * commentElements.length);
  const targetComment = commentElements[randomIndex];
  
  // Click reply button on that comment
  const replyButton = await targetComment.$('button:has-text("Reply"), .reply-btn, [class*="reply"]');
  if (!replyButton) {
    throw new Error('No reply button found on selected comment');
  }
  
  await replyButton.click();
  await sleep(1000);
  
  // Type reply
  const textarea = await page.$('textarea, [contenteditable="true"], .reply-input');
  if (!textarea) {
    throw new Error('No input field found for reply');
  }
  
  await textarea.type(replyText, { delay: 50 });
  await sleep(500);
  
  // Submit reply
  const submitButton = await page.$('button[type="submit"], .submit-reply, button:has-text("Post"), button:has-text("Reply")');
  if (!submitButton) {
    throw new Error('No submit button found');
  }
  
  await submitButton.click();
  await sleep(2000);
  
  // Get the current URL after reply (might redirect)
  const currentUrl = page.url();
  return currentUrl;
}

async function main() {
  console.log('Starting BoTTube comment reply bot...');
  console.log(`Wallet: ${WALLET}`);
  
  const browser = await puppeteer.launch({
    headless: false,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  
  const page = await browser.newPage();
  await page.setViewport({ width: 1280, height: 800 });
  
  const replyLinks = [];
  
  try {
    for (let i = 0; i < 3; i++) {
      console.log(`\n--- Reply ${i + 1} of 3 ---`);
      
      let success = false;
      let attempts = 0;
      
      while (!success && attempts < 5) {
        try {
          const videoUrl = await getRandomVideoUrl(page);
          console.log(`Found video: ${videoUrl}`);
          
          const replyText = replies[i % replies.length];
          const replyUrl = await findAndReplyToComment(page, videoUrl, replyText);
          
          console.log(`Successfully replied! URL: ${replyUrl}`);
          replyLinks.push(replyUrl);
          success = true;
          
          // Wait between replies
          if (i < 2) {
            await sleep(5000);
          }
        } catch (error) {
          attempts++;
          console.log(`Attempt ${attempts} failed: ${error.message}`);
          await sleep(3000);
        }
      }
      
      if (!success) {
        console.log(`Failed to complete reply ${i + 1} after 5 attempts`);
      }
    }
    
    console.log('\n=== All replies completed ===');
    console.log('Reply links:');
    replyLinks.forEach((link, index) => {
      console.log(`${index + 1}. ${link}`);
    });
    
    // Save proof to file
    const proofContent = `BoTTube Comment Replies - ${new Date().toISOString()}\nWallet: ${WALLET}\n\n${replyLinks.map((link, i) => `${i+1}. ${link}`).join('\n')}`;
    fs.writeFileSync(path.join(__dirname, 'proof.txt'), proofContent);
    console.log('\nProof saved to proof.txt');
    
  } catch (error) {
    console.error('Fatal error:', error);
  } finally {
    await browser.close();
  }
}

main().catch(console.error);